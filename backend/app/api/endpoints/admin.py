from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app.models import User, Problem, TestCase, Submission
from app.api.endpoints.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class TestCaseCreate(BaseModel):
    input_data: str
    expected_output: str


class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    test_cases: Optional[List[TestCaseCreate]] = None


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")


class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: int
    username: str
    email: str
    xp: int
    current_streak: int
    is_admin: int
    last_submission_date: Optional[date]

    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    total_users: int
    total_problems: int
    total_submissions: int
    daily_submission_count: int
    accepted_ratio: float
    top_language_used: str


# ============================================================
# PROBLEM MANAGEMENT ENDPOINTS
# ============================================================

@router.post("/problems", response_model=ProblemResponse, status_code=201)
def admin_create_problem(
    problem: ProblemCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Create a new problem with optional test cases.
    Admin only.
    """
    # Create problem
    db_problem = Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)

    # Add test cases if provided
    if problem.test_cases:
        for tc in problem.test_cases:
            test_case = TestCase(
                problem_id=db_problem.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output
            )
            db.add(test_case)
        db.commit()
        db.refresh(db_problem)

    return db_problem


@router.put("/problems/{problem_id}", response_model=ProblemResponse)
def admin_update_problem(
    problem_id: int,
    problem_update: ProblemUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Update a problem's details.
    Admin only.
    """
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Update only provided fields
    if problem_update.title is not None:
        db_problem.title = problem_update.title
    if problem_update.description is not None:
        db_problem.description = problem_update.description
    if problem_update.difficulty is not None:
        db_problem.difficulty = problem_update.difficulty

    db.commit()
    db.refresh(db_problem)
    return db_problem


@router.delete("/problems/{problem_id}", status_code=204)
def admin_delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Delete a problem and all its test cases (cascade).
    Admin only.
    """
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    db.delete(db_problem)
    db.commit()
    return None


@router.post("/problems/{problem_id}/testcases", status_code=201)
def admin_add_test_case(
    problem_id: int,
    test_case: TestCaseCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Add a test case to an existing problem.
    Admin only.
    """
    # Check if problem exists
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Create test case
    db_test_case = TestCase(
        problem_id=problem_id,
        input_data=test_case.input_data,
        expected_output=test_case.expected_output
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)

    return {
        "id": db_test_case.id,
        "problem_id": db_test_case.problem_id,
        "input_data": db_test_case.input_data,
        "expected_output": db_test_case.expected_output
    }


@router.delete("/testcases/{testcase_id}", status_code=204)
def admin_delete_test_case(
    testcase_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Delete a specific test case.
    Admin only.
    """
    db_test_case = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not db_test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    db.delete(db_test_case)
    db.commit()
    return None


# ============================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================

@router.get("/users", response_model=List[UserListResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    List all users in the system.
    Admin only.
    """
    users = db.query(User).all()
    return users


@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Delete a user and all their submissions.
    Admin only.
    """
    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete all user's submissions first (if not cascade configured)
    db.query(Submission).filter(Submission.user_id == user_id).delete()
    
    # Delete user
    db.delete(db_user)
    db.commit()
    return None


# ============================================================
# METRICS ENDPOINT
# ============================================================

@router.get("/stats", response_model=AdminStatsResponse)
def admin_get_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    Get platform statistics.
    Admin only.
    """
    # Total counts
    total_users = db.query(func.count(User.id)).scalar()
    total_problems = db.query(func.count(Problem.id)).scalar()
    total_submissions = db.query(func.count(Submission.id)).scalar()

    # Daily submission count (today)
    today = date.today()
    daily_count = db.query(func.count(Submission.id)).filter(
        func.date(Submission.created_at) == today
    ).scalar()

    # Accepted ratio
    accepted_count = db.query(func.count(Submission.id)).filter(
        Submission.status == "Accepted"
    ).scalar()
    
    if total_submissions > 0:
        accepted_ratio = round((accepted_count / total_submissions) * 100, 2)
    else:
        accepted_ratio = 0.0

    # Top language used
    language_stats = db.query(
        Submission.language,
        func.count(Submission.id).label("count")
    ).group_by(Submission.language).order_by(func.count(Submission.id).desc()).first()

    top_language = language_stats[0] if language_stats else "N/A"

    return {
        "total_users": total_users,
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "daily_submission_count": daily_count,
        "accepted_ratio": accepted_ratio,
        "top_language_used": top_language
    }
