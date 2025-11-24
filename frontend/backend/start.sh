#!/bin/bash

echo "🚀 Starting DevArena Dummy Backend Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo ""
echo "✅ Starting server on http://127.0.0.1:8000"
echo "📚 API Documentation available at http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 127.0.0.1 --port 8000
