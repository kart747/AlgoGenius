from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Optional

app = FastAPI(title="AlgoGenius Dummy Backend", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SubmissionRequest(BaseModel):
    problem_id: Optional[int] = None
    code: str
    language: str

class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class RegisterRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to AlgoGenius Dummy Backend!",
        "status": "running",
        "endpoints": [
            "/problems/today",
            "/submissions",
            "/users/leaderboard",
            "/auth/login",
            "/auth/register"
        ]
    }


# 1. GET /problems/today - Returns today's problem
@app.get("/problems/today")
def get_daily_problem():
    return {
        "id": 1,
        "title": "Sum of Two Numbers",
        "problem_statement": "Write a program that reads two integers from stdin (one per line) and outputs their sum to stdout. This tests your ability to handle stdin/stdout for competitive programming.",
        "test_cases": [
            {
                "input": "5\n3",
                "expected_output": "8",
                "explanation": "5 + 3 = 8"
            },
            {
                "input": "10\n20",
                "expected_output": "30",
                "explanation": "10 + 20 = 30"
            },
            {
                "input": "-5\n15",
                "expected_output": "10",
                "explanation": "-5 + 15 = 10"
            }
        ]
    }


# 2. POST /submissions - Simulates code submission with stdin/stdout testing
@app.post("/submissions")
async def submit_code(submission: SubmissionRequest):
    # Simulate processing time (2 seconds)
    await asyncio.sleep(2)
    
    # Simulate test case execution
    # In a real system, you would execute the code with each test case's input
    # and compare the actual output with expected output
    
    test_results = [
        {
            "test_case": 1,
            "passed": True,
            "input": "5\n3",
            "expected": "8",
            "actual": "8"
        },
        {
            "test_case": 2,
            "passed": True,
            "input": "10\n20",
            "expected": "30",
            "actual": "30"
        },
        {
            "test_case": 3,
            "passed": True,
            "input": "-5\n15",
            "expected": "10",
            "actual": "10"
        }
    ]
    
    # Check if all tests passed
    all_passed = all(test["passed"] for test in test_results)
    
    return {
        "status": "Accepted" if all_passed else "Wrong Answer",
        "message": "All test cases passed! Your solution is correct." if all_passed else "Some test cases failed.",
        "test_results": test_results,
        "total_tests": len(test_results),
        "passed_tests": sum(1 for test in test_results if test["passed"]),
        "language": submission.language,
        "problem_id": submission.problem_id
    }


# 3. GET /users/leaderboard - Returns leaderboard data
@app.get("/users/leaderboard")
def get_leaderboard():
    return [
        {"rank": 1, "username": "Alice", "xp": 1500, "streak": 50},
        {"rank": 2, "username": "Bob", "xp": 1450, "streak": 45},
        {"rank": 3, "username": "Charlie", "xp": 1300, "streak": 30},
        {"rank": 4, "username": "Diana", "xp": 1250, "streak": 28},
        {"rank": 5, "username": "Eve", "xp": 1200, "streak": 25},
        {"rank": 6, "username": "Frank", "xp": 1150, "streak": 22},
        {"rank": 7, "username": "Grace", "xp": 1100, "streak": 20},
        {"rank": 8, "username": "Henry", "xp": 1050, "streak": 18},
        {"rank": 9, "username": "Ivy", "xp": 1000, "streak": 15},
        {"rank": 10, "username": "Jack", "xp": 950, "streak": 12}
    ]


# 4. POST /auth/login - Simulates user login
@app.post("/auth/login")
def login(credentials: LoginRequest):
    return {
        "message": "Login successful!",
        "access_token": "dummy_jwt_token_for_testing",
        "user": {
            "email": credentials.email,
            "username": "DummyUser"
        }
    }


# Bonus: POST /auth/register - Simulates user registration
@app.post("/auth/register")
def register(user_data: RegisterRequest):
    return {
        "message": "Registration successful!",
        "access_token": "dummy_jwt_token_for_new_user",
        "user": {
            "username": user_data.username,
            "email": user_data.email
        }
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running smoothly"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
