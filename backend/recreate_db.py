#!/usr/bin/env python3
"""
Script to recreate database tables.
WARNING: This will drop all existing data!
"""

from app.database import engine
from app import models

print("\n" + "="*50)
print("Recreating Database Tables")
print("="*50 + "\n")

print("⚠️  Dropping all existing tables...")
models.Base.metadata.drop_all(bind=engine)

print("✅ Creating new tables...")
models.Base.metadata.create_all(bind=engine)

print("\n✅ Database tables recreated successfully!")
print("\n" + "="*50)
print("Next steps:")
print("  1. Run: python create_test_user.py")
print("  2. Run: python create_test_cases.py")
print("  3. Run: python test_submissions_api.py")
print("="*50 + "\n")
