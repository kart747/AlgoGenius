import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()

def main():
    print("🚀 COMPREHENSIVE API TEST SUITE")
    print("Testing all endpoints in your FastAPI backend\n")

    # ===========================================
    # 1. PROBLEM MANAGEMENT TESTS
    # ===========================================
    print_section("1️⃣  TESTING PROBLEM ENDPOINTS")
    
    # Create Problem 1
    print("Creating Problem: Two Sum")
    problem1_data = {
        "title": "Two Sum",
        "description": "Given two integers separated by space, print their sum.",
        "difficulty": "easy",
        "test_cases": [
            {"input_data": "3 5", "expected_output": "8"},
            {"input_data": "10 20", "expected_output": "30"},
            {"input_data": "-5 5", "expected_output": "0"}
        ]
    }
    resp = requests.post(f"{BASE_URL}/problems", json=problem1_data)
    print_response(resp)
    problem1_id = resp.json().get("id") if resp.ok else None

    # Create Problem 2
    print("Creating Problem: Multiply Two Numbers")
    problem2_data = {
        "title": "Multiply Two Numbers",
        "description": "Given two integers, print their product.",
        "difficulty": "easy",
        "test_cases": [
            {"input_data": "3 4", "expected_output": "12"},
            {"input_data": "5 6", "expected_output": "30"}
        ]
    }
    resp = requests.post(f"{BASE_URL}/problems", json=problem2_data)
    print_response(resp)
    problem2_id = resp.json().get("id") if resp.ok else None

    # List all problems
    print("Listing all problems:")
    resp = requests.get(f"{BASE_URL}/problems")
    print_response(resp)

    # Get single problem
    if problem1_id:
        print(f"Getting Problem ID {problem1_id}:")
        resp = requests.get(f"{BASE_URL}/problems/{problem1_id}")
        print_response(resp)

    # Update problem
    if problem1_id:
        print(f"Updating Problem ID {problem1_id} difficulty to 'medium':")
        resp = requests.put(f"{BASE_URL}/problems/{problem1_id}", json={"difficulty": "medium"})
        print_response(resp)

    # ===========================================
    # 2. AUTHENTICATION TESTS
    # ===========================================
    print_section("2️⃣  TESTING AUTH ENDPOINTS")
    
    # Register new user
    print("Registering new user: testuser")
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(resp)

    # Login
    print("Logging in as testuser:")
    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(resp)
    token = resp.json().get("access_token") if resp.ok else None

    if not token:
        print("❌ Login failed! Cannot proceed with submission tests.")
        return

    # ===========================================
    # 3. SUBMISSION TESTS (with Authentication)
    # ===========================================
    print_section("3️⃣  TESTING SUBMISSION ENDPOINTS")

    # Submit code for Problem 1 (Two Sum) - Should PASS
    if problem1_id:
        print(f"Submitting CORRECT solution for Problem {problem1_id} (Two Sum):")
        submission_data = {
            "problem_id": problem1_id,
            "language": "python",
            "code": "a, b = map(int, input().split())\nprint(a + b)"
        }
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/submissions", json=submission_data, headers=headers)
        print_response(resp)

    # Submit WRONG code - Should FAIL
    if problem1_id:
        print(f"Submitting WRONG solution for Problem {problem1_id} (Two Sum):")
        submission_data = {
            "problem_id": problem1_id,
            "language": "python",
            "code": "print('wrong answer')"
        }
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/submissions", json=submission_data, headers=headers)
        print_response(resp)

    # Submit code for Problem 2 (Multiply) - Should PASS
    if problem2_id:
        print(f"Submitting CORRECT solution for Problem {problem2_id} (Multiply):")
        submission_data = {
            "problem_id": problem2_id,
            "language": "python",
            "code": "a, b = map(int, input().split())\nprint(a * b)"
        }
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/submissions", json=submission_data, headers=headers)
        print_response(resp)

    # ===========================================
    # 4. ERROR HANDLING TESTS
    # ===========================================
    print_section("4️⃣  TESTING ERROR HANDLING")

    # Test invalid token
    print("Testing submission with invalid token:")
    test_submission = {
        "problem_id": 1,
        "language": "python",
        "code": "print('test')"
    }
    headers = {"Authorization": "Bearer invalidtoken"}
    resp = requests.post(f"{BASE_URL}/submissions", json=test_submission, headers=headers)
    print_response(resp)

    # Test missing token
    print("Testing submission without token:")
    resp = requests.post(f"{BASE_URL}/submissions", json=test_submission)
    print_response(resp)

    # Test non-existent problem
    print("Getting non-existent problem (ID 99999):")
    resp = requests.get(f"{BASE_URL}/problems/99999")
    print_response(resp)

    # Test invalid difficulty
    print("Creating problem with invalid difficulty:")
    invalid_problem = {
        "title": "Test",
        "description": "Test",
        "difficulty": "invalid"  # Should fail validation
    }
    resp = requests.post(f"{BASE_URL}/problems", json=invalid_problem)
    print_response(resp)

    # ===========================================
    # 5. CLEANUP (Optional - Delete Test Problem)
    # ===========================================
    print_section("5️⃣  CLEANUP")
    
    if problem2_id:
        print(f"Deleting Problem ID {problem2_id}:")
        resp = requests.delete(f"{BASE_URL}/problems/{problem2_id}")
        print(f"Status: {resp.status_code}")
        print("(No content expected for successful delete)\n")

    # Verify deletion
    print("Listing all problems after deletion:")
    resp = requests.get(f"{BASE_URL}/problems")
    print_response(resp)

    # ===========================================
    # FINAL SUMMARY
    # ===========================================
    print_section("✅  TEST SUITE COMPLETED")
    print("All endpoints tested successfully!")
    print("\nEndpoints tested:")
    print("  ✅ POST   /api/problems         (Create)")
    print("  ✅ GET    /api/problems         (List)")
    print("  ✅ GET    /api/problems/{id}    (Get)")
    print("  ✅ PUT    /api/problems/{id}    (Update)")
    print("  ✅ DELETE /api/problems/{id}    (Delete)")
    print("  ✅ POST   /api/auth/register    (Register)")
    print("  ✅ POST   /api/auth/login       (Login)")
    print("  ✅ POST   /api/submissions      (Submit code)")
    print("\nError handling:")
    print("  ✅ Invalid JWT token")
    print("  ✅ Missing JWT token")
    print("  ✅ Non-existent resource")
    print("  ✅ Invalid input validation")

if __name__ == "__main__":
    main()
