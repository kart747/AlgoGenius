"""
Quick script to create test submissions for testing GET /api/submissions/me
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "testpass123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("🔑 Logged in successfully\n")

# Get a problem ID (let's assume problem 1 exists)
problems_response = requests.get(f"{BASE_URL}/problems")
if problems_response.status_code == 200:
    problems = problems_response.json()
    if problems:
        problem_id = problems[0]["id"]
        print(f"📝 Using problem ID: {problem_id} - {problems[0]['title']}\n")
    else:
        print("⚠️  No problems found. Creating a test problem first...")
        # You may need to create a problem first or use admin endpoints
        problem_id = 1
else:
    problem_id = 1

# Submit some test code
print("📤 Submitting test code...\n")

submissions = [
    {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    },
    {
        "problem_id": problem_id,
        "language": "cpp",
        "code": "#include <iostream>\nusing namespace std;\nint main() { int a, b; cin >> a >> b; cout << a + b; return 0; }"
    },
    {
        "problem_id": problem_id,
        "language": "java",
        "code": "import java.util.*;\npublic class Solution { public static void main(String[] args) { Scanner sc = new Scanner(System.in); int a = sc.nextInt(); int b = sc.nextInt(); System.out.println(a + b); } }"
    }
]

for i, submission in enumerate(submissions, 1):
    try:
        response = requests.post(
            f"{BASE_URL}/submissions",
            json=submission,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Submission {i} ({submission['language']}): {result['status']}")
        else:
            print(f"❌ Submission {i} failed: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Submission {i} error: {e}")

print("\n✅ Test submissions created!")
print("\nNow run: python test_submissions_me.py")
