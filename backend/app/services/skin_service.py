from PIL import Image
import io
import base64
import numpy as np
from sklearn.cluster import KMeans

def extract_skin_color_from_b64(image_b64: str) -> str:
    """
    Extracts the dominant skin color from the center of the image using K-Means clustering.
    Returns a hex string like '#RRGGBB'.
    """
    try:
        if image_b64.startswith("data:"):
            image_b64 = image_b64.split(",", 1)[1]
        
        img_bytes = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Sample the center area of the image (where the face usually is)
        # We increase the sample slightly but keep it focused to avoid background
        w, h = img.size
        left = w * 0.35
        top = h * 0.25
        right = w * 0.65
        bottom = h * 0.55
        
        face_crop = img.crop((left, top, right, bottom))
        
        # Convert to numpy and reshape for clustering
        data = np.array(face_crop).reshape(-1, 3)
        
        # Use K-Means to find dominant colors (K=3 to separate skin from shadows/features)
        kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
        kmeans.fit(data)
        
        # Count pixels in each cluster
        counts = np.bincount(kmeans.labels_)
        
        # The skin tone is usually the most represented color in a face crop
        # but we also want to avoid pure black or pure white artifacts if they exist
        centers = kmeans.cluster_centers_
        
        # Sort by pixel count descending
        sorted_indices = np.argsort(counts)[::-1]
        
        # Take the largest cluster as skin tone (first pass)
        dominant_color = centers[sorted_indices[0]].astype(int)
        
        # Safety check: if the largest is very dark or very bright, try the second largest
        # (Very dark < 30, Very bright > 240)
        if (np.mean(dominant_color) < 40 or np.mean(dominant_color) > 230) and len(sorted_indices) > 1:
            dominant_color = centers[sorted_indices[1]].astype(int)

        return "#{:02x}{:02x}{:02x}".format(
            max(0, min(255, dominant_color[0])),
            max(0, min(255, dominant_color[1])),
            max(0, min(255, dominant_color[2]))
        )
    except Exception as e:
        print(f"Error extracting skin color with K-Means: {e}")
        return "#f1c27d" # Default Caucasian-ish skin tone
