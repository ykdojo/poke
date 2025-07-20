#!/usr/bin/env python3
"""
Generate CLIP embeddings for Pokemon images - simple version without Daft write issues
"""
import daft
from daft import col
import numpy as np

@daft.udf(return_dtype=daft.DataType.embedding(daft.DataType.float32(), 512))
class CLIPImageEncoder:
    def __init__(self):
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch
            
            # Initialize CLIP model once per process
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Error in UDF __init__: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def __call__(self, images):
        import torch
        from PIL import Image
        import numpy as np
        
        embeddings = []
        
        for img_array in images.to_pylist():
            # Handle numpy arrays - images are already RGB
            if isinstance(img_array, np.ndarray):
                pil_image = Image.fromarray(img_array)
            else:
                pil_image = img_array
            
            # Process with CLIP
            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # Normalize embeddings (CLIP standard practice)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                embedding = image_features.cpu().numpy().squeeze()
            
            embeddings.append(embedding)
        
        return embeddings

def generate_pokemon_embeddings():
    """Generate embeddings for Pokemon artwork"""
    
    print("Creating Pokemon dataframe...")
    
    # Generate data for all 1025 Pokemon
    pokemon_ids = list(range(1, 1026))  # 1 to 1025
    image_paths = [f"pokemon_artwork_rgb/{pid:04d}.png" for pid in pokemon_ids]
    
    pokemon_data = {
        "pokemon_id": pokemon_ids,
        "image_path": image_paths
    }
    
    print(f"Processing {len(pokemon_ids)} Pokemon images...")
    
    df = daft.from_pydict(pokemon_data)
    
    print("Loading images...")
    
    # Read and decode images
    df = df.with_column(
        "image",
        col("image_path").url.download().image.decode()
    )
    
    print("Generating CLIP embeddings...")
    
    # Generate CLIP embeddings
    df = df.with_column(
        "embedding",
        CLIPImageEncoder(col("image"))
    )
    
    # Select only the columns we need
    df = df.select("pokemon_id", "embedding")
    
    print("\nCollecting results...")
    print("This may take a few minutes for all 1025 Pokemon...")
    try:
        # Collect the results
        results = df.collect()
        print(f"Successfully collected {len(results)} rows")
        
        # Save as numpy arrays instead
        embeddings_list = []
        ids_list = []
        
        for row in results:
            ids_list.append(row["pokemon_id"])
            embeddings_list.append(row["embedding"])
        
        # Convert to numpy arrays
        ids_array = np.array(ids_list)
        embeddings_array = np.array(embeddings_list)
        
        print(f"\nEmbeddings array shape: {embeddings_array.shape}")
        print(f"IDs array shape: {ids_array.shape}")
        
        # Save as numpy files
        np.save("pokemon_ids.npy", ids_array)
        np.save("pokemon_embeddings.npy", embeddings_array)
        
        print(f"\n✅ Saved embeddings to:")
        print(f"  - pokemon_ids.npy")
        print(f"  - pokemon_embeddings.npy")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_pokemon_embeddings()