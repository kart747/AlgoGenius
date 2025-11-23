from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, joinedload

from app.api.endpoints.auth import get_current_user, require_admin
from app.database import get_db
from app.models import (
    Problem,
    TestCase,
    ProblemExample,
    ProblemReferenceSolution,
    ProblemComment,
    User,
)
from app.services.gemini_service import get_gemini_service, GeminiService


logger = logging.getLogger("algogenius.problems")


router = APIRouter(prefix="/problems", tags=["problems"])

MIN_GENERATED_TEST_CASES = 10
FALLBACK_EXAMPLE_LIMIT = 3

_FUNCTION_TEMPLATE_CACHE: Dict[Tuple[int, str], Tuple[str, str]] = {}


def _normalize_topics(primary: Optional[str], extras: List[str]) -> List[str]:
    ordered: List[str] = []
    seen = set()
    candidates: List[str] = []
    if primary:
        candidates.append(primary)
    candidates.extend(extras or [])

    for candidate in candidates:
        if not candidate:
            continue
        normalized = candidate.strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(normalized)

    if not ordered:
        raise HTTPException(
            status_code=400, detail="At least one topic is required to generate a problem."
        )

    return ordered


def _dedupe_test_cases(cases: List[TestCaseCreate]) -> List[TestCaseCreate]:
    """Remove duplicate/empty test cases while preserving order."""
    unique: List[TestCaseCreate] = []
    seen = set()
    for case in cases:
        input_val = ((case.input_data or "").strip())
        output_val = ((case.expected_output or "").strip())
        if not input_val or not output_val:
            continue
        key = (input_val, output_val)
        if key in seen:
            continue
        unique.append(TestCaseCreate(input_data=input_val, expected_output=output_val))
        seen.add(key)
    return unique


async def _ensure_minimum_test_cases(
    *,
    service: GeminiService,
    description: str,
    test_cases: List[TestCaseCreate],
    examples: List[ProblemExampleCreate],
) -> List[TestCaseCreate]:
    """Guarantee at least MIN_GENERATED_TEST_CASES test cases by topping up via Gemini."""

    normalized = _dedupe_test_cases(test_cases)

    if len(normalized) >= MIN_GENERATED_TEST_CASES:
        return normalized

    supplemental: List[TestCaseCreate] = []
    prompt = (description or "").strip()
    if prompt:
        try:
            extra_cases = await service.generate_test_cases(
                prompt,
                num_cases=MIN_GENERATED_TEST_CASES,
            )
        except Exception as exc:  # pragma: no cover - network failure
            logger.warning("Supplemental test case generation failed: %s", exc)
        else:
            for case in extra_cases:
                input_val = _stringify_field(case.get("input_data") or case.get("input"))
                output_val = _stringify_field(
                    case.get("expected_output") or case.get("output")
                )
                if input_val and output_val:
                    supplemental.append(
                        TestCaseCreate(input_data=input_val, expected_output=output_val)
                    )

    if supplemental:
        normalized = _dedupe_test_cases(normalized + supplemental)

    if len(normalized) < MIN_GENERATED_TEST_CASES and examples:
        example_cases = [
            TestCaseCreate(input_data=ex.input, expected_output=ex.output)
            for ex in examples
            if ex.input and ex.output
        ]
        if example_cases:
            normalized = _dedupe_test_cases(normalized + example_cases)

    if normalized:
        while len(normalized) < MIN_GENERATED_TEST_CASES:
            seed = normalized[len(normalized) % len(normalized)]
            normalized.append(
                TestCaseCreate(
                    input_data=seed.input_data,
                    expected_output=seed.expected_output,
                )
            )

    if not normalized:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate sufficient test cases for this problem.",
        )

    return normalized


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
    function_templates: Dict[str, str] = Field(default_factory=dict)


class ProblemCountResponse(BaseModel):
    easy: int
    medium: int
    hard: int
    total: int


