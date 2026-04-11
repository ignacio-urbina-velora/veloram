
from huggingface_hub import HfApi, login
import os

token = os.environ.get("HF_TOKEN") # Replaced hardcoded token for security

def verify_token():
    print(f"Testing token: {token[:10]}...")
    try:
        login(token=token)
        api = HfApi()
        user_info = api.whoami()
        print(f"Token is valid! Logged in as: {user_info['name']}")
        
        # Check access to black-forest-labs/FLUX.1-schnell
        model_id = "black-forest-labs/FLUX.1-schnell"
        print(f"Checking access to {model_id}...")
        try:
            api.model_info(model_id)
            print(f"SUCCESS: Token has access to {model_id}")
        except Exception as e:
            print(f"FAILURE: No access to {model_id}. Error: {e}")
            
    except Exception as e:
        print(f"Token invalid or login failed: {e}")

if __name__ == "__main__":
    verify_token()
