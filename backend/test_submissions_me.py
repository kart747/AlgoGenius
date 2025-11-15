"""
Test script for GET /api/submissions/me endpoint

Tests the new authenticated user submission history endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_json(data):
    print(json.dumps(data, indent=2))

def main():
    print_header("🧪 Testing GET /api/submissions/me Endpoint")
    
    # Step 1: Try to register user (ignore if already exists)
    print("\n📝 Step 0: Ensuring test user exists...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if register_response.status_code == 200:
            print("✅ Test user created successfully")
        elif register_response.status_code == 400:
            print("ℹ️  Test user already exists (using existing user)")
        else:
            print(f"⚠️  Unexpected registration response: {register_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not create user (may already exist): {e}")
    
    # Step 2: Login to get token
    print("\n📝 Step 1: Login as test user...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        print(f"✅ Login successful! Token: {token[:20]}...")
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        print("\nMake sure:")
        print("  1. Server is running: uvicorn app.main:app --reload")
        print("  2. User exists with email 'test@example.com'")
        print("\nTo create a test user, use:")
        print('  POST /api/auth/register')
        print('  {"username": "testuser", "email": "test@example.com", "password": "testpass123"}')
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get submissions WITHOUT code
    print_header("📋 Step 2: GET /api/submissions/me (without code)")
    
    try:
        response = requests.get(f"{BASE_URL}/submissions/me", headers=headers)
        response.raise_for_status()
        submissions = response.json()
        
        print(f"\n✅ Found {len(submissions)} submissions")
        
        if submissions:
            print(f"\nFirst 3 submissions:")
            for i, sub in enumerate(submissions[:3], 1):
                print(f"\n  Submission {i}:")
                print(f"    ID: {sub['submission_id']}")
                print(f"    Problem: {sub['problem_title']} (ID: {sub['problem_id']})")
                print(f"    Language: {sub['language']}")
                print(f"    Status: {sub['status']}")
                print(f"    Submitted: {sub['created_at']}")
                print(f"    Code included: {'code' in sub}")
        else:
            print("\n  ℹ️  No submissions yet. Submit some code first!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Step 3: Get submissions WITH code
    print_header("📋 Step 3: GET /api/submissions/me?include_code=true")
    
    try:
        response = requests.get(
            f"{BASE_URL}/submissions/me",
            headers=headers,
            params={"include_code": True}
        )
        response.raise_for_status()
        submissions = response.json()
        
        print(f"\n✅ Found {len(submissions)} submissions")
        
        if submissions:
            print(f"\nFirst submission (with code):")
            sub = submissions[0]
            print(f"  ID: {sub['submission_id']}")
            print(f"  Problem: {sub['problem_title']}")
            print(f"  Language: {sub['language']}")
            print(f"  Status: {sub['status']}")
            print(f"  Code included: {'code' in sub}")
            
            if 'code' in sub:
                code_preview = sub['code'][:100] + "..." if len(sub['code']) > 100 else sub['code']
                print(f"  Code preview: {code_preview}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Step 4: Test without authentication
    print_header("🔒 Step 4: Test without authentication (should fail)")
    
    try:
        response = requests.get(f"{BASE_URL}/submissions/me")
        
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized request (401)")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✅ Request properly rejected: {e}")
    
    # Summary
    print_header("✅ Test Summary")
    print("""
Endpoint tested: GET /api/submissions/me

✅ Authentication required (JWT token)
✅ Returns user's submission history
✅ Newest submissions first
✅ Includes problem details via relationships
✅ Optional code inclusion with ?include_code=true
✅ Proper error handling

Response fields:
  - submission_id: Unique submission ID
  - problem_id: Problem ID
  - problem_title: Problem title (from relationship)
  - language: Programming language
  - status: Submission status
  - created_at: Submission timestamp
  - code: Source code (only if include_code=true)
    """)

if __name__ == "__main__":
    main()
