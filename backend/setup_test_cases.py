from app.database import SessionLocal
from app.models import TestCase

def main():
    db = SessionLocal()
    
    # Clear existing test cases for problem_id=1
    db.query(TestCase).filter(TestCase.problem_id == 1).delete()
    
    # Add test cases for problem_id=1 (Two Sum problem)
    test_cases = [
        TestCase(problem_id=1, input_data="3 5", expected_output="8"),
        TestCase(problem_id=1, input_data="10 20", expected_output="30"),
        TestCase(problem_id=1, input_data="-5 5", expected_output="0"),
        TestCase(problem_id=1, input_data="100 200", expected_output="300"),
    ]
    
    for tc in test_cases:
        db.add(tc)
    
    db.commit()
    print(f"Added {len(test_cases)} test cases for problem_id=1")
    
    # Verify
    cases = db.query(TestCase).filter(TestCase.problem_id == 1).all()
    print(f"\nTest cases in database:")
    for idx, case in enumerate(cases, 1):
        print(f"  {idx}. Input: {case.input_data!r} -> Expected: {case.expected_output!r}")

if __name__ == "__main__":
    main()
