"""
Simple end-to-end integration test script that uses requests to exercise the API.
Run from the backend/ directory while backend is running (http://localhost:8000).
"""
import requests
import uuid
import time

BASE = "http://localhost:8000/api"

session = requests.Session()

results = {}

# 1) Register a temporary user
username = f"e2e_user_{uuid.uuid4().hex[:8]}"
email = f"{username}@example.com"
password = "TestPass123!"

print("Registering user:", username, email)
resp = session.post(f"{BASE}/auth/register", json={
    "username": username,
    "email": email,
    "password": password
})
results['register_status'] = resp.status_code
results['register_body'] = resp.json() if resp.text else None
print('Register ->', resp.status_code, resp.text)

# If user already exists, proceed to login path
# 2) Login
resp = session.post(f"{BASE}/auth/login", json={"email": email, "password": password})
results['login_status'] = resp.status_code
if resp.ok:
    data = resp.json()
    token = data.get('access_token')
    user_id = data.get('user_id')
    print('Login succeeded, token length:', len(token) if token else None)
    session.headers.update({'Authorization': f'Bearer {token}'})
    results['token'] = token
else:
    print('Login failed:', resp.status_code, resp.text)
    results['login_body'] = resp.text
    raise SystemExit('Login failed; aborting E2E test')

# 3) Fetch problems (list or today)
print('\nFetching problems list...')
resp = session.get(f"{BASE}/problems")
results['problems_status'] = resp.status_code
results['problems_body'] = resp.json() if resp.text else None
print('Problems ->', resp.status_code)

# If problems list is empty, try /problems/today
problems = results['problems_body'] or []
problem_id = None
if isinstance(problems, list) and len(problems) > 0:
    problem_id = problems[0].get('id')
else:
    print('Problems list empty, trying /problems/today')
    resp2 = session.get(f"{BASE}/problems/today")
    results['today_status'] = resp2.status_code
    results['today_body'] = resp2.json() if resp2.text else None
    print('/problems/today ->', resp2.status_code)
    if resp2.ok:
        problem = resp2.json()
        problem_id = problem.get('id')

if not problem_id:
    print('No problem available to submit to; finishing with report')
else:
    # 4) Submit code: post to /submissions
    print('\nSubmitting code for problem id:', problem_id)
    # Example minimal submission payload - may need to match backend expectations
    payload = {
        "problem_id": problem_id,
        "code": "print(\"hello\")",
        "language": "python"
    }
    resp = session.post(f"{BASE}/submissions", json=payload)
    results['submission_status'] = resp.status_code
    results['submission_body'] = resp.json() if resp.text else None
    print('Submission ->', resp.status_code, resp.text)

# 5) Fetch leaderboard
print('\nFetching leaderboard...')
resp = session.get(f"{BASE}/users/leaderboard")
results['leaderboard_status'] = resp.status_code
results['leaderboard_body'] = resp.json() if resp.text else None
print('Leaderboard ->', resp.status_code)

# 6) Simulate token expiry: make request with invalid token
print('\nSimulating expired token...')
bad_session = requests.Session()
bad_session.headers.update({'Authorization': 'Bearer THIS_IS_EXPIRED_OR_INVALID'})
resp = bad_session.get(f"{BASE}/problems")
results['expired_token_status'] = resp.status_code
results['expired_token_body'] = resp.text
print('Expired token request ->', resp.status_code, resp.text[:200])

# Print a concise report
print('\n--- E2E Results Summary ---')
for k, v in results.items():
    if isinstance(v, dict) or isinstance(v, list):
        print(f"{k}: (json) {str(v)[:200]}")
    else:
        print(f"{k}: {v}")

# Exit status
ok = resp.status_code == 401
print('\nExpired token expected 401 ->', ok)
if not ok:
    print('If the expired token simulation did not return 401, the backend may accept invalid tokens (or return 403).')

