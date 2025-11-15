import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, joinedload

from app.api.endpoints.auth import get_current_user, require_admin
from app.database import get_db
from app.models import (
    Problem,
    TestCase,
    ProblemExample,
    ProblemReferenceSolution,
    User,
)
from app.services.gemini_service import get_gemini_service, GeminiService


logger = logging.getLogger("algogenius.problems")


router = APIRouter(prefix="/problems", tags=["problems"])


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class ProblemExampleCreate(BaseModel):
    input: str = Field(..., description="Sample input")
    output: str = Field(..., description="Sample output")
    explanation: Optional[str] = Field(
        None, description="Optional explanation for the example"
    )


class ProblemExampleResponse(ProblemExampleCreate):
    id: Optional[int] = Field(None, description="Example identifier")


class TestCaseCreate(BaseModel):
    input_data: str = Field(..., description="Raw stdin payload")
    expected_output: str = Field(..., description="Expected stdout payload")


class TestCaseResponse(BaseModel):
    id: Optional[int]
    input: str
    expected_output: str


class ProblemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: str = Field(
        "easy",
        pattern="^(easy|medium|hard)$",
        description="Problem difficulty",
    )


class ProblemCreate(ProblemBase):
    test_cases: List[TestCaseCreate] = Field(default_factory=list)
    examples: List[ProblemExampleCreate] = Field(default_factory=list)
    reference_solution: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of language -> reference implementation",
    )


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[str] = Field(
        None, pattern="^(easy|medium|hard)$"
    )


class ProblemOut(BaseModel):
    id: Optional[int]
    title: str
    description: str
    difficulty: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    examples: List[ProblemExampleResponse] = Field(default_factory=list)
    test_cases: List[TestCaseResponse] = Field(default_factory=list)
    reference_solution: Dict[str, str] = Field(default_factory=dict)


class ProblemCountResponse(BaseModel):
    easy: int
    medium: int
    hard: int
    total: int


class ProblemGenerateRequest(BaseModel):
    topic: str = Field(..., description="Topic or free-form prompt for the problem")
    difficulty: str = Field(
        "easy",
        pattern="^(easy|medium|hard)$",
        description="Desired difficulty tier",
    )


class ProblemGenerateBatchRequest(ProblemGenerateRequest):
    count: int = Field(
        1,
        ge=1,
        le=10,
        description="Number of problems to generate in this batch",
    )


class ProblemGenerateResponse(BaseModel):
    problem: ProblemOut
    model_used: str


class ProblemGenerateBatchResponse(BaseModel):
    problems: List[ProblemOut]
    model_used: str
    created_count: int


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _serialize_problem(problem: Problem) -> ProblemOut:
    return ProblemOut(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        examples=[
            ProblemExampleResponse(
                id=example.id,
                input=example.input_data,
                output=example.output_data,
                explanation=example.explanation,
            )
            for example in (problem.examples or [])
        ],
        test_cases=[
            TestCaseResponse(
                id=test_case.id,
                input=test_case.input_data,
                expected_output=test_case.expected_output,
            )
            for test_case in (problem.test_cases or [])
        ],
        reference_solution={
            ref.language: ref.solution_code for ref in (problem.reference_solutions or [])
        },
    )


def _create_problem_with_related(
    *,
    db: Session,
    title: str,
    description: str,
    difficulty: str,
    test_cases: List[TestCaseCreate],
    examples: List[ProblemExampleCreate],
    reference_solution: Dict[str, str],
) -> Problem:
    problem = Problem(
        title=title,
        description=description,
        difficulty=difficulty.lower(),
    )

    for tc in test_cases:
        problem.test_cases.append(
            TestCase(input_data=tc.input_data, expected_output=tc.expected_output)
        )

    for ex in examples:
        problem.examples.append(
            ProblemExample(
                input_data=ex.input,
                output_data=ex.output,
                explanation=ex.explanation,
            )
        )

    for language, code in reference_solution.items():
        if code:
            problem.reference_solutions.append(
                ProblemReferenceSolution(language=language.lower(), solution_code=code)
            )

    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def _stringify_field(value: Any, *, allow_empty: bool = False) -> Optional[str]:
    """Coerce AI responses into strings suitable for Pydantic validation."""
    if value is None:
        return None if allow_empty else ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    try:
        serialised = json.dumps(value, ensure_ascii=False)
    except TypeError:
        serialised = str(value)
    return serialised


