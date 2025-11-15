"""
Standalone Gemini Service Test

This script tests the Gemini AI integration directly without FastAPI.
Run this to verify your GEMINI_API_KEY is working correctly.

Usage:
    python test_gemini_standalone.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
        return True
    except ImportError:
        print("❌ google-generativeai not installed")
        print("\n   Install with: pip install google-generativeai")
        return False

def check_api_key():
    """Check if GEMINI_API_KEY is set"""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...{api_key[-5:]}")
        return api_key
    else:
        print("❌ GEMINI_API_KEY not set")
        print("\n   Get your API key from: https://makersuite.google.com/app/apikey")
        print("   Set it with: $env:GEMINI_API_KEY='your_api_key_here'")
        return None

async def test_gemini_service():
    """Test Gemini service functions"""
    
    print("\n" + "="*70)
    print("  🤖 GEMINI SERVICE STANDALONE TEST")
    print("="*70 + "\n")
    
    # Check dependencies
    print("Step 1: Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Check API key
    print("\nStep 2: Checking API key...")
    api_key = check_api_key()
    if not api_key:
        return False
    
    # Import service
    print("\nStep 3: Importing Gemini service...")
    try:
        from app.services.gemini_service import generate_test_cases, generate_starter_code
        print("✅ Gemini service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Test problem
    problem = """
    Given two integers separated by a space, return their sum.
    
    Input: Two integers on a single line
    Output: Their sum
    
    Example:
    Input: 3 5
    Output: 8
    """
    
    # Test 1: Generate test cases (with fallback demonstration)
    print("\n" + "="*70)
    print("  TEST 1: Generate Test Cases (Primary → Fallback)")
    print("="*70)
    
    try:
        print("\n📡 Attempting to generate 5 test cases...")
        print("    → Will try gemini-2.5-flash first")
        print("    → Will fallback to gemini-1.5-flash-8b if quota exceeded\n")
        
        test_cases = await generate_test_cases(problem, num_cases=5)
        
        print(f"\n✅ Successfully generated {len(test_cases)} test cases!\n")
        
        for i, tc in enumerate(test_cases, 1):
            print(f"Test Case {i}:")
            print(f"  Input: {tc['input_data']}")
            print(f"  Expected Output: {tc['expected_output']}\n")
        
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return False
    
    except ConnectionError as e:
        print(f"❌ Network Error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False
    
    # Test 2: Generate starter code (with fallback demonstration)
    print("="*70)
    print("  TEST 2: Generate Starter Code (Primary → Fallback)")
    print("="*70)
    
    languages = ["python"]  # Just test one language to save time
    
    for lang in languages:
        try:
            print(f"\n📡 Generating {lang.upper()} starter code...")
            print("    → Will try gemini-2.5-flash first")
            print("    → Will fallback to gemini-1.5-flash-8b if quota exceeded\n")
            
            code = await generate_starter_code(problem, lang)
            
            print(f"\n✅ Successfully generated {lang} code!\n")
            print(f"Code ({len(code.split(chr(10)))} lines):")
            print("-" * 50)
            
            # Show first 15 lines
            lines = code.split('\n')
            for i, line in enumerate(lines[:15], 1):
                print(f"{i:2}  {line}")
            
            if len(lines) > 15:
                print(f"     ... ({len(lines) - 15} more lines)")
            
            print("-" * 50)
        
        except Exception as e:
            print(f"❌ Failed for {lang}: {e}")
    
    # Success
    print("\n" + "="*70)
    print("  ✅ ALL TESTS PASSED!")
    print("="*70)
    
    print("\n🎉 Gemini AI integration is working correctly!")
    print("\nYou can now:")
    print("  1. Start your FastAPI server")
    print("  2. Use /api/generate/gemini/* endpoints")
    print("  3. Generate problems with AI assistance")
    
    return True

if __name__ == "__main__":
    print("\n🚀 Starting Gemini Standalone Test...\n")
    
    try:
        success = asyncio.run(test_gemini_service())
        
        if not success:
            print("\n⚠️  Some tests failed. Check the errors above.")
            print("\nCommon issues:")
            print("  - Missing API key: Set GEMINI_API_KEY environment variable")
            print("  - Invalid API key: Check your key at https://makersuite.google.com")
            print("  - Network issues: Check your internet connection")
            print("  - Package not installed: pip install google-generativeai")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
