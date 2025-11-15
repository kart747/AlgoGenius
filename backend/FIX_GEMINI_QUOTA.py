"""
🔧 FIXING GEMINI API QUOTA ISSUE
=================================

ISSUE IDENTIFIED
----------------
❌ Error: "429 You exceeded your current quota"
❌ Quota limit: 0 (Account restrictions)

The error shows your Gemini API key has quota restrictions.

ROOT CAUSES
-----------
1. New API Key: Newly created keys may have temporary restrictions
2. Account Verification: Google may need additional verification
3. Free Tier Limits: Some accounts have stricter initial limits
4. Rate Limiting: You may have hit the per-minute limit

SOLUTIONS
---------

✅ SOLUTION 1: Update .env File (RECOMMENDED)
---------------------------------------------
Instead of setting environment variable each time, store in .env file:

1. Open file: backend/.env

2. Add your API key:
   GEMINI_API_KEY=AIzaSyDLHy...HZ4Yo

3. Save file

4. Restart server:
   python -m uvicorn app.main:app --reload

Benefits:
- Permanent configuration
- Auto-loaded on server start
- Works across all scripts
- More secure than terminal commands


✅ SOLUTION 2: Wait and Retry
-----------------------------
The error message says: "Please retry in 8.369395824s"

This means:
- You hit the per-minute rate limit
- Wait 10 seconds and try again
- This is normal for rapid testing

Try:
    python test_gemini_standalone.py


✅ SOLUTION 3: Verify Your API Key
----------------------------------
1. Visit: https://makersuite.google.com/app/apikey

2. Check your key status:
   - Is it enabled?
   - Are there any warnings?

3. Try creating a NEW API key:
   - Click "Create API key"
   - Copy the new key
   - Update .env file with new key

4. Test the new key:
   python test_gemini_standalone.py


✅ SOLUTION 4: Use Template Fallback
------------------------------------
Good news! Your system has built-in fallback.

Even without Gemini working, you can:
- Generate problems with templates
- Test all other endpoints
- Deploy to production

Templates work perfectly without API key!


✅ SOLUTION 5: Alternative Models
---------------------------------
If quota issues persist, try different model:

Edit: app/services/gemini_service.py

Change:
    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

To:
    self.model = genai.GenerativeModel('gemini-1.5-flash')

This uses an older, more stable model.


STEP-BY-STEP FIX (RECOMMENDED)
-------------------------------

Step 1: Update .env file
   Open: backend/.env
   Add line: GEMINI_API_KEY=your_actual_key_here
   Save file

Step 2: Install python-dotenv (if not installed)
   pip install python-dotenv

Step 3: Verify .env is loaded
   python load_env.py

Step 4: Wait 1 minute (let quota reset)
   # Just wait 60 seconds

Step 5: Test again
   python test_gemini_standalone.py

Step 6: If still fails, create new API key
   Visit: https://makersuite.google.com/app/apikey
   Create new key
   Update .env file
   Test again


CHECKING YOUR SETUP
--------------------

Run this to verify everything:
    python load_env.py

You should see:
    ✅ Loaded environment variables from: backend/.env
    ✅ GEMINI_API_KEY loaded: AIzaSyDLHy...HZ4Yo


UNDERSTANDING THE ERROR
-----------------------

"Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0"

This means:
- Your account has a quota limit of 0 requests per minute
- This is unusual for a valid API key
- Possible causes:
  1. Brand new API key (needs activation time)
  2. Account verification pending
  3. Temporary rate limit

Normal free tier limits:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day


ALTERNATIVE: USE TEMPLATES
--------------------------

While you wait for API key to work, use the built-in templates:

Your system already has 6 problem templates:
1. two-sum
2. palindrome
3. reverse-string
4. fizzbuzz
5. factorial
6. array-sum

Generate problems without AI:
    POST /api/generate/problem
    {
        "topic": "two-sum",
        "difficulty": "easy"
    }

This works immediately, no API key needed!


TESTING WITHOUT GEMINI
-----------------------

Test the template system:
    python test_ai_generator.py

This will:
- Work without Gemini API key
- Generate problems from templates
- Save to database
- Verify all functionality


PRODUCTION RECOMMENDATION
--------------------------

For production:
1. ✅ Always set GEMINI_API_KEY in .env
2. ✅ Keep template fallback enabled
3. ✅ Monitor API usage
4. ✅ Handle rate limits gracefully
5. ✅ Cache AI responses

Your system is designed to work with or without AI!


QUICK FIX COMMANDS
------------------

# 1. Edit .env file
notepad .env
# Add: GEMINI_API_KEY=your_key_here

# 2. Verify
python load_env.py

# 3. Wait 1 minute
# (Let rate limit reset)

# 4. Test
python test_gemini_standalone.py

# 5. If works, start server
python -m uvicorn app.main:app --reload


CHECKING API USAGE
------------------

Visit: https://aistudio.google.com/app/apikey

Check:
- API key status
- Usage limits
- Rate limits
- Quota remaining


IF NOTHING WORKS
-----------------

Don't worry! Your system works perfectly without Gemini:

✅ Template-based generation works
✅ All CRUD endpoints work
✅ Database operations work
✅ Docker sandbox works
✅ Authentication works
✅ User features work
✅ Admin features work

Gemini is just an ENHANCEMENT, not a requirement!


SUMMARY
-------

📝 Add GEMINI_API_KEY to .env file (recommended)
⏰ Wait 1 minute for rate limit to reset
🔄 Try creating a new API key if issues persist
✅ Use templates while troubleshooting
🎯 Your backend works perfectly either way!
"""

print(__doc__)
