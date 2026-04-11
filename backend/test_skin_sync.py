import asyncio
import base64
import os
from app.services.skin_service import extract_skin_color_from_b64

async def test_skin_extraction():
    # Use an existing debug image if available
    test_image = r"c:\Users\user\.gemini\antigravity\scratch\ai-video-platform\debug_output.png"
    if not os.path.exists(test_image):
        print(f"Test image {test_image} not found, skipping local test.")
        return

    with open(test_image, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    print(f"Testing skin extraction on {test_image}...")
    color = extract_skin_color_from_b64(img_b64)
    print(f"Extracted Color: {color}")
    
    # Expected color should be a hex string
    if color.startswith("#") and len(color) == 7:
        print("Success: Valid hex color extracted.")
    else:
        print(f"Failure: Invalid color format: {color}")

if __name__ == "__main__":
    asyncio.run(test_skin_extraction())
