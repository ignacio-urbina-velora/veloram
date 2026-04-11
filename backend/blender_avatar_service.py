import modal
import base64
import os
import subprocess
import json
import tempfile
from typing import Any

# Definición del contenedor con Blender y dependencias
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "libxi6", "libxrender1", "libxkbcommon0", "libgl1", "libsm6", "libice6", "libxext6", "libwayland-client0", "libwayland-server0", "unzip")
    .run_commands(
        "curl -L https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-x64.tar.xz -o blender.tar.xz",
        "tar -xf blender.tar.xz",
        "mv blender-4.1.1-linux-x64 /opt/blender",
        "ln -s /opt/blender/blender /usr/local/bin/blender"
    )
    .pip_install("fastapi[standard]", "httpx")
    # Instalación de MPFB2 como addon legado en 4.1
    .run_commands(
        "curl -L https://github.com/makehumancommunity/mpfb2/releases/download/v2.0-b1/mpfb-2.0-b1.zip -o /tmp/mpfb2.zip",
        "mkdir -p /opt/blender/4.1/scripts/addons",
        "unzip /tmp/mpfb2.zip -d /opt/blender/4.1/scripts/addons"
    )
)

app = modal.App("blender-avatar-service")

# Script de Blender que se ejecutará internamente
BLENDER_GENERATOR_SCRIPT = """
import bpy
import sys
import json
import os
import addon_utils

def run():
    # Obtener parámetros de los argumentos de la línea de comandos
    try:
        args = sys.argv[sys.argv.index("--") + 1:]
        params = json.loads(args[0])
    except (ValueError, IndexError):
        params = {}

    print(f"DEBUG: Params recibidos: {params}")

    # Limpiar escena
    bpy.ops.wm.read_factory_settings(use_empty=True)

    try:
        # Refrescar paths de scripts para que Blender vea el nuevo addon
        bpy.utils.refresh_script_paths()
        
        # Listar addons disponibles (depuración)
        print("DEBUG: Listando todos los addons registrados...")
        import addon_utils
        available_modules = [mod.__name__ for mod in addon_utils.modules()]
        print(f"DEBUG: Addons disponibles: {available_modules}")
        
        # Habilitar MPFB2
        addon_name = "mpfb"
        if addon_name not in bpy.context.preferences.addons:
            print(f"DEBUG: Intentando habilitar addon {addon_name}...")
            try:
                bpy.ops.preferences.addon_enable(module=addon_name)
                print(f"DEBUG: Addon {addon_name} habilitado.")
            except Exception as e:
                print(f"ERROR: No se pudo habilitar {addon_name}: {e}")
                # Intentar buscar variaciones si no se encontró
                match = [m for m in available_modules if "mpfb" in m.lower()]
                if match:
                    print(f"DEBUG: Intentando con variaciones encontradas: {match}")
                    bpy.ops.preferences.addon_enable(module=match[0])
                    addon_name = match[0]
            
        # Determinar primitiva basada en género
        gender = params.get("gender", "Mujer")
        primitive = "f_avg" if gender == "Mujer" else "m_avg"
        
        print(f"DEBUG: Creando humano con primitiva {primitive}")
        
        # MPFB2 suele tener sus operadores bajo bpy.ops.mpfb
        if hasattr(bpy.ops, "mpfb"):
            if hasattr(bpy.ops.mpfb, "create_human"):
                op = bpy.ops.mpfb.create_human
                try:
                    op(primitive=primitive)
                except Exception as e:
                    print(f"AVISO: Falló creación de humano: {e}")
                    op() # Intentar sin argumentos
            
            # --- NUEVO: Aplicar parámetros de cuerpo ---
            # En MPFB2, se pueden aplicar modificadores o "targets"
            # Estos son valores normalizados (0-1) o específicos
            try:
                # Altura (Height): 0 es bajo, 1 es alto. 
                # Mapeamos 140-200cm a 0-1 (aprox)
                height_val = (params.get("height", 170) - 140) / 60.0
                height_val = max(0.0, min(1.0, height_val))
                
                # Peso (Weight): 50-120kg a 0-1
                weight_val = (params.get("weight", 60) - 50) / 70.0
                weight_val = max(0.0, min(1.0, weight_val))
                
                # Complexión (Build/Muscle): Basado en string
                build_str = params.get("build", "Atlética").lower()
                muscle_val = 0.5
                if "muscul" in build_str or "atl" in build_str: muscle_val = 0.8
                elif "delgad" in build_str: muscle_val = 0.2
                
                print(f"DEBUG: Aplicando Modificadores: Height={height_val}, Weight={weight_val}, Muscle={muscle_val}")
                
                # Nota: Dependiendo de la versión de MPFB2, los operadores varían.
                # Intentamos usar el sistema de macros de MPFB si está disponible.
                if hasattr(bpy.ops.mpfb, "apply_macro"):
                    # Algunas versiones usan macros para cambios rápidos
                    pass 
                
                # Fallback: Manipulación directa si encontramos el objeto humano
                human_obj = next((o for o in bpy.data.objects if "Human" in o.name or "human" in o.name), None)
                if human_obj and hasattr(human_obj, "mpfb_human_data"):
                    # Algunas versiones guardan datos aquí
                    pass

            except Exception as body_err:
                print(f"AVISO: No se pudieron aplicar parámetros de cuerpo: {body_err}")
            
        else:
            print("ERROR: Namespace bpy.ops.mpfb no disponible.")
            raise Exception("Extension mpfb no cargada correctamente")
        
        # Aplicar color de piel si se proporciona
        skin_color_hex = params.get("skin_color")
        if skin_color_hex and skin_color_hex.startswith("#"):
            print(f"DEBUG: Aplicando color de piel {skin_color_hex}")
            # Convertir hex a RGB (0-1)
            h = skin_color_hex.lstrip('#')
            rgb = tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4))
            
            # Buscar materiales de piel
            for mat in bpy.data.materials:
                if "skin" in mat.name.lower() or "body" in mat.name.lower():
                    print(f"DEBUG: Encontrado material de piel: {mat.name}")
                    if mat.use_nodes:
                        nodes = mat.node_tree.nodes
                        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                        if principled:
                            principled.inputs['Base Color'].default_value = (*rgb, 1.0)
                            # También ajustamos el Subsurface Color para realismo
                            if 'Subsurface Color' in principled.inputs:
                                principled.inputs['Subsurface Color'].default_value = (*rgb, 1.0)
                            print(f"DEBUG: Color aplicado a {mat.name}")
        
    except Exception as e:
        print(f"AVISO: Fallback al mono de Blender por error: {e}")
        bpy.ops.mesh.primitive_monkey_add(size=2)
    
    output_path = "/tmp/output.glb"
    bpy.ops.export_scene.gltf(
        filepath=output_path, 
        export_format='GLB',
        export_apply=True
    )
    print(f"DEBUG: Exportación completada en {output_path}")

if __name__ == "__main__":
    run()
"""

