"""
===================================================================================
  FRONTEND-BACKEND INTEGRATION GUIDE
  React + Axios with FastAPI Backend
===================================================================================

This guide shows how to integrate your React frontend with the FastAPI backend,
including CORS setup, authentication, and API calls.

===================================================================================
  📋 TABLE OF CONTENTS
===================================================================================

1. Backend CORS Configuration (COMPLETED ✅)
2. Frontend Project Setup
3. Axios Configuration with Interceptors
4. Authentication Service
5. API Service Functions
6. React Components Examples
7. Testing the Integration
8. Running Both Servers

===================================================================================
  ✅ 1. BACKEND CORS CONFIGURATION (COMPLETED)
===================================================================================

The backend has been updated with CORS middleware in app/main.py:

✅ Allows frontend origins (localhost:5173, localhost:3000, etc.)
✅ Allows credentials (JWT tokens in headers)
✅ Allows all HTTP methods (GET, POST, PUT, DELETE)
✅ Allows all headers (Authorization, Content-Type, etc.)

No further backend changes needed for CORS!

===================================================================================
  📦 2. FRONTEND PROJECT SETUP
===================================================================================

Step 1: Create React App with Vite
-----------------------------------
npm create vite@latest frontend -- --template react
cd frontend
npm install

Step 2: Install Required Dependencies
--------------------------------------
npm install axios
npm install react-router-dom

Optional (for better UI):
npm install @mui/material @emotion/react @emotion/styled  # Material-UI
npm install react-hot-toast  # Toast notifications

Step 3: Project Structure
-------------------------
frontend/
  ├── src/
  │   ├── api/
  │   │   ├── axios.js           # Axios instance with interceptors
  │   │   ├── auth.js            # Authentication API calls
  │   │   ├── problems.js        # Problem API calls
  │   │   └── submissions.js     # Submission API calls
  │   ├── components/
  │   │   ├── Login.jsx
  │   │   ├── Register.jsx
  │   │   ├── ProblemList.jsx
  │   │   └── CodeEditor.jsx
  │   ├── context/
  │   │   └── AuthContext.jsx    # Global auth state
  │   ├── App.jsx
  │   └── main.jsx

===================================================================================
  🔧 3. AXIOS CONFIGURATION WITH INTERCEPTORS
===================================================================================

File: frontend/src/api/axios.js
-------------------------------
"""

# JavaScript code for axios.js
AXIOS_CONFIG = '''
import axios from 'axios';

// Backend API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor - Add JWT token to every request
axiosInstance.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    
    // If token exists, add it to Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log('Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('Response error:', error.response.status, error.response.data);
      
      // Handle 401 Unauthorized - Token expired or invalid
      if (error.response.status === 401) {
        console.log('Unauthorized! Clearing token and redirecting to login...');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      
      // Handle 403 Forbidden - Insufficient permissions
      if (error.response.status === 403) {
        console.log('Forbidden! Admin privileges required.');
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server:', error.request);
    } else {
      // Error in request setup
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
export { API_BASE_URL };
'''

print(__doc__)
print("\n" + "="*80)
print("  File: frontend/src/api/axios.js")
print("="*80)
print(AXIOS_CONFIG)

# JavaScript code for auth.js
AUTH_SERVICE = '''
===================================================================================
  File: frontend/src/api/auth.js
===================================================================================

import axiosInstance from './axios';

// ============================================================
// AUTHENTICATION API CALLS
// ============================================================

/**
 * Register a new user
 * @param {Object} userData - { username, email, password }
 * @returns {Promise} Response with user_id and message
 */
export const register = async (userData) => {
  try {
    const response = await axiosInstance.post('/auth/register', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Registration failed' };
  }
};

/**
 * Login user and get JWT token
 * @param {Object} credentials - { email, password }
 * @returns {Promise} Response with access_token, user_id, username
 */
export const login = async (credentials) => {
  try {
    const response = await axiosInstance.post('/auth/login', credentials);
    const { access_token, user_id, username } = response.data;
    
    // Store token and user info in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify({ user_id, username }));
    
    console.log('Login successful! Token stored.');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Login failed' };
  }
};

/**
 * Logout user (clear local storage)
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  console.log('Logged out successfully');
};

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return localStorage.getItem('access_token') !== null;
};

/**
 * Get current user from localStorage
 * @returns {Object|null}
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Get JWT token from localStorage
 * @returns {string|null}
 */
export const getToken = () => {
  return localStorage.getItem('access_token');
};
'''

print(AUTH_SERVICE)

