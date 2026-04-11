import requests
import base64
import os
import json

# Replace with your actual Modal endpoint after deployment
MODAL_URL = "https://ignaciourbinakonecta--avatar-generate-fastapi-app.modal.run"


# Auth tokens (should match modal_app.py defaults or secrets)
AUTH_HEADERS = {
    "x-modal-token-id": "wk-zgKLgaMEjSbsJJfCnoGZm4",
    "x-modal-token-secret": "ws-fKNahBbuJRC4OXpd8pnrkO",
    "Content-Type": "application/json"
}

def test_refinement():
    # Load a sample image to act as the 3D snapshot
    # For testing, we'll just use a blank or existing image if available, 
    # or just send a dummy base64 if we just want to test connectivity.
    
    # Let's try to find a png in the workspace to use as a test
    test_image_path = "debug_output.png"
    if not os.path.exists(test_image_path):
        print(f"Test image {test_image_path} not found. Using dummy.")
        init_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    else:
        with open(test_image_path, "rb") as f:
            init_image_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "prompt": "A professional hyper-realistic portrait of a man, cinematic lighting, 8k, highly detailed skin pores",
        "init_image_b64": init_image_b64,
        "width": 512,
        "height": 512,
        "steps": 20,
        "controlnet_scale": 0.8
    }

    print(f"Sending request to {MODAL_URL}...")
    try:
        response = requests.post(MODAL_URL, headers=AUTH_HEADERS, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        
        if "image_b64" in result:
            output_path = "refined_test_output.png"
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(result["image_b64"]))
            print(f"Success! Refined image saved to {output_path}")
        else:
            print("Error: No image_b64 in response")
            print(result)
            
    except Exception as e:
        print(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    test_refinement()
