from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from app.database import get_db
from app.models import Problem, TestCase
from app.services.ai_generator import AIGenerator
from app.api.endpoints.auth import require_admin, get_current_user

router = APIRouter(prefix="/generate", tags=["AI Generator"])

# Initialize AI Generator
# Check if Gemini API key is available
gemini_api_key = os.getenv("GEMINI_API_KEY")
use_ai = gemini_api_key is not None

ALLOW_PUBLIC_PROBLEM_SAVE = os.getenv("ALLOW_PUBLIC_PROBLEM_SAVE", "true").lower() == "true"
SaveDependency = get_current_user if ALLOW_PUBLIC_PROBLEM_SAVE else require_admin

if use_ai:
    print("Gemini AI enabled for problem generation")
else:
    print("Using template-based problem generation (set GEMINI_API_KEY to enable AI)")

ai_generator = AIGenerator(ai_api_key=gemini_api_key, use_ai=use_ai)


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class ProblemGenerateRequest(BaseModel):
    """Request model for generating a problem"""
    topic: str = Field(..., description="Problem topic (e.g., 'two-sum', 'palindrome', 'fizzbuzz')")
    difficulty: str = Field("easy", pattern="^(easy|medium|hard)$", description="Problem difficulty")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "two-sum",
                "difficulty": "easy"
            }
        }


class SampleIO(BaseModel):
    """Sample input/output model"""
    input: str
    output: str


class TestCaseIO(BaseModel):
    """Test case input/output model"""
    input: str
    expected_output: str


class ProblemGenerateResponse(BaseModel):
    """Response model for generated problem"""
    title: str
    difficulty: str
    description: str
    constraints: List[str]
    samples: List[SampleIO]
    test_cases: List[TestCaseIO]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Two Sum",
                "difficulty": "easy",
                "description": "Given an array of integers...",
                "constraints": ["2 <= nums.length <= 10^4"],
                "samples": [{"input": "2 7 11 15\n9", "output": "0 1"}],
                "test_cases": [{"input": "2 7 11 15\n9", "expected_output": "0 1"}]
            }
        }


class ProblemSavedResponse(BaseModel):
    """Response model when problem is saved to database"""
    problem_id: int
    title: str
    difficulty: str
    test_case_count: int
    message: str


class AvailableTopicsResponse(BaseModel):
    """Response model for available topics"""
    topics: List[str]
    count: int


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/topics", response_model=AvailableTopicsResponse)
def get_available_topics():
    """
    Get list of available problem topics.
    
    Returns:
        List of available topics for problem generation
    """
    topics = ai_generator.list_available_topics()
    return {
        "topics": topics,
        "count": len(topics)
    }


@router.post("/problem", response_model=ProblemGenerateResponse)
def generate_problem(request: ProblemGenerateRequest):
    """
    Generate a coding problem with test cases using AI.
    
    This endpoint generates a complete problem including:
    - Title and description
    - Difficulty level
    - Constraints
    - Sample inputs/outputs
    - Test cases
    
    The problem is NOT saved to the database. Use /generate/and/save for that.
    
    Args:
        request: Problem generation parameters (topic, difficulty)
    
    Returns:
        Generated problem with all details and test cases
    """
    try:
        problem_data = ai_generator.generate_problem(
            topic=request.topic,
            difficulty=request.difficulty
        )
        
        return problem_data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate problem: {str(e)}"
        )


@router.post("/and/save", response_model=ProblemSavedResponse)
def generate_and_save_problem(
    request: ProblemGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(SaveDependency)
):
    """
    Generate a problem and automatically save it to the database.
    
    This endpoint:
    1. Generates a complete problem using AI
    2. Creates a Problem record in the database
    3. Creates TestCase records for all test cases
    4. Returns the problem_id for immediate use
    
    Requires admin unless ALLOW_PUBLIC_PROBLEM_SAVE=true in the environment.
    
    Args:
        request: Problem generation parameters
        db: Database session
        current_user: Authenticated user (must be admin unless override enabled)
    
    Returns:
        Saved problem details including problem_id
    """
    try:
        # Step 1: Generate problem
        problem_data = ai_generator.generate_problem(
            topic=request.topic,
            difficulty=request.difficulty
        )
        
        # Step 2: Create Problem record
        db_problem = Problem(
            title=problem_data["title"],
            description=problem_data["description"],
            difficulty=problem_data["difficulty"]
        )
        db.add(db_problem)
        db.commit()
        db.refresh(db_problem)
        
        # Step 3: Create TestCase records
        test_case_count = 0
        for tc in problem_data["test_cases"]:
            test_case = TestCase(
                problem_id=db_problem.id,
                input_data=tc["input"],
                expected_output=tc["expected_output"]
            )
            db.add(test_case)
            test_case_count += 1
        
        db.commit()
        
        return {
            "problem_id": db_problem.id,
            "title": db_problem.title,
            "difficulty": db_problem.difficulty,
            "test_case_count": test_case_count,
            "message": f"Problem '{db_problem.title}' created successfully with {test_case_count} test cases"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate and save problem: {str(e)}"
        )


