import requests

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    resp = requests.post(url, json=payload)
    if resp.ok:
        return resp.json().get("access_token")
    print("Login failed:", resp.text)
    return None

def main():
    token = get_token()
    if not token:
        print("Could not get token, aborting.")
        return

    url = f"{BASE_URL}/submissions"
    payload = {
        "problem_id": 1,
        "language": "python",
        "code": "a, b = map(int, input().split()); print(a+b)"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.post(url, json=payload, headers=headers)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)

if __name__ == "__main__":
    main()
