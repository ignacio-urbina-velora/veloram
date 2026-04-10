"""
Modal deployment script for Llama-3-8B-Instruct with vLLM.
Deploy this using: `modal deploy backend/app/agents/director/modal_worker.py`
"""

import modal
import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# 1. Define the Modal App
app = modal.App("director-brain")

# 2. Volume for model caching to avoid repeated downloads
model_volume = modal.Volume.from_name("llm-weights", create_if_missing=True)
CACHE_DIR = "/cache"

# 3. Image setup with vLLM
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "vllm",
        "fastapi[standard]",
        "huggingface_hub"
    )
)

# Auth setup
# We use the modal secret 'hf-token' which should contain HF_TOKEN
# ...

def check_auth(request: Request):
    # Use the tokens from settings or hardcoded for this private worker
    auth_id = request.headers.get("x-modal-token-id")
    auth_secret = request.headers.get("x-modal-token-secret")
    # Using the standard tokens from the user's setup
    if auth_id != "wk-zgKLgaMEjSbsJJfCnoGZm4" or auth_secret != "ws-fKNahBbuJRC4OXpd8pnrkO":
        raise HTTPException(status_code=401, detail="Unauthorized")

# 4. In-Process/Class based LLM Service
@app.cls(
    gpu="L4", # Extremely cost-efficient (24GB VRAM)
    scaledown_window=300, 
    image=image, 
    volumes={CACHE_DIR: model_volume},
    secrets=[modal.Secret.from_name("hf-token")]
)
class DirectorWorker:
    @modal.enter()
    def setup(self):
        from vllm import LLM as VLLM_Engine
        from vllm import SamplingParams
        print(f"Loading Llama-3-8B-Instruct from HuggingFace to {CACHE_DIR}...")
        
        self.llm = VLLM_Engine(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            download_dir=CACHE_DIR,
            max_model_len=4096,
            enforce_eager=True # Saves memory for L4
        )
        print("Model Loaded and Ready with vLLM.")

    @modal.method()
    def generate(self, prompt: str, system_prompt: str = ""):
        from vllm import SamplingParams
        
        sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=2048,
        )
        
        # Construct message format for Llama 3
        # No safety filters injected!
        full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        print("Starting inference...")
        outputs = self.llm.generate([full_prompt], sampling_params)
        generated_text = outputs[0].outputs[0].text
        
        return generated_text

# 5. Fast API Endpoint
@app.function(image=image, timeout=600)
@modal.fastapi_endpoint(method="POST")
async def generate_response(request: Request):
    """
    Main Endpoint for Director AI Brain inference.
    """
    check_auth(request)
    body = await request.json()
    
    prompt = body.get("prompt")
    system_prompt = body.get("system_prompt", "Eres un Director experto.")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    try:
        worker = DirectorWorker()
        response_text = worker.generate.remote(
            prompt,
            system_prompt=system_prompt
        )
        return JSONResponse({"response": response_text})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