class ProblemGenerateRequest(BaseModel):
    topic: Optional[str] = Field(
        None,
        description="Primary topic or free-form prompt",
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Optional list of topics to blend into the generated problem",
    )
    difficulty: str = Field(
        "easy",
        pattern="^(easy|medium|hard)$",
        description="Desired difficulty tier",
    )

    @model_validator(mode="after")
    def ensure_topic_present(self):
        normalized_topics = []
        if self.topic:
            normalized_topics.append(self.topic.strip())
        normalized_topics.extend([entry.strip() for entry in self.topics if entry and entry.strip()])

        normalized_topics = [entry for entry in normalized_topics if entry]

        if not normalized_topics:
            raise ValueError("Provide at least one topic before generating a problem.")

        self.topic = normalized_topics[0]
        self.topics = normalized_topics[1:]
        return self


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
    fallback_used: bool = False


class ProblemGenerateBatchResponse(BaseModel):
    problems: List[ProblemOut]
    model_used: str
    created_count: int


class FunctionTemplateResponse(BaseModel):
    language: str
    template: str
    powered_by: str


class ProblemAssistantRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User question or hint request")
    mode: Optional[str] = Field(
        "hint",
        pattern="^(hint|explain|debug)$",
        description="Response style: hint/explain/debug",
    )
    code_context: Optional[str] = Field(
        None,
        max_length=8000,
        description="Optional code snippet to include for debugging",
    )


class ProblemAssistantResponse(BaseModel):
    reply: str
    powered_by: str


class ProblemCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Comment body")


class ProblemCommentResponse(BaseModel):
    id: int
    problem_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _serialize_problem(problem: Problem) -> ProblemOut:
    example_payloads = [
        ProblemExampleResponse(
            id=example.id,
            input=example.input_data,
            output=example.output_data,
            explanation=example.explanation,
        )
        for example in (problem.examples or [])
        if example.input_data and example.output_data
    ]

    if not example_payloads:
        fallback_examples = []
        for test_case in (problem.test_cases or [])[:FALLBACK_EXAMPLE_LIMIT]:
            if not test_case.input_data or not test_case.expected_output:
                continue
            fallback_examples.append(
                ProblemExampleResponse(
                    id=None,
                    input=test_case.input_data,
                    output=test_case.expected_output,
                    explanation=None,
                )
            )
        example_payloads = fallback_examples

    return ProblemOut(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        examples=example_payloads,
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
        function_templates={},
    )

def _serialize_comment(comment: ProblemComment) -> ProblemCommentResponse:
    user = comment.user
    username = user.username if user else "Unknown"
    return ProblemCommentResponse(
        id=comment.id,
        problem_id=comment.problem_id,
        user_id=comment.user_id,
        username=username,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
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
    *,
    topic: str,
    difficulty: str,
    db: Optional[Session] = None,
    ensure_unique_title: bool = False,
    max_attempts: int = 5,
) -> Dict[str, Any]:
    service: GeminiService
    try:
        service = get_gemini_service()
    except Exception as exc:  # pragma: no cover
        logger.error("Gemini service init failed: %s", exc)
        raise HTTPException(status_code=500, detail="Gemini service not configured")

    attempts_allowed = max_attempts if (ensure_unique_title and db) else 1

    for attempt in range(1, attempts_allowed + 1):
        ai_problem = await service.generate_complete_problem(topic, difficulty)
        problem_model_used = service.get_last_model_used()

        title_candidate = (ai_problem.get("title") or topic.title()).strip()

        if ensure_unique_title and db:
            duplicate = (
                db.query(Problem.id)
                .filter(func.lower(Problem.title) == title_candidate.lower())
                .first()
            )
            if duplicate:
                logger.info(
                    "Gemini generated duplicate problem title '%s' (attempt %d/%d); regenerating.",
                    title_candidate,
                    attempt,
                    attempts_allowed,
                )
                if attempt == attempts_allowed:
                    raise HTTPException(
                        status_code=400,
                        detail="Generated problem already exists. Please try again or choose a different topic.",
                    )
                continue

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

        test_cases = await _ensure_minimum_test_cases(
            service=service,
            description=ai_problem.get("description") or ai_problem.get("title") or topic,
            test_cases=test_cases,
            examples=examples,
        )

        reference_solution: Dict[str, str] = {}
        function_templates: Dict[str, str] = {}
        problem_context = f"{title_candidate}\n\n{ai_problem.get('description', '')}".strip()
        description_text = ai_problem.get("description", "")

        async def build_language_assets(language: str):
            starter = None
            template = None
            try:
                starter = await service.generate_starter_code(
                    description_text,
                    language,
                )
            except Exception as code_error:
                logger.warning(
                    "Failed to generate %s starter code: %s",
                    language,
                    code_error,
                )

            try:
                template = await service.generate_function_template(
                    problem_context or description_text,
                    language,
                )
            except Exception as template_error:
                logger.warning(
                    "Failed to generate %s function template: %s",
                    language,
                    template_error,
                )
            return language, starter, template

        language_results = await asyncio.gather(
            *(build_language_assets(language) for language in ("python", "cpp", "java"))
        )

        for language, starter, template in language_results:
            if starter:
                reference_solution[language] = starter
            if template:
                function_templates[language] = template

        fallback_used = bool(
            problem_model_used and problem_model_used != GeminiService.MODEL_PRIMARY
        )

        problem_payload = {
            "title": title_candidate,
            "description": ai_problem.get("description", ""),
            "difficulty": ai_problem.get("difficulty", difficulty).lower(),
            "examples": examples,
            "test_cases": test_cases,
            "reference_solution": reference_solution,
            "function_templates": function_templates,
            "model_used": problem_model_used or GeminiService.MODEL_PRIMARY,
            "fallback_used": fallback_used,
        }

        return problem_payload

    # Should never reach here because loop either returns or raises
    raise HTTPException(status_code=500, detail="Unable to generate a unique problem.")


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


