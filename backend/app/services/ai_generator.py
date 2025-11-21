"""
AI-Powered Problem Generator Service

This service generates coding problems with test cases.
Currently uses a template-based approach, but designed to be easily
replaced with actual AI API calls (Gemini, ChatGPT, etc.)
"""

from typing import Dict, List, Optional
import random
import os
import asyncio
import copy


# Try to import Gemini service (optional)
try:
    from .gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


MIN_TEST_CASES = 10


class AIGenerator:
    """
    AI Generator for creating coding problems.
    
    This is a template-based implementation that can be easily replaced
    with actual AI API calls (Gemini, OpenAI, etc.)
    """
    
    # Problem templates for different topics
    PROBLEM_TEMPLATES = {
        "two-sum": {
            "title": "Two Sum",
            "difficulty": "easy",
            "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers in the array such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order. The array is 0-indexed, meaning the first element is at index 0.

For example, if `nums = [2, 7, 11, 15]` and `target = 9`, the function should return `[0, 1]` because `nums[0] + nums[1] = 2 + 7 = 9`.""",
            "constraints": [
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9",
                "Only one valid answer exists"
            ],
            "samples": [
                {"input": "2 7 11 15\n9", "output": "0 1"},
                {"input": "3 2 4\n6", "output": "1 2"}
            ],
            "test_cases": [
                {"input": "2 7 11 15\n9", "expected_output": "0 1"},
                {"input": "3 2 4\n6", "expected_output": "1 2"},
                {"input": "3 3\n6", "expected_output": "0 1"},
                {"input": "1 2 3 4 5\n9", "expected_output": "3 4"},
                {"input": "10 20 30 40\n50", "expected_output": "1 2"},
                {"input": "-1 -2 -3 -4 -5\n-8", "expected_output": "2 4"},
                {"input": "0 4 3 0\n0", "expected_output": "0 3"},
                {"input": "100 200 300 400 500\n700", "expected_output": "2 4"},
                {"input": "1 1 1 1 1\n2", "expected_output": "0 1"},
                {"input": "5 5 5 5 5\n10", "expected_output": "0 1"}
            ]
        },
        "palindrome": {
            "title": "Valid Palindrome",
            "difficulty": "easy",
            "description": """A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.

Given a string `s`, return `true` if it is a palindrome, or `false` otherwise.

For example, `"A man, a plan, a canal: Panama"` is a palindrome because after removing spaces and punctuation and converting to lowercase, it becomes `"amanaplanacanalpanama"` which reads the same forwards and backwards.""",
            "constraints": [
                "1 <= s.length <= 2 * 10^5",
                "s consists only of printable ASCII characters"
            ],
            "samples": [
                {"input": "A man, a plan, a canal: Panama", "output": "true"},
                {"input": "race a car", "output": "false"}
            ],
            "test_cases": [
                {"input": "A man, a plan, a canal: Panama", "expected_output": "true"},
                {"input": "race a car", "expected_output": "false"},
                {"input": " ", "expected_output": "true"},
                {"input": "a", "expected_output": "true"},
                {"input": "ab", "expected_output": "false"},
                {"input": "aba", "expected_output": "true"},
                {"input": "Madam", "expected_output": "true"},
                {"input": "Was it a car or a cat I saw", "expected_output": "true"},
                {"input": "Never odd or even", "expected_output": "true"},
                {"input": "hello world", "expected_output": "false"}
            ]
        },
        "reverse-string": {
            "title": "Reverse String",
            "difficulty": "easy",
            "description": """Write a function that reverses a string. The input string is given as an array of characters.

You must do this by modifying the input array in-place with O(1) extra memory.

For example, given input `["h","e","l","l","o"]`, your function should modify it to `["o","l","l","e","h"]`.

Print the result as a single string without spaces.""",
            "constraints": [
                "1 <= s.length <= 10^5",
                "s[i] is a printable ascii character"
            ],
            "samples": [
                {"input": "hello", "output": "olleh"},
                {"input": "world", "output": "dlrow"}
            ],
            "test_cases": [
                {"input": "hello", "expected_output": "olleh"},
                {"input": "world", "expected_output": "dlrow"},
                {"input": "a", "expected_output": "a"},
                {"input": "ab", "expected_output": "ba"},
                {"input": "abc", "expected_output": "cba"},
                {"input": "abcd", "expected_output": "dcba"},
                {"input": "python", "expected_output": "nohtyp"},
                {"input": "12345", "expected_output": "54321"},
                {"input": "race car", "expected_output": "rac ecar"},
                {"input": "A man a plan a canal Panama", "expected_output": "amanaP lanac a nalp a nam A"}
            ]
        },
        "fizzbuzz": {
            "title": "FizzBuzz",
            "difficulty": "easy",
            "description": """Given an integer `n`, return a string array answer (1-indexed) where:

- answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
- answer[i] == "Fizz" if i is divisible by 3.
- answer[i] == "Buzz" if i is divisible by 5.
- answer[i] == i (as a string) if none of the above conditions are true.

Print each answer on a new line.

For example, if n = 5, the output should be:
1
2
Fizz
4
Buzz""",
            "constraints": [
                "1 <= n <= 10^4"
            ],
            "samples": [
                {"input": "5", "output": "1\n2\nFizz\n4\nBuzz"},
                {"input": "15", "output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"}
            ],
            "test_cases": [
                {"input": "5", "expected_output": "1\n2\nFizz\n4\nBuzz"},
                {"input": "15", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"},
                {"input": "1", "expected_output": "1"},
                {"input": "3", "expected_output": "1\n2\nFizz"},
                {"input": "10", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz"},
                {"input": "20", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n16\n17\nFizz\n19\nBuzz"},
                {"input": "30", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n16\n17\nFizz\n19\nBuzz\nFizz\n22\n23\nFizz\nBuzz\n26\nFizz\n28\n29\nFizzBuzz"},
                {"input": "2", "expected_output": "1\n2"},
                {"input": "6", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz"},
                {"input": "9", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz"}
            ]
        },
        "factorial": {
            "title": "Factorial Calculation",
            "difficulty": "easy",
            "description": """Given a non-negative integer `n`, calculate and return its factorial.

The factorial of a non-negative integer n, denoted by n!, is the product of all positive integers less than or equal to n.

For example:
- 5! = 5 × 4 × 3 × 2 × 1 = 120
- 0! = 1 (by definition)
- 1! = 1

Your function should take an integer as input and print its factorial.""",
            "constraints": [
                "0 <= n <= 20",
                "Result will fit in a 64-bit integer"
            ],
            "samples": [
                {"input": "5", "output": "120"},
                {"input": "0", "output": "1"}
            ],
            "test_cases": [
                {"input": "0", "expected_output": "1"},
                {"input": "1", "expected_output": "1"},
                {"input": "2", "expected_output": "2"},
                {"input": "3", "expected_output": "6"},
                {"input": "4", "expected_output": "24"},
                {"input": "5", "expected_output": "120"},
                {"input": "6", "expected_output": "720"},
                {"input": "7", "expected_output": "5040"},
                {"input": "10", "expected_output": "3628800"},
                {"input": "15", "expected_output": "1307674368000"}
            ]
        },
        "array-sum": {
            "title": "Array Sum",
            "difficulty": "easy",
            "description": """Given an array of integers, calculate and return the sum of all elements in the array.

The array will contain at least one element. The input format will be all integers on a single line separated by spaces.

For example, if the input is `1 2 3 4 5`, the output should be `15`.""",
            "constraints": [
                "1 <= array.length <= 10^4",
                "-10^9 <= array[i] <= 10^9",
                "The sum will fit in a 64-bit signed integer"
            ],
            "samples": [
                {"input": "1 2 3 4 5", "output": "15"},
                {"input": "10 20 30", "output": "60"}
            ],
            "test_cases": [
                {"input": "1 2 3 4 5", "expected_output": "15"},
                {"input": "10 20 30", "expected_output": "60"},
                {"input": "1", "expected_output": "1"},
                {"input": "0", "expected_output": "0"},
                {"input": "-1 -2 -3", "expected_output": "-6"},
                {"input": "100 200 300 400 500", "expected_output": "1500"},
                {"input": "1 1 1 1 1 1 1 1 1 1", "expected_output": "10"},
                {"input": "-5 5", "expected_output": "0"},
                {"input": "999 999 999", "expected_output": "2997"},
                {"input": "123 456 789", "expected_output": "1368"}
            ]
        }
    }
    
    def __init__(self, ai_api_key: Optional[str] = None, use_ai: bool = False):
        """
        Initialize the AI Generator.
        
        Args:
            ai_api_key: API key for external AI service (Gemini)
            use_ai: Whether to use AI (Gemini) or templates (default: False)
        """
        self.ai_api_key = ai_api_key
        self.use_ai = use_ai and GEMINI_AVAILABLE
        
        # Initialize Gemini if enabled
        if self.use_ai:
            try:
                self.gemini_service = GeminiService(ai_api_key)
                print("Gemini AI enabled for problem generation")
            except Exception as e:
                print(f"WARNING: Gemini initialization failed: {e}")
                print("   Falling back to template-based generation")
                self.use_ai = False
                self.gemini_service = None
        else:
            self.gemini_service = None
    
    def generate_problem(self, topic: str = "two-sum", difficulty: str = "easy") -> Dict:
        """
        Generate a coding problem with test cases.
        
        Uses Gemini AI if enabled, otherwise falls back to templates.
        
        Args:
            topic: Problem topic/type (e.g., "two-sum", "palindrome")
            difficulty: Problem difficulty ("easy", "medium", "hard")
        
        Returns:
            Dict containing problem details and test cases
        
        Example:
            {
                "title": "Two Sum",
                "difficulty": "easy",
                "description": "...",
                "constraints": [...],
                "samples": [...],
                "test_cases": [...]
            }
        """
        # Try Gemini AI if enabled
        if self.use_ai and self.gemini_service:
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                problem = loop.run_until_complete(
                    self.gemini_service.generate_complete_problem(topic, difficulty)
                )
                loop.close()
                return self._normalize_problem(problem)
            except Exception as e:
                print(f"WARNING: Gemini generation failed: {e}")
                print("   Falling back to templates...")
        
        # Use templates (original behavior)
        topic_key = topic.lower().replace(" ", "-")
        template = self.PROBLEM_TEMPLATES.get(topic_key)
        
        if not template:
            # Return a generic problem if topic not found
            template = self._generate_generic_problem(topic, difficulty)
        
            # Override difficulty if specified
            problem = template
        if difficulty in ["easy", "medium", "hard"]:
            problem["difficulty"] = difficulty
        
        return self._normalize_problem(problem)

    def _normalize_problem(self, problem: Dict) -> Dict:
        """Ensure downstream consumers receive consistent problem structure."""
        if not isinstance(problem, dict):
            return problem

        # Protect against templates sharing nested lists
        normalized = copy.deepcopy(problem)
        self._ensure_min_test_cases(normalized)
        return normalized

    def _stringify(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        return str(value).strip()

    def _ensure_min_test_cases(self, problem: Dict) -> None:
        raw_cases = problem.get("test_cases") or []
        normalized: List[Dict[str, str]] = []
        seen = set()

        for case in raw_cases:
            input_val = self._stringify(case.get("input") or case.get("input_data"))
            output_val = self._stringify(
                case.get("expected_output") or case.get("output")
            )
            if not input_val or not output_val:
                continue
            key = (input_val, output_val)
            if key in seen:
                continue
            normalized.append({"input": input_val, "expected_output": output_val})
            seen.add(key)

        sample_source = problem.get("samples") or []
        for sample in sample_source:
            if len(normalized) >= MIN_TEST_CASES:
                break
            input_val = self._stringify(sample.get("input") or sample.get("input_data"))
            output_val = self._stringify(sample.get("output") or sample.get("expected_output"))
            if not input_val or not output_val:
                continue
            key = (input_val, output_val)
            if key in seen:
                continue
            normalized.append({"input": input_val, "expected_output": output_val})
            seen.add(key)

        if normalized:
            while len(normalized) < MIN_TEST_CASES:
                seed = normalized[len(normalized) % len(normalized)]
                normalized.append({"input": seed["input"], "expected_output": seed["expected_output"]})
        else:
            for i in range(1, MIN_TEST_CASES + 1):
                normalized.append({"input": str(i), "expected_output": str(i)})

        problem["test_cases"] = normalized
    
    def _generate_generic_problem(self, topic: str, difficulty: str) -> Dict:
        """
        Generate a generic problem when specific template not found.
        
        Args:
            topic: Problem topic
            difficulty: Problem difficulty
        
        Returns:
            Generic problem template
        """
        return {
            "title": f"{topic.title()} Problem",
            "difficulty": difficulty,
            "description": f"""This is a {difficulty} level problem about {topic}.

Implement a solution that solves the {topic} problem efficiently.

The input will be provided on separate lines, and you should output the result according to the problem requirements.

Make sure to handle edge cases and follow the constraints provided.""",
            "constraints": [
                "1 <= input.length <= 10^4",
                "Follow standard input/output format",
                "Optimize for time complexity"
            ],
            "samples": [
                {"input": "5", "output": "5"},
                {"input": "10", "output": "10"}
            ],
            "test_cases": [
                {"input": "1", "expected_output": "1"},
                {"input": "2", "expected_output": "2"},
                {"input": "3", "expected_output": "3"},
                {"input": "5", "expected_output": "5"},
                {"input": "10", "expected_output": "10"},
                {"input": "15", "expected_output": "15"},
                {"input": "20", "expected_output": "20"},
                {"input": "50", "expected_output": "50"},
                {"input": "100", "expected_output": "100"},
                {"input": "1000", "expected_output": "1000"}
            ]
        }
    
    def list_available_topics(self) -> List[str]:
        """
        List all available problem topics.
        
        Returns:
            List of topic names
        """
        return list(self.PROBLEM_TEMPLATES.keys())


# TODO: Integration with actual AI APIs
# 
# To integrate with Gemini API:
# def generate_problem_with_gemini(self, prompt: str) -> Dict:
#     import google.generativeai as genai
#     genai.configure(api_key=self.ai_api_key)
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content(prompt)
#     # Parse response and return structured data
#     return parse_ai_response(response.text)
#
# To integrate with OpenAI API:
# def generate_problem_with_openai(self, prompt: str) -> Dict:
#     import openai
#     openai.api_key = self.ai_api_key
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     # Parse response and return structured data
#     return parse_ai_response(response.choices[0].message.content)
