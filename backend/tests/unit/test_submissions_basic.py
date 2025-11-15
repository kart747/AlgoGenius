# tests/unit/test_submissions_basic.py
# Basic unit tests for the submissions endpoint (synchronous path).
# These tests avoid running Docker by mocking SandboxManager methods.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.api.endpoints import submissions as submissions_module

# Use in-memory SQLite for quick tests
ENGINE = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=ENGINE)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=ENGINE)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=ENGINE)


class DummySandboxAccepted:
    def __init__(self, outputs):
        # outputs is a list of outputs to return for each test case
        self.outputs = list(outputs)

    def run_python(self, code, input_data):
        return {"status": "Success", "output": self.outputs.pop(0), "exit_code": 0, "runtime_ms": 5}

    def run_cpp(self, code, input_data):
        return self.run_python(code, input_data)

    def run_java(self, code, input_data):
        return self.run_python(code, input_data)


def create_sample_problem_with_cases(db):
    # Create a user
    user = models.User(username="testuser", email="test@example.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)

    problem = models.Problem(title="Sum Problem", description="", difficulty="easy")
    db.add(problem)
    db.commit()
    db.refresh(problem)

    # Add three test cases
    tc1 = models.TestCase(problem_id=problem.id, input_data="1 2", expected_output="3")
    tc2 = models.TestCase(problem_id=problem.id, input_data="2 3", expected_output="5")
    tc3 = models.TestCase(problem_id=problem.id, input_data="10 4", expected_output="14")
    db.add_all([tc1, tc2, tc3])
    db.commit()

    return user, problem, [tc1, tc2, tc3]


def test_submit_python_accepted(db_session, monkeypatch):
    user, problem, tcs = create_sample_problem_with_cases(db_session)

    # Mock SandboxManager so it returns exactly the expected outputs
    outputs = [tc.expected_output for tc in tcs]
    monkeypatch.setattr(submissions_module, "SandboxManager", lambda: DummySandboxAccepted(outputs))

    request = submissions_module.SubmissionRequest(problem_id=problem.id, language="python", code="print(\"stub\")")

    result = submissions_module.submit_code(request, current_user=user, db=db_session)

    assert result["status"] == "Accepted"
    assert result["failed_case"] is None

    # Confirm user XP increased by easy mapping
    db_session.refresh(user)
    assert user.xp >= 10


def test_submit_python_wrong_answer(db_session, monkeypatch):
    user, problem, tcs = create_sample_problem_with_cases(db_session)

    # First test passes, second fails
    outputs = [tcs[0].expected_output, "WRONG", tcs[2].expected_output]
    monkeypatch.setattr(submissions_module, "SandboxManager", lambda: DummySandboxAccepted(outputs))

    request = submissions_module.SubmissionRequest(problem_id=problem.id, language="python", code="print(\"stub\")")
    result = submissions_module.submit_code(request, current_user=user, db=db_session)

    assert result["status"] == "Wrong Answer"
    assert result["failed_case"] == 2