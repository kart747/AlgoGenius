from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# Load environment variables before importing route modules so they can
# read settings (e.g., GEMINI_API_KEY) at import time.
load_dotenv(dotenv_path=ENV_PATH, override=False)

from app.api.endpoints import submissions, auth, problems, users, admin, generator

app = FastAPI(
    title="AlgoGenius Code Submission Platform",
    version="1.0.0",
    description="LeetCode-style platform with AI-powered problem generation"
)

# ============================================================
# CORS CONFIGURATION FOR FRONTEND INTEGRATION
# ============================================================

# Allow frontend to access backend API
# In production, replace "*" with specific frontend URL
origins = [
    "http://localhost:5173",      # Vite default (React)
    "http://localhost:3000",      # Create React App default
    "http://localhost:5174",      # Vite alternative port
    "http://localhost:8080",      # Vue CLI default
    "http://127.0.0.1:5173",      # Alternative localhost
    "http://127.0.0.1:3000",      # Alternative localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Frontend URLs
    allow_credentials=True,             # Allow cookies/auth headers
    allow_methods=["*"],                # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],                # Allow all headers (Authorization, Content-Type, etc.)
    expose_headers=["*"],               # Expose all response headers to frontend
)

# ============================================================
# ROUTE REGISTRATION
# ============================================================

app.include_router(auth.router, prefix="/api")
app.include_router(problems.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(generator.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")

# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AlgoGenius API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }