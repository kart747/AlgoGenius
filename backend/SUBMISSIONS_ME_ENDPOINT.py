"""
===================================================================================
  NEW ENDPOINT ADDED: GET /api/submissions/me
===================================================================================

✅ Successfully added authenticated user submission history endpoint!

===================================================================================
  📋 ENDPOINT DETAILS
===================================================================================

Endpoint:     GET /api/submissions/me
Method:       GET
Auth:         Required (JWT Bearer token)
Router:       submissions
Tags:         ["submissions"]

===================================================================================
  🔧 FEATURES
===================================================================================

✅ Authentication:     Uses get_current_user dependency for JWT auth
✅ Database Query:     Uses SQLAlchemy relationships to join tables
✅ Sorting:            Returns newest submissions first (created_at DESC)
✅ Optional Code:      ?include_code=true to include source code
✅ Response Model:     Pydantic validation with SubmissionHistoryResponse

===================================================================================
  📊 REQUEST PARAMETERS
===================================================================================

Query Parameters:
  - include_code (bool, optional, default=false)
    Set to true to include submission code in response

Headers:
  - Authorization: Bearer <JWT_TOKEN>

Example Request:
  GET /api/submissions/me
  GET /api/submissions/me?include_code=true

===================================================================================
  📤 RESPONSE FORMAT
===================================================================================

Response Model: List[SubmissionHistoryResponse]

Fields:
  - submission_id (int):        Unique submission ID
  - problem_id (int):           Problem ID
  - problem_title (str):        Problem title (from relationship)
  - language (str):             Programming language used
  - status (str):               Submission status (Accepted, Wrong Answer, etc.)
  - created_at (datetime):      Timestamp of submission
  - code (str, optional):       Source code (only if include_code=true)

Example Response (without code):
[
  {
    "submission_id": 123,
    "problem_id": 5,
    "problem_title": "Two Sum",
    "language": "python",
    "status": "Accepted",
    "created_at": "2025-11-11T10:30:00"
  },
  {
    "submission_id": 122,
    "problem_id": 3,
    "problem_title": "Reverse String",
    "language": "cpp",
    "status": "Wrong Answer",
    "created_at": "2025-11-11T09:15:00"
  }
]

Example Response (with code):
[
  {
    "submission_id": 123,
    "problem_id": 5,
    "problem_title": "Two Sum",
    "language": "python",
    "status": "Accepted",
    "created_at": "2025-11-11T10:30:00",
    "code": "def solve():\\n    a, b = map(int, input().split())\\n    print(a + b)"
  }
]

===================================================================================
  💻 CODE CHANGES
===================================================================================

File: app/api/endpoints/submissions.py

1. Added imports:
   - Query from fastapi
   - datetime from datetime
   - List, Optional from typing

2. Added response schema:
   class SubmissionHistoryResponse(BaseModel):
       submission_id: int
       problem_id: int
       problem_title: str
       language: str
       status: str
       created_at: datetime
       code: Optional[str] = None

3. Added endpoint:
   @router.get("/me", response_model=List[SubmissionHistoryResponse])
   def get_my_submissions(...)

===================================================================================
  🔄 HOW IT WORKS
===================================================================================

1. User Authentication:
   - Uses get_current_user dependency
   - Validates JWT token from Authorization header
   - Extracts current_user.id

2. Database Query:
   - Queries Submission model filtered by user_id
   - Orders by created_at DESC (newest first)
   - Uses SQLAlchemy relationship to access problem.title

3. Response Building:
   - Iterates through submissions
   - Builds response dict with required fields
   - Conditionally includes code if include_code=true
   - Returns validated list of SubmissionHistoryResponse

4. SQLAlchemy Relationships Used:
   - submission.problem → accesses Problem model
   - submission.problem.title → gets problem title

===================================================================================
  🧪 TESTING
===================================================================================

To test the endpoint:

1. Start the server:
   uvicorn app.main:app --reload

2. Run the test script:
   python test_submissions_me.py

3. Or use curl:
   # Get token
   curl -X POST http://localhost:8000/api/auth/login \\
     -H "Content-Type: application/json" \\
     -d '{"username": "testuser", "password": "testpass123"}'

   # Get submissions without code
   curl -X GET http://localhost:8000/api/submissions/me \\
     -H "Authorization: Bearer <TOKEN>"

   # Get submissions with code
   curl -X GET "http://localhost:8000/api/submissions/me?include_code=true" \\
     -H "Authorization: Bearer <TOKEN>"

===================================================================================
  📝 DIFFERENCES FROM /api/users/me/submissions
===================================================================================

Existing Endpoint:  GET /api/users/me/submissions
New Endpoint:       GET /api/submissions/me

Both endpoints serve the same purpose but are organized differently:
- Old: Part of users router (/api/users/*)
- New: Part of submissions router (/api/submissions/*)

The new endpoint is more RESTful as it groups submission-related
operations under the /submissions prefix.

===================================================================================
  ✅ SUMMARY
===================================================================================

Successfully implemented:
✅ GET /api/submissions/me endpoint
✅ JWT authentication with get_current_user
✅ SQLAlchemy relationship queries (submission.problem.title)
✅ Newest-first sorting (order_by created_at DESC)
✅ Optional code inclusion (?include_code=true)
✅ Pydantic response validation
✅ Comprehensive test script

The endpoint is ready for production use! 🎉

===================================================================================
"""

if __name__ == "__main__":
    print(__doc__)
