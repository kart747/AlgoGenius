#!/usr/bin/env python3
"""
Test script for FastAPI /submissions/submissions POST endpoint.
Tests Python, C++, and Java code submissions.
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/submissions/"


def send_submission(user_id: int, problem_id: int, language: str, code: str) -> Dict[str, Any]:
    """
    Send a submission to the API endpoint.
    
    Args:
        user_id: The ID of the user submitting
        problem_id: The ID of the problem
        language: Programming language (python, cpp, java)
        code: Source code to submit
    
    Returns:
        JSON response from the server
    """
    payload = {
        "user_id": user_id,
        "problem_id": problem_id,
        "language": language,
        "code": code
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.json()
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed. Is the server running?"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": f"HTTP Error: {e}",
            "response": response.json() if response.content and response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def print_result(language: str, result: Dict[str, Any]):
    """Print formatted test result."""
    print(f"\n{'='*60}")
    print(f"Testing {language.upper()} Submission")
    print(f"{'='*60}")
    
    if result.get("success"):
        print(f"✅ Status Code: {result['status_code']}")
        print(f"Response: {json.dumps(result['response'], indent=2)}")
    else:
        print(f"❌ Error: {result.get('error')}")
        if result.get('response'):
            print(f"Response: {json.dumps(result['response'], indent=2)}")


def test_python_submission():
    """Test Python code submission."""
    code = """
# Simple Python program
def solve():
    n = int(input())
    print(f"The answer is {n * 2}")

solve()
"""
    
    result = send_submission(
        user_id=1,
        problem_id=1,
        language="python",
        code=code
    )
    print_result("Python", result)


def test_cpp_submission():
    """Test C++ code submission."""
    code = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << "The answer is " << n * 2 << endl;
    return 0;
}
"""
    
    result = send_submission(
        user_id=1,
        problem_id=2,
        language="cpp",
        code=code
    )
    print_result("C++", result)


def test_java_submission():
    """Test Java code submission."""
    code = """
import java.util.Scanner;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println("The answer is " + (n * 2));
        sc.close();
    }
}
"""
    
    result = send_submission(
        user_id=1,
        problem_id=3,
        language="java",
        code=code
    )
    print_result("Java", result)


def test_invalid_submission():
    """Test submission with missing fields."""
    print(f"\n{'='*60}")
    print("Testing Invalid Submission (Missing Code)")
    print(f"{'='*60}")
    
    try:
        # Missing 'code' field
        payload = {
            "user_id": 1,
            "problem_id": 4,
            "language": "python"
        }
        response = requests.post(ENDPOINT, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_empty_code_submission():
    """Test submission with empty code."""
    result = send_submission(
        user_id=1,
        problem_id=5,
        language="python",
        code=""
    )
    print_result("Empty Code", result)


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 STARTING API SUBMISSION TESTS")
    print("="*60)
    print(f"\nServer URL: {BASE_URL}")
    print(f"Endpoint: {ENDPOINT}")
    print("\nMake sure your FastAPI server is running:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    
    # Run all tests
    test_python_submission()
    test_cpp_submission()
    test_java_submission()
    test_invalid_submission()
    test_empty_code_submission()
    
    print(f"\n{'='*60}")
    print("✅ ALL TESTS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
