"""
Recreate the database with the updated User model (is_admin field added).
This will drop all existing tables and recreate them.
"""
from app.database import engine, Base
from app.models import User, Submission, Problem, TestCase

def recreate_database():
    print("🔄 Recreating database with updated schema...")
    print("⚠️  WARNING: This will delete all existing data!")
    
    # Drop all tables
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")
    
    # Create all tables with new schema
    print("Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    print("\n📊 Database schema updated successfully!")
    print("\nNew User model includes:")
    print("  - is_admin field (default=0)")
    print("\nYou can now:")
    print("  1. Create test users with register endpoint")
    print("  2. Manually set is_admin=1 for admin users")
    print("  3. Test admin endpoints")

if __name__ == "__main__":
    recreate_database()
