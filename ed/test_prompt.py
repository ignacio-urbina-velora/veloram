import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock app.config settings
class MockSettings:
    MODAL_ENDPOINT_URL = "test"
    MODAL_TOKEN_ID = "test"
    MODAL_TOKEN_SECRET = "test"

import app.config
app.config.settings = MockSettings()

from app.services.modal_service import build_avatar_prompt

def test():
    params = {
        "gender": "Mujer",
        "age": 25,
        "country": "España",
        "eyes": "verdes",
        "hair_color": "rubio",
        "hairstyle": "largo ondulado",
        "face_shape": "corazón",
        "skin_tone": "pálido",
        "makeup": "natural",
        "expression": "sonriente",
        "lighting": "luz de tarde",
        "extra": "pecas en las mejillas"
    }
    
    prompt = build_avatar_prompt(**params)
    print("--- GENERATED PROMPT ---")
    print(prompt)
    print("--- END ---")

    # Check for key elements
    assert "close-up portrait" in prompt
    assert "Spain" in prompt or "España" in prompt
    assert "head and neck only, no body visible" in prompt
    assert "pecas en las mejillas" in prompt
    print("\nTest passed!")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
