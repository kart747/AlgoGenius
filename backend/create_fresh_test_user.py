import requests
import json

BASE_URL = "http://localhost:8000/api"

def reset_test_user():
    """
    Creates a fresh test user for testing.
    Uses a unique email to avoid conflicts.
    """
    print("🔧 Creating fresh test user for testing...")
    
    # Create a new user with timestamp to make it unique
    import time
    timestamp = int(time.time())
    
    username = f"testuser_{timestamp}"
    email = f"testuser_{timestamp}@example.com"
    password = "password123"
    
    # Register the user
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    if register_response.status_code in [200, 201]:
        print("✅ Test user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print("\n📝 Save these credentials for testing!")
        
        # Test login immediately
        print("\n🔐 Testing login...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            token_data = login_response.json()
            print(f"   Token received: {token_data['access_token'][:50]}...")
            print(f"   User ID: {token_data['user_id']}")
            
            # Save to a file for the test script
            with open("test_credentials.json", "w") as f:
                json.dump({
                    "email": email,
                    "password": password,
                    "username": username
                }, f, indent=2)
            print("\n💾 Credentials saved to test_credentials.json")
        else:
            print(f"❌ Login failed: {login_response.text}")
    else:
        print(f"❌ Registration failed")
        print(f"   Status: {register_response.status_code}")
        print(f"   Response: {register_response.text}")

if __name__ == "__main__":
    reset_test_user()
