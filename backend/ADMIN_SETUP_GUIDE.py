"""
Quick Setup Guide for Admin Features
=====================================

This guide will help you set up and test the new admin features.

Step 1: Update Database Schema
-------------------------------
The User model now includes an 'is_admin' field. You need to update your database.

Option A - Recreate Database (RECOMMENDED for development):
    python recreate_db_with_admin.py

Option B - Manual SQL (if you want to keep existing data):
    ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;

Step 2: Create Admin User
--------------------------
Run the admin user creation script:
    python create_admin_user.py

This will:
- Create a user with credentials: admin@example.com / admin123
- Set is_admin=1 in the database
- Save credentials to admin_credentials.json

Step 3: Test Admin Features
----------------------------
Run the comprehensive test suite:
    python test_admin_features.py

This will test:
- Admin authentication
- Access control (regular users can't access admin endpoints)
- Problem management (create, update, delete)
- Test case management (add, remove)
- User management (list users)
- Platform statistics

Admin Endpoints Available
--------------------------
Problem Management:
  POST   /api/admin/problems              - Create problem
  PUT    /api/admin/problems/{id}         - Update problem
  DELETE /api/admin/problems/{id}         - Delete problem
  POST   /api/admin/problems/{id}/testcases - Add test case
  DELETE /api/admin/testcases/{id}        - Remove test case

User Management:
  GET    /api/admin/users                 - List all users
  DELETE /api/admin/users/{id}            - Delete user

Platform Stats:
  GET    /api/admin/stats                 - Get platform statistics

All endpoints require:
- Valid JWT token
- User with is_admin=1

Security Features
-----------------
✅ Admin-only access via require_admin dependency
✅ 403 Forbidden for non-admin users
✅ JWT authentication required
✅ Self-deletion prevention (admin can't delete their own account)
✅ Cascade deletes (deleting problem removes test cases)

Quick Start Commands
--------------------
1. python recreate_db_with_admin.py
2. python create_admin_user.py
3. python test_admin_features.py

Troubleshooting
---------------
If you get "Admin privileges required" error:
- Verify is_admin=1 in database
- Check you're using the admin token
- Ensure admin user was created successfully

If login fails:
- Verify admin user exists in database
- Check password is "admin123"
- Try recreating the admin user
"""

print(__doc__)
