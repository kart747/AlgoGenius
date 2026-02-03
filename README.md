# 🚀 DevArena - Competitive Programming Platform

A full-stack LeetCode-style competitive programming platform with AI-powered problem generation, Docker-based code execution sandbox, and modern UI.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![React](https://img.shields.io/badge/React-19-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)

## ✨ Features

### 🎯 Core Features

- **Professional Solve Interface** - Split-panel layout with Monaco editor
- **Multi-Language Support** - Python, C++, Java with syntax highlighting
- **AI Problem Generation** - Google Gemini-powered problem creation with topic tagging
- **Docker Sandbox** - Secure isolated code execution with timeout and memory limits
- **Real-time Execution** - Run code with custom input or submit against hidden test cases
- **User Authentication** - JWT-based secure auth system with registration/login
- **Admin Dashboard** - Problem management, user administration, and analytics
- **XP & Streaks** - Gamification with experience points and daily streaks tracking
- **Leaderboard** - Competitive rankings with user statistics
- **Daily Questions** - Featured problem of the day for consistent practice
- **Problem Topics/Tags** - Categorize and filter problems by difficulty and topic
- **Submission History** - Track all user submissions with detailed results
- **Profile Management** - User stats, progress tracking, and personal settings
- **Code Persistence** - Save and restore code between sessions
- **Custom Input Pre-filling** - Auto-fill test cases for quick testing

### 🎨 UI/UX Features

- **Dark Mode** - Modern dark theme with glass effects and smooth transitions
- **Responsive Design** - Optimized for mobile, tablet, and desktop devices
- **Toast Notifications** - Real-time feedback for actions and results
- **Fullscreen Code Editor** - Distraction-free coding environment
- **Resizable Panels** - Adjustable layout for personalized workspace
- **Copy/Reset/Fullscreen Controls** - Quick editor management tools
- **Theme Switcher** - Dark/light/high-contrast mode options
- **Keyboard Shortcuts** - Ctrl+Enter to run, efficient workflow shortcuts
- **Celebration Animations** - Success feedback with visual celebrations
- **Loading States** - Smooth loading indicators and progress feedback

### 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication system
- **Docker Isolation** - Code runs in isolated containers preventing system access
- **Memory Limits** - Prevent resource exhaustion with enforced limits
- **Timeout Enforcement** - Kill long-running processes automatically
- **Network Disabled** - No external network access during code execution
- **Read-only Code Mount** - Prevent file system modification attempts
- **Capability Drop** - Remove all Linux capabilities for enhanced security

### 🧪 Testing Features

- **E2E Integration Tests** - Full user flow testing from registration to submission
- **Unit Tests** - Component and function-level testing
- **API Endpoint Testing** - Backend route validation and error handling
- **Sandbox Testing** - Code execution verification across languages
- **Authentication Testing** - JWT token and access control validation

### 🤖 AI & Automation Features

- **AI Problem Generation** - Google Gemini-powered problem creation
- **Fallback AI Models** - Multiple Gemini models (2.5-flash + 1.5-flash-8b) for reliability
- **Topic Classification** - Automatic problem categorization and tagging
- **Quota Management** - Intelligent API usage tracking and fallback handling

### 📊 Analytics & Monitoring

- **Backend Status Reports** - System health and performance monitoring
- **Submission Analytics** - Detailed submission statistics and trends
- **User Progress Tracking** - XP accumulation, streak maintenance, and achievements
- **Admin Analytics** - User activity monitoring and problem performance metrics

## 🏗️ Tech Stack

### Frontend

- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS v4
- **Editor**: Monaco Editor
- **HTTP Client**: Axios
- **Language**: JavaScript/JSX

### Backend

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Code Execution**: Docker SDK for Python
- **AI Integration**: Google Gemini AI (2.5-flash + 1.5-flash-8b fallback)
- **Language**: Python 3.11+

## 📋 Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **PostgreSQL** 14+
- **Docker Desktop** (for code execution sandbox)
- **Google Gemini API Key** (free tier available)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/devarena.git
cd devarena
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# Required:
#   - DATABASE_URL (PostgreSQL connection string)
#   - JWT_SECRET_KEY (random secure string)
#   - GEMINI_API_KEY (get from https://ai.google.dev/)
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb devarena

# Initialize database tables
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Optional: Create admin user
python create_admin_user.py
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy example env file
cp .env.local.example .env.local

# Edit .env.local if needed (default works for local development)
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Start Development Servers

**Terminal 1 - Backend:**

```bash
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔐 Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/devarena

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Docker Images
PY_IMAGE=python:3.11-slim
CPP_IMAGE=gcc:12
JAVA_IMAGE=eclipse-temurin:17-jdk
SANDBOX_TIMEOUT_SEC=5
SANDBOX_USER=nobody
```

### Frontend (.env.local)

```bash
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_API_URL=http://localhost:8000

# API Timeout (milliseconds)
NEXT_PUBLIC_API_TIMEOUT_MS=60000
```

## 📁 Project Structure

```
devarena/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/      # API route handlers
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── database.py        # Database configuration
│   │   └── main.py            # FastAPI app entry
│   ├── services/
│   │   ├── gemini_service.py  # AI problem generation
│   │   └── sandbox_manager.py # Docker code execution
│   ├── .env.example           # Environment template
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── app/                   # Next.js pages (App Router)
│   ├── components/            # React components
│   │   ├── solve/            # Solve interface components
│   │   ├── UserProvider.jsx  # Auth context
│   │   └── Navbar.js         # Navigation
│   ├── lib/                  # Utilities
│   │   └── toast.js          # Notification system
│   ├── src/lib/
│   │   └── api.js            # Axios HTTP client
│   ├── .env.local.example    # Environment template
│   └── package.json          # Node dependencies
│
└── .gitignore                # Git ignore rules
```

## 🎮 Usage

### For Students/Users

1. **Register/Login** - Create account or login
2. **Browse Problems** - View problem list by difficulty
3. **Solve Problems** - Write code in Monaco editor
4. **Run Code** - Test with custom input
5. **Submit Solution** - Evaluate against hidden test cases
6. **Track Progress** - Earn XP and maintain streaks

### For Admins

1. **Generate Problems** - Use AI to create new problems
2. **Manage Problems** - Edit or delete existing problems
3. **View Submissions** - Monitor user activity
4. **Manage Users** - Admin panel access

## 🔧 API Endpoints

### Authentication

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)

