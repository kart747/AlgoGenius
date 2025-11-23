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
import re
import google.generativeai as genai
from typing import List, Dict, Optional
import asyncio
from functools import wraps
from textwrap import dedent
from app.database import SessionLocal
from app.models import User

try:
    from google.generativeai.types import FinishReason
except ImportError:  # pragma: no cover - defensive import if typing changes
    FinishReason = None


class NonLiteralValueError(ValueError):
    """Raised when Gemini returns descriptive inputs instead of literal data."""


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
    MODEL_FALLBACK = "gemini-2.5-flash-lite"  # Free fallback model
    MAX_LITERAL_ATTEMPTS = 3
    _LITERAL_PREFIX_PATTERN = re.compile(r"^\s*(input|inputs|stdin|expected output|expected_output|output|stdout)\s*[:\-]\s*",
                                         re.IGNORECASE)
    _NON_LITERAL_REGEXES = [
        re.compile(r"\(.*?\brepeat(?:ed)?\b.*?\)", re.IGNORECASE),
        re.compile(r"\brepeat(?:ed)?\b.*?\btime(s)?\b", re.IGNORECASE),
        re.compile(r"\(.*?\bx\s*\d+.*?\)", re.IGNORECASE),
        re.compile(r"=\s*\[", re.IGNORECASE),
        re.compile(r"\b(arr|array|nums?|numbers?|target|value|values|k)\s*=\s*", re.IGNORECASE),
        re.compile(r"\[\s*-?\d+(?:\s*,\s*-?\d+)+\s*\]"),
    ]
    
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

    def _strip_markdown_fence(self, text: str) -> str:
        """Remove optional markdown fences from model output."""
        stripped = text.strip()
        if stripped.startswith("```"):
            parts = stripped.split("```")
            if len(parts) >= 2:
                candidate = parts[1].strip()
                newline_index = candidate.find("\n")
                if newline_index != -1:
                    first_line = candidate[:newline_index].strip().lower()
                    if first_line in {"json", "python", "cpp", "c++", "java", "text"}:
                        candidate = candidate[newline_index + 1 :].strip()
                return candidate
        return stripped

    def _compose_test_case_prompt(self, problem_text: str, num_cases: int, attempt: int) -> str:
        """Build the prompt with optional extra emphasis for literal inputs."""
        literal_rules = """
Input/Output Rules:
- Every input_data value must be the literal stdin text that the program receives.
- Follow HackerRank-style stdin formatting: place each scalar on its own line (or as whitespace-separated tokens) exactly as described. For one-dimensional arrays, print either `n` on its own line (if the statement specifies the length) or just the space-separated elements. For matrices, print `rows cols` on the first line, then each subsequent line contains a row's space-separated values.
- NEVER include variable names, assignment operators, JSON brackets, bullet lists, or narration like "arr = [1, 2, 3] target = 2". The correct form for that example is:
  5\n1 2 3 4 5\n2
- Do not wrap the entire input in [] or {}. Each value must appear exactly as typed on stdin.
- Expand repetitions explicitly. Do NOT describe repetition using words like "repeated" or "times".
- Never prepend labels like "Input:" or "Output:". Provide just the raw values.
- Use \n characters to denote newlines when needed and nothing else.
- The expected_output field must also only contain literal text with no narration or explanations.
    - Keep each test case modest: no more than 10 lines of stdin, no arrays longer than 30 elements, and prefer small integers (|value| <= 10^4) unless the statement explicitly demands otherwise.
    - Before finalizing a test case, manually recompute the correct output for the provided input and double-check that expected_output matches exactly. If unsure, discard the case.
""".strip()

        if attempt > 1:
            literal_rules += "\n- STRICT: Attempt {} failed. Do not use descriptive language—write the exact characters that would be typed.".format(attempt)

        return f"""Generate {num_cases} test cases for this coding problem.

Problem:
{problem_text}

Requirements:
1. Cover basic cases, edge cases, and boundary conditions
2. Each test case must have valid input and exact expected output
3. No duplicate test cases
4. Input format should be clear and consistent
5. Expected output must be precise (no extra spaces or newlines unless required)
{literal_rules}

Return ONLY valid JSON array in this exact format:
[
  {{"input_data": "example input", "expected_output": "example output"}},
  {{"input_data": "another input", "expected_output": "another output"}}
]

Do not include any markdown formatting, code blocks, or explanations.
Only return the raw JSON array."""

    async def _request_test_cases(self, prompt: str) -> List[Dict[str, str]]:
        """Call Gemini with the provided prompt and return parsed JSON data."""
        response_text = await self._generate_with_fallback(prompt)
        cleaned_text = self._strip_markdown_fence(response_text)
        test_cases = json.loads(cleaned_text)

        if not isinstance(test_cases, list):
            raise ValueError("Response is not a JSON array")

        return test_cases

    def _strip_label_prefix(self, value: str) -> str:
        """Remove leading labels like 'Input:' to keep data literal."""
        return re.sub(self._LITERAL_PREFIX_PATTERN, "", value)

    def _contains_non_literal_phrase(self, value: str) -> bool:
        """Detect natural-language descriptions such as '(repeated 3 times)'."""
        return any(pattern.search(value) for pattern in self._NON_LITERAL_REGEXES)

    def _normalize_literal_field(self, raw_value: Optional[str], field_label: str, strict_literal: bool = False) -> str:
        if raw_value is None:
            raise ValueError(f"{field_label} missing in Gemini response")

        value = str(raw_value).strip()
        if not value:
            raise ValueError(f"{field_label} is empty")

        if strict_literal:
            value = self._strip_label_prefix(value)
            value = value.replace("\r\n", "\n")
            if self._contains_non_literal_phrase(value):
                raise NonLiteralValueError(
                    f"{field_label} contains descriptive text instead of literal stdin data"
                )

        return value

    def _sanitize_test_cases(self, raw_cases: List[Dict[str, str]], minimum_cases: int) -> List[Dict[str, str]]:
        sanitized: List[Dict[str, str]] = []

        for idx, tc in enumerate(raw_cases, start=1):
            if not isinstance(tc, dict):
                raise ValueError("Test case is not an object")

            input_value = self._normalize_literal_field(
                tc.get("input_data") or tc.get("input"),
                f"test_cases[{idx}].input_data",
                strict_literal=True,
            )
            output_value = self._normalize_literal_field(
                tc.get("expected_output") or tc.get("output"),
                f"test_cases[{idx}].expected_output",
            )

            line_count = input_value.count("\n") + 1
            token_count = len(input_value.split())
            if line_count > 10 or token_count > 120:
                raise ValueError(
                    f"test_cases[{idx}].input_data is too large (lines={line_count}, tokens={token_count}); keep stdin concise"
                )
            sanitized.append({"input_data": input_value, "expected_output": output_value})

        if len(sanitized) < minimum_cases:
            raise ValueError(
                f"Gemini returned only {len(sanitized)} test cases, expected at least {minimum_cases}"
            )

        return sanitized

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
        try:
            last_literal_error: Optional[NonLiteralValueError] = None

            for attempt in range(1, self.MAX_LITERAL_ATTEMPTS + 1):
                prompt = self._compose_test_case_prompt(problem_text, num_cases, attempt)
                try:
                    raw_cases = await self._request_test_cases(prompt)
                    sanitized_cases = self._sanitize_test_cases(raw_cases, num_cases)
                    return sanitized_cases
                except NonLiteralValueError as literal_error:
                    last_literal_error = literal_error
                    self._log(
                        f"🔁 Non-literal test cases detected on attempt {attempt}. Requesting regeneration."
                    )
                    if attempt == self.MAX_LITERAL_ATTEMPTS:
                        raise
                    continue
            # Should never reach here, but guard for safety
            if last_literal_error:
                raise last_literal_error
            raise ValueError("Gemini did not return any test cases")
        
        except NonLiteralValueError as e:
            raise ValueError(
                "Gemini kept returning descriptive test inputs. Please try again or adjust the prompt."
            ) from e
        
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
    
    async def generate_function_template(
        self,
        problem_text: str,
        language: str,
    ) -> str:
        """Generate a pure function template with explicit parameters instead of stdin handling."""

        supported_languages = {
            "python": {
                "name": "Python 3",
                "function": "solve_problem",
                "parser": "parse_input",
            },
            "cpp": {
                "name": "C++",
                "function": "solveProblem",
                "parser": "ParseInput",
            },
            "java": {
                "name": "Java",
                "function": "solveProblem",
                "parser": "ParsedInput",
            },
        }

        language_key = language.lower()
        if language_key not in supported_languages:
            raise ValueError(
                f"Unsupported language: {language}. Supported: {', '.join(supported_languages.keys())}"
            )

        lang_data = supported_languages[language_key]
        lang_name = lang_data["name"]

        minimal_templates = {
            "python": (
                "def main():\n"
                "    # TODO: read from stdin and write to stdout\n"
                "    pass\n\n"
                "if __name__ == \"__main__\":\n"
                "    main()\n"
            ),
            "cpp": (
                "#include <bits/stdc++.h>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    ios::sync_with_stdio(false);\n"
                "    cin.tie(nullptr);\n\n"
                "    // TODO: read from stdin and write to stdout\n"
                "    return 0;\n"
                "}\n"
            ),
            "java": (
                "import java.io.*;\n"
                "import java.util.*;\n\n"
                "public class Main {\n"
                "    public static void main(String[] args) throws Exception {\n"
                "        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n"
                "        PrintWriter out = new PrintWriter(System.out);\n"
                "        // TODO: read input via br and write output via out\n"
                "        out.flush();\n"
                "    }\n"
                "}\n"
            ),
        }

        return minimal_templates[language_key]

    async def generate_problem_hint(
        self,
        problem_context: str,
        user_message: str,
        mode: str = "hint",
        code_context: Optional[str] = None,
    ) -> str:
        """Provide conversational help (hints/explanations) about a problem."""

        normalized_mode = (mode or "hint").lower()
        if normalized_mode not in {"hint", "explain", "debug"}:
            normalized_mode = "hint"

        style_map = {
            "hint": "Guide the learner with incremental hints. Ask leading questions, point out key observations, but avoid giving the full solution or code snippet.",
            "explain": "Deliver a thorough explanation of the approach, covering intuition, algorithm steps, complexity, and edge cases. You may reference pseudocode but avoid dumping the entire solution unless explicitly requested.",
            "debug": "Review the provided code context, highlight logical or structural issues, and suggest targeted corrections without rewriting everything from scratch.",
        }

        tone_instruction = style_map[normalized_mode]
        code_section = f"\n\nUser Code Context:\n{code_context.strip()}" if code_context else ""

        prompt = f"""You are an encouraging AI coding mentor helping a learner with a single programming problem.

Problem Context:
{problem_context.strip()}

Learner Question:
{user_message.strip()}
{code_section}

Guidelines:
- {tone_instruction}
- Keep the tone friendly and focus on reasoning steps the learner can follow next.
- Reference the problem context (constraints, inputs/outputs, tricky cases) where helpful.
- Use short paragraphs or bullet points for readability.
- Never reveal hidden test cases or paste complete final code unless the learner explicitly insists.
"""

        try:
            reply = await self._generate_with_fallback(prompt)
            return reply.strip()
        except Exception as e:
            raise Exception(f"Gemini problem assistant error: {str(e)}")
    
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
        prompt = dedent(
            f"""Generate a complete {difficulty} level coding problem about {topic}.

Requirements:
1. Clear problem title
2. Detailed description (3-5 paragraphs)
3. Specific constraints with ranges
4. 2 sample inputs/outputs with explanations
5. 10 unique test cases covering edge cases
6. All `samples[].input` and `test_cases[].input` values must be the exact stdin text a judge like HackerRank/HackerEarth/Codeforces would provide.
7. Keep each stdin reasonably small (<= 10 lines, <= 30 numbers per array, values within ±10^4 unless the problem demands larger).

Input/Output formatting rules:
- Never wrap inputs in [] or {{}} and never include variable names (no `arr = [1, 2, 3]`).
- Scalars go on their own line or as whitespace-separated tokens.
- One-dimensional arrays: optionally output `n` on its own line, then the space-separated elements on the next line.
- Matrices: first line `rows cols`, then each row as space-separated values on its own line.
- Use literal `\n` characters to denote newlines inside JSON strings; no bullet points or narration.
- `expected_output`/`output` must also be raw stdout text with no explanations appended.
- Double-check every expected_output by actually reasoning through the provided input; never guess.

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
        ).strip()

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


async def generate_function_template(problem_text: str, language: str) -> str:
    """Generate a parameterized function template without stdin handling."""
    service = get_gemini_service()
    return await service.generate_function_template(problem_text, language)


async def generate_problem_hint(
    problem_context: str,
    user_message: str,
    mode: str = "hint",
    code_context: Optional[str] = None,
) -> str:
    """Expose conversational assistance for other modules."""
    service = get_gemini_service()
    return await service.generate_problem_hint(
        problem_context,
        user_message,
        mode=mode,
        code_context=code_context,
    )


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