@router.post("/{problem_id}/assistant", response_model=ProblemAssistantResponse)
async def problem_assistant(
    problem_id: int,
    payload: ProblemAssistantRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    del current_user  # auth check only
    problem = (
        db.query(Problem)
        .options(joinedload(Problem.examples))
        .filter(Problem.id == problem_id)
        .first()
    )

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    try:
        service = get_gemini_service()
    except Exception as exc:  # pragma: no cover
        logger.error("Gemini service init failed: %s", exc)
        raise HTTPException(status_code=503, detail="Gemini assistant unavailable") from exc

    context_parts = [
        f"Title: {problem.title}",
        f"Difficulty: {problem.difficulty}",
        problem.description,
    ]

    if problem.examples:
        example_lines = ["Examples:"]
        for example in problem.examples[:2]:
            example_lines.append(
                f"Input: {example.input_data}\nOutput: {example.output_data}"
            )
        context_parts.append("\n".join(example_lines))

    problem_context = "\n\n".join(part for part in context_parts if part)

    try:
        reply = await service.generate_problem_hint(
            problem_context=problem_context,
            user_message=payload.message,
            mode=payload.mode or "hint",
            code_context=payload.code_context,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except ConnectionError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except Exception as err:
        logger.error("Problem assistant failed: %s", err)
        raise HTTPException(status_code=500, detail="Assistant failed to answer")

    powered_by = service.get_last_model_used() or GeminiService.MODEL_PRIMARY
    return ProblemAssistantResponse(reply=reply, powered_by=powered_by)


@router.get("/{problem_id}/comments", response_model=List[ProblemCommentResponse])
def list_problem_comments(problem_id: int, db: Session = Depends(get_db)) -> List[ProblemCommentResponse]:
    problem_exists = db.query(Problem.id).filter(Problem.id == problem_id).first()
    if not problem_exists:
        raise HTTPException(status_code=404, detail="Problem not found")

    comments = (
        db.query(ProblemComment)
        .options(joinedload(ProblemComment.user))
        .filter(ProblemComment.problem_id == problem_id)
        .order_by(ProblemComment.created_at.asc())
        .all()
    )
    return [_serialize_comment(comment) for comment in comments]


@router.post(
    "/{problem_id}/comments",
    response_model=ProblemCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_problem_comment(
    problem_id: int,
    payload: ProblemCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProblemCommentResponse:
    problem_exists = db.query(Problem.id).filter(Problem.id == problem_id).first()
    if not problem_exists:
        raise HTTPException(status_code=404, detail="Problem not found")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    comment = ProblemComment(
        problem_id=problem_id,
        user_id=current_user.id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment.user = current_user
    return _serialize_comment(comment)


@router.get("/{problem_id}/function-template", response_model=FunctionTemplateResponse)
async def get_function_template_for_problem(
    problem_id: int,
    language: str = Query(..., pattern="^(python|cpp|java)$", description="Language for the template"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    normalized_language = language.lower()
    cache_key = (problem_id, normalized_language)
    cached = _FUNCTION_TEMPLATE_CACHE.get(cache_key)
    if cached:
        template, powered_by = cached
        return FunctionTemplateResponse(
            language=normalized_language,
            template=template,
            powered_by=powered_by,
        )

    try:
        service = get_gemini_service()
    except Exception as exc:  # pragma: no cover
        logger.error("Gemini service init failed: %s", exc)
        raise HTTPException(status_code=503, detail="Gemini service not configured") from exc

    problem_context = f"{problem.title}\n\n{problem.description}".strip()
    try:
        template = await service.generate_function_template(
            problem_context or problem.description,
            normalized_language,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except ConnectionError as err:
        raise HTTPException(status_code=503, detail=str(err))
    except Exception as err:
        logger.error("Function template generation failed: %s", err)
        raise HTTPException(status_code=500, detail="Failed to generate function template")

    powered_by = service.get_last_model_used() or GeminiService.MODEL_PRIMARY
    _FUNCTION_TEMPLATE_CACHE[cache_key] = (template, powered_by)

    return FunctionTemplateResponse(
        language=normalized_language,
        template=template,
        powered_by=powered_by,
    )


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


@router.delete(
    "/{problem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_problem(
    problem_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
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
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # ensure authenticated user
) -> ProblemGenerateResponse:
    topic_order = _normalize_topics(payload.topic, payload.topics)
    topic_prompt = ", ".join(topic_order)

    problem_payload = await _generate_problem_payload(
        topic=topic_prompt,
        difficulty=payload.difficulty,
        db=db,
        ensure_unique_title=True,
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
        function_templates=problem_payload.get("function_templates", {}),
        created_at=None,
        updated_at=None,
    )

    return ProblemGenerateResponse(
        problem=problem_out,
        model_used=problem_payload["model_used"],
        fallback_used=problem_payload["fallback_used"],
    )


ALLOW_PUBLIC_PROBLEM_SAVE = os.getenv("ALLOW_PUBLIC_PROBLEM_SAVE", "true").lower() == "true"
SaveDependency = get_current_user if ALLOW_PUBLIC_PROBLEM_SAVE else require_admin


@router.post("/generate/save", response_model=ProblemGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_and_save_problem(
    payload: ProblemGenerateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(SaveDependency),
) -> ProblemGenerateResponse:
    topic_order = _normalize_topics(payload.topic, payload.topics)
    topic_prompt = ", ".join(topic_order)

    problem_payload = await _generate_problem_payload(
        topic=topic_prompt,
        difficulty=payload.difficulty,
        db=db,
        ensure_unique_title=True,
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
    problem_out.function_templates = problem_payload.get("function_templates", {})
    return ProblemGenerateResponse(
        problem=problem_out,
        model_used=problem_payload["model_used"],
        fallback_used=problem_payload["fallback_used"],
    )


@router.post("/generate/batch", response_model=ProblemGenerateBatchResponse, status_code=status.HTTP_201_CREATED)
async def generate_problem_batch(
    payload: ProblemGenerateBatchRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ProblemGenerateBatchResponse:
    generated_problems: List[ProblemOut] = []
    model_used = ""

    topic_order = _normalize_topics(payload.topic, payload.topics)
    topic_prompt = ", ".join(topic_order)

    for _ in range(payload.count):
        problem_payload = await _generate_problem_payload(
            topic=topic_prompt,
            difficulty=payload.difficulty,
            db=db,
            ensure_unique_title=True,
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
        serialized = _serialize_problem(db_problem)
        serialized.function_templates = problem_payload.get("function_templates", {})
        generated_problems.append(serialized)
        model_used = problem_payload["model_used"]

    return ProblemGenerateBatchResponse(
        problems=generated_problems,
        model_used=model_used or GeminiService.MODEL_PRIMARY,
        created_count=len(generated_problems),
    )

