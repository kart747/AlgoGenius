"""
Load environment variables from .env file

This ensures the .env file is loaded before running any tests or services.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Get the backend directory path
backend_dir = Path(__file__).parent
env_file = backend_dir / '.env'

# Load .env file
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from: {env_file}")
else:
    print(f"⚠️  .env file not found at: {env_file}")

# Check if GEMINI_API_KEY is loaded
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and gemini_key != "your_gemini_api_key_here":
    print(f"✅ GEMINI_API_KEY loaded: {gemini_key[:10]}...{gemini_key[-5:]}")
else:
    print("⚠️  GEMINI_API_KEY not set or using placeholder")
    print("\n   Please update .env file with your actual Gemini API key:")
    print(f"   Edit: {env_file}")
    print("   Change: GEMINI_API_KEY=your_actual_api_key_here")
