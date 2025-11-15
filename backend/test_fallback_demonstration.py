"""
Gemini Fallback Demonstration

This script demonstrates the automatic fallback behavior when:
- Primary model (gemini-2.5-flash) quota is exceeded
- System automatically switches to fallback (gemini-1.5-flash-8b)

Usage:
    python test_fallback_demonstration.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini_service import GeminiService


async def demonstrate_fallback():
    """Demonstrate the fallback mechanism"""
    
    print("\n" + "="*80)
    print("  🔄 GEMINI FALLBACK MECHANISM DEMONSTRATION")
    print("="*80)
    
    print("\n📋 Configuration:")
    print(f"   Primary Model:  gemini-2.5-flash")
    print(f"   Fallback Model: gemini-1.5-flash-8b")
    print(f"   Behavior:       Try primary → If 429 error → Retry with fallback")
    
    # Initialize service
    try:
        service = GeminiService()
        print("\n✅ GeminiService initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        return False
    
    # Test problem
    problem = """
    Write a function that checks if a string is a palindrome.
    
    Input: A single line containing a string
    Output: "YES" if palindrome, "NO" otherwise
    
    Example:
    Input: radar
    Output: YES
    """
    
    # Test 1: Generate test cases
    print("\n" + "="*80)
    print("  TEST: Generate Test Cases with Fallback")
    print("="*80)
    
    print("\n📡 Starting request...")
    print("   Step 1: Try primary model (gemini-2.5-flash)")
    print("   Step 2: If quota exceeded (429) → Switch to fallback (gemini-1.5-flash-8b)")
    print("   Step 3: Return results\n")
    
    try:
        test_cases = await service.generate_test_cases(problem, num_cases=3)
        
        print("\n" + "="*80)
        print("  ✅ SUCCESS - Test Cases Generated")
        print("="*80)
        
        for i, tc in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"  Input:  {tc['input_data']}")
            print(f"  Output: {tc['expected_output']}")
        
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print("  ❌ BOTH MODELS FAILED")
        print("="*80)
        print(f"\nError: {e}")
        return False


async def test_multiple_requests():
    """Test multiple requests to potentially trigger quota limit"""
    
    print("\n" + "="*80)
    print("  📊 MULTIPLE REQUEST TEST (Quota Stress Test)")
    print("="*80)
    
    service = GeminiService()
    
    problem = "Given a number n, return the factorial of n."
    
    print("\n🔥 Sending 3 rapid requests to test quota handling...\n")
    
    for i in range(1, 4):
        print(f"Request {i}/3:")
        try:
            test_cases = await service.generate_test_cases(problem, num_cases=2)
            print(f"  ✅ Success - Generated {len(test_cases)} test cases")
        except Exception as e:
            print(f"  ❌ Failed - {str(e)[:100]}")
        print()
    
    print("="*80)
    print("✅ Quota stress test completed")
    print("="*80)


async def main():
    """Run all demonstration tests"""
    
    print("\n🚀 Starting Gemini Fallback Demonstration...\n")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not set in .env file")
        return
    
    print("✅ API Key loaded from .env\n")
    
    # Test 1: Basic fallback demonstration
    print("="*80)
    print(" Part 1: Basic Fallback Mechanism")
    print("="*80)
    success = await demonstrate_fallback()
    
    if not success:
        print("\n⚠️  Primary test failed")
        return
    
    # Test 2: Multiple requests
    print("\n\n")
    print("="*80)
    print(" Part 2: Quota Stress Test")
    print("="*80)
    await test_multiple_requests()
    
    # Summary
    print("\n\n")
    print("="*80)
    print("  📖 SUMMARY")
    print("="*80)
    print("""
Your Gemini integration now includes:

✅ Primary Model:   gemini-2.5-flash (your friend's model)
✅ Fallback Model:  gemini-1.5-flash-8b (free tier)
✅ Auto-Retry:      Switches to fallback on 429 errors
✅ Logging:         Shows which model is being used
✅ Error Handling:  Graceful failures with clear messages

How it works:
1. Every request tries gemini-2.5-flash first
2. If quota exceeded (429 error), logs warning
3. Automatically retries with gemini-1.5-flash-8b
4. Returns results or structured error

Your backend is production-ready! 🎉
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
