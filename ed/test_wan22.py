"""Test Wan 2.2 v3.0 — Improved prompts comparison."""

import asyncio
import sys
import os
import base64
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def test_profile(name, params, tier="professional"):
    from app.services.wan_service import build_wan22_prompt, generate_wan22_image

    prompt = build_wan22_prompt(**params)
    print(f"\n{'='*60}")
    print(f"🎯 Profile: {name} (tier={tier})")
    print(f"{'='*60}")
    print(f"📝 Prompt preview: {prompt[:120]}...")
    print(f"🚀 Generating...")

    image_b64 = await generate_wan22_image(prompt, tier=tier)

    if image_b64:
        img_bytes = base64.b64decode(image_b64)
        filename = f"wan22_v3_{name.lower().replace(' ', '_')}.png"
        Path(filename).write_bytes(img_bytes)
        print(f"✅ {filename} — {len(img_bytes):,} bytes")
        return True
    else:
        print(f"❌ FAILED")
        return False

async def main():
    profiles = {
        "latina_natural": {
            "gender": "woman",
            "age": 24,
            "ethnicity": "Colombian",
            "hair_color": "dark brown",
            "hairstyle": "long wavy",
            "expression": "relaxed subtle smile",
            "skin_tone": "warm olive",
            "eye_color": "dark brown",
            "eye_shape": "almond",
            "face_shape": "oval",
            "makeup": "minimal natural",
            "lighting": "soft golden hour window",
        },
        "nordic_editorial": {
            "gender": "woman",
            "age": 28,
            "ethnicity": "Scandinavian",
            "hair_color": "platinum blonde",
            "hairstyle": "short textured bob",
            "expression": "confident direct gaze",
            "skin_tone": "fair with light freckles",
            "eye_color": "ice blue",
            "eye_shape": "round",
            "face_shape": "angular",
            "makeup": "soft smoky eye",
            "lighting": "overcast diffused daylight",
        },
        "urban_male": {
            "gender": "man",
            "age": 30,
            "ethnicity": "African American",
            "hair_color": "black",
            "hairstyle": "short textured fade",
            "expression": "calm thoughtful",
            "skin_tone": "deep rich brown",
            "eye_color": "dark brown",
            "eye_shape": "deep-set",
            "face_shape": "strong jawline",
            "makeup": "none",
            "lighting": "dramatic side window light",
        },
    }

    results = {}
    for name, params in profiles.items():
        results[name] = await test_profile(name, params)

    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")

if __name__ == "__main__":
    asyncio.run(main())
