"""
AI API Integration Guide
========================

This guide shows how to replace the template-based generator with real AI APIs.

Current Implementation
----------------------
The system currently uses predefined templates in ai_generator.py.
This works perfectly for testing and development, but you can easily
integrate real AI APIs for dynamic problem generation.

Integration Options
-------------------

1. GOOGLE GEMINI API
--------------------
Install: pip install google-generativeai

Code Example:

    import google.generativeai as genai
    
    class AIGenerator:
        def __init__(self, ai_api_key: str):
            genai.configure(api_key=ai_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        def generate_problem(self, topic: str, difficulty: str) -> Dict:
            prompt = f'''
            Generate a {difficulty} coding problem about {topic}.
            Return JSON format:
            {{
                "title": "Problem Title",
                "difficulty": "{difficulty}",
                "description": "Detailed description...",
                "constraints": ["constraint 1", "constraint 2"],
                "samples": [{{"input": "...", "output": "..."}}],
                "test_cases": [{{"input": "...", "expected_output": "..."}}]
            }}
            '''
            
            response = self.model.generate_content(prompt)
            return json.loads(response.text)

2. OPENAI CHATGPT API
----------------------
Install: pip install openai

Code Example:

    import openai
    
    class AIGenerator:
        def __init__(self, ai_api_key: str):
            openai.api_key = ai_api_key
        
        def generate_problem(self, topic: str, difficulty: str) -> Dict:
            prompt = f'''
            Generate a {difficulty} level coding problem about {topic}.
            Include: title, description, constraints, sample I/O, and 10 test cases.
            Return valid JSON only.
            '''
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a coding problem generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)

3. ANTHROPIC CLAUDE API
------------------------
Install: pip install anthropic

Code Example:

    import anthropic
    
    class AIGenerator:
        def __init__(self, ai_api_key: str):
            self.client = anthropic.Anthropic(api_key=ai_api_key)
        
        def generate_problem(self, topic: str, difficulty: str) -> Dict:
            prompt = f'''Generate a {difficulty} coding problem about {topic}...'''
            
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(message.content[0].text)

Step-by-Step Integration
-------------------------

Step 1: Choose your AI provider
- Gemini: Free tier available, good for coding
- ChatGPT: Best quality, requires paid API
- Claude: Great at structured output

Step 2: Get API key
- Visit provider's website
- Create API key
- Store in environment variable

Step 3: Update ai_generator.py
Replace the generate_problem() method with AI API calls.

Step 4: Add API key to .env
Add to your .env file:
    AI_API_KEY=your_actual_api_key_here
    AI_PROVIDER=gemini  # or openai, claude

Step 5: Load API key in generator.py
Update the router initialization:

    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    ai_api_key = os.getenv("AI_API_KEY")
    ai_generator = AIGenerator(ai_api_key=ai_api_key)

Step 6: Test
Run: python test_ai_generator.py

Best Practices
--------------

1. Prompt Engineering
   - Be specific about output format
   - Request JSON structure explicitly
   - Include examples in prompt
   - Specify test case requirements

2. Error Handling
   - Wrap AI calls in try-except
   - Validate JSON structure
   - Have fallback to templates
   - Log API errors

3. Cost Optimization
   - Cache generated problems
   - Use templates for common problems
   - Set token limits
   - Monitor API usage

4. Quality Control
   - Validate test cases programmatically
   - Check for duplicate test cases
   - Verify expected outputs
   - Review generated problems

Example Prompt Template
-----------------------

GENERATE_PROBLEM_PROMPT = '''
Generate a competitive programming problem with the following requirements:

Topic: {topic}
Difficulty: {difficulty}

Requirements:
1. Clear problem statement (3-5 paragraphs)
2. Specific constraints with ranges
3. 2 sample inputs/outputs with explanations
4. 10 unique test cases covering:
   - Basic cases
   - Edge cases (empty, single element, max size)
   - Corner cases (negative numbers, duplicates)
   - Maximum constraint tests

Output must be valid JSON with this exact structure:
{{
    "title": "Problem Title",
    "difficulty": "easy|medium|hard",
    "description": "Full problem description",
    "constraints": ["constraint 1", "constraint 2"],
    "samples": [
        {{"input": "test input", "output": "expected output"}}
    ],
    "test_cases": [
        {{"input": "test input", "expected_output": "exact output"}}
    ]
}}

Important:
- No code solutions
- Exact expected outputs (no extra spaces)
- Input format must be clear
- Test cases must be valid
'''

Hybrid Approach (Recommended)
------------------------------

Use templates for common problems, AI for custom requests:

    def generate_problem(self, topic: str, difficulty: str) -> Dict:
        # Check if template exists
        if topic in self.PROBLEM_TEMPLATES:
            return self.PROBLEM_TEMPLATES[topic]
        
        # Use AI for new topics
        return self._generate_with_ai(topic, difficulty)

Testing Your Integration
-------------------------

1. Test with simple topics first
2. Verify JSON structure
3. Check test case validity
4. Run generated problems through sandbox
5. Monitor API costs
6. Compare AI vs template quality

Environment Variables Setup
---------------------------

Create .env file:

    # AI Configuration
    AI_API_KEY=your_key_here
    AI_PROVIDER=gemini
    AI_MODEL=gemini-pro
    
    # Existing config
    JWT_SECRET=your_jwt_secret
    DATABASE_URL=postgresql://...

Common Issues & Solutions
-------------------------

Issue: AI returns invalid JSON
Solution: Add JSON validation and retry logic

Issue: Test cases don't work
Solution: Validate test cases before saving

Issue: API timeout
Solution: Implement async calls and caching

Issue: High API costs
Solution: Use caching and template fallback

Need Help?
----------
- Check AI provider documentation
- Test with small examples first
- Monitor API usage dashboard
- Use temperature=0.7 for consistency
'''

print(__doc__)
