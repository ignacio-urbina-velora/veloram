
import requests

def verify_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)
    if response.status_code == 200:
        print(f"Token is valid! User: {response.json().get('name')}")
    else:
        print(f"Token is invalid or has issues. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    import os
    verify_token(os.environ.get("HF_TOKEN"))
