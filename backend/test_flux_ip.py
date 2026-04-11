import modal

# Use the same image as the app to avoid redownloading
app = modal.App("test-flux-ip")
image = (
    modal.Image.debian_slim()
    .pip_install("torch", "diffusers>=0.30.2", "transformers", "accelerate")
)

@app.function(image=image)
def test_ip_adapter():
    try:
        from diffusers import FluxPipeline
        import inspect
        
        has_load = hasattr(FluxPipeline, 'load_ip_adapter')
        
        # Enumerate signature arguments of FluxPipeline.__call__ to check ip_adapter_image
        call_sig = inspect.signature(FluxPipeline.__call__)
        has_ip_arg = 'ip_adapter_image' in call_sig.parameters

        print("========================")
        print(f"has_load_ip_adapter: {has_load}")
        print(f"has_ip_adapter_image_arg: {has_ip_arg}")
        print("========================")
        return has_load, has_ip_arg
    except Exception as e:
        print(f"Error: {e}")
        return False, False

@app.local_entrypoint()
def main():
    test_ip_adapter.remote()
