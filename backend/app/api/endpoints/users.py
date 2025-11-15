from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models import User, Submission, Problem
from app.api.endpoints.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic Response Schemas
class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    xp: int
    current_streak: int
    last_submission_date: Optional[date]

    class Config:
        from_attributes = True


class SubmissionHistoryResponse(BaseModel):
    submission_id: int
    problem_id: int
    problem_title: str
    language: str
    status: str
    created_at: str  # ISO format datetime string

    class Config:
        from_attributes = True


class LeaderboardUserResponse(BaseModel):
    id: int
    username: str
    xp: int
    current_streak: int

    class Config:
        from_attributes = True


# Endpoints
@router.get("/me", response_model=UserProfileResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the authenticated user's profile.
    Requires JWT authentication.
    """
    return current_user


@router.get("/me/submissions", response_model=List[SubmissionHistoryResponse])
def get_user_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated user's submission history.
    Returns submissions ordered by newest first.
    Requires JWT authentication.
    """
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    # Build response with problem titles
    result = []
    for sub in submissions:
        problem = db.query(Problem).filter(Problem.id == sub.problem_id).first()
        result.append({
            "submission_id": sub.id,
            "problem_id": sub.problem_id,
            "problem_title": problem.title if problem else "Unknown",
            "language": sub.language,
            "status": sub.status,
            "created_at": sub.created_at.isoformat() if sub.created_at else ""
        })

    return result


@router.get("/leaderboard", response_model=List[LeaderboardUserResponse])
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Get the top 20 users ordered by XP (descending).
    Public endpoint - no authentication required.
    """
    top_users = (
        db.query(User)
        .order_by(User.xp.desc())
        .limit(20)
        .all()
    )

    return top_users