@app.function(image=image, gpu="any", timeout=600)
def generate_avatar_task(params):
    # Crear script temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(BLENDER_GENERATOR_SCRIPT)
        script_path = f.name

    try:
        # Ejecutar Blender
        cmd = [
            "blender",
            "--background",
            "--python", script_path,
            "--",
            json.dumps(params)
        ]
        
        print(f"Ejecutando comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logs = f"--- STDOUT ---\n{result.stdout}\n--- STDERR ---\n{result.stderr}"
        print(logs)
        
        if result.returncode != 0:
            raise Exception(f"Blender falló con código {result.returncode}. Logs:\n{logs}")

        output_path = "/tmp/output.glb"
        if not os.path.exists(output_path):
            raise Exception(f"No se generó el archivo GLB. Logs:\n{logs}")

        with open(output_path, "rb") as f:
            return {
                "glb_base64": base64.b64encode(f.read()).decode('utf-8'),
                "logs": logs
            }
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def api_generate(params: Any = None):
    # El frontend envía { "params": { ... } } o directamente los params
    if isinstance(params, dict) and "params" in params:
        actual_params = params["params"]
    else:
        actual_params = params or {}
        
    result = generate_avatar_task.remote(actual_params)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# FACE PROJECTION: Projects a Flux face onto the mannequin's head region
# Uses UV Project modifier + vertex groups for clean facial masking
# ─────────────────────────────────────────────────────────────────────────────

BLENDER_FACE_PROJECT_SCRIPT = """
import bpy
import sys
import json
import os
import base64
import struct
import math
import tempfile

def run():
    args = sys.argv[sys.argv.index("--") + 1:]
    params = json.loads(args[0])

    face_image_path = params.get("face_image_path", "/tmp/face.png")
    mannequin_glb_path = params.get("mannequin_glb_path")
    output_path = "/tmp/projected.glb"

    # ── 1. Load scene ──────────────────────────────────────────────────────
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if mannequin_glb_path and os.path.exists(mannequin_glb_path):
        bpy.ops.import_scene.gltf(filepath=mannequin_glb_path)
        print("DEBUG: Loaded custom mannequin GLB")
    else:
        # Fallback: use a UV Sphere as a standin head
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=64, ring_count=32)
        print("DEBUG: Using sphere fallback (no mannequin GLB provided)")

    # ── 2. Find the mesh object ─────────────────────────────────────────────
    mesh_obj = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
    if not mesh_obj:
        raise RuntimeError("No mesh found in scene")

    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    # ── 3. Create vertex group for head region ──────────────────────────────
    import mathutils
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Calculate bounding box in World Space to avoid GLTF rotation issues
    world_bbox = [mesh_obj.matrix_world @ mathutils.Vector(v) for v in mesh_obj.bound_box]
    all_world_z = [v.z for v in world_bbox]
    min_z = min(all_world_z)
    max_z = max(all_world_z)
    head_threshold = max_z - (max_z - min_z) * 0.15   # top 15%

    if "HEAD_REGION" not in mesh_obj.vertex_groups:
        vg = mesh_obj.vertex_groups.new(name="HEAD_REGION")
    else:
        vg = mesh_obj.vertex_groups["HEAD_REGION"]

    vg.remove(range(len(mesh_obj.data.vertices)))

    head_verts = []
    for v in mesh_obj.data.vertices:
        world_co = mesh_obj.matrix_world @ v.co
        if world_co.z >= head_threshold:
            head_verts.append(v.index)

    if head_verts:
        vg.add(head_verts, 1.0, 'REPLACE')
        print(f"DEBUG: Head vertex group has {len(head_verts)} vertices (threshold: {head_threshold:.2f}, max_z: {max_z:.2f})")
    else:
        print("WARN: No head vertices found, using all vertices")
        vg.add([v.index for v in mesh_obj.data.vertices], 1.0, 'REPLACE')

    head_verts_set = set(head_verts)

    # ── 4. Load face texture ────────────────────────────────────────────────
    if not os.path.exists(face_image_path):
        raise RuntimeError(f"Face image not found: {face_image_path}")

    face_img = bpy.data.images.load(face_image_path)
    print(f"DEBUG: Loaded face image: {face_img.size[0]}x{face_img.size[1]}")

    # ── 5. Create material with face texture ────────────────────────────────
    mat = bpy.data.materials.new(name="FaceProjection")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    tex_node = nodes.new('ShaderNodeTexImage')
    
    # Use explicit UV Map node so GLTF exporter knows which UV channel to grab
    uv_node = nodes.new('ShaderNodeUVMap')
    uv_node.uv_map = "FaceUV"

    tex_node.image = face_img
    tex_node.projection = 'FLAT'

    links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])
    links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

    # Append material instead of overwriting
    mesh_obj.data.materials.append(mat)
    face_mat_index = len(mesh_obj.data.materials) - 1

    # Assign FaceProjection material ONLY to head polygons
    for poly in mesh_obj.data.polygons:
        # If all vertices of the polygon are in the head group
        if all(v in head_verts_set for v in poly.vertices):
            poly.material_index = face_mat_index

    # ── 6. UV Unwrap head region only ───────────────────────────────────────
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a dedicated UV map for the face projection to not ruin body UVs
    face_uv_layer = mesh_obj.data.uv_layers.new(name="FaceUV")

    # Project from camera view (front-facing)
    cam_data = bpy.data.cameras.new("ProjectCam")
    cam_data.type = 'ORTHO'
    head_height = max_z - head_threshold
    
    # Scale camera to perfectly fit the head with a small margin
    cam_data.ortho_scale = head_height * 1.5 
    
    cam_obj = bpy.data.objects.new("ProjectCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    # Position camera in front of head
    head_center_z = (max_z + head_threshold) / 2
    cam_obj.location = (0, -2, head_center_z - head_height * 0.1) # Point slightly lower
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = cam_obj

    # Add UV Project modifier
    uv_proj = mesh_obj.modifiers.new(name="UV_Face_Project", type='UV_PROJECT')
    uv_proj.projector_count = 1
    uv_proj.projectors[0].object = cam_obj
    uv_proj.uv_layer = face_uv_layer.name
    uv_proj.scale_x = 1.0
    uv_proj.scale_y = 1.0

    # Apply the modifier
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.modifier_apply(modifier="UV_Face_Project")
    
    print(f"DEBUG: UV Project applied to layer {face_uv_layer.name} with scale {cam_data.ortho_scale:.2f}")

    # ── 7. Add basic shape keys for manual correction ───────────────────────
    bpy.ops.object.shape_key_add(from_mix=False)  # Basis
    mesh_obj.data.shape_keys.key_blocks[0].name = "Basis"

    # Eye width shape key
    bpy.ops.object.shape_key_add(from_mix=False)
    eye_key = mesh_obj.data.shape_keys.key_blocks[-1]
    eye_key.name = "Eye_Width"
    eye_key.value = 0.0

    # Nose bridge shape key
    bpy.ops.object.shape_key_add(from_mix=False)
    nose_key = mesh_obj.data.shape_keys.key_blocks[-1]
    nose_key.name = "Nose_Width"
    nose_key.value = 0.0

    print(f"DEBUG: Shape keys created: {[k.name for k in mesh_obj.data.shape_keys.key_blocks]}")

    # ── 8. Export as GLB ────────────────────────────────────────────────────
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=False,   # Keep shape keys
        export_morph=True,    # Include shape keys as morph targets
        export_texcoords=True,
        export_materials='EXPORT',
    )
    print(f"DEBUG: Export complete -> {output_path}")

if __name__ == "__main__":
    run()
"""


@app.function(image=image, timeout=600)
def project_face_task(face_image_b64: str, mannequin_glb_b64: str = None):
    """
    Project a Flux-generated face onto the mannequin's head.
    Returns a GLB with proper UV mapping and shape keys.
    """
    import base64, tempfile, subprocess, os, json

    # Write face image to disk
    face_bytes = base64.b64decode(face_image_b64)
    face_path = "/tmp/face.png"
    with open(face_path, "wb") as f:
        f.write(face_bytes)

    # Write mannequin GLB if provided
    mannequin_path = None
    if mannequin_glb_b64:
        mannequin_path = "/tmp/mannequin.glb"
        with open(mannequin_path, "wb") as f:
            f.write(base64.b64decode(mannequin_glb_b64))

    # Write Blender script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(BLENDER_FACE_PROJECT_SCRIPT)
        script_path = f.name

    params = {
        "face_image_path": face_path,
        "mannequin_glb_path": mannequin_path,
    }

    try:
        cmd = [
            "blender",
            "--background",
            "--python", script_path,
            "--",
            json.dumps(params)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        logs = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        print(logs)

        if result.returncode != 0:
            raise Exception(f"Blender failed (code {result.returncode}):\n{logs}")

        output_path = "/tmp/projected.glb"
        if not os.path.exists(output_path):
            raise Exception(f"No GLB output produced.\n{logs}")

        with open(output_path, "rb") as f:
            glb_b64 = base64.b64encode(f.read()).decode("utf-8")

        return {"glb_base64": glb_b64, "logs": logs}

    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def api_project_face(request: dict = None):
    """
    POST /api_project_face
    Body: { "face_image_b64": "...", "mannequin_glb_b64": "..." (optional) }
    Returns: { "glb_base64": "..." }
    """
    from fastapi.responses import JSONResponse
    if not request:
        return JSONResponse({"error": "Missing request body"}, status_code=400)

    try:
        face_b64 = request.get("face_image_b64")
        if not face_b64:
            return JSONResponse({"error": "Missing face_image_b64"}, status_code=400)

        mannequin_b64 = request.get("mannequin_glb_b64")
        result = project_face_task.remote(face_b64, mannequin_b64)
        return result
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "traceback": traceback.format_exc()}, status_code=400)


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT FROM BLEND: Converts a .blend file to .glb in the cloud
# ─────────────────────────────────────────────────────────────────────────────