# JavaScript code for problems.js
PROBLEMS_SERVICE = '''
===================================================================================
  File: frontend/src/api/problems.js
===================================================================================

import axiosInstance from './axios';

// ============================================================
// PROBLEM API CALLS
// ============================================================

/**
 * Get all problems
 * @returns {Promise<Array>} List of all problems
 */
export const getAllProblems = async () => {
  try {
    const response = await axiosInstance.get('/problems');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch problems' };
  }
};

/**
 * Get single problem by ID
 * @param {number} problemId
 * @returns {Promise<Object>} Problem with test cases
 */
export const getProblemById = async (problemId) => {
  try {
    const response = await axiosInstance.get(`/problems/${problemId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Problem not found' };
  }
};

/**
 * Create a new problem (Admin only)
 * @param {Object} problemData
 * @returns {Promise<Object>} Created problem
 */
export const createProblem = async (problemData) => {
  try {
    const response = await axiosInstance.post('/problems', problemData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to create problem' };
  }
};
'''

print(PROBLEMS_SERVICE)

# JavaScript code for submissions.js
SUBMISSIONS_SERVICE = '''
===================================================================================
  File: frontend/src/api/submissions.js
===================================================================================

import axiosInstance from './axios';

// ============================================================
// SUBMISSION API CALLS (REQUIRES AUTHENTICATION)
// ============================================================

/**
 * Submit code for a problem
 * @param {Object} submissionData - { problem_id, language, code }
 * @returns {Promise<Object>} Submission result with status
 */
export const submitCode = async (submissionData) => {
  try {
    const response = await axiosInstance.post('/submissions', submissionData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Submission failed' };
  }
};

/**
 * Get user's submission history
 * @param {boolean} includeCode - Include code in response
 * @returns {Promise<Array>} List of submissions
 */
export const getMySubmissions = async (includeCode = false) => {
  try {
    const url = includeCode ? '/submissions/me?include_code=true' : '/submissions/me';
    const response = await axiosInstance.get(url);
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch submissions' };
  }
};
'''

print(SUBMISSIONS_SERVICE)

# JavaScript code for users.js
USERS_SERVICE = '''
===================================================================================
  File: frontend/src/api/users.js
===================================================================================

import axiosInstance from './axios';

// ============================================================
// USER API CALLS (REQUIRES AUTHENTICATION)
// ============================================================

/**
 * Get current user profile
 * @returns {Promise<Object>} User profile with XP, streak, etc.
 */
export const getProfile = async () => {
  try {
    const response = await axiosInstance.get('/users/me');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch profile' };
  }
};

/**
 * Get leaderboard (public)
 * @returns {Promise<Array>} Top 20 users
 */
export const getLeaderboard = async () => {
  try {
    const response = await axiosInstance.get('/users/leaderboard');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch leaderboard' };
  }
};

/**
 * Get user submission history
 * @returns {Promise<Array>} User's submissions
 */
export const getUserSubmissions = async () => {
  try {
    const response = await axiosInstance.get('/users/me/submissions');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to fetch submissions' };
  }
};
'''

print(USERS_SERVICE)

print("""
===================================================================================
  📱 4. REACT COMPONENTS EXAMPLES
===================================================================================

These are example React components showing how to use the API services.
""")

# React Login Component
LOGIN_COMPONENT = '''
===================================================================================
  File: frontend/src/components/Login.jsx
===================================================================================

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login({ email, password });
      console.log('Login successful:', response);
      
      // Redirect to problems page
      navigate('/problems');
    } catch (err) {
      setError(err.detail || 'Login failed. Please check your credentials.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login to AlgoGenius</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="your@email.com"
          />
        </div>

        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter password"
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p>
        Don't have an account? <a href="/register">Register</a>
      </p>
    </div>
  );
}

export default Login;
'''

print(LOGIN_COMPONENT)

# React Problems Component
PROBLEMS_COMPONENT = '''
===================================================================================
  File: frontend/src/components/ProblemList.jsx
===================================================================================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllProblems } from '../api/problems';
import { isAuthenticated } from '../api/auth';

function ProblemList() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProblems();
  }, []);

  const fetchProblems = async () => {
    try {
      const data = await getAllProblems();
      setProblems(data);
      setLoading(false);
    } catch (err) {
      setError(err.detail || 'Failed to load problems');
      setLoading(false);
    }
  };

  const handleProblemClick = (problemId) => {
    if (!isAuthenticated()) {
      alert('Please login to solve problems');
      navigate('/login');
      return;
    }
    navigate(`/problem/${problemId}`);
  };

  if (loading) return <div>Loading problems...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="problem-list">
      <h1>Coding Problems</h1>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Difficulty</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {problems.map((problem) => (
            <tr key={problem.id}>
              <td>{problem.id}</td>
              <td>{problem.title}</td>
              <td>
                <span className={`badge badge-${problem.difficulty}`}>
                  {problem.difficulty}
                </span>
              </td>
              <td>
                <button onClick={() => handleProblemClick(problem.id)}>
                  Solve
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ProblemList;
'''

