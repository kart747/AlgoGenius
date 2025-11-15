from app.database import SessionLocal, engine, Base
from app.models import Problem, TestCase


SEED_PROBLEMS = [
    {
        "title": "Sum Two Numbers",
        "description": "Read two integers from stdin and print their sum.",
        "difficulty": "easy",
        "test_cases": [
            {"input_data": "1 2", "expected_output": "3"},
            {"input_data": "3 5", "expected_output": "8"},
            {"input_data": "10 -4", "expected_output": "6"},
        ],
    },
    {
        "title": "Palindrome Check",
        "description": "Print true if the supplied string is a palindrome ignoring case and punctuation.",
        "difficulty": "easy",
        "test_cases": [
            {"input_data": "racecar", "expected_output": "true"},
            {"input_data": "RaceCar", "expected_output": "true"},
            {"input_data": "hello", "expected_output": "false"},
        ],
    },
    {
        "title": "FizzBuzz",
        "description": "Print the FizzBuzz sequence from 1 to n where n is provided on stdin.",
        "difficulty": "easy",
        "test_cases": [
            {
                "input_data": "5",
                "expected_output": "1\n2\nFizz\n4\nBuzz",
            },
            {
                "input_data": "3",
                "expected_output": "1\n2\nFizz",
            },
        ],
    },
]

def main():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        for payload in SEED_PROBLEMS:
            problem = Problem(
                title=payload["title"],
                description=payload["description"],
                difficulty=payload["difficulty"],
            )
            session.add(problem)
            session.flush()

            for tc in payload["test_cases"]:
                session.add(
                    TestCase(
                        problem_id=problem.id,
                        input_data=tc["input_data"],
                        expected_output=tc["expected_output"],
                    )
                )

        session.commit()
        print("Database recreated and seeded with sample problems.")
    except Exception as exc:
        session.rollback()
        print(f"Error seeding problems: {exc}")
    finally:
        session.close()

    print("\nTables created:")
    print("  - users")
    print("  - problems")
    print("  - test_cases")
    print("  - submissions")

if __name__ == "__main__":
    main()
