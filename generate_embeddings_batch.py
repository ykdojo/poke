#!/usr/bin/env python3
"""
Generate CLIP embeddings for all Pokemon images using batch processing
"""
import numpy as np
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import torch
from pathlib import Path
import time

def generate_all_pokemon_embeddings(batch_size=32):
    """Generate embeddings for all Pokemon images with batch processing"""
    
    print("Initializing CLIP model...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model.to(device)
    model.eval()
    
    # Prepare all Pokemon IDs and paths
    pokemon_ids = list(range(1, 1026))  # 1 to 1025
    image_paths = [f"pokemon_artwork_rgb/{pid:04d}.png" for pid in pokemon_ids]
    
    all_embeddings = []
    all_ids = []
    
    print(f"\nProcessing {len(pokemon_ids)} Pokemon images in batches of {batch_size}...")
    start_time = time.time()
    
    # Process in batches
    for i in range(0, len(pokemon_ids), batch_size):
        batch_end = min(i + batch_size, len(pokemon_ids))
        batch_ids = pokemon_ids[i:batch_end]
        batch_paths = image_paths[i:batch_end]
        
        # Load batch of images
        batch_images = []
        for path in batch_paths:
            image = Image.open(path)
            batch_images.append(image)
        
        # Process batch with CLIP
        inputs = processor(images=batch_images, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            embeddings = image_features.cpu().numpy()
        
        all_embeddings.extend(embeddings)
        all_ids.extend(batch_ids)
        
        # Progress update
        if (i + batch_size) % 100 == 0 or batch_end == len(pokemon_ids):
            elapsed = time.time() - start_time
            progress = batch_end / len(pokemon_ids) * 100
            print(f"  Processed {batch_end}/{len(pokemon_ids)} ({progress:.1f}%) - {elapsed:.1f}s elapsed")
    
    # Convert to numpy arrays
    embeddings_array = np.array(all_embeddings)
    ids_array = np.array(all_ids)
    
    print(f"\nEmbeddings shape: {embeddings_array.shape}")
    print(f"IDs shape: {ids_array.shape}")
    
    # Verify embeddings are normalized
    norms = np.linalg.norm(embeddings_array, axis=1)
    print(f"Embeddings normalized: {np.allclose(norms, 1.0)}")
    
    # Save arrays
    print("\nSaving embeddings...")
    np.save("pokemon_ids.npy", ids_array)
    np.save("pokemon_embeddings.npy", embeddings_array)
    
    total_time = time.time() - start_time
    print(f"\n✅ Successfully generated embeddings for {len(pokemon_ids)} Pokemon!")
    print(f"   Total time: {total_time:.1f} seconds ({total_time/len(pokemon_ids):.2f}s per image)")
    print(f"   Saved to:")
    print(f"   - pokemon_ids.npy")
    print(f"   - pokemon_embeddings.npy")
    
    return embeddings_array, ids_array

if __name__ == "__main__":
    generate_all_pokemon_embeddings()