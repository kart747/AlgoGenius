"""
🤖 GOOGLE GEMINI AI INTEGRATION GUIDE
=====================================

Complete guide to enable AI-powered problem generation in your FastAPI backend.

WHAT YOU GET
------------
✅ Automatic test case generation (input/output pairs)
✅ Starter code generation (Python, C++, Java)
✅ Complete problem generation with AI
✅ Smart fallback to templates if AI unavailable

STEP-BY-STEP SETUP
------------------

Step 1: Install Required Package
---------------------------------
pip install google-generativeai

Verify installation:
    python -c "import google.generativeai; print('✅ Installed')"


Step 2: Get Gemini API Key (FREE)
----------------------------------
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your API key


Step 3: Set Environment Variable
---------------------------------
PowerShell (Windows):
    $env:GEMINI_API_KEY="your_api_key_here"

Bash (Linux/Mac):
    export GEMINI_API_KEY="your_api_key_here"

Permanent (add to .env file):
    GEMINI_API_KEY=your_api_key_here


Step 4: Test Gemini Connection
-------------------------------
Run standalone test:
    python test_gemini_standalone.py

This will verify:
- Package installation ✓
- API key validity ✓
- Network connectivity ✓
- Test case generation ✓
- Code generation ✓


Step 5: Restart FastAPI Server
-------------------------------
    python -m uvicorn app.main:app --reload

You should see:
    🤖 Gemini AI enabled for problem generation


Step 6: Test via API
---------------------
    python test_gemini_integration.py

This tests all Gemini endpoints:
- POST /api/generate/gemini/testcases
- POST /api/generate/gemini/startercode
- POST /api/generate/problem (with AI)


NEW API ENDPOINTS
-----------------

1. Generate Test Cases with AI
   POST /api/generate/gemini/testcases
   
   Request:
   {
       "problem_text": "Given two integers, return their sum",
       "num_cases": 10
   }
   
   Response:
   {
       "test_cases": [
           {"input_data": "3 5", "expected_output": "8"},
           {"input_data": "10 20", "expected_output": "30"}
       ],
       "count": 10,
       "powered_by": "Google Gemini 2.0 Flash"
   }


2. Generate Starter Code with AI
   POST /api/generate/gemini/startercode
   
   Request:
   {
       "problem_text": "Given two integers, return their sum",
       "language": "python"
   }
   
   Response:
   {
       "code": "def solve():\n    a, b = map(int, input().split())\n    ...",
       "language": "python",
       "powered_by": "Google Gemini 2.0 Flash"
   }


3. Generate Complete Problem (Enhanced with AI)
   POST /api/generate/problem
   
   Request:
   {
       "topic": "binary-search",
       "difficulty": "medium"
   }
   
   Response: (Now uses AI if available, falls back to templates)
   {
       "title": "Binary Search Implementation",
       "difficulty": "medium",
       "description": "...",
       "constraints": [...],
       "samples": [...],
       "test_cases": [...]
   }


USAGE EXAMPLES
--------------

Python Example:
```python
import requests

# Generate test cases
response = requests.post(
    "http://localhost:8000/api/generate/gemini/testcases",
    json={
        "problem_text": "Calculate factorial of n",
        "num_cases": 10
    }
)
test_cases = response.json()["test_cases"]

# Generate starter code
response = requests.post(
    "http://localhost:8000/api/generate/gemini/startercode",
    json={
        "problem_text": "Calculate factorial of n",
        "language": "python"
    }
)
code = response.json()["code"]
print(code)
```

cURL Example:
```bash
curl -X POST http://localhost:8000/api/generate/gemini/testcases \
  -H "Content-Type: application/json" \
  -d '{"problem_text": "Sum two numbers", "num_cases": 5}'
```


FEATURES
--------

Smart Fallback System:
- If GEMINI_API_KEY is set → Uses AI
- If not set → Uses templates
- If AI fails → Falls back to templates
- No downtime, always works!

Error Handling:
- Invalid API key → Clear error message
- Network error → Graceful fallback
- Rate limits → Template fallback
- Invalid JSON → Retry with cleanup

Cost: FREE!
- Gemini 2.0 Flash is free tier
- No credit card required
- Generous rate limits
- Perfect for development


TROUBLESHOOTING
---------------

Issue: "GEMINI_API_KEY not found"
Solution: Set environment variable and restart server

Issue: "Invalid API key"
Solution: 
  1. Check key at https://makersuite.google.com/app/apikey
  2. Verify no extra spaces in key
  3. Try creating a new key

Issue: "Network error"
Solution:
  1. Check internet connection
  2. Verify no firewall blocking
  3. Try again in a few seconds

Issue: "Module 'google.generativeai' not found"
Solution: pip install google-generativeai

Issue: "Rate limit exceeded"
Solution:
  - Wait a minute and retry
  - System automatically falls back to templates
  - Consider caching results


ADVANCED CONFIGURATION
----------------------

In ai_generator.py, you can customize:

1. Temperature (creativity):
   generation_config = genai.types.GenerationConfig(
       temperature=0.7,  # 0.0 = deterministic, 1.0 = creative
   )

2. Max tokens (response length):
   generation_config = genai.types.GenerationConfig(
       max_output_tokens=8192,
   )

3. Model selection:
   self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
   # Options: gemini-2.0-flash-exp (free, fastest)


PRODUCTION TIPS
---------------

1. Cache AI responses to reduce API calls
2. Set reasonable timeouts
3. Monitor API usage
4. Have template fallback always ready
5. Log AI errors for debugging
6. Test edge cases thoroughly


CHECKING STATUS
---------------

To check if AI is enabled:
- Start server and look for: 🤖 Gemini AI enabled
- Or check: GET /api/generate/topics
- Or run: python test_gemini_integration.py


GETTING HELP
------------

Common Resources:
- Gemini API Docs: https://ai.google.dev/docs
- API Key Console: https://makersuite.google.com/app/apikey
- Python Package: https://pypi.org/project/google-generativeai/

Error Messages:
- All errors include helpful hints
- Check server logs for details
- Run standalone test for diagnosis


EXAMPLE SESSION
---------------

$ pip install google-generativeai
✅ Successfully installed

$ $env:GEMINI_API_KEY="AIza..."
✅ Environment variable set

$ python test_gemini_standalone.py
✅ Dependencies installed
✅ API key found
✅ Service imported
✅ Test cases generated
✅ Starter code generated
🎉 All tests passed!

$ python -m uvicorn app.main:app --reload
🤖 Gemini AI enabled for problem generation
INFO: Started server process

$ python test_gemini_integration.py
✅ Gemini AI is active and working!


YOU'RE ALL SET! 🎉
------------------
Your backend now has AI-powered problem generation.
Start using the /api/generate/gemini/* endpoints!
"""

print(__doc__)
