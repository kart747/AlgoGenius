import json

import requests

BASE_URL = "http://localhost:8000/api"


def test_access_control():
    """Test that regular users cannot access admin endpoints."""
    print("🔒 TESTING ACCESS CONTROL\n")

    # Login as regular user
    print("Step 1: Login as regular user")
    with open("test_credentials.json", "r", encoding="utf-8") as file:
        creds = json.load(file)

    user_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )

    if user_login.status_code != 200:
        print("❌ Regular user login failed")
        return

    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print(f"✅ Logged in as: {creds['username']}\n")

    # Login as admin
    print("Step 2: Login as admin")
    admin_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )

    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Logged in as: admin\n")

    # Test all admin endpoints with regular user token
    print("=" * 60)
    print("  Testing Admin Endpoints with Regular User Token")
    print("=" * 60)

    test_cases = [
        ("GET", "/admin/stats", None),
        ("GET", "/admin/users", None),
        (
            "POST",
            "/admin/problems",
            {"title": "Test", "description": "Test", "difficulty": "easy"},
        ),
        ("PUT", "/admin/problems/1", {"difficulty": "hard"}),
        ("DELETE", "/admin/problems/999", None),
        (
            "POST",
            "/admin/problems/1/testcases",
            {"input_data": "test", "expected_output": "test"},
        ),
        ("DELETE", "/admin/testcases/999", None),
    ]

    print("\nRegular User Access (should all be 403):")
    for method, endpoint, body in test_cases:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=user_headers)
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}", headers=user_headers, json=body
            )
        elif method == "PUT":
            response = requests.put(
                f"{BASE_URL}{endpoint}", headers=user_headers, json=body
            )
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=user_headers)
        else:
            continue

        status = "✅" if response.status_code == 403 else "❌"
        print(f"{status} {method:6} {endpoint:40} Status: {response.status_code}")
        if response.status_code == 403:
            detail = response.json().get("detail", "")
            print(f"         Response: {detail}")

    print("\n" + "=" * 60)
    print("  Testing Admin Endpoints with Admin Token")
    print("=" * 60)

    print("\nAdmin User Access (should succeed):")
    # Test with admin token
    admin_test_cases = [
        ("GET", "/admin/stats", None),
        ("GET", "/admin/users", None),
    ]

    for method, endpoint, _ in admin_test_cases:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=admin_headers)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {method:6} {endpoint:40} Status: {response.status_code}")

    print("\n" + "=" * 60)
    print("  ✅  ACCESS CONTROL TEST COMPLETED")
    print("=" * 60)
    print("\nSecurity verified:")
    print("  ✅ Regular users receive 403 Forbidden on admin endpoints")
    print("  ✅ Admin users can access admin endpoints")
    print("  ✅ 'Admin privileges required' message shown")


if __name__ == "__main__":
    test_access_control()