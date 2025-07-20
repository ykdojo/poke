#!/usr/bin/env python3
"""
Generate CLIP embeddings for 100 Pokemon images using Daft.
This script demonstrates the WORKING case with a small dataset.
"""
import daft
from daft import col
import numpy as np
import time

@daft.udf(return_dtype=daft.DataType.python())
class CLIPImageEncoder:
    def __init__(self):
        from transformers import CLIPProcessor, CLIPModel
        import torch
        
        print("[UDF Init] Loading CLIP model...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        print(f"[UDF Init] Model loaded on {self.device}")
    
    def __call__(self, images):
        import torch
        from PIL import Image
        
        embeddings = []
        
        for img_array in images.to_pylist():
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(img_array)
            
            # Process with CLIP
            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # Normalize embeddings (CLIP standard practice)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                embedding = image_features.cpu().numpy().squeeze()
            
            embeddings.append(embedding.tolist())
        
        return embeddings

def main():
    print("=" * 60)
    print("Daft CLIP Embeddings - Working Case (100 images)")
    print("=" * 60)
    
    # Create dataframe with 100 Pokemon
    num_pokemon = 100
    pokemon_data = {
        "pokemon_id": list(range(1, num_pokemon + 1)),
        "image_path": [f"pokemon_artwork_rgb/{i:04d}.png" for i in range(1, num_pokemon + 1)]
    }
    
    print(f"\n1. Creating dataframe with {num_pokemon} Pokemon...")
    df = daft.from_pydict(pokemon_data)
    
    print("\n2. Loading images...")
    df = df.with_column(
        "image",
        col("image_path").url.download().image.decode()
    )
    
    print("\n3. Generating CLIP embeddings...")
    start_time = time.time()
    
    df = df.with_column(
        "embedding",
        CLIPImageEncoder(col("image"))
    )
    
    # Select only the columns we need
    df = df.select("pokemon_id", "embedding")
    
    print("\n4. Collecting results...")
    results = df.collect()
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ Successfully generated {len(results)} embeddings in {elapsed_time:.2f} seconds")
    
    # Convert to numpy array and save
    print("\n5. Saving embeddings...")
    embeddings_list = [row["embedding"] for row in results]
    embeddings_array = np.array(embeddings_list, dtype=np.float32)
    
    output_file = "pokemon_embeddings_100.npy"
    np.save(output_file, embeddings_array)
    
    file_size_mb = embeddings_array.nbytes / (1024 * 1024)
    print(f"✅ Saved to {output_file} ({file_size_mb:.2f} MB)")
    print(f"   Shape: {embeddings_array.shape}")
    print(f"   Dtype: {embeddings_array.dtype}")
    
    # Verify embeddings
    print("\n6. Verification:")
    print(f"   First embedding shape: {embeddings_array[0].shape}")
    print(f"   All embeddings normalized: {np.allclose(np.linalg.norm(embeddings_array, axis=1), 1.0)}")
    
    print("\n✅ Script completed successfully!")

if __name__ == "__main__":
    main()