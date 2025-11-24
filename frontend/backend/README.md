# DevArena Dummy Backend

This is a simple FastAPI dummy backend server for testing the DevArena frontend.

## Setup Instructions

### 1. Create a virtual environment (recommended)

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
# Method 1: Using uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Method 2: Running the Python file directly
python main.py
```

The server will start on `http://127.0.0.1:8000`

## API Endpoints

### 1. GET /problems/today
Returns the daily problem with examples.

**Response:**
```json
{
  "title": "Dummy Problem: Sum of Two Numbers",
  "problem_statement": "Given an array of integers...",
  "examples": [...]
}
```

### 2. POST /submissions
Submit code for evaluation (simulates 2-second processing).

**Request Body:**
```json
{
  "code": "def solution(): ...",
  "language": "python"
}
```

**Response:**
```json
{
  "status": "Accepted",
  "message": "Your solution was correct!"
}
```

### 3. GET /users/leaderboard
Returns leaderboard data.

**Response:**
```json
[
  {"rank": 1, "username": "Alice", "xp": 1500, "streak": 50},
  ...
]
```

### 4. POST /auth/login
Simulates user login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful!",
  "access_token": "dummy_jwt_token_for_testing"
}
```

### 5. POST /auth/register
Simulates user registration.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

## Testing

Once the server is running, you can:

1. Visit `http://127.0.0.1:8000` to see the welcome message
2. Visit `http://127.0.0.1:8000/docs` to see the interactive API documentation (Swagger UI)
3. Visit `http://127.0.0.1:8000/redoc` for alternative API documentation

## Notes

- CORS is enabled for `http://localhost:3000` (Next.js default)
- All endpoints return dummy data for testing purposes
- The `/submissions` endpoint includes a 2-second delay to simulate real processing
