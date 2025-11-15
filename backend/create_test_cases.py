#!/usr/bin/env python3
"""
Script to create test problems and test cases in the database.
Run this before testing the submissions API.
"""

from app.database import SessionLocal, engine
from app import models

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

def create_test_cases():
    """Create test cases for problems 1, 2, and 3"""
    db = SessionLocal()
    
    try:
        # Problem 1: Python - Double the input number
        test_cases_data = [
            # Problem 1: Python
            {"problem_id": 1, "input_data": "5", "expected_output": "The answer is 10"},
            {"problem_id": 1, "input_data": "10", "expected_output": "The answer is 20"},
            
            # Problem 2: C++
            {"problem_id": 2, "input_data": "5", "expected_output": "The answer is 10"},
            {"problem_id": 2, "input_data": "10", "expected_output": "The answer is 20"},
            
            # Problem 3: Java
            {"problem_id": 3, "input_data": "5", "expected_output": "The answer is 10"},
            {"problem_id": 3, "input_data": "10", "expected_output": "The answer is 20"},
        ]
        
        # Delete existing test cases to avoid duplicates
        db.query(models.TestCase).filter(
            models.TestCase.problem_id.in_([1, 2, 3])
        ).delete(synchronize_session=False)
        db.commit()
        
        # Add new test cases
        for tc_data in test_cases_data:
            test_case = models.TestCase(**tc_data)
            db.add(test_case)
        
        db.commit()
        
        print("✅ Test cases created successfully!")
        print(f"   Total test cases: {len(test_cases_data)}")
        print("\n   Problem 1 (Python): 2 test cases")
        print("   Problem 2 (C++): 2 test cases")
        print("   Problem 3 (Java): 2 test cases")
        
    except Exception as e:
        print(f"❌ Error creating test cases: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Creating Test Cases")
    print("="*50 + "\n")
    
    create_test_cases()
    
    print("\n" + "="*50)
    print("Done! You can now run the API tests.")
    print("="*50 + "\n")
