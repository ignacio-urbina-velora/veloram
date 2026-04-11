import modal
import os

app = modal.App("cleanup-volume")
model_volume = modal.Volume.from_name("flux-dev-weights")

@app.function(volumes={"/cache": model_volume})
def cleanup():
    print("Checking for corrupted models in /cache...")
    for root, dirs, files in os.walk("/cache"):
        for file in files:
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            # Generic check: files smaller than a few MBs that should be large
            # Or specifically look for suspicious files
            if file.endswith((".pt", ".bin", ".safetensors")) and size < 1024 * 1024:
                print(f"Deleting potentially corrupted file: {path} ({size} bytes)")
                os.remove(path)
            elif file == "4x-UltraSharp.pth" and size < 100 * 1024: # UltraSharp is usually ~60MB
                print(f"Deleting corrupted upscaler: {path}")
                os.remove(path)
    
    # Also clean ultralytics default download location if it exists
    yolo_local = "face_yolov8n.pt"
    if os.path.exists(yolo_local):
        os.remove(yolo_local)
        print("Removed local YOLO file.")

@app.local_entrypoint()
def main():
    cleanup.remote()
    print("Cleanup complete.")
