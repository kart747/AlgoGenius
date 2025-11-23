from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import User, Submission, Problem, UserSolvedProblem
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
    is_admin: bool
    solved_count: int

    class Config:
        from_attributes = True


class PublicUserProfileResponse(BaseModel):
    id: int
    username: str
    xp: int
    current_streak: int
    last_submission_date: Optional[date]
    solved_count: int

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


class SolvedProblemResponse(BaseModel):
    problem_id: int
    problem_title: str
    difficulty: str
    language: str
    solved_at: datetime
    solution_code: str

    class Config:
        from_attributes = True


# Endpoints
@router.get("/me", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the authenticated user's profile.
    Requires JWT authentication.
    """
    solved_count = (
        db.query(UserSolvedProblem)
        .filter(UserSolvedProblem.user_id == current_user.id)
        .count()
    )

    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        xp=current_user.xp or 0,
        current_streak=current_user.current_streak or 0,
        last_submission_date=current_user.last_submission_date,
        is_admin=bool(current_user.is_admin),
        solved_count=solved_count,
    )


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


@router.get("/me/solved", response_model=List[SolvedProblemResponse])
def get_solved_problems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(UserSolvedProblem)
        .options(joinedload(UserSolvedProblem.problem))
        .filter(UserSolvedProblem.user_id == current_user.id)
        .order_by(UserSolvedProblem.solved_at.desc())
        .all()
    )

    return _build_solved_responses(entries, db)


@router.get("/profile/{user_id}", response_model=PublicUserProfileResponse)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    solved_count = (
        db.query(UserSolvedProblem)
        .filter(UserSolvedProblem.user_id == user_id)
        .count()
    )

    return PublicUserProfileResponse(
        id=user.id,
        username=user.username,
        xp=user.xp or 0,
        current_streak=user.current_streak or 0,
        last_submission_date=user.last_submission_date,
        solved_count=solved_count,
    )


@router.get("/{user_id}/solved", response_model=List[SolvedProblemResponse])
def get_user_solved_problems(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entries = (
        db.query(UserSolvedProblem)
        .options(joinedload(UserSolvedProblem.problem))
        .filter(UserSolvedProblem.user_id == user_id)
        .order_by(UserSolvedProblem.solved_at.desc())
        .all()
    )

    return _build_solved_responses(entries, db)


def _build_solved_responses(
    entries: List[UserSolvedProblem],
    db: Session,
) -> List[SolvedProblemResponse]:
    response: List[SolvedProblemResponse] = []
    problem_cache: Dict[int, Problem] = {}

    for entry in entries:
        problem = entry.problem
        if not problem:
            problem = problem_cache.get(entry.problem_id)
            if not problem:
                problem = (
                    db.query(Problem)
                    .filter(Problem.id == entry.problem_id)
                    .first()
                )
                if problem:
                    problem_cache[entry.problem_id] = problem

        response.append(
            SolvedProblemResponse(
                problem_id=entry.problem_id,
                problem_title=problem.title if problem else "Unknown",
                difficulty=problem.difficulty if problem else "unknown",
                language=entry.language,
                solved_at=entry.solved_at,
                solution_code=entry.solution_code,
            )
        )

    return response