async def _generate_problem_payload(
    *, topic: str, difficulty: str
) -> Dict[str, Any]:
    service: GeminiService
    try:
        service = get_gemini_service()
    except Exception as exc:  # pragma: no cover
        logger.error("Gemini service init failed: %s", exc)
        raise HTTPException(status_code=500, detail="Gemini service not configured")

    ai_problem = await service.generate_complete_problem(topic, difficulty)
    model_used = service.get_last_model_used()

    # Normalise examples/samples
    samples = ai_problem.get("samples", [])
    examples: List[ProblemExampleCreate] = []
    for sample in samples:
        input_val = _stringify_field(sample.get("input") or sample.get("input_data"))
        output_val = _stringify_field(sample.get("output") or sample.get("expected_output"))
        explanation_val = _stringify_field(sample.get("explanation"), allow_empty=True)
        if input_val and output_val:
            examples.append(
                ProblemExampleCreate(
                    input=input_val,
                    output=output_val,
                    explanation=explanation_val,
                )
            )

    test_cases_data = ai_problem.get("test_cases", [])
    test_cases: List[TestCaseCreate] = []
    for case in test_cases_data:
        input_val = _stringify_field(case.get("input") or case.get("input_data"))
        expected_val = _stringify_field(case.get("expected_output") or case.get("output"))
        if input_val and expected_val:
            test_cases.append(
                TestCaseCreate(input_data=input_val, expected_output=expected_val)
            )

    reference_solution: Dict[str, str] = {}
    for language in ("python", "cpp", "java"):
        try:
            starter = await service.generate_starter_code(
                ai_problem.get("description", ""), language
            )
            reference_solution[language] = starter
        except Exception as code_error:
            logger.warning(
                "Failed to generate %s starter code: %s", language, code_error
            )

    problem_payload = {
        "title": ai_problem.get("title", topic.title()),
        "description": ai_problem.get("description", ""),
        "difficulty": ai_problem.get("difficulty", difficulty).lower(),
        "examples": examples,
        "test_cases": test_cases,
        "reference_solution": reference_solution,
        "model_used": model_used or GeminiService.MODEL_PRIMARY,
    }

    return problem_payload


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------


@router.post("/", response_model=ProblemOut, status_code=status.HTTP_201_CREATED)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)) -> ProblemOut:
    db_problem = _create_problem_with_related(
        db=db,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        test_cases=problem.test_cases,
        examples=problem.examples,
        reference_solution=problem.reference_solution,
    )
    return _serialize_problem(db_problem)


@router.get("/", response_model=List[ProblemOut])
def list_problems(
    difficulty: Optional[str] = Query(
        None, pattern="^(easy|medium|hard)$", description="Difficulty filter"
    ),
    sort: Optional[str] = Query(
        "latest",
        pattern="^(latest|oldest|alphabetical)$",
        description="Sort order",
    ),
    db: Session = Depends(get_db),
) -> List[ProblemOut]:
    query = (
        db.query(Problem)
        .options(
            joinedload(Problem.test_cases),
            joinedload(Problem.examples),
            joinedload(Problem.reference_solutions),
        )
    )

    if difficulty:
        query = query.filter(Problem.difficulty == difficulty.lower())

    if sort == "latest":
        query = query.order_by(desc(Problem.created_at))
    elif sort == "oldest":
        query = query.order_by(asc(Problem.created_at))
    elif sort == "alphabetical":
        query = query.order_by(asc(Problem.title))

    return [_serialize_problem(problem) for problem in query.all()]


@router.get("/today", response_model=ProblemOut)
def get_daily_problem(db: Session = Depends(get_db)) -> ProblemOut:
    total = db.query(func.count(Problem.id)).scalar()
    if not total:
        raise HTTPException(status_code=404, detail="No problems available")

    ordinal = date.today().toordinal()
    offset = ordinal % total

    problem = (
        db.query(Problem)
        .options(
            joinedload(Problem.test_cases),
            joinedload(Problem.examples),
            joinedload(Problem.reference_solutions),
        )
        .order_by(Problem.created_at.asc(), Problem.id.asc())
        .offset(offset)
        .limit(1)
        .first()
    )

    if not problem:
        raise HTTPException(status_code=404, detail="Daily problem not found")

    return _serialize_problem(problem)


@router.get("/random", response_model=ProblemOut)
def get_random_problem(db: Session = Depends(get_db)) -> ProblemOut:
    problem = (
        db.query(Problem)
        .options(
            joinedload(Problem.test_cases),
            joinedload(Problem.examples),
            joinedload(Problem.reference_solutions),
        )
        .order_by(func.random())
        .first()
    )

    if not problem:
        raise HTTPException(status_code=404, detail="No problems available")

    return _serialize_problem(problem)


