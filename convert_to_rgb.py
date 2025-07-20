#!/usr/bin/env python3
"""Convert Pokemon RGBA images to RGB with white background"""
import os
import glob
from PIL import Image
import numpy as np
from tqdm import tqdm

def convert_rgba_to_rgb(image_path, output_path):
    """Convert single RGBA image to RGB with white background"""
    img = Image.open(image_path)
    
    # Convert to RGBA if not already (in case some are RGB)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create white background
    white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    
    # Composite image over white background
    white_bg.paste(img, (0, 0), img)
    
    # Convert to RGB
    rgb_img = white_bg.convert('RGB')
    
    # Save
    rgb_img.save(output_path, 'PNG')

def main():
    # Create output directory
    output_dir = "pokemon_artwork_rgb"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all Pokemon images
    image_files = sorted(glob.glob("pokemon_artwork/*.png"))
    
    print(f"Found {len(image_files)} Pokemon images")
    print(f"Converting to RGB and saving to '{output_dir}/'...")
    
    # Convert each image
    for img_path in tqdm(image_files, desc="Converting"):
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        
        try:
            convert_rgba_to_rgb(img_path, output_path)
        except Exception as e:
            print(f"\nError converting {filename}: {e}")
    
    print(f"\n✅ Conversion complete! RGB images saved to '{output_dir}/'")
    
    # Show some stats
    converted_files = glob.glob(f"{output_dir}/*.png")
    print(f"Successfully converted: {len(converted_files)} images")

if __name__ == "__main__":
    main()