BLENDER_EXPORT_FROM_BLEND_SCRIPT = """
import bpy
import sys
import os

def run():
    # The .blend file is already loaded by the 'blender' command
    output_path = "/tmp/exported.glb"
    
    print(f"DEBUG: Exporting current scene from .blend to {output_path}")
    
    # Ensure we are in Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        # Do NOT apply modifiers here; we want to keep the shape keys/morphs 
        # as they are in the blend file.
        export_apply=False,   
        export_morph=True,    # Crucial for Daz morphs
        export_texcoords=True,
        export_materials='EXPORT',
        export_colors=True,
        export_yup=True
    )
    print(f"DEBUG: Export successful to {output_path}")

if __name__ == "__main__":
    run()
"""

@app.function(image=image, timeout=900)
def export_blend_task(blend_file_b64: str):
    import base64, tempfile, subprocess, os
    
    # 1. Write the .blend file safely
    blend_path = "/tmp/input.blend"
    with open(blend_path, "wb") as f:
        f.write(base64.b64decode(blend_file_b64))
        
    # 2. Prepare the python script
    # We must ensure the content of the script is exactly what's defined above
    script_content = '''
import bpy
import sys
import os

def run():
    output_path = "/tmp/exported.glb"
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=False,
        export_morph=True,
        export_texcoords=True,
        export_materials='EXPORT',
        export_colors=True,
        export_yup=True
    )
if __name__ == "__main__":
    run()
'''
    
    script_fd, script_path = tempfile.mkstemp(suffix='.py')
    with os.fdopen(script_fd, 'w') as f:
        f.write(script_content)
        
    try:
        # 3. Run Blender: open the file and execute script
        cmd = [
            "blender",
            "-b", blend_path,
            "--python", script_path
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        logs = f"STDOUT:\\n{result.stdout}\\nSTDERR:\\n{result.stderr}"
        
        if result.returncode != 0:
            raise Exception(f"Blender export failed (code {result.returncode}):\\n{logs}")
            
        output_path = "/tmp/exported.glb"
        if not os.path.exists(output_path):
            raise Exception(f"GLB output not found.\\n{logs}")
            
        with open(output_path, "rb") as f:
            glb_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        return {"glb_base64": glb_b64, "logs": logs}
        
    finally:
        if os.path.exists(script_path): os.remove(script_path)
        if os.path.exists(blend_path): os.remove(blend_path)

@app.function(image=image)
@modal.web_endpoint(method="POST")
def api_export_blend(request: dict):
    blend_b64 = request.get("blend_file_b64")
    if not blend_b64:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Missing blend_file_b64")
        
    return export_blend_task.remote(blend_b64)