@router.get("/count", response_model=ProblemCountResponse)
def get_problem_counts(db: Session = Depends(get_db)) -> ProblemCountResponse:
    rows = db.query(Problem.difficulty, func.count(Problem.id)).group_by(Problem.difficulty)
    counts = {difficulty: count for difficulty, count in rows}
    easy = counts.get("easy", 0)
    medium = counts.get("medium", 0)
    hard = counts.get("hard", 0)
    return ProblemCountResponse(easy=easy, medium=medium, hard=hard, total=easy + medium + hard)


@router.get("/{problem_id}", response_model=ProblemOut)
def get_problem(problem_id: int, db: Session = Depends(get_db)) -> ProblemOut:
    problem = (
        db.query(Problem)
        .options(
            joinedload(Problem.test_cases),
            joinedload(Problem.examples),
            joinedload(Problem.reference_solutions),
        )
        .filter(Problem.id == problem_id)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return _serialize_problem(problem)


@router.put("/{problem_id}", response_model=ProblemOut)
def update_problem(
    problem_id: int, problem_update: ProblemUpdate, db: Session = Depends(get_db)
) -> ProblemOut:
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if problem_update.title is not None:
        db_problem.title = problem_update.title
    if problem_update.description is not None:
        db_problem.description = problem_update.description
    if problem_update.difficulty is not None:
        db_problem.difficulty = problem_update.difficulty.lower()

    db.commit()
    db.refresh(db_problem)
    db_problem = (
        db.query(Problem)
        .options(
            joinedload(Problem.test_cases),
            joinedload(Problem.examples),
            joinedload(Problem.reference_solutions),
        )
        .filter(Problem.id == problem_id)
        .first()
    )
    return _serialize_problem(db_problem)


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem(problem_id: int, db: Session = Depends(get_db)) -> None:
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    db.delete(db_problem)
    db.commit()


# ---------------------------------------------------------------------------
# AI Generation Endpoints
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=ProblemGenerateResponse)
async def generate_problem(
    payload: ProblemGenerateRequest,
    _: User = Depends(get_current_user),  # ensure authenticated user
) -> ProblemGenerateResponse:
    problem_payload = await _generate_problem_payload(
        topic=payload.topic, difficulty=payload.difficulty
    )

    problem_out = ProblemOut(
        id=None,
        title=problem_payload["title"],
        description=problem_payload["description"],
        difficulty=problem_payload["difficulty"],
        examples=[
            ProblemExampleResponse(
                id=None, input=ex.input, output=ex.output, explanation=ex.explanation
            )
            for ex in problem_payload["examples"]
        ],
        test_cases=[
            TestCaseResponse(id=None, input=tc.input_data, expected_output=tc.expected_output)
            for tc in problem_payload["test_cases"]
        ],
        reference_solution=problem_payload["reference_solution"],
        created_at=None,
        updated_at=None,
    )

    return ProblemGenerateResponse(problem=problem_out, model_used=problem_payload["model_used"])


@router.post("/generate/save", response_model=ProblemGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_and_save_problem(
    payload: ProblemGenerateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ProblemGenerateResponse:
    problem_payload = await _generate_problem_payload(
        topic=payload.topic, difficulty=payload.difficulty
    )

    db_problem = _create_problem_with_related(
        db=db,
        title=problem_payload["title"],
        description=problem_payload["description"],
        difficulty=problem_payload["difficulty"],
        test_cases=problem_payload["test_cases"],
        examples=problem_payload["examples"],
        reference_solution=problem_payload["reference_solution"],
    )

    problem_out = _serialize_problem(db_problem)
    return ProblemGenerateResponse(problem=problem_out, model_used=problem_payload["model_used"])


@router.post("/generate/batch", response_model=ProblemGenerateBatchResponse, status_code=status.HTTP_201_CREATED)
async def generate_problem_batch(
    payload: ProblemGenerateBatchRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ProblemGenerateBatchResponse:
    generated_problems: List[ProblemOut] = []
    model_used = ""

    for _ in range(payload.count):
        problem_payload = await _generate_problem_payload(
            topic=payload.topic, difficulty=payload.difficulty
        )
        db_problem = _create_problem_with_related(
            db=db,
            title=problem_payload["title"],
            description=problem_payload["description"],
            difficulty=problem_payload["difficulty"],
            test_cases=problem_payload["test_cases"],
            examples=problem_payload["examples"],
            reference_solution=problem_payload["reference_solution"],
        )
        generated_problems.append(_serialize_problem(db_problem))
        model_used = problem_payload["model_used"]

    return ProblemGenerateBatchResponse(
        problems=generated_problems,
        model_used=model_used or GeminiService.MODEL_PRIMARY,
        created_count=len(generated_problems),
    )

