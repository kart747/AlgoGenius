import requests

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "e2euser@example.com"
PASSWORD = "e2epass123"


def get_token():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
    }
    resp = requests.post(url, json=payload)
    if resp.ok and "access_token" in resp.json():
        return resp.json()["access_token"]
    print("Login failed:", resp.text)
    raise Exception("Could not get token!")


def main():
    token = get_token()
    url = f"{BASE_URL}/submissions"
    payload = {
        "problem_id": 1,
        "language": "python",
        "code": "a, b = map(int, input().split()); print(a+b)",
    }
    headers = {
        "Authorization": f"Bearer {token}",
    }
    resp = requests.post(url, json=payload, headers=headers)
    print("Submission status:", resp.status_code)
    try:
        data = resp.json()
    except Exception:
        print("Submission raw response:", resp.text)
        raise Exception("Submission did not return JSON!")
    print("Submission response:", data)
    if resp.status_code != 200 or "submission_id" not in data:
        raise Exception("Submission failed or missing submission_id!")


if __name__ == "__main__":
    main()