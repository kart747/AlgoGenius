"""
Simple script to list users in the database for debugging.

Usage:
  python inspect_users.py
"""
from app.database import SessionLocal
from app.models import User

def main():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in database.")
            return

        print(f"Found {len(users)} user(s):")
        for u in users:
            print("-" * 50)
            print(f"ID: {u.id}")
            print(f"Username: {u.username}")
            print(f"Email: {u.email}")
            print(f"Is admin: {bool(u.is_admin)}")
            print(f"Hashed password: {u.hashed_password}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
