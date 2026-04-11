import asyncio
import httpx

EMAIL = "ignaciourbina.96@gmail.com"
PASSWORD = "password123"

async def test():
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Login
        print("[1] Login...")
        r = await client.post(
            "http://127.0.0.1:8000/api/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        print(f"    Status: {r.status_code}")
        if r.status_code != 200:
            print(f"    Error: {r.text[:300]}")
            return

        token = r.json().get("access_token")
        print(f"    Token: {token[:40]}...")

        # 2. Llamar generate-portrait con prompt largo
        print("\n[2] Llamando /api/avatars/generate-portrait...")
        prompt = "A professional 8k portrait of a 25 year old woman with medium brown hair, cinematic lighting, photorealistic, studio background"
        r2 = await client.post(
            "http://127.0.0.1:8000/api/avatars/generate-portrait",
            json={"prompt": prompt},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0
        )
        print(f"    Status: {r2.status_code}")
        if r2.status_code == 200:
            data = r2.json()
            b64 = data.get("image_b64", "")
            print(f"    image_b64 length: {len(b64)}")
            print(f"    credits_deducted: {data.get('credits_deducted')}")
            if len(b64) > 100:
                print("    ✅ IMAGEN GENERADA CORRECTAMENTE")
                # Guardar como archivo de prueba
                import base64
                img = base64.b64decode(b64)
                with open("test_portrait_result.jpg", "wb") as f:
                    f.write(img)
                print(f"    Guardada: test_portrait_result.jpg ({len(img)} bytes)")
            else:
                print(f"    ❌ image_b64 muy corta o vacía: '{b64[:100]}'")
        else:
            print(f"    ❌ Error: {r2.text[:600]}")

asyncio.run(test())
