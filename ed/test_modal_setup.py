import modal
from backend.modal_app import AvatarGenerator

app = modal.App("test-setup-hang")

@app.local_entrypoint()
def test_setup():
    gen = AvatarGenerator()
    print("Remote call started...")
    try:
        # Pinger pass to trigger setup natively and wait for output
        res = gen.generate.remote(prompt="test", init_image_b64=None)
        print("Done successfully!")
    except Exception as e:
        print(f"FAILED WITH ERR: {e}")
