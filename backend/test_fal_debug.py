"""Diagnóstico específico: por qué generate_image devuelve el placeholder."""
import asyncio
import httpx
import sys
import os

# Simular el entorno del backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAL_KEY = "007994d3-8bf4-4968-871d-3f4c1cc81e4a:3e85731d856b698eb004da49d22e0e7d"

async def test_fal_portrait_size():
    """Replicate exactly what generate_avatar_image does."""
    prompt = "A professional 8k portrait of a 25 year old woman with medium brown hair, cinematic lighting, photorealistic, studio background"
    
    print(f"[TEST] Llamando Fal.ai con dimensiones de portrait (896x1152)...")
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        # Esto es exactamente lo que hace generate_image con width=896, height=1152
        payload = {
            "prompt": prompt,
            "image_size": {"width": 896, "height": 1152},
            "num_inference_steps": 4,
            "enable_safety_checker": False
        }
        
        try:
            response = await client.post(
                "https://fal.run/fal-ai/flux/schnell",
                json=payload,
                headers={"Authorization": f"Key {FAL_KEY}"}
            )
            
            print(f"[TEST] Status: {response.status_code}")
            print(f"[TEST] Response: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                print(f"[TEST] images count: {len(images)}")
                if images:
                    url = images[0].get("url", "")
                    print(f"[TEST] URL: {url[:80]}")
                    
                    # Descargar
                    img_res = await client.get(url)
                    print(f"[TEST] Download status: {img_res.status_code}")
                    print(f"[TEST] Image size: {len(img_res.content)} bytes")
                    
                    if len(img_res.content) > 1000:
                        print("[TEST] ✅ Fal.ai portrait funciona perfectamente")
                        import base64
                        b64 = base64.b64encode(img_res.content).decode()
                        print(f"[TEST] b64 length: {len(b64)} chars")
                    else:
                        print("[TEST] ❌ Imagen muy pequeña")
            else:
                print(f"[TEST] ❌ Fal.ai error: {response.status_code}")
                print(f"[TEST] Body: {response.text}")
                
        except Exception as e:
            print(f"[TEST] ❌ Exception: {type(e).__name__}: {e}")
    
    print("\n[TEST] Aislando el bug: cargando modal_service.generate_avatar_image...")
    try:
        from app.services.modal_service import generate_avatar_image
        result = await generate_avatar_image(prompt)
        print(f"[TEST] Result length: {len(result)} chars")
        if len(result) < 500:
            print(f"[TEST] ❌ PLACEHOLDER DEVUELTO: '{result[:100]}'")
            print("[TEST] Esto confirma que algo falla DENTRO de generate_image()")
        else:
            print("[TEST] ✅ Imagen real generada desde modal_service")
    except Exception as e:
        print(f"[TEST] ❌ Exception en modal_service: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_fal_portrait_size())
