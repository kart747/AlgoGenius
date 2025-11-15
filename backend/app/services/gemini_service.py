"""
Google Gemini AI Integration for Test Case & Code Generation

This module provides functions to generate test cases and starter code
using Google's Gemini 2.0 Flash model (free tier).

Setup:
    pip install google-generativeai

Environment:
    GEMINI_API_KEY=your_api_key_here
"""

import os
import json
import google.generativeai as genai
from typing import List, Dict, Optional
import asyncio
from functools import wraps

try:
    from google.generativeai.types import FinishReason
except ImportError:  # pragma: no cover - defensive import if typing changes
    FinishReason = None


def async_wrap(func):
    """Wrapper to run sync functions in async context"""
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return run


class GeminiService:
    """Service class for Google Gemini API interactions with automatic fallback"""
    
    # Model configuration
    MODEL_PRIMARY = "gemini-2.5-flash"      # Primary model (requires quota)
    MODEL_FALLBACK = "gemini-1.5-flash-8b"  # Free fallback model
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini service with primary and fallback models.
        
        Args:
            api_key: Gemini API key. If None, loads from GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._last_model_used: Optional[str] = None
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize both models
        self.primary_model = genai.GenerativeModel(self.MODEL_PRIMARY)
        self.fallback_model = genai.GenerativeModel(self.MODEL_FALLBACK)
        
        # Generation config for JSON output
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
    
    def _log(self, message: str):
        """Structured logging for model usage"""
        print(f"[GeminiService] {message}")

    def _safe_response_text(self, response) -> str:
        """Extract text from a Gemini response without triggering quick accessor errors."""
        if not response:
            return ""

        # Attempt to use the quick accessor first
        try:
            text = response.text
            if text:
                return text
        except Exception:
            pass

        candidates = getattr(response, "candidates", None) or []
        collected_parts = []

        for candidate in candidates:
            finish_reason = getattr(candidate, "finish_reason", None)
            # Skip candidates cancelled for safety or similar reasons
            if FinishReason is not None and isinstance(finish_reason, FinishReason):
                if finish_reason.name.upper() == "SAFETY":  # pragma: no cover - depends on SDK enum values
                    continue
            elif isinstance(finish_reason, str) and finish_reason.upper() == "SAFETY":
                continue
            elif isinstance(finish_reason, int) and finish_reason == 2:
                continue

            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) if content else None
            if not parts:
                continue
            for part in parts:
                text_part = getattr(part, "text", None)
                if text_part:
                    collected_parts.append(text_part)

        if not collected_parts and candidates:
            reasons = ", ".join(
                str(getattr(candidate, "finish_reason", "unknown")) for candidate in candidates
            )
            self._log(f"⚠️  Received Gemini candidates without text. finish_reasons={reasons}")

        return "\n".join(collected_parts).strip()
    
    async def _generate_with_fallback(self, prompt: str) -> str:
        """
        Generate content with automatic fallback from primary to fallback model.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If both models fail
        """
        # Try primary model first
        self._log(f"Using primary model: {self.MODEL_PRIMARY}")
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.primary_model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            )

            text = self._safe_response_text(response)
            if text:
                self._log("✅ Primary model succeeded")
                self._last_model_used = self.MODEL_PRIMARY
                return text
            else:
                raise ValueError("Empty response from primary model")
                
        except Exception as e:
            error_str = str(e)
            is_quota_error = "429" in error_str or "quota" in error_str.lower() or "limit: 0" in error_str
            should_try_fallback = is_quota_error or isinstance(e, ValueError)
            
            if should_try_fallback:
                if is_quota_error:
                    self._log(
                        f"⚠️  Primary model quota exceeded (429), switching to fallback model: {self.MODEL_FALLBACK}"
                    )
                else:
                    self._log(
                        f"⚠️  Primary model returned empty/invalid content, switching to fallback model: {self.MODEL_FALLBACK}"
                    )
                
                # Try fallback model
                try:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.fallback_model.generate_content(
                            prompt,
                            generation_config=self.generation_config
                        )
                    )

                    text = self._safe_response_text(response)
                    if text:
                        self._log("✅ Fallback model succeeded")
                        self._last_model_used = self.MODEL_FALLBACK
                        return text
                    else:
                        raise ValueError("Empty response from fallback model")
                        
                except Exception as fallback_error:
                    self._log(f"❌ Fallback model failed: {str(fallback_error)}")
                    raise Exception(
                        f"Both models failed. Primary: {error_str}, "
                        f"Fallback: {str(fallback_error)}"
                    )
            else:
                # Non-quota error, don't retry with fallback
                self._log(f"❌ Primary model failed (non-quota error): {error_str}")
                raise e

    def get_last_model_used(self) -> Optional[str]:
        """Expose the most recent model used for generation."""
        return self._last_model_used
    
    async def generate_test_cases(
        self, 
        problem_text: str, 
        num_cases: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate test cases for a coding problem using Gemini AI.
        
        Args:
            problem_text: The problem description
            num_cases: Number of test cases to generate (default: 10)
        
        Returns:
            List of test cases with input_data and expected_output
            
        Raises:
            ValueError: If API key is invalid or response is malformed
            ConnectionError: If network error occurs
            Exception: For other API errors
        
        Example:
            test_cases = await generate_test_cases(
                "Given two integers, return their sum"
            )
            # Returns: [
            #     {"input_data": "3 5", "expected_output": "8"},
            #     {"input_data": "10 20", "expected_output": "30"},
            #     ...
            # ]
        """
        prompt = f"""Generate {num_cases} test cases for this coding problem.

Problem:
{problem_text}

Requirements:
1. Cover basic cases, edge cases, and boundary conditions
2. Each test case must have valid input and exact expected output
3. No duplicate test cases
4. Input format should be clear and consistent
5. Expected output must be precise (no extra spaces or newlines unless required)

Return ONLY valid JSON array in this exact format:
[
  {{"input_data": "example input", "expected_output": "example output"}},
  {{"input_data": "another input", "expected_output": "another output"}}
]

Do not include any markdown formatting, code blocks, or explanations.
Only return the raw JSON array."""

        try:
            # Use fallback logic to try primary then fallback model
            response_text = await self._generate_with_fallback(prompt)
            response_text = response_text.strip()
            
            # Clean markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            test_cases = json.loads(response_text)
            
            # Validate structure
            if not isinstance(test_cases, list):
                raise ValueError("Response is not a JSON array")
            
            for tc in test_cases:
                if "input_data" not in tc or "expected_output" not in tc:
                    raise ValueError("Test case missing required fields")
            
            return test_cases
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api key" in error_msg or "authentication" in error_msg:
                raise ValueError("Invalid Gemini API key. Check GEMINI_API_KEY environment variable.")
            
            elif "network" in error_msg or "connection" in error_msg:
                raise ConnectionError(f"Network error connecting to Gemini API: {str(e)}")
            
            else:
                raise Exception(f"Gemini API error: {str(e)}")
    
    async def generate_starter_code(
        self, 
        problem_text: str, 
        language: str
    ) -> str:
        """
        Generate starter/boilerplate code for a problem.
        
        Args:
            problem_text: The problem description
            language: Programming language ("python", "cpp", "java")
        
        Returns:
            Starter code as a string
        
        Raises:
            ValueError: If language is not supported or API error
            ConnectionError: If network error occurs
        
        Example:
            code = await generate_starter_code(
                "Given two integers, return their sum",
                "python"
            )
            # Returns:
            # def solve():
            #     a, b = map(int, input().split())
            #     # Your code here
            #     result = a + b
            #     print(result)
            #
            # solve()
        """
        # Validate language
        supported_languages = {
            "python": "Python 3",
            "cpp": "C++",
            "java": "Java"
        }
        
        if language.lower() not in supported_languages:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {', '.join(supported_languages.keys())}"
            )
        
        lang_name = supported_languages[language.lower()]
        
        prompt = f"""Generate clean starter/boilerplate code for this coding problem in {lang_name}.

Problem:
{problem_text}

Requirements:
1. Include proper input reading based on problem description
2. Add clear comments showing where to write solution logic
3. Include basic output formatting
4. Follow language best practices and conventions
5. Keep it simple and educational
6. Do NOT include the full solution - only starter template

For Python: Use standard input() and print()
For C++: Use cin/cout with proper headers
For Java: Use Scanner and System.out

Return ONLY the code without any markdown formatting or explanations.
Do not wrap in code blocks or add any text before/after the code."""

        try:
            # Use fallback logic to try primary then fallback model
            code = await self._generate_with_fallback(prompt)
            code = code.strip()
            
            # Clean markdown code blocks if present
            if "```" in code:
                # Extract code from markdown blocks
                parts = code.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are code blocks
                        # Remove language identifier
                        lines = part.split("\n")
                        if lines[0].strip().lower() in ["python", "cpp", "c++", "java", "javascript"]:
                            code = "\n".join(lines[1:])
                        else:
                            code = part
                        break
            
            return code.strip()
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api key" in error_msg or "authentication" in error_msg:
                raise ValueError("Invalid Gemini API key. Check GEMINI_API_KEY environment variable.")
            
            elif "network" in error_msg or "connection" in error_msg:
                raise ConnectionError(f"Network error connecting to Gemini API: {str(e)}")
            
            else:
                raise Exception(f"Gemini API error: {str(e)}")
    
    async def generate_complete_problem(
        self,
        topic: str,
        difficulty: str = "easy"
    ) -> Dict:
        """
        Generate a complete coding problem with description and test cases.
        
        Args:
            topic: Problem topic (e.g., "two-sum", "palindrome")
            difficulty: Problem difficulty ("easy", "medium", "hard")
        
        Returns:
            Complete problem with title, description, constraints, samples, test_cases
        """
        prompt = f"""Generate a complete {difficulty} level coding problem about {topic}.

Requirements:
1. Clear problem title
2. Detailed description (3-5 paragraphs)
3. Specific constraints with ranges
4. 2 sample inputs/outputs with explanations
5. 10 unique test cases covering edge cases

Return ONLY valid JSON in this exact format:
{{
    "title": "Problem Title",
    "difficulty": "{difficulty}",
    "description": "Full problem description...",
    "constraints": ["constraint 1", "constraint 2"],
    "samples": [
        {{"input": "sample input", "output": "expected output"}}
    ],
    "test_cases": [
        {{"input": "test input", "expected_output": "exact output"}}
    ]
}}

Do not include markdown formatting or code blocks."""

        try:
            # Use fallback logic to try primary then fallback model
            response_text = await self._generate_with_fallback(prompt)
            response_text = response_text.strip()
            
            # Clean markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            problem_data = json.loads(response_text)
            
            return problem_data
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")


# Convenience functions for direct use
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create singleton Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


async def generate_test_cases(problem_text: str, num_cases: int = 10) -> List[Dict[str, str]]:
    """
    Generate test cases for a coding problem.
    
    Args:
        problem_text: The problem description
        num_cases: Number of test cases to generate
    
    Returns:
        List of test cases with input_data and expected_output
    """
    service = get_gemini_service()
    return await service.generate_test_cases(problem_text, num_cases)


async def generate_starter_code(problem_text: str, language: str) -> str:
    """
    Generate starter/boilerplate code for a problem.
    
    Args:
        problem_text: The problem description
        language: Programming language ("python", "cpp", "java")
    
    Returns:
        Starter code as a string
    """
    service = get_gemini_service()
    return await service.generate_starter_code(problem_text, language)


# Example usage
if __name__ == "__main__":
    async def main():
        # Example problem
        problem = """
        Given two integers separated by a space, return their sum.
        
        Input: Two integers on a single line
        Output: Their sum
        
        Example:
        Input: 3 5
        Output: 8
        """
        
        print("🤖 Testing Gemini Integration\n")
        
        # Test 1: Generate test cases
        print("1. Generating test cases...")
        try:
            test_cases = await generate_test_cases(problem, num_cases=5)
            print(f"✅ Generated {len(test_cases)} test cases:")
            for i, tc in enumerate(test_cases, 1):
                print(f"   {i}. Input: {tc['input_data']}")
                print(f"      Output: {tc['expected_output']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n2. Generating Python starter code...")
        try:
            code = await generate_starter_code(problem, "python")
            print("✅ Generated code:")
            print(code)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Run example
    asyncio.run(main())