print(PROBLEMS_COMPONENT)

# React Code Submission Component
SUBMISSION_COMPONENT = '''
===================================================================================
  File: frontend/src/components/CodeSubmission.jsx
===================================================================================

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getProblemById } from '../api/problems';
import { submitCode } from '../api/submissions';

function CodeSubmission() {
  const { problemId } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProblem();
  }, [problemId]);

  const loadProblem = async () => {
    try {
      const data = await getProblemById(problemId);
      setProblem(data);
      
      // Set default starter code
      if (language === 'python') {
        setCode('# Write your solution here\\n\\ndef solve():\\n    pass\\n\\nsolve()');
      }
    } catch (err) {
      console.error('Failed to load problem:', err);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) {
      alert('Please write some code first!');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await submitCode({
        problem_id: parseInt(problemId),
        language: language,
        code: code
      });

      setResult(response);
      console.log('Submission result:', response);
    } catch (err) {
      setResult({
        status: 'Error',
        message: err.detail || 'Submission failed'
      });
    } finally {
      setLoading(false);
    }
  };

  if (!problem) return <div>Loading problem...</div>;

  return (
    <div className="code-submission">
      <div className="problem-description">
        <h2>{problem.title}</h2>
        <span className={`badge badge-${problem.difficulty}`}>
          {problem.difficulty}
        </span>
        <p>{problem.description}</p>
      </div>

      <div className="code-editor">
        <div className="editor-header">
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="cpp">C++</option>
            <option value="java">Java</option>
          </select>
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Code'}
          </button>
        </div>

        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={20}
          placeholder="Write your code here..."
        />
      </div>

      {result && (
        <div className={`result result-${result.status.toLowerCase()}`}>
          <h3>Result: {result.status}</h3>
          <p>{result.message}</p>
          {result.output && (
            <pre>Output: {result.output}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default CodeSubmission;
'''

print(SUBMISSION_COMPONENT)

print("""
===================================================================================
  🧪 5. TESTING THE INTEGRATION
===================================================================================

Test Script: test_frontend_integration.html
--------------------------------------------
Create this file in frontend/public/ for quick testing:
""")

