
import httpx
import asyncio
import os

async def test_api_portrait():
    # Use the local backend since I just updated it
    api_url = "http://localhost:8000/api/avatars/generate-portrait"
    
    # We need a valid token to bypass Depends(get_current_user)
    # However, for a quick test of the logic, I'll bypass AUTH locally if I could,
    # but the easiest way is to use a real token from the DB or login.
    # Since I don't have a token handy, I'll try to reach the endpoint 
    # and expect a 401 if it's working but unauthorized.
    
    # Wait, I'll check my backend logs when I trigger this.
    
    payload = {
        "prompt": "Test portrait of a young woman"
    }
    
    print(f"Calling backend API: {api_url}")
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # First attempt without token to check if reachable
            response = await client.post(api_url, json=payload)
            print(f"Status Code (without token): {response.status_code}")
            if response.status_code == 401:
                print("Reachable! 401 Unauthorized as expected.")
            else:
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_portrait())
