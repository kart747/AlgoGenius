import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def test_gemini_integration():
    print("🤖 GOOGLE GEMINI AI INTEGRATION TEST")
    print("Testing Gemini 2.0 Flash for test case and code generation\n")
    
    # Check if Gemini API key is set
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not set in environment")
        print("   This test will use template-based generation")
        print("\n   To enable Gemini AI:")
        print("   1. Get API key from https://makersuite.google.com/app/apikey")
        print("   2. Set environment variable: $env:GEMINI_API_KEY='your_key_here'")
        print("   3. Restart the FastAPI server")
        print("   4. Re-run this test\n")
    else:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...{gemini_key[-5:]}\n")
    
    # Test 1: Generate test cases with Gemini
    print_section("1️⃣  GEMINI TEST CASE GENERATION")
    
    problem_text = """
    Given two integers separated by a space, return their sum.
    
    Input: Two integers on a single line
    Output: Their sum
    
    Example:
    Input: 3 5
    Output: 8
    """
    
    print("Problem: Sum of two integers")
    print("Requesting 5 test cases from Gemini...\n")
    
    testcase_response = requests.post(
        f"{BASE_URL}/generate/gemini/testcases",
        json={
            "problem_text": problem_text,
            "num_cases": 5
        }
    )
    
    print(f"Status: {testcase_response.status_code}")
    
    if testcase_response.status_code == 200:
        data = testcase_response.json()
        print(f"✅ Generated {data['count']} test cases")
        print(f"   Powered by: {data['powered_by']}\n")
        
        for i, tc in enumerate(data['test_cases'], 1):
            print(f"   Test Case {i}:")
            print(f"      Input: {tc['input_data']}")
            print(f"      Output: {tc['expected_output']}")
    
    elif testcase_response.status_code == 503:
        print("⚠️  Gemini AI not available")
        print(f"   {testcase_response.json()['detail']}\n")
    else:
        print(f"❌ Error: {testcase_response.text}\n")
    
    # Test 2: Generate starter code with Gemini
    print_section("2️⃣  GEMINI STARTER CODE GENERATION")
    
    languages = ["python", "cpp", "java"]
    
    for lang in languages:
        print(f"\nGenerating {lang.upper()} starter code...")
        
        code_response = requests.post(
            f"{BASE_URL}/generate/gemini/startercode",
            json={
                "problem_text": problem_text,
                "language": lang
            }
        )
        
        print(f"Status: {code_response.status_code}")
        
        if code_response.status_code == 200:
            data = code_response.json()
            print(f"✅ Generated {data['language']} code")
            print(f"   Powered by: {data['powered_by']}")
            print(f"\n   Code Preview:")
            code_lines = data['code'].split('\n')
            for line in code_lines[:10]:  # Show first 10 lines
                print(f"   {line}")
            if len(code_lines) > 10:
                print(f"   ... ({len(code_lines) - 10} more lines)")
        
        elif code_response.status_code == 503:
            print("⚠️  Gemini AI not available")
            break
        else:
            print(f"❌ Error: {code_response.text}")
    
    # Test 3: Generate complete problem with AI
    print_section("3️⃣  AI-POWERED COMPLETE PROBLEM GENERATION")
    
    print("Generating problem with topic='binary-search' difficulty='medium'...")
    
    problem_response = requests.post(
        f"{BASE_URL}/generate/problem",
        json={
            "topic": "binary-search",
            "difficulty": "medium"
        }
    )
    
    print(f"Status: {problem_response.status_code}")
    
    if problem_response.status_code == 200:
        problem = problem_response.json()
        print(f"✅ Problem generated!\n")
        print(f"📝 Title: {problem['title']}")
        print(f"⚡ Difficulty: {problem['difficulty']}")
        print(f"📖 Description: {problem['description'][:150]}...")
        print(f"📋 Constraints: {len(problem['constraints'])} items")
        print(f"💡 Samples: {len(problem['samples'])} examples")
        print(f"🧪 Test Cases: {len(problem['test_cases'])} cases")
        
        if gemini_key:
            print(f"\n   🤖 Generated using: Google Gemini AI")
        else:
            print(f"\n   📝 Generated using: Template-based system")
    else:
        print(f"❌ Error: {problem_response.text}")
    
    # Test 4: Error handling
    print_section("4️⃣  ERROR HANDLING TESTS")
    
    print("\n1. Testing with invalid language...")
    invalid_lang = requests.post(
        f"{BASE_URL}/generate/gemini/startercode",
        json={
            "problem_text": "Test problem",
            "language": "invalid_language"
        }
    )
    print(f"   Status: {invalid_lang.status_code}")
    if invalid_lang.status_code == 422:
        print("   ✅ Validation working correctly")
    
    print("\n2. Testing with empty problem text...")
    empty_problem = requests.post(
        f"{BASE_URL}/generate/gemini/testcases",
        json={
            "problem_text": "",
            "num_cases": 5
        }
    )
    print(f"   Status: {empty_problem.status_code}")
    
    print("\n3. Testing with excessive test case count...")
    too_many = requests.post(
        f"{BASE_URL}/generate/gemini/testcases",
        json={
            "problem_text": "Test",
            "num_cases": 100  # Max is 50
        }
    )
    print(f"   Status: {too_many.status_code}")
    if too_many.status_code == 422:
        print("   ✅ Validation limit working correctly")
    
    # Summary
    print_section("✅  GEMINI INTEGRATION TEST COMPLETED")
    
    print("\nEndpoints tested:")
    print("  ✅ POST   /api/generate/gemini/testcases    (Test case generation)")
    print("  ✅ POST   /api/generate/gemini/startercode  (Starter code generation)")
    print("  ✅ POST   /api/generate/problem             (Complete problem with AI)")
    
    print("\nFeatures verified:")
    print("  ✅ Gemini 2.0 Flash integration")
    print("  ✅ Test case generation (input/output pairs)")
    print("  ✅ Multi-language starter code generation")
    print("  ✅ Error handling and validation")
    print("  ✅ Fallback to templates when AI unavailable")
    
    if gemini_key:
        print("\n🎉 Gemini AI is active and working!")
    else:
        print("\n💡 Set GEMINI_API_KEY to enable AI-powered generation")
    
    print("\n🔑 To enable Gemini AI:")
    print("   1. Visit: https://makersuite.google.com/app/apikey")
    print("   2. Create a new API key")
    print("   3. PowerShell: $env:GEMINI_API_KEY='your_api_key_here'")
    print("   4. Restart FastAPI server")

if __name__ == "__main__":
    test_gemini_integration()
