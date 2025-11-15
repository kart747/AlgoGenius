"""
Create an admin user for testing admin endpoints.
"""
import requests
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User

BASE_URL = "http://localhost:8000/api"

def create_admin_user_via_api():
    """Create admin user via API and then update in database"""
    print("🔐 Creating Admin User\n")
    
    # Step 1: Register via API
    print("Step 1: Registering user via API...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123"
        }
    )
    
    if register_response.status_code in [200, 201]:
        print("✅ User registered successfully")
        user_data = register_response.json()
        user_id = user_data.get("user_id")
    elif register_response.status_code == 400:
        print("⚠️  User already exists, proceeding to upgrade...")
        # Login to get user ID
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        if login_response.status_code == 200:
            user_id = login_response.json().get("user_id")
        else:
            print("❌ Could not login. Password may have changed.")
            return False
    else:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    # Step 2: Upgrade to admin in database
    print(f"\nStep 2: Upgrading user ID {user_id} to admin...")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_admin = 1
            db.commit()
            print("✅ User upgraded to admin successfully!")
            
            print("\n" + "="*60)
            print("  🎉 ADMIN USER CREATED")
            print("="*60)
            print(f"Username: admin")
            print(f"Email: admin@example.com")
            print(f"Password: admin123")
            print(f"User ID: {user_id}")
            print(f"Admin Status: True")
            print("="*60)
            
            # Save credentials
            with open("admin_credentials.json", "w") as f:
                json.dump({
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": "admin123",
                    "user_id": user_id
                }, f, indent=2)
            print("\n💾 Credentials saved to admin_credentials.json")
            
            # Test login
            print("\n🧪 Testing admin login...")
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": "admin@example.com", "password": "admin123"}
            )
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                print("✅ Login successful!")
                print(f"Token: {token[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
        else:
            print("❌ User not found in database")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user_via_api()
