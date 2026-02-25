import requests

BASE_URL = "http://127.0.0.1:8000"

def test_auth_flow():
    # 1. Create a user
    print("Creating user...")
    resp = requests.post(
        f"{BASE_URL}/users/test-user",
        params={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    print(resp.status_code, resp.json())

    # 2. Login (OAuth2 password flow = form data, not JSON)
    print("\nLogging in...")
    resp = requests.post(
        f"{BASE_URL}/users/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    login_data = resp.json()
    print(resp.status_code, login_data)

    if "access_token" not in login_data:
        print("Login failed!")
        return

    token = login_data["access_token"]

    # 3. Access protected route
    print("\nAccessing protected /users/me...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    test_auth_flow()
