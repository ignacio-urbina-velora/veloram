import modal
import os

# Define the image with Ollama and Llama 3
# We'll use a base image and install requirements
image = (
    modal.Image.debian_slim()
    .pip_install("requests", "fastapi", "uvicorn")
    .run_commands(
        "curl -fsSL https://ollama.com/install.sh | sh",
    )
)

app = modal.App("reasoning-agent")

@app.cls(
    gpu="T4",  # The cheapest GPU on Modal ($0.59/hr)
    image=image,
    concurrency_limit=1,
    timeout=600,
)
class ReasoningAgent:
    @modal.enter()
    def start_ollama(self):
        import subprocess
        import time
        import requests

        # Start Ollama server in background
        subprocess.Popen(["ollama", "serve"])
        
        # Wait for server and download Llama 3
        max_retries = 20
        for i in range(max_retries):
            try:
                requests.get("http://localhost:11434")
                break
            except:
                time.sleep(1)
        
        print("Downloading Llama 3 8B...")
        subprocess.run(["ollama", "pull", "llama3"])
        print("Llama 3 is ready.")

    @modal.fastapi_endpoint(method="POST")
    def reason(self, req: dict):
        import requests
        
        prompt = req.get("prompt", "")
        system_prompt = req.get("system_prompt", "Eres un asistente experto en producción cinematográfica de IA. Tu objetivo es ayudar al usuario a crear guiones, shots y prompts visuales de alta calidad para videos de 15 minutos.")

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
        )
        
        res_json = response.json()
        return {"response": res_json.get("response", "Error en el razonamiento")}


# Deployment command: modal deploy reasoning_worker.py
