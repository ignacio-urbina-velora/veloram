import requests

def test_login(email, password):
    url = "http://localhost:8000/auth/login"
    payload = {"email": email, "password": password}
    resp = requests.post(url, json=payload)
    print(f"Testing {email}:")
    print(f"Status: {resp.status_code}")
    print(f"Detail: {resp.json().get('detail')}")
    print("-" * 20)

if __name__ == "__main__":
    # 1. Non-existent email
    test_login("nonexistent@void.com", "any_password")
    
    # 2. Existing email, wrong password
    test_login("ignacio@test.com", "wrong_pass")
