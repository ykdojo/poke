#!/usr/bin/env python3
"""
Reproduce the Daft write_parquet() issue with CLIP embeddings.
Based on the original generate_embeddings_daft.py that exhibited the problem.
"""
import sys
import daft
from daft import col
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

@daft.udf(return_dtype=daft.DataType.embedding(daft.DataType.float32(), 512))
class CLIPImageEncoder:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = None
    
    def __call__(self, images):
        # Lazy load the model in the worker process
        if self.model is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            # Try loading model without any device operations
            import os
            os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
            
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            # Don't move to device - keep on CPU to avoid meta tensor issues
            self.model.eval()
        
        embeddings = []
        
        for img_array in images.to_pylist():
            pil_image = Image.fromarray(img_array)
            
            inputs = self.processor(images=pil_image, return_tensors="pt")
            # Keep everything on CPU to avoid device issues
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
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