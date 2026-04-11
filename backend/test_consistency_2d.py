import sys
import os
import asyncio
import base64
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.modal_service import build_avatar_prompt, generate_consistent_avatar, generate_flux_general

async def test_identity_consistency():
    print("=== PHASE 1: GENERATING ANCHOR IDENTITY ===")
    
    # Define a specific persona
    persona = {
        "gender": "Mujer",
        "age": 25,
        "country": "Brasil",
        "eyes": "miel",
        "hair_color": "castaño oscuro",
        "hairstyle": "ondulado largo",
        "skin_tone": "bronceado natural",
        "makeup": "sutil",
        "expression": "sonrisa ligera",
        "lighting": "luz dorada de atardecer",
        "extra": "textura de piel hiper-realista, pecas en la nariz"
    }
    
    anchor_prompt = build_avatar_prompt(**persona)
    print(f"Anchor Prompt: {anchor_prompt[:100]}...")
    
    try:
        # Step 1: Generate the Anchor Image (Identity Reference)
        # We use generate_flux_general directly for the first one to get a clean base
        anchor_b64 = await generate_flux_general(anchor_prompt, width=896, height=1152, seed=42)
        
        with open("test_anchor_identity.png", "wb") as f:
            f.write(base64.b64decode(anchor_b64))
        print("✅ Anchor identity saved to test_anchor_identity.png")
        
        print("\n=== PHASE 2: GENERATING CONSISTENT VARIANT ===")
        
        # Now change the context but keep the identity (same persona + new context)
        variant_persona = persona.copy()
        variant_persona["lighting"] = "luz de oficina de neón, sombras duras"
        variant_persona["expression"] = "sorpresa"
        variant_persona["extra"] = "usando gafas de lectura elegantes"
        
        variant_prompt = build_avatar_prompt(**variant_persona)
        print(f"Variant Prompt: {variant_prompt[:100]}...")
        
        # Step 2: Generate with IP-Adapter (Identity)
        variant_b64 = await generate_consistent_avatar(
            prompt=variant_prompt,
            anchor_image_b64=anchor_b64,
            face_weight=0.75, # Strong identity
            seed=42 # Link seed for even more consistency
        )
        
        with open("test_variant_consistent.png", "wb") as f:
            f.write(base64.b64decode(variant_b64))
        print("✅ Consistent variant saved to test_variant_consistent.png")
        
        print("\n=== SUCCESS: Check the two images for identity comparison ===")
        
    except Exception as e:
        print(f"❌ Error during consistency test: {e}")

if __name__ == "__main__":
    asyncio.run(test_identity_consistency())
