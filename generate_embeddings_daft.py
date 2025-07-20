#!/usr/bin/env python3
"""
Generate CLIP embeddings for all Pokemon images using Daft
Saves only as Parquet format
"""
import daft
from daft import col

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
            # Handle numpy arrays - convert RGBA to RGB if needed
            if isinstance(img_array, np.ndarray):
                # If RGBA (4 channels), convert to RGB
                if img_array.shape[-1] == 4:
                    # Create RGB image and composite alpha channel over white background
                    rgb_array = img_array[:, :, :3]
                    alpha = img_array[:, :, 3] / 255.0
                    # Composite over white background
                    white_bg = np.ones_like(rgb_array) * 255
                    rgb_array = (rgb_array * alpha[:, :, np.newaxis] + 
                                white_bg * (1 - alpha[:, :, np.newaxis])).astype(np.uint8)
                    pil_image = Image.fromarray(rgb_array)
                else:
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
    """Generate embeddings for all Pokemon artwork"""
    
    print("Creating Pokemon dataframe...")
    
    # Create initial dataframe with Pokemon IDs and image paths
    # Start with just 1 image for debugging
    pokemon_data = {
        "pokemon_id": [1],
        "image_path": ["pokemon_artwork/0001.png"]
    }
    
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
    
    # Save as parquet
    output_path = "pokemon_embeddings.parquet"
    print(f"Saving embeddings to {output_path}...")
    
    df.write_parquet(output_path)
    
    print(f"✅ Embeddings saved to {output_path}")
    
    # Print file size
    import os
    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"File size: {file_size:.2f} MB")

if __name__ == "__main__":
    generate_pokemon_embeddings()