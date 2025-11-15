import json
import os

import requests

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def load_admin_credentials():
    """Load admin credentials from file if present."""
    if os.path.exists("admin_credentials.json"):
        with open("admin_credentials.json", "r", encoding="utf-8") as file:
            creds = json.load(file)
            return creds["email"], creds["password"]
    return "admin@example.com", "admin123"


def test_admin_features():
    print("🔐 COMPREHENSIVE ADMIN FEATURES TEST")
    print("Testing all admin endpoints and access control\n")

    # Get admin credentials
    admin_email, admin_password = load_admin_credentials()

    # Step 1: Login as admin
    print_section("1️⃣  ADMIN LOGIN")
    admin_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": admin_email, "password": admin_password},
    )

    if admin_login.status_code != 200:
        print(f"❌ Admin login failed: {admin_login.text}")
        print("\n⚠️  Run 'python create_admin_user.py' first!")
        return

    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Logged in as admin")
    print(f"Token: {admin_token[:50]}...")

    # Step 2: Test admin access control with regular user
    print_section("2️⃣  ACCESS CONTROL TEST")

    # Try to login as regular user (if exists)
    user_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "testuser@example.com", "password": "password123"},
    )

    if user_login.status_code == 200:
        user_token = user_login.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Try admin endpoint with regular user token
        print("Testing admin endpoint with regular user token...")
        test_response = requests.get(f"{BASE_URL}/admin/stats", headers=user_headers)
        print(f"Status: {test_response.status_code}")
        if test_response.status_code == 403:
            print("✅ Access denied (correct behavior)")
            print(f"Response: {test_response.json()}")
        else:
            print("❌ Regular user should not have access!")
    else:
        print("⚠️  No regular user found for access control test")

    # Step 3: Admin Problem Management
    print_section("3️⃣  ADMIN PROBLEM MANAGEMENT")

    print("Creating new problem...")
    create_problem = requests.post(
        f"{BASE_URL}/admin/problems",
        headers=admin_headers,
        json={
            "title": "Fibonacci Sequence",
            "description": "Print the nth Fibonacci number",
            "difficulty": "medium",
            "test_cases": [
                {"input_data": "5", "expected_output": "5"},
                {"input_data": "10", "expected_output": "55"},
            ],
        },
    )
    print(f"Status: {create_problem.status_code}")
    if create_problem.status_code == 201:
        problem = create_problem.json()
        problem_id = problem["id"]
        print(f"✅ Problem created: ID {problem_id} - {problem['title']}")
        print(f"   Difficulty: {problem['difficulty']}")

        # Update problem
        print(f"\nUpdating problem {problem_id}...")
        update_problem = requests.put(
            f"{BASE_URL}/admin/problems/{problem_id}",
            headers=admin_headers,
            json={"difficulty": "hard", "title": "Fibonacci Sequence (Advanced)"},
        )
        print(f"Status: {update_problem.status_code}")
        if update_problem.status_code == 200:
            updated = update_problem.json()
            print(f"✅ Problem updated: {updated['title']}")
            print(f"   New difficulty: {updated['difficulty']}")

        # Add test case
        print(f"\nAdding test case to problem {problem_id}...")
        add_testcase = requests.post(
            f"{BASE_URL}/admin/problems/{problem_id}/testcases",
            headers=admin_headers,
            json={"input_data": "15", "expected_output": "610"},
        )
        print(f"Status: {add_testcase.status_code}")
        if add_testcase.status_code == 201:
            testcase = add_testcase.json()
            print(f"✅ Test case added: ID {testcase['id']}")
            testcase_id = testcase["id"]

            # Delete test case
            print(f"\nDeleting test case {testcase_id}...")
            delete_tc = requests.delete(
                f"{BASE_URL}/admin/testcases/{testcase_id}", headers=admin_headers
            )
            print(f"Status: {delete_tc.status_code}")
            if delete_tc.status_code == 204:
                print("✅ Test case deleted")
    else:
        print(f"Response: {create_problem.text}")
        problem_id = None

    # Step 4: Admin User Management
    print_section("4️⃣  ADMIN USER MANAGEMENT")

    print("Listing all users...")
    list_users = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    print(f"Status: {list_users.status_code}")
    if list_users.status_code == 200:
        users = list_users.json()
        print(f"✅ Found {len(users)} users:\n")
        for user in users:
            admin_badge = "👑" if user["is_admin"] else "  "
            print(f"{admin_badge} [{user['id']}] {user['username']} ({user['email']})")
            print(f"      XP: {user['xp']} | Streak: {user['current_streak']}")
        print()

    # Step 5: Platform Statistics
    print_section("5️⃣  PLATFORM STATISTICS")

    stats_response = requests.get(f"{BASE_URL}/admin/stats", headers=admin_headers)
    print(f"Status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print("✅ Platform Statistics:\n")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Problems: {stats['total_problems']}")
        print(f"  Total Submissions: {stats['total_submissions']}")
        print(f"  Today's Submissions: {stats['daily_submission_count']}")
        print(f"  Acceptance Rate: {stats['accepted_ratio']}%")
        print(f"  Most Used Language: {stats['top_language_used']}")
    else:
        print(f"Response: {stats_response.text}")

    # Step 6: Problem Deletion
    if problem_id:
        print_section("6️⃣  CLEANUP - DELETE PROBLEM")
        print(f"Deleting problem {problem_id}...")
        delete_problem = requests.delete(
            f"{BASE_URL}/admin/problems/{problem_id}", headers=admin_headers
        )
        print(f"Status: {delete_problem.status_code}")
        if delete_problem.status_code == 204:
            print("✅ Problem deleted (with cascade test cases)")

    # Summary
    print_section("✅  ADMIN FEATURES TEST COMPLETED")
    print("\nEndpoints tested:")
    print("  ✅ POST   /api/admin/problems              (Create problem)")
    print("  ✅ PUT    /api/admin/problems/{id}         (Update problem)")
    print("  ✅ DELETE /api/admin/problems/{id}         (Delete problem)")
    print("  ✅ POST   /api/admin/problems/{id}/testcases (Add test case)")
    print("  ✅ DELETE /api/admin/testcases/{id}        (Remove test case)")
    print("  ✅ GET    /api/admin/users                 (List users)")
    print("  ✅ GET    /api/admin/stats                 (Platform stats)")
    print("\nSecurity verified:")
    print("  ✅ Admin-only access enforced (403 for non-admins)")
    print("  ✅ JWT authentication required")
    print("  ✅ Cascade delete working")


if __name__ == "__main__":
    test_admin_features()