### Problems

- `GET /api/problems` - List all problems
- `GET /api/problems/{id}` - Get problem details
- `POST /api/problems` - Create problem (admin)
- `DELETE /api/problems/{id}` - Delete problem (admin)

### Submissions

- `POST /api/submissions/run` - Run code with custom input
- `POST /api/submissions` - Submit solution
- `GET /api/submissions/me` - Get user submission history

### AI Generation

- `POST /api/problems/generate` - Generate AI problem
- `POST /api/problems/generate/save` - Generate and save

### Users

- `GET /api/users/me` - Get current user profile
- `GET /api/users/leaderboard` - Get top users

## 🐳 Docker Setup (Code Execution)

The platform uses Docker to execute user code securely. Ensure Docker Desktop is running:

```bash
# Verify Docker is running
docker --version

# Pull required images (optional, done automatically)
docker pull python:3.11-slim
docker pull gcc:12
docker pull eclipse-temurin:17-jdk
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🛡️ Security Features

- **JWT Authentication** - Secure token-based auth
- **Docker Isolation** - Code runs in isolated containers
- **Memory Limits** - Prevent resource exhaustion
- **Timeout Enforcement** - Kill long-running processes
- **Network Disabled** - No external access during execution
- **Read-only Code Mount** - Prevent file system modification
- **Capability Drop** - Remove all Linux capabilities

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for problem generation
- Monaco Editor for code editing
- FastAPI for backend framework
- Next.js for frontend framework
- Docker for secure code execution

## 📧 Support

For issues and questions:

- Open an issue on GitHub
- Email: support@devarena.dev

## 🗺️ Roadmap

- [ ] Real-time collaborative coding
- [ ] Code review system
- [ ] Discussion forums
- [ ] Video tutorials
- [ ] Mobile app
- [ ] More programming languages (Rust, Go, TypeScript)
- [ ] Contest mode
- [ ] Company-specific problem sets

---

Built with ❤️ by the DevArena Team
