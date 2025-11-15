import requests

BASE_URL = "http://127.0.0.1:8000/api"


def main():
    url = f"{BASE_URL}/submissions"
    payload = {
        "problem_id": 1,
        "language": "python",
        "code": "print('should fail')",
    }
    resp = requests.post(url, json=payload)
    print("Missing token status:", resp.status_code)
    print("Missing token response:", resp.text)
    assert resp.status_code in (401, 403), "Expected 401/403 for missing token!"


if __name__ == "__main__":
    main()