TEST_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>API Integration Test</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .test { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .success { background: #d4edda; }
        .error { background: #f8d7da; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Frontend-Backend Integration Test</h1>
    
    <div class="test">
        <h3>Test 1: Register User</h3>
        <button onclick="testRegister()">Run Test</button>
        <pre id="register-result"></pre>
    </div>
    
    <div class="test">
        <h3>Test 2: Login User</h3>
        <button onclick="testLogin()">Run Test</button>
        <pre id="login-result"></pre>
    </div>
    
    <div class="test">
        <h3>Test 3: Get Problems (Public)</h3>
        <button onclick="testProblems()">Run Test</button>
        <pre id="problems-result"></pre>
    </div>
    
    <div class="test">
        <h3>Test 4: Get Profile (Protected)</h3>
        <button onclick="testProfile()">Run Test</button>
        <pre id="profile-result"></pre>
    </div>
    
    <div class="test">
        <h3>Test 5: Submit Code (Protected)</h3>
        <button onclick="testSubmission()">Run Test</button>
        <pre id="submission-result"></pre>
    </div>

    <script>
        const API_URL = 'http://localhost:8000/api';
        let authToken = '';

        async function testRegister() {
            const result = document.getElementById('register-result');
            try {
                const response = await fetch(`${API_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: 'testuser' + Date.now(),
                        email: `test${Date.now()}@example.com`,
                        password: 'testpass123'
                    })
                });
                const data = await response.json();
                result.textContent = JSON.stringify(data, null, 2);
                result.parentElement.className = response.ok ? 'test success' : 'test error';
            } catch (err) {
                result.textContent = 'Error: ' + err.message;
                result.parentElement.className = 'test error';
            }
        }

        async function testLogin() {
            const result = document.getElementById('login-result');
            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'test@example.com',
                        password: 'testpass123'
                    })
                });
                const data = await response.json();
                if (response.ok && data.access_token) {
                    authToken = data.access_token;
                    localStorage.setItem('access_token', authToken);
                }
                result.textContent = JSON.stringify(data, null, 2);
                result.parentElement.className = response.ok ? 'test success' : 'test error';
            } catch (err) {
                result.textContent = 'Error: ' + err.message;
                result.parentElement.className = 'test error';
            }
        }

        async function testProblems() {
            const result = document.getElementById('problems-result');
            try {
                const response = await fetch(`${API_URL}/problems`);
                const data = await response.json();
                result.textContent = JSON.stringify(data, null, 2);
                result.parentElement.className = response.ok ? 'test success' : 'test error';
            } catch (err) {
                result.textContent = 'Error: ' + err.message;
                result.parentElement.className = 'test error';
            }
        }

        async function testProfile() {
            const result = document.getElementById('profile-result');
            const token = authToken || localStorage.getItem('access_token');
            
            if (!token) {
                result.textContent = 'Error: Please login first (Test 2)';
                result.parentElement.className = 'test error';
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/users/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                result.textContent = JSON.stringify(data, null, 2);
                result.parentElement.className = response.ok ? 'test success' : 'test error';
            } catch (err) {
                result.textContent = 'Error: ' + err.message;
                result.parentElement.className = 'test error';
            }
        }

        async function testSubmission() {
            const result = document.getElementById('submission-result');
            const token = authToken || localStorage.getItem('access_token');
            
            if (!token) {
                result.textContent = 'Error: Please login first (Test 2)';
                result.parentElement.className = 'test error';
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/submissions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        problem_id: 1,
                        language: 'python',
                        code: 'a, b = map(int, input().split())\\nprint(a + b)'
                    })
                });
                const data = await response.json();
                result.textContent = JSON.stringify(data, null, 2);
                result.parentElement.className = response.ok ? 'test success' : 'test error';
            } catch (err) {
                result.textContent = 'Error: ' + err.message;
                result.parentElement.className = 'test error';
            }
        }
    </script>
</body>
</html>
'''

print("Save this as: frontend/public/test_integration.html")
print(TEST_HTML)

print("""
===================================================================================
  🚀 6. RUNNING BOTH SERVERS CONCURRENTLY
===================================================================================

Option 1: Using Two Terminals (Recommended for Development)
------------------------------------------------------------

Terminal 1 - Backend:
  cd backend
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Terminal 2 - Frontend:
  cd frontend
  npm run dev

Option 2: Using npm-run-all (Single Terminal)
----------------------------------------------

1. Install concurrently in your project root:
   npm install -D concurrently

2. Add scripts to package.json (in project root):
   {
     "scripts": {
       "start:backend": "cd backend && python -m uvicorn app.main:app --reload",
       "start:frontend": "cd frontend && npm run dev",
       "start": "concurrently \\"npm:start:backend\\" \\"npm:start:frontend\\""
     }
   }

3. Run both:
   npm start

Option 3: Using Docker Compose (Production-like)
-------------------------------------------------

Create docker-compose.yml in project root:

version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    command: npm run dev -- --host

Run with:
  docker-compose up

===================================================================================
  ✅ 7. VERIFICATION CHECKLIST
===================================================================================

Backend (http://localhost:8000):
  ✅ Visit http://localhost:8000 - Should show {"status": "online"}
  ✅ Visit http://localhost:8000/docs - Should show Swagger API docs
  ✅ Check CORS headers in browser dev tools (Network tab)

Frontend (http://localhost:5173):
  ✅ npm run dev starts without errors
  ✅ Console shows no CORS errors
  ✅ Can register a new user
  ✅ Can login and see token in localStorage
  ✅ Can view problems list
  ✅ Can submit code and see results
  ✅ Protected routes redirect to login when not authenticated

Testing Flow:
  1. Open http://localhost:5173/test_integration.html
  2. Run Test 1 (Register) - Should succeed
  3. Run Test 2 (Login) - Should get access_token
  4. Run Test 3 (Problems) - Should list problems
  5. Run Test 4 (Profile) - Should show user data with token
  6. Run Test 5 (Submit) - Should submit code successfully

===================================================================================
  📝 8. COMMON ISSUES & SOLUTIONS
===================================================================================

Issue: CORS Error "Access-Control-Allow-Origin"
Solution: ✅ Backend CORS is configured. Clear browser cache and restart servers.

Issue: 401 Unauthorized on protected routes
Solution: Check that token is saved in localStorage and axios interceptor is working.

Issue: "Failed to fetch" or "Network Error"
Solution: Ensure backend is running on port 8000. Check firewall settings.

Issue: Token not being sent in requests
Solution: Verify axios interceptor is reading from localStorage correctly.

Issue: Frontend can't connect to localhost:8000
Solution: Try 127.0.0.1:8000 instead, or check backend is binding to 0.0.0.0.

===================================================================================
  🎉 SUMMARY
===================================================================================

✅ Backend CORS configured in app/main.py
✅ Frontend axios setup with interceptors
✅ Authentication service with localStorage
✅ API services for problems and submissions
✅ React component examples
✅ Test HTML page for quick verification
✅ Instructions for running both servers

Your frontend and backend are now fully integrated! 🚀

Next steps:
  1. Start backend: uvicorn app.main:app --reload
  2. Start frontend: npm run dev (in frontend directory)
  3. Open http://localhost:5173
  4. Test login → browse problems → submit code flow

===================================================================================
""")

if __name__ == "__main__":
    pass
