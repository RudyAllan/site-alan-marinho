# ComfyUI Image Generation Script for Alan Marinho
# Uses the ComfyUI API to generate professional headshot

import json
import urllib.request
import urllib.parse
import time
import sys
import uuid
import os
import shutil

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = r"C:\Users\rudya\AppData\Local\Comfy-Desktop\ComfyUI-Shared\output"
SITE_ASSETS = sys.argv[1] if len(sys.argv) > 1 else r"D:\###     PROJETOS EM ANDAMENTO\#RAC - FullService\EERAC - AGENCIA FULL SERVICE\AGente RAC 01\site-alan-marinho\assets"

# Workflow prompt for professional headshot
workflow = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 892451237,
            "steps": 6,
            "cfg": 2.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "z-image-turbo-bf16-aio.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "width": 768,
            "height": 1024,
            "batch_size": 1
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "Professional headshot portrait photo of a confident Brazilian male business administrator in his early 30s, wearing a navy blue tailored suit with a light blue tie, clean-shaven, short dark hair, warm confident smile, studio lighting with a soft dark navy gradient background, professional corporate photography style, high quality, sharp focus, business executive look, 8k, detailed, photorealistic",
            "clip": ["4", 1]
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "blurry, low quality, deformed, ugly, bad anatomy, extra fingers, mutated hands, poorly drawn face, bad proportions, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, watermark, text, signature",
            "clip": ["4", 1]
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "alan_marinho_headshot",
            "images": ["8", 0]
        }
    }
}

def queue_prompt(prompt):
    """Queue a prompt via ComfyUI API"""
    p = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_history(prompt_id):
    """Get generation history"""
    req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def wait_for_completion(prompt_id, timeout=120):
    """Wait for the generation to complete"""
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id)
        if prompt_id in history:
            status = history[prompt_id].get("status", {})
            if status.get("completed", False) or status.get("status_str") == "success":
                return history[prompt_id]
            if status.get("status_str") == "error":
                print(f"ERROR: Generation failed: {json.dumps(status, indent=2)}")
                return None
        time.sleep(2)
        elapsed = int(time.time() - start)
        print(f"  Aguardando... ({elapsed}s)")
    print("ERROR: Timeout waiting for generation")
    return None

def main():
    print("=" * 50)
    print("ComfyUI Image Generator - Alan Marinho")
    print("=" * 50)
    
    # Check if ComfyUI is reachable
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
        resp = urllib.request.urlopen(req)
        stats = json.loads(resp.read())
        print(f"ComfyUI v{stats['system']['comfyui_version']} conectado!")
        print(f"GPU: {stats['devices'][0]['name']}")
        print()
    except Exception as e:
        print(f"ERRO: ComfyUI não está acessível em {COMFYUI_URL}")
        print(f"Detalhe: {e}")
        sys.exit(1)

    # List existing output files before generation
    existing_files = set()
    if os.path.exists(OUTPUT_DIR):
        existing_files = set(os.listdir(OUTPUT_DIR))

    # Queue the prompt
    print("Enviando workflow para geração...")
    result = queue_prompt(workflow)
    prompt_id = result.get("prompt_id")
    
    if not prompt_id:
        print(f"ERRO: Falha ao enviar prompt: {json.dumps(result, indent=2)}")
        sys.exit(1)
    
    print(f"Prompt ID: {prompt_id}")
    print("Gerando imagem...")
    print()

    # Wait for completion
    history = wait_for_completion(prompt_id)
    
    if history is None:
        sys.exit(1)

    # Find the generated image
    outputs = history.get("outputs", {})
    image_filename = None
    
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img in node_output["images"]:
                image_filename = img.get("filename")
                subfolder = img.get("subfolder", "")
                print(f"Imagem gerada: {image_filename}")
                
                # Build source path
                src_path = os.path.join(OUTPUT_DIR, subfolder, image_filename) if subfolder else os.path.join(OUTPUT_DIR, image_filename)
                
                if os.path.exists(src_path):
                    # Copy to site assets
                    dest_path = os.path.join(SITE_ASSETS, "alan-marinho.jpg")
                    shutil.copy2(src_path, dest_path)
                    print(f"Copiada para: {dest_path}")
                    print()
                    print("SUCESSO! Imagem gerada e copiada para o site.")
                else:
                    print(f"AVISO: Arquivo não encontrado em {src_path}")
                    # Try to find it
                    if os.path.exists(OUTPUT_DIR):
                        new_files = set(os.listdir(OUTPUT_DIR)) - existing_files
                        if new_files:
                            newest = sorted(new_files)[-1]
                            src_path = os.path.join(OUTPUT_DIR, newest)
                            dest_path = os.path.join(SITE_ASSETS, "alan-marinho.jpg")
                            shutil.copy2(src_path, dest_path)
                            print(f"Encontrado e copiado: {newest} -> {dest_path}")
                            print("SUCESSO!")

    if not image_filename:
        print("AVISO: Nenhuma imagem encontrada no output.")
        # Fallback: check for new files
        if os.path.exists(OUTPUT_DIR):
            new_files = set(os.listdir(OUTPUT_DIR)) - existing_files
            alan_files = [f for f in new_files if "alan_marinho" in f.lower()]
            if alan_files:
                newest = sorted(alan_files)[-1]
                src_path = os.path.join(OUTPUT_DIR, newest)
                dest_path = os.path.join(SITE_ASSETS, "alan-marinho.jpg")
                shutil.copy2(src_path, dest_path)
                print(f"Encontrado e copiado: {newest}")
                print("SUCESSO!")

if __name__ == "__main__":
    main()
