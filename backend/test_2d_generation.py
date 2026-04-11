"""Test rápido del endpoint /api/avatars/generate-portrait sin autenticación.
Llama directamente Fal.ai para verificar que la clave funciona."""
import asyncio
import httpx
import json
import os
import sys

# Simular la configuración
FAL_KEY = "007994d3-8bf4-4968-871d-3f4c1cc81e4a:3e85731d856b698eb004da49d22e0e7d"

async def test_fal_direct():
    """Prueba directa a Fal.ai sin pasar por el backend."""
    prompt = "candid photo of a 25 year old woman, brown hair, natural lighting, portrait"
    print(f"\n[TEST] Llamando Fal.ai directamente...")
    print(f"[TEST] Prompt: {prompt[:60]}...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://fal.run/fal-ai/flux/schnell",
                json={
                    "prompt": prompt,
                    "image_size": {"width": 512, "height": 640},
                    "num_inference_steps": 4,
                    "enable_safety_checker": False
                },
                headers={"Authorization": f"Key {FAL_KEY}"}
            )
            
            print(f"[TEST] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if images:
                    url = images[0].get("url", "")
                    print(f"[TEST] ✅ ÉXITO — URL imagen: {url[:80]}...")
                    
                    # Descargar la imagen
                    img_res = await client.get(url)
                    if img_res.status_code == 200:
                        size = len(img_res.content)
                        print(f"[TEST] ✅ Imagen descargada: {size} bytes")
                        # Guardar como archivo de prueba
                        with open("test_output.jpg", "wb") as f:
                            f.write(img_res.content)
                        print("[TEST] ✅ Guardada como test_output.jpg")
                    else:
                        print(f"[TEST] ❌ Error descargando imagen: {img_res.status_code}")
                else:
                    print(f"[TEST] ❌ Sin imágenes en respuesta: {data}")
            else:
                print(f"[TEST] ❌ Error Fal.ai: {response.status_code}")
                print(f"[TEST] Detalle: {response.text[:500]}")
                
        except Exception as e:
            print(f"[TEST] ❌ Excepción: {type(e).__name__}: {e}")

async def test_backend_endpoint():
    """Prueba el backend directamente con token de login."""
    print(f"\n[TEST] Probando login en backend...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Intentar login
        try:
            login_res = await client.post(
                "http://127.0.0.1:8000/api/auth/login",
                json={"email": "admin@velora.ai", "password": "admin123"}
            )
            print(f"[TEST] Login status: {login_res.status_code}")
            
            if login_res.status_code == 200:
                token = login_res.json().get("access_token")
                print(f"[TEST] ✅ Token obtenido: {token[:30]}...")
                
                # Llamar generate-portrait
                print(f"\n[TEST] Llamando /api/avatars/generate-portrait...")
                gen_res = await client.post(
                    "http://127.0.0.1:8000/api/avatars/generate-portrait",
                    json={
                        "prompt": "A professional 8k portrait of a 25 year old woman with brown hair, cinematic lighting"
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"[TEST] Generate status: {gen_res.status_code}")
                
                if gen_res.status_code == 200:
                    data = gen_res.json()
                    b64 = data.get("image_b64", "")
                    print(f"[TEST] ✅ imagen_b64 length: {len(b64)}")
                    print(f"[TEST] Prompt usado: {data.get('prompt_used', '')[:80]}...")
                else:
                    print(f"[TEST] ❌ Error: {gen_res.text[:500]}")
            else:
                print(f"[TEST] ❌ Login fallido: {login_res.text[:200]}")
        except Exception as e:
            print(f"[TEST] ❌ Backend no disponible: {e}")

if __name__ == "__main__":
    asyncio.run(test_fal_direct())
    asyncio.run(test_backend_endpoint())
