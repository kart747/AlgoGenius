#!/usr/bin/env python3
"""
Script to create a test user in the database.
Run this before testing the submissions API.
"""

from app.database import SessionLocal, engine
from app import models
import bcrypt

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)


def hash_password(password: str) -> str:
    """Return a bcrypt hashed password (utf-8 decoded)."""
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')


def create_test_user():
    """Create a test user with id=1 and a valid bcrypt hashed password.

    The inserted user will be usable with the /api/auth/login endpoint.
    """
    db = SessionLocal()

    try:
        # Check if user already exists by email
        existing_user = db.query(models.User).filter(models.User.email == 'testuser@example.com').first()

        if existing_user:
            print("✅ Test user already exists in DB")
            print(f"   ID: {existing_user.id}")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            return

        # Create new test user with bcrypt hashed password
        pwd = 'password123'
        hashed = hash_password(pwd)

        test_user = models.User(
            username='testuser',
            email='testuser@example.com',
            hashed_password=hashed,
            xp=0,
            current_streak=0
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print('✅ Test user created successfully!')
        print(f'   ID: {test_user.id}')
        print(f'   Username: {test_user.username}')
        print(f'   Email: {test_user.email}')
        print('   Password: password123')

    except Exception as e:
        print(f'❌ Error creating user: {e}')
        db.rollback()

    finally:
        db.close()


if __name__ == '__main__':
    print('\n' + '=' * 50)
    print('Creating Test User (direct DB insert with bcrypt hashed password)')
    print('=' * 50 + '\n')
    create_test_user()
    print('\n' + '=' * 50)
    print('Done!')
    print('=' * 50 + '\n')
