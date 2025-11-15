import requests

BASE_URL = "http://127.0.0.1:8000/api"

def main():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "testpass123"
    }
    resp = requests.post(url, json=payload)
    print("Status:", resp.status_code)
    print("Response:", resp.json())

if __name__ == "__main__":
    main()
