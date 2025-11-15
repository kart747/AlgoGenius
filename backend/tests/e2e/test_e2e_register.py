import requests

BASE_URL = "http://127.0.0.1:8000/api"
USERNAME = "e2euser"
EMAIL = "e2euser@example.com"
PASSWORD = "e2epass123"


def main():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD,
    }
    resp = requests.post(url, json=payload)
    print("Register status:", resp.status_code)
    print("Register response:", resp.json())
    if resp.status_code not in (200, 201):
        raise Exception("Registration failed!")


if __name__ == "__main__":
    main()