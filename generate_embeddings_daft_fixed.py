#!/usr/bin/env python3
"""
Reproduce the Daft write_parquet() issue with CLIP embeddings.
Based on the original generate_embeddings_daft.py that exhibited the problem.
"""
import sys
import threading
import os
import daft
from daft import col
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

# Thread-safe global model cache
_model_lock = threading.Lock()
_model_cache = {}

def get_clip_model():
    """Thread-safe model loading to prevent race conditions."""
    pid = os.getpid()
    
    # Fast path - model already loaded
    if pid in _model_cache:
        return _model_cache[pid]['model'], _model_cache[pid]['processor']
    
    # Slow path - need to load model with lock
    with _model_lock:
        # Double-check - another thread might have loaded it
        if pid in _model_cache:
            return _model_cache[pid]['model'], _model_cache[pid]['processor']
        
        # Load model once per process
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model.eval()
        
        _model_cache[pid] = {
            'model': model,
            'processor': processor
        }
        
    return _model_cache[pid]['model'], _model_cache[pid]['processor']

@daft.udf(return_dtype=daft.DataType.embedding(daft.DataType.float32(), 512))
class CLIPImageEncoder:
    def __init__(self):
        pass
    
    def __call__(self, images):
        model, processor = get_clip_model()
        embeddings = []
        
        for img_array in images.to_pylist():
            pil_image = Image.fromarray(img_array)
            
            inputs = processor(images=pil_image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = model.get_image_features(**inputs)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                embedding = image_features.cpu().numpy().squeeze()
            
            embeddings.append(embedding)
        
        return embeddings

# Get number of images from command line, default to 10
num_images = int(sys.argv[1]) if len(sys.argv) > 1 else 10

print(f"\nTesting with {num_images} images...")

# Create dataframe
pokemon_data = {
    "pokemon_id": list(range(1, num_images + 1)),
    "image_path": [f"pokemon_artwork_rgb/{i:04d}.png" for i in range(1, num_images + 1)]
}

df = daft.from_pydict(pokemon_data)

# Load images
print("Loading images...")
df = df.with_column(
    "image",
    col("image_path").url.download().image.decode()
)

# Generate embeddings
print("Generating embeddings...")
df = df.with_column(
    "embedding",
    CLIPImageEncoder(col("image"))
)

# Select columns
df = df.select("pokemon_id", "embedding")

print("Attempting write_parquet()...")
import time
start = time.time()
df.write_parquet(f"pokemon_embeddings_{num_images}.parquet")
print(f"Done in {time.time() - start:.2f} seconds!")