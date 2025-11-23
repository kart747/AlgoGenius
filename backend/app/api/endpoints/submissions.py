
from fastapi import APIRouter, HTTPException, Depends, Query
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from services.sandbox_manager import SandboxManager
from app.database import get_db
from app import models
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any
import math

# Configuration / Limits
ALLOWED_LANGUAGES = {"python", "cpp", "java"}
MAX_CODE_BYTES = 50 * 1024  # 50 KB
MAX_INPUT_BYTES = 64 * 1024  # 64 KB
OUTPUT_SNIPPET_LIMIT = 1200

# Simple XP mapping by difficulty
XP_BY_DIFFICULTY = {"easy": 10, "medium": 25, "hard": 50}


# Request schema
class SubmissionRequest(BaseModel):
    problem_id: int
    language: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class SubmissionRunRequest(BaseModel):
    problem_id: int
    language: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    stdin: Optional[str] = ""


# Response schema for history
class SubmissionHistoryResponse(BaseModel):
    submission_id: int
    problem_id: int
    problem_title: str
    language: str
    status: str
    created_at: datetime
    code: Optional[str] = None

    class Config:
        from_attributes = True


router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/run", status_code=200)
def run_code(
    submission: SubmissionRunRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run code against a custom stdin payload without persisting a submission."""

    lang = submission.language.lower()
    if lang not in ALLOWED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {submission.language}")

    code_bytes = len(submission.code.encode("utf-8"))
    if code_bytes > MAX_CODE_BYTES:
        raise HTTPException(status_code=400, detail="Code size exceeds 50KB limit")

    problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    sandbox = SandboxManager()
    runtime_ms = 0.0

    if lang == "python":
        result = sandbox.run_python(submission.code, submission.stdin)
    elif lang == "cpp":
        result = sandbox.run_cpp(submission.code, submission.stdin)
    elif lang == "java":
        result = sandbox.run_java(submission.code, submission.stdin)
    else:
        raise HTTPException(status_code=400, detail="Unsupported language")

    try:
        runtime_ms = float(result.get("runtime_ms", 0.0))
    except Exception:
        runtime_ms = 0.0

    exit_code = int(result.get("exit_code", -1))
    output = (result.get("output") or "")[:OUTPUT_SNIPPET_LIMIT]

    if result.get("status") != "Success" or exit_code != 0:
        # Split output into stdout and stderr for better error display
        error_msg = output if output else "Execution failed"
        return {
            "status": "RE",
            "message": "Runtime Error",
            "stdout": "",
            "stderr": error_msg,
            "output": error_msg,
            "runtime_ms": int(math.ceil(runtime_ms)),
            "memory_kb": None,
        }

    return {
        "status": "AC",
        "message": "Execution complete",
        "stdout": output,
        "stderr": "",
        "output": output,
        "runtime_ms": int(math.ceil(runtime_ms)),
        "memory_kb": None,
    }


@router.post("", status_code=200)
@router.post("/", status_code=200)
def submit_code(
    submission: SubmissionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Synchronously execute submitted code against a problem's test cases.

    Notes:
    - This synchronous implementation is useful for initial testing. For production scale it's
      recommended to enqueue execution to a background worker (RQ/Celery) and return 202 Accepted.
    - Inputs and outputs are trimmed for comparison; whitespace differences are ignored.
    """

    lang = submission.language.lower()
    if lang not in ALLOWED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {submission.language}")

    code_bytes = len(submission.code.encode("utf-8"))
    if code_bytes > MAX_CODE_BYTES:
        raise HTTPException(status_code=400, detail="Code size exceeds 50KB limit")

    # Load problem and test cases
    problem = db.query(models.Problem).filter(models.Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    test_cases = (
        db.query(models.TestCase)
        .filter(models.TestCase.problem_id == submission.problem_id)
        .order_by(models.TestCase.id.asc())
        .all()
    )

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for problem")

    sandbox = SandboxManager()

    passed_all = True
    failed_case_index: Optional[int] = None
    failed_case_input: Optional[str] = None
    failed_case_expected: Optional[str] = None
    output_snippet = ""
    aggregate_runtime_ms = 0.0

    # Iterate test cases sequentially (can be parallelized later)
    for idx, case in enumerate(test_cases, start=1):
        input_data = case.input_data or ""
        if len(input_data.encode("utf-8")) > MAX_INPUT_BYTES:
            raise HTTPException(status_code=400, detail="Test case input too large")

        # Dispatch to correct runner
        if lang == "python":
            result = sandbox.run_python(submission.code, input_data)
        elif lang == "cpp":
            result = sandbox.run_cpp(submission.code, input_data)
        elif lang == "java":
            result = sandbox.run_java(submission.code, input_data)
        else:
            # defensive: should never reach here due to prior check
            raise HTTPException(status_code=400, detail="Unsupported language")

        # Update aggregate runtime
        try:
            aggregate_runtime_ms = max(aggregate_runtime_ms, float(result.get("runtime_ms", 0.0)))
        except Exception:
            aggregate_runtime_ms = aggregate_runtime_ms

        output = result.get("output", "") or ""
        # Save last output snippet (trim to size)
        output_snippet = (output[:OUTPUT_SNIPPET_LIMIT]) if output else ""

        # If execution returned an error status, treat as runtime error
        if result.get("status") != "Success" or result.get("exit_code", 0) != 0:
            passed_all = False
            failed_case_index = idx
            failed_case_input = input_data
            failed_case_expected = case.expected_output
            # store error output as snippet
            output_snippet = output_snippet or (result.get("output") or "")[:OUTPUT_SNIPPET_LIMIT]
            break

        # Compare trimmed outputs (ignore trailing/leading whitespace)
        expected = (case.expected_output or "").strip()
        received = output.strip()
        if received != expected:
            passed_all = False
            failed_case_index = idx
            failed_case_input = input_data
            failed_case_expected = expected
            break

    # Persist submission record
    status = "Accepted" if passed_all else ("Error" if failed_case_index is None else "Wrong Answer")
    submission_record = models.Submission(
        user_id=current_user.id,
        problem_id=submission.problem_id,
        language=lang,
        code=submission.code,
        input_data=test_cases[0].input_data if test_cases else None,
        output=(output_snippet or "")[:OUTPUT_SNIPPET_LIMIT],
        status=status,
        failed_case=(failed_case_index if failed_case_index is not None else None),
        runtime_ms=int(math.ceil(aggregate_runtime_ms)),
    )

    db.add(submission_record)
    db.commit()
    db.refresh(submission_record)

    # On Accepted: award XP, update streak, persist solved solution
    if passed_all:
        xp_award = XP_BY_DIFFICULTY.get((problem.difficulty or "").lower(), 10)
        current_user.xp = (current_user.xp or 0) + xp_award

        today = date.today()
        if current_user.last_submission_date:
            yesterday = today - timedelta(days=1)
            if current_user.last_submission_date == yesterday:
                current_user.current_streak = (current_user.current_streak or 0) + 1
            elif current_user.last_submission_date == today:
                pass
            else:
                current_user.current_streak = 1
        else:
            current_user.current_streak = 1

        current_user.last_submission_date = today

        solved_entry = (
            db.query(models.UserSolvedProblem)
            .filter(
                models.UserSolvedProblem.user_id == current_user.id,
                models.UserSolvedProblem.problem_id == submission.problem_id,
            )
            .first()
        )

        if solved_entry:
            solved_entry.language = lang
            solved_entry.solution_code = submission.code
            solved_entry.solved_at = datetime.utcnow()
        else:
            solved_entry = models.UserSolvedProblem(
                user_id=current_user.id,
                problem_id=submission.problem_id,
                language=lang,
                solution_code=submission.code,
                solved_at=datetime.utcnow(),
            )
            db.add(solved_entry)

        db.commit()
        db.refresh(current_user)

    # Prepare response with normalized status codes
    if passed_all:
        message = "All test cases passed"
        response_status = "AC"
    elif failed_case_index is not None:
        message = f"Failed on test case #{failed_case_index}"
        response_status = "WA"
    else:
        message = "Runtime error or container failed"
        response_status = "RE"

    return {
        "submission_id": submission_record.id,
        "status": response_status,
        "message": message,
        "failed_case": failed_case_index,
        "failed_case_input": failed_case_input if not passed_all else None,
        "failed_case_expected_output": failed_case_expected if not passed_all else None,
        "stdout": submission_record.output if passed_all else "",
        "stderr": submission_record.output if not passed_all else "",
        "output": submission_record.output,
        "runtime_ms": submission_record.runtime_ms,
        "memory_kb": None,
    }


@router.get("/me", response_model=List[SubmissionHistoryResponse])
def get_my_submissions(
    include_code: bool = Query(False, description="Include submission code in response"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissions = (
        db.query(models.Submission)
        .filter(models.Submission.user_id == current_user.id)
        .order_by(models.Submission.created_at.desc())
        .all()
    )

    result: List[SubmissionHistoryResponse] = []
    for s in submissions:
        payload: Dict[str, Any] = {
            "submission_id": s.id,
            "problem_id": s.problem_id,
            "problem_title": s.problem.title if s.problem is not None else "",
            "language": s.language,
            "status": s.status,
            "created_at": s.created_at,
        }
        if include_code:
            payload["code"] = s.code
        result.append(SubmissionHistoryResponse(**payload))

    return result

# ------------------------------------------------------------------
# Background execution notes (minimal pattern)
#
# For production, offload execution to a worker. Example pattern (RQ / Celery):
# - POST /api/submissions creates a Submission record with status='Queued'
# - Enqueue job with submission_id
# - Worker picks up job, runs SandboxManager, updates submission.status/output/runtime_ms
# - Return 202 Accepted from POST with submission_id and polling endpoint
#
# A very small sample (pseudocode):
# from rq import Queue
# from worker import conn
# q = Queue(connection=conn)
# job = q.enqueue(run_submission_job, submission_id)
# return JSONResponse(status_code=202, content={"submission_id": submission_id})

