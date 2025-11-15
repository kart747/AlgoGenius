import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def load_test_credentials():
    """Load test credentials from file"""
    if os.path.exists("test_credentials.json"):
        with open("test_credentials.json", "r") as f:
            creds = json.load(f)
            return creds["email"], creds["password"]
    return None, None

def test_multiple_submissions():
    """Test XP accumulation with multiple submissions"""
    print("🎮 TESTING MULTIPLE SUBMISSIONS & XP ACCUMULATION\n")
    
    # Login
    email, password = load_test_credentials()
    if not email:
        print("❌ No test credentials found. Run create_fresh_test_user.py first.")
        return
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get initial profile
    profile = requests.get(f"{BASE_URL}/users/me", headers=headers).json()
    print(f"📊 Initial State:")
    print(f"   XP: {profile['xp']}")
    print(f"   Streak: {profile['current_streak']}")
    print(f"   Last submission: {profile['last_submission_date']}\n")
    
    # Get problems
    problems = requests.get(f"{BASE_URL}/problems").json()
    
    # Submit solutions to multiple problems
    print("🚀 Submitting multiple solutions...\n")
    
    test_cases = [
        {
            "problem_id": 1,
            "code": "a, b = map(int, input().split())\nprint(a + b)",
            "name": "Two Sum"
        },
        {
            "problem_id": 2,
            "code": "a, b = map(int, input().split())\nprint(a * b)",
            "name": "Multiply"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        if test["problem_id"] <= len(problems):
            print(f"Submission #{i}: {test['name']}")
            response = requests.post(
                f"{BASE_URL}/submissions/",
                headers=headers,
                json={
                    "problem_id": test["problem_id"],
                    "language": "python",
                    "code": test["code"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['status']}: {result['message']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
            print()
    
    # Get updated profile
    updated_profile = requests.get(f"{BASE_URL}/users/me", headers=headers).json()
    print(f"📊 Final State:")
    print(f"   XP: {updated_profile['xp']} (+{updated_profile['xp'] - profile['xp']})")
    print(f"   Streak: {updated_profile['current_streak']}")
    print(f"   Last submission: {updated_profile['last_submission_date']}\n")
    
    # Get submission history
    history = requests.get(f"{BASE_URL}/users/me/submissions", headers=headers).json()
    print(f"📜 Submission History ({len(history)} total):")
    for sub in history[:5]:
        print(f"   [{sub['submission_id']}] {sub['problem_title']} - {sub['status']}")
    
    # Check leaderboard position
    leaderboard = requests.get(f"{BASE_URL}/users/leaderboard").json()
    print(f"\n🏆 Leaderboard Position:")
    for rank, user in enumerate(leaderboard[:3], 1):
        marker = "👑" if user['username'] == updated_profile['username'] else "  "
        print(f"   {marker} #{rank} {user['username']} - {user['xp']} XP")

if __name__ == "__main__":
    test_multiple_submissions()
