import json
import struct
import os

GLB_PATH = "frontend/public/model/amala.glb"

def verify_glb():
    if not os.path.exists(GLB_PATH):
        print(f"Error: {GLB_PATH} not found.")
        return

    with open(GLB_PATH, "rb") as f:
        # GLB Header: magic (4), version (4), length (4)
        magic = f.read(4)
        if magic != b"glTF":
            print("Error: Not a valid GLB file.")
            return
        
        version = struct.unpack("<I", f.read(4))[0]
        length = struct.unpack("<I", f.read(4))[0]
        print(f"GLB Version: {version}")
        print(f"GLB Total Length: {length} bytes")

        # First Chunk: JSON
        chunk_length = struct.unpack("<I", f.read(4))[0]
        chunk_type = f.read(4)
        if chunk_type != b"JSON":
            print(f"Error: Expected JSON chunk, got {chunk_type}")
            return
        
        json_data = json.loads(f.read(chunk_length).decode("utf-8"))
        
        # Check targets (morph targets / shape keys)
        meshes = json_data.get("meshes", [])
        if not meshes:
            print("Error: No meshes found in GLB.")
            return
        
        print(f"Found {len(meshes)} meshes.")
        for i, mesh in enumerate(meshes):
            name = mesh.get("name", f"Mesh {i}")
            primitives = mesh.get("primitives", [])
            for j, prim in enumerate(primitives):
                targets = prim.get("targets", [])
                print(f"  - {name} Prim {j}: {len(targets)} Morph Targets")
                
        # Check vertex count (approx from accessors)
        accessors = json_data.get("accessors", [])
        total_verts = 0
        for mesh in meshes:
            for prim in mesh.get("primitives", []):
                pos_accessor_idx = prim.get("attributes", {}).get("POSITION")
                if pos_accessor_idx is not None:
                    count = accessors[pos_accessor_idx].get("count", 0)
                    total_verts += count
        
        print(f"Total Vertices: {total_verts}")
        
        if total_verts > 0 and any(len(m.get("primitives", [{}])[0].get("targets", [])) > 0 for m in meshes):
            print("\nRESULT: GLB looks healthy and functional (Geometry + Morphs found).")
        else:
            print("\nRESULT: GLB might be missing morph targets or geometry.")

if __name__ == "__main__":
    verify_glb()
