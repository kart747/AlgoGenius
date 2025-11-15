# 🔒 Security & Deployment Checklist

## ✅ Pre-Commit Checklist

Before pushing to GitHub, ensure:

### Environment Files

- [ ] `.env` files are in `.gitignore`
- [ ] No `.env` files are committed
- [ ] `.env.example` files have placeholder values only
- [ ] All API keys are in environment variables
- [ ] Database credentials are in environment variables
- [ ] JWT secrets are in environment variables

### Sensitive Files

- [ ] `test_credentials.json` is not committed
- [ ] No `*.db` or `*.sqlite` files committed
- [ ] No credential files committed
- [ ] No `.pem` or `.key` files committed

### Code Review

- [ ] No hardcoded API keys in source code
- [ ] No hardcoded passwords in source code
- [ ] No database credentials in source code
- [ ] All secrets loaded from `os.getenv()` or `process.env`

## 🔐 Secrets Inventory

### Backend Secrets (.env)

1. **DATABASE_URL** - PostgreSQL connection string

   - Contains: username, password, host, port, database name
   - Format: `postgresql+psycopg2://user:pass@host:port/dbname`

2. **JWT_SECRET_KEY** - JSON Web Token signing key

   - Must be: minimum 32 characters, random, secure
   - Used for: user authentication tokens

3. **GEMINI_API_KEY** - Google Gemini AI API key
   - Get from: https://ai.google.dev/
   - Used for: AI problem generation

### Frontend Secrets (.env.local)

1. **NEXT_PUBLIC_API_BASE_URL** - Backend API base URL

   - Development: `http://localhost:8000/api`
   - Production: `https://your-api-domain.com/api`

2. **NEXT_PUBLIC_API_URL** - Backend API root URL
   - Development: `http://localhost:8000`
   - Production: `https://your-api-domain.com`

## 🚨 Files That Should NEVER Be Committed

### Environment Files

- `backend/.env`
- `frontend/.env.local`
- Any file matching `*.env` pattern (except `.env.example`)

### Credentials

- `test_credentials.json`
- `credentials.json`
- `*_credentials.json`
- `secrets.json`
- `*.pem`
- `*.key`

### Databases

- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `*.db-journal`

### Dependencies

- `node_modules/`
- `venv/`
- `__pycache__/`
- `.pytest_cache/`

### Build Artifacts

- `.next/`
- `build/`
- `dist/`
- `out/`

### IDE/OS Files

- `.vscode/`
- `.idea/`
- `.DS_Store`
- `Thumbs.db`

## 🔍 Security Scan Results

### ✅ Secrets Properly Configured

- All environment variables use `os.getenv()` in Python
- All environment variables use `process.env.NEXT_PUBLIC_*` in Next.js
- No hardcoded credentials found in source code

### ✅ Files Protected by .gitignore

- Environment files excluded
- Credentials files excluded
- Database files excluded
- Temporary files excluded

### ⚠️ Files Requiring Manual Review

**Before pushing, manually review these files:**

1. **backend/.env** - Ensure no real secrets committed
2. **frontend/.env.local** - Ensure no real secrets committed
3. **test_credentials.json** - Should be in .gitignore, not committed
4. **Any files in backend/ containing "test\_" prefix** - Review for hardcoded credentials

## 🛡️ Production Deployment Security

### Required Changes for Production

1. **Generate Strong JWT Secret**

   ```bash
   # Linux/Mac
   openssl rand -hex 32

   # Python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use Strong Database Password**

   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Store in environment variable only

3. **Update CORS Origins**
   In `backend/app/main.py`, replace:

   ```python
   origins = [
       "http://localhost:3000",
       "http://localhost:5173",
   ]
   ```

   With your production domain:

   ```python
   origins = [
       "https://your-frontend-domain.com",
   ]
   ```

4. **Enable HTTPS**

   - Use SSL/TLS certificates
   - Force HTTPS redirects
   - Set secure cookie flags

5. **Set Secure Headers**

   ```python
   # Add to FastAPI app
   app.add_middleware(
       SecurityHeadersMiddleware,
       content_security_policy="default-src 'self'",
       x_frame_options="DENY",
   )
   ```

6. **Rate Limiting**

   - Add rate limiting middleware
   - Limit problem generation requests
   - Limit submission frequency

7. **Database Security**

   - Use connection pooling
   - Enable SSL for database connections
   - Regularly backup database

8. **Docker Security**
   - Keep images updated
   - Use minimal base images
   - Scan for vulnerabilities

## 📝 Environment Setup Guide

### Development Setup

```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your development credentials
# Use localhost database
# Use development JWT secret

# Frontend
cd frontend
cp .env.local.example .env.local
# Use localhost:8000 for API
```

### Production Setup

```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with:
# - Production database URL (managed database recommended)
# - Strong JWT secret (generated with openssl)
# - Production Gemini API key (separate from dev)

# Frontend
cd frontend
cp .env.local.example .env.local
# Edit .env.local with:
# - Production API URL (https://api.your-domain.com)
```

## 🔄 Git Workflow

### Initial Commit

```bash
# 1. Ensure .gitignore is in place
git add .gitignore

# 2. Add example files only
git add backend/.env.example
git add frontend/.env.local.example

# 3. Add source code
git add backend/app backend/services
git add frontend/app frontend/components frontend/src

# 4. Commit
git commit -m "Initial commit - secure setup"

# 5. Push
git push origin main
```

### Before Every Push

```bash
# 1. Check git status
git status

# 2. Verify no .env files are staged
git diff --cached | grep -E "(\.env|credentials|secrets)"

# 3. If found, unstage them
git reset HEAD backend/.env
git reset HEAD frontend/.env.local

# 4. Add to .gitignore if needed
echo "backend/.env" >> .gitignore
```

## 🚨 Emergency: Secret Leaked

If you accidentally commit a secret:

### Step 1: Rotate Secrets Immediately

- Generate new JWT secret
- Create new Gemini API key
- Change database password
- Update environment variables

### Step 2: Remove from Git History

```bash
# Remove file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (dangerous!)
git push origin --force --all
```

### Step 3: Notify

- Notify team members
- Update documentation
- Monitor for unauthorized access

## ✅ Final Verification

Before pushing, run this checklist:

```bash
# 1. Check no .env files in git
git ls-files | grep -E "\.env$"
# Should return nothing

# 2. Check .gitignore is working
git status --ignored | grep -E "(\.env|credentials)"
# Should show ignored files

# 3. Verify example files exist
ls backend/.env.example
ls frontend/.env.local.example
# Both should exist

# 4. Verify no secrets in staged files
git diff --cached | grep -iE "(api_key|secret|password|token=)"
# Should return nothing (or only example placeholders)
```

## 📞 Support

If you're unsure about any security aspect:

1. DON'T push until verified
2. Review this checklist again
3. Ask for code review
4. Use GitHub secret scanning tools

---

**Remember**: Once a secret is committed to Git, assume it's compromised.
Always rotate secrets if accidentally committed.
