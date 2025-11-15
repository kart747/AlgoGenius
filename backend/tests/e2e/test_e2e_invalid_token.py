import requests

BASE_URL = "http://127.0.0.1:8000/api"


def main():
    url = f"{BASE_URL}/submissions"
    payload = {
        "problem_id": 1,
        "language": "python",
        "code": "print('should fail')",
    }
    headers = {
        "Authorization": "Bearer invalidtoken",
    }
    resp = requests.post(url, json=payload, headers=headers)
    print("Invalid token status:", resp.status_code)
    print("Invalid token response:", resp.text)
    assert resp.status_code == 401, "Expected 401 Unauthorized for invalid token!"


if __name__ == "__main__":
    main()