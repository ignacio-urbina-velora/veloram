import asyncio
import httpx
import base64
from io import BytesIO
from PIL import Image

API_URL = "http://localhost:8000"

def create_dummy_image():
    # Create a 512x512 solid color image
    img = Image.new('RGB', (512, 512), color=(200, 200, 200))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

async def test_avatar_flow():
    print("starting test...")
    async with httpx.AsyncClient() as client:
        # 1. Login
        login_data = {
            "email": "ignaciourbina.96@gmail.com",
            "password": "campeon19"
        }
        resp = await client.post(f"{API_URL}/auth/login", json=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")

        # 2. Check Me
        resp = await client.get(f"{API_URL}/auth/me", headers=headers)
        user = resp.json()
        print(f"✅ User fetch: {user['email']}, Credits: {user['credits']}")

        # 3. Generate Avatar
        print("⏳ Generating avatar via Modal (this takes ~15-20s)...")
        b64_img = create_dummy_image()
        generate_payload = {
            "gender": "Mujer",
            "age": 25,
            "height": 165,
            "weight": 55,
            "build": "Normal",
            "country": "España",
            "eyes": "Marrón",
            "hairstyle": "Largo",
            "hair_color": "Castaño",
            "extra_prompt": "foto muy realista y detallada",
            "base_image_b64": b64_img,
            "strength": 0.8
        }
        
        # Setting a large timeout for Modal
        resp = await client.post(f"{API_URL}/avatars/generate", json=generate_payload, headers=headers, timeout=60.0)
        
        if resp.status_code != 200:
            print(f"❌ Generate failed: {resp.status_code} - {resp.text}")
            return
            
        data = resp.json()
        print(f"✅ Avatar generated! Credits deducted: {data['credits_deducted']}")
        new_b64 = data['image_b64']
        
        # 4. Save Avatar
        print("⏳ Saving avatar...")
        save_payload = {
            "name": "Avatar Test Workflow",
            "image_b64": new_b64,
            "morphs": {"gender": 0.5, "muscle": 0.5},
            "styles": {}
        }
        resp = await client.post(f"{API_URL}/avatars/save", json=save_payload, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Save failed: {resp.status_code} - {resp.text}")
            return
            
        save_data = resp.json()
        print(f"✅ Avatar saved with ID: {save_data['id']}")
        
        # 5. Check director plan to make sure workflow connects
        print("⏳ Testing director bot plan generation...")
        plan_req = {
            "idea": "Haz un video de 3 minutos de terror en un bosque",
            "target_duration_sec": 180,
            "style": "cinematic"
        }
        resp = await client.post(f"{API_URL}/api/director/plan", json=plan_req, headers=headers, timeout=30.0)
        if resp.status_code == 200:
            print("✅ Director plan successful!")
            print(resp.json())
        else:
            print(f"❌ Director plan failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_avatar_flow())
