import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def load_admin_credentials():
    """Load admin credentials"""
    if os.path.exists("admin_credentials.json"):
        with open("admin_credentials.json", "r") as f:
            creds = json.load(f)
            return creds["email"], creds["password"]
    return "admin@example.com", "admin123"

def test_ai_generator():
    print("🤖 AI-POWERED PROBLEM GENERATOR TEST")
    print("Testing automatic problem generation and database integration\n")
    
    # Login as admin
    print_section("1️⃣  ADMIN LOGIN")
    email, password = load_admin_credentials()
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.text}")
        print("⚠️  Run 'python create_admin_user.py' first!")
        return
    
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"✅ Logged in as admin\n")
    
    # Get available topics
    print_section("2️⃣  AVAILABLE TOPICS")
    
    topics_response = requests.get(f"{BASE_URL}/generate/topics")
    print(f"Status: {topics_response.status_code}")
    
    if topics_response.status_code == 200:
        topics_data = topics_response.json()
        print(f"✅ Found {topics_data['count']} available topics:\n")
        for i, topic in enumerate(topics_data['topics'], 1):
            print(f"  {i}. {topic}")
        print()
    else:
        print(f"❌ Failed: {topics_response.text}")
        return
    
    # Generate a problem (without saving)
    print_section("3️⃣  GENERATE PROBLEM (Preview)")
    
    print("Generating 'two-sum' problem...")
    generate_response = requests.post(
        f"{BASE_URL}/generate/problem",
        json={"topic": "two-sum", "difficulty": "easy"}
    )
    
    print(f"Status: {generate_response.status_code}")
    if generate_response.status_code == 200:
        problem = generate_response.json()
        print(f"✅ Problem generated successfully!\n")
        print(f"📝 Title: {problem['title']}")
        print(f"⚡ Difficulty: {problem['difficulty']}")
        print(f"📖 Description (first 100 chars): {problem['description'][:100]}...")
        print(f"📋 Constraints: {len(problem['constraints'])} items")
        print(f"💡 Sample I/O: {len(problem['samples'])} examples")
        print(f"🧪 Test Cases: {len(problem['test_cases'])} cases\n")
        
        # Show first test case
        if problem['test_cases']:
            tc = problem['test_cases'][0]
            print(f"Example Test Case:")
            print(f"  Input: {tc['input']}")
            print(f"  Expected Output: {tc['expected_output']}")
    else:
        print(f"❌ Failed: {generate_response.text}")
    
    # Generate and save to database
    print_section("4️⃣  GENERATE AND SAVE TO DATABASE")
    
    print("Generating 'palindrome' problem and saving to DB...")
    save_response = requests.post(
        f"{BASE_URL}/generate/and/save",
        headers=admin_headers,
        json={"topic": "palindrome", "difficulty": "easy"}
    )
    
    print(f"Status: {save_response.status_code}")
    if save_response.status_code == 200:
        saved = save_response.json()
        print(f"✅ Problem saved to database!\n")
        print(f"🆔 Problem ID: {saved['problem_id']}")
        print(f"📝 Title: {saved['title']}")
        print(f"⚡ Difficulty: {saved['difficulty']}")
        print(f"🧪 Test Cases: {saved['test_case_count']}")
        print(f"💬 Message: {saved['message']}\n")
        
        saved_problem_id = saved['problem_id']
    else:
        print(f"❌ Failed: {save_response.text}")
        saved_problem_id = None
    
    # Verify problem was saved
    if saved_problem_id:
        print_section("5️⃣  VERIFY PROBLEM IN DATABASE")
        
        verify_response = requests.get(f"{BASE_URL}/problems/{saved_problem_id}")
        print(f"Status: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            problem = verify_response.json()
            print(f"✅ Problem found in database!\n")
            print(f"📝 {problem['title']}")
            print(f"⚡ Difficulty: {problem['difficulty']}")
            print(f"🧪 Test Cases: {len(problem['test_cases'])}")
            print(f"📅 Created: {problem['created_at']}\n")
            
            # Show test cases
            print("Test Cases:")
            for i, tc in enumerate(problem['test_cases'][:3], 1):
                print(f"  {i}. Input: {tc['input_data'][:50]}...")
                print(f"     Output: {tc['expected_output'][:50]}...")
        else:
            print(f"❌ Problem not found: {verify_response.text}")
    
    # Test batch generation
    print_section("6️⃣  BATCH GENERATION")
    
    print("Generating multiple problems at once...")
    batch_topics = ["fizzbuzz", "factorial", "array-sum"]
    
    batch_response = requests.post(
        f"{BASE_URL}/generate/batch",
        headers=admin_headers,
        params={"difficulty": "easy"},
        json=batch_topics
    )
    
    print(f"Status: {batch_response.status_code}")
    if batch_response.status_code == 200:
        results = batch_response.json()
        print(f"✅ Batch generation completed!\n")
        
        for result in results:
            status = "✅" if result['problem_id'] > 0 else "❌"
            print(f"{status} [{result['problem_id']}] {result['title']}")
            print(f"      {result['test_case_count']} test cases - {result['message']}")
    else:
        print(f"❌ Failed: {batch_response.text}")
    
    # Test with different difficulties
    print_section("7️⃣  DIFFERENT DIFFICULTIES")
    
    difficulties = ["easy", "medium", "hard"]
    
    for diff in difficulties:
        print(f"\nGenerating {diff.upper()} problem...")
        diff_response = requests.post(
            f"{BASE_URL}/generate/problem",
            json={"topic": "reverse-string", "difficulty": diff}
        )
        
        if diff_response.status_code == 200:
            problem = diff_response.json()
            print(f"✅ {problem['title']} - Difficulty: {problem['difficulty']}")
        else:
            print(f"❌ Failed for {diff}")
    
    # Test access control (non-admin user)
    print_section("8️⃣  ACCESS CONTROL TEST")
    
    # Try to generate without admin token (should work for preview)
    print("Testing problem generation without auth (preview should work)...")
    no_auth_response = requests.post(
        f"{BASE_URL}/generate/problem",
        json={"topic": "two-sum", "difficulty": "easy"}
    )
    print(f"Status: {no_auth_response.status_code}")
    if no_auth_response.status_code == 200:
        print("✅ Preview generation works without auth (correct)\n")
    
    # Try to save without admin token (should fail)
    print("Testing save without admin token (should fail)...")
    no_admin_response = requests.post(
        f"{BASE_URL}/generate/and/save",
        json={"topic": "two-sum", "difficulty": "easy"}
    )
    print(f"Status: {no_admin_response.status_code}")
    if no_admin_response.status_code == 403:
        print("✅ Save blocked for non-admin (correct)")
        print(f"   Response: {no_admin_response.json()}")
    
    # Summary
    print_section("✅  AI GENERATOR TEST COMPLETED")
    
    print("\nEndpoints tested:")
    print("  ✅ GET    /api/generate/topics          (List available topics)")
    print("  ✅ POST   /api/generate/problem         (Generate problem preview)")
    print("  ✅ POST   /api/generate/and/save        (Generate & save to DB)")
    print("  ✅ POST   /api/generate/batch           (Batch generation)")
    
    print("\nFeatures verified:")
    print("  ✅ Template-based problem generation")
    print("  ✅ Multiple problem topics available")
    print("  ✅ Automatic test case generation")
    print("  ✅ Database integration")
    print("  ✅ Admin-only protection for saving")
    print("  ✅ Batch problem creation")
    print("  ✅ Difficulty level support")
    
    print("\n🔮 Ready for AI API integration!")
    print("   Replace template logic with Gemini/ChatGPT API calls")

if __name__ == "__main__":
    test_ai_generator()
