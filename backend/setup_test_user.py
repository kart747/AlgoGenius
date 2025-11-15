import requests
import json

BASE_URL = "http://localhost:8000/api"

def setup_test_user():
    """
    Creates a test user if it doesn't exist.
    """
    print("🔧 Setting up test user...")
    
    # Try to register the user
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
    )
    
    if register_response.status_code == 201 or register_response.status_code == 200:
        print("✅ Test user created successfully!")
        print(f"   Username: testuser")
        print(f"   Email: testuser@example.com")
        print(f"   Password: password123")
        return True
    elif register_response.status_code == 400:
        response_data = register_response.json()
        if "already registered" in response_data.get("detail", "").lower():
            print("✅ Test user already exists - ready to use!")
            print(f"   Username: testuser")
            print(f"   Email: testuser@example.com")
            return True
        else:
            print(f"❌ Error: {response_data}")
            return False
    else:
        print(f"❌ Failed to create test user")
        print(f"   Status: {register_response.status_code}")
        print(f"   Response: {register_response.text}")
        return False

if __name__ == "__main__":
    setup_test_user()
