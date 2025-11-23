from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    last_submission_date = Column(Date)
    is_admin = Column(Integer, default=0)  # Using Integer for SQLite compatibility (0=False, 1=True)
    
    # Relationship to submissions
    submissions = relationship("Submission", back_populates="user")
    comments = relationship("ProblemComment", back_populates="user", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))
    language = Column(String, nullable=False)  # 'python', 'cpp', 'java'
    code = Column(Text, nullable=False)
    input_data = Column(Text)
    output = Column(Text)
    status = Column(String)  # Accepted / Wrong Answer / Error
    failed_case = Column(Integer, nullable=True)
    runtime_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False, default="easy")  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem")
    examples = relationship(
        "ProblemExample",
        back_populates="problem",
        cascade="all, delete-orphan",
    )
    reference_solutions = relationship(
        "ProblemReferenceSolution",
        back_populates="problem",
        cascade="all, delete-orphan",
    )
    comments = relationship(
        "ProblemComment",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="ProblemComment.created_at",
    )


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)

    # Relationship to problem
    problem = relationship("Problem", back_populates="test_cases")


class ProblemExample(Base):
    __tablename__ = "problem_examples"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    explanation = Column(Text)

    problem = relationship("Problem", back_populates="examples")


class ProblemReferenceSolution(Base):
    __tablename__ = "problem_reference_solutions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    language = Column(String, nullable=False)
    solution_code = Column(Text, nullable=False)

    problem = relationship("Problem", back_populates="reference_solutions")


class ProblemComment(Base):
    __tablename__ = "problem_comments"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    problem = relationship("Problem", back_populates="comments")
    user = relationship("User", back_populates="comments")