@router.post("/batch", response_model=List[ProblemSavedResponse])
def generate_multiple_problems(
    topics: List[str],
    difficulty: str = "easy",
    db: Session = Depends(get_db),
    current_admin = Depends(require_admin)
):
    """
    Generate and save multiple problems at once.
    
    Useful for quickly populating the database with multiple problems.
    Admin only.
    
    Args:
        topics: List of topics to generate
        difficulty: Difficulty level for all problems
        db: Database session
        current_admin: Admin user
    
    Returns:
        List of saved problem details
    """
    results = []
    
    for topic in topics:
        try:
            problem_data = ai_generator.generate_problem(
                topic=topic,
                difficulty=difficulty
            )
            
            # Create Problem
            db_problem = Problem(
                title=problem_data["title"],
                description=problem_data["description"],
                difficulty=problem_data["difficulty"]
            )
            db.add(db_problem)
            db.commit()
            db.refresh(db_problem)
            
            # Create TestCases
            test_case_count = 0
            for tc in problem_data["test_cases"]:
                test_case = TestCase(
                    problem_id=db_problem.id,
                    input_data=tc["input"],
                    expected_output=tc["expected_output"]
                )
                db.add(test_case)
                test_case_count += 1
            
            db.commit()
            
            results.append({
                "problem_id": db_problem.id,
                "title": db_problem.title,
                "difficulty": db_problem.difficulty,
                "test_case_count": test_case_count,
                "message": f"Successfully created"
            })
        
        except Exception as e:
            # Continue with other problems if one fails
            results.append({
                "problem_id": -1,
                "title": f"Failed: {topic}",
                "difficulty": difficulty,
                "test_case_count": 0,
                "message": f"Error: {str(e)}"
            })
    
    return results


# ============================================================
# GEMINI AI-SPECIFIC ENDPOINTS
# ============================================================

class GeminiTestCaseRequest(BaseModel):
    """Request for Gemini test case generation"""
    problem_text: str = Field(..., description="Problem description")
    num_cases: int = Field(10, ge=1, le=50, description="Number of test cases to generate")


class GeminiStarterCodeRequest(BaseModel):
    """Request for Gemini starter code generation"""
    problem_text: str = Field(..., description="Problem description")
    language: str = Field(..., pattern="^(python|cpp|java)$", description="Programming language")


class GeminiTestCaseResponse(BaseModel):
    """Response for Gemini test case generation"""
    test_cases: List[TestCaseIO]
    count: int
    powered_by: str = "Google Gemini 2.0 Flash"


class GeminiStarterCodeResponse(BaseModel):
    """Response for Gemini starter code generation"""
    code: str
    language: str
    powered_by: str = "Google Gemini 2.0 Flash"


class GeminiFunctionTemplateRequest(BaseModel):
    """Request for Gemini function template generation"""
    problem_text: str = Field(..., description="Problem description")
    language: str = Field(..., pattern="^(python|cpp|java)$", description="Programming language")


class GeminiFunctionTemplateResponse(BaseModel):
    """Response for Gemini function template generation"""
    template: str
    language: str
    powered_by: str = "Google Gemini 2.0 Flash"


@router.post("/gemini/testcases", response_model=GeminiTestCaseResponse)
async def generate_testcases_with_gemini(request: GeminiTestCaseRequest):
    """
    Generate test cases using Google Gemini AI.
    
    Requires GEMINI_API_KEY environment variable.
    
    Args:
        request: Problem text and number of cases to generate
    
    Returns:
        Generated test cases with input and expected output
    """
    if not use_ai:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not available. Set GEMINI_API_KEY environment variable."
        )
    
    try:
        from app.services.gemini_service import generate_test_cases
        
        test_cases = await generate_test_cases(
            request.problem_text,
            request.num_cases
        )
        
        return {
            "test_cases": test_cases,
            "count": len(test_cases),
            "powered_by": "Google Gemini 2.0 Flash"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test cases: {str(e)}"
        )


@router.post("/gemini/startercode", response_model=GeminiStarterCodeResponse)
async def generate_startercode_with_gemini(request: GeminiStarterCodeRequest):
    """
    Generate starter/boilerplate code using Google Gemini AI.
    
    Requires GEMINI_API_KEY environment variable.
    
    Args:
        request: Problem text and target language
    
    Returns:
        Generated starter code
    """
    if not use_ai:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not available. Set GEMINI_API_KEY environment variable."
        )
    
    try:
        from app.services.gemini_service import generate_starter_code
        
        code = await generate_starter_code(
            request.problem_text,
            request.language
        )
        
        return {
            "code": code,
            "language": request.language,
            "powered_by": "Google Gemini 2.0 Flash"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate starter code: {str(e)}"
        )


@router.post("/gemini/function-template", response_model=GeminiFunctionTemplateResponse)
async def generate_function_template_with_gemini(request: GeminiFunctionTemplateRequest):
    """Generate a parameterized function template using Google Gemini."""
    if not use_ai:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not available. Set GEMINI_API_KEY environment variable."
        )

    try:
        from app.services.gemini_service import generate_function_template

        template = await generate_function_template(
            request.problem_text,
            request.language,
        )

        return {
            "template": template,
            "language": request.language,
            "powered_by": "Google Gemini 2.0 Flash",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate function template: {str(e)}"
        )
