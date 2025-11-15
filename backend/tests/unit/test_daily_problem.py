"""Unit tests for the daily problem endpoint helper."""

from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.api.endpoints import problems as problems_module
from app.database import Base


ENGINE = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=ENGINE)


def setup_function():
    Base.metadata.create_all(bind=ENGINE)


def teardown_function():
    Base.metadata.drop_all(bind=ENGINE)


def _seed_problems(session):
    base_problem = models.Problem(title="One", description="", difficulty="easy")
    session.add(base_problem)
    session.commit()
    session.refresh(base_problem)

    second = models.Problem(title="Two", description="", difficulty="medium")
    third = models.Problem(title="Three", description="", difficulty="hard")

    # Manually adjust created_at to ensure deterministic ordering
    second.created_at = base_problem.created_at + timedelta(minutes=5)
    third.created_at = base_problem.created_at + timedelta(minutes=10)

    session.add_all([second, third])
    session.commit()

    return [base_problem, second, third]


def test_get_daily_problem_cycles_through_available_records(monkeypatch):
    session = SessionLocal()
    problems = _seed_problems(session)

    # Monkeypatch today ordinal to guarantee deterministic selection
    class _DummyDate:
        def __init__(self, ordinal):
            self._ordinal = ordinal

        def toordinal(self):
            return self._ordinal

    dummy_date_factory = type(
        "_DateWrapper",
        (),
        {"today": staticmethod(lambda: _DummyDate(1))},
    )

    monkeypatch.setattr(problems_module, "date", dummy_date_factory)

    result = problems_module.get_daily_problem(db=session)

    # When ordinal aligns with second problem, we expect that entry
    assert result.title == "Two"

    session.close()