import requests

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "e2euser@example.com"
PASSWORD = "e2epass123"


def main():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
    }
    resp = requests.post(url, json=payload)
    print("Login status:", resp.status_code)
    try:
        data = resp.json()
    except Exception:
        print("Login raw response:", resp.text)
        raise Exception("Login did not return JSON!")
    print("Login response:", data)
    if resp.status_code != 200 or "access_token" not in data:
        raise Exception("Login failed or token missing!")
    print("Access token:", data["access_token"])
    return data["access_token"]


if __name__ == "__main__":
    main()