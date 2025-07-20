# Pokemon Embeddings Generation Progress

## Current Status
Work in progress on generating CLIP embeddings for Pokemon images using Daft.

## Setup Instructions

### Environment Setup
```bash
# Using uv (recommended - much faster for ML dependencies)
uv venv
source .venv/bin/activate  # macOS/Linux
uv pip install -r requirements.txt
```

### Dependencies
- `daft` - Distributed dataframe processing
- `transformers` - For CLIP model
- `torch` & `torchvision` - PyTorch dependencies  
- `pillow` - Image handling
- `numpy` - Array operations

## What We've Learned

### Image Format
Through debugging, we discovered that Pokemon images have the following format:
- **Shape**: (475, 475, 4) - Square images, 475x475 pixels
- **Channels**: 4 (RGBA - RGB + Alpha channel)
- **Data type**: uint8 (0-255 values)
- **Format**: NumPy arrays when loaded by Daft

### CLIP Model Requirements
- CLIP expects RGB images (3 channels), not RGBA
- We handle this by compositing the alpha channel over a white background
- The model outputs 512-dimensional float32 embeddings

### Technical Implementation

#### UDF Structure
```python
@daft.udf(return_dtype=daft.DataType.embedding(daft.DataType.float32(), 512))
class CLIPImageEncoder:
    def __init__(self):
        # Model initialization happens once per worker
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    def __call__(self, images):
        # Process batch of images
        # Convert RGBA to RGB, generate embeddings
```

#### Key Findings
1. **Import location matters**: Imports work fine inside Daft UDF methods
2. **RGBA conversion**: Essential to convert 4-channel images to 3-channel RGB
3. **Batch processing**: Daft passes images as Series objects, use `.to_pylist()` to iterate
4. **Embedding normalization**: CLIP best practice is to L2-normalize embeddings

## Testing Status

### Completed Tests
- ✅ Verified CLIP model loads and runs correctly (test_clip.py)
- ✅ Confirmed Daft UDF imports work properly (test_daft_simple.py)
- ✅ Successfully generated embeddings for single image
- ✅ Identified and handled RGBA image format

### Known Issues
- Import error occurred initially but was resolved
- Need to test with full dataset (1025 Pokemon images)

## Next Steps
1. Test with larger batches of images
2. Verify embeddings are correct by testing similarity searches
3. Scale up to full dataset
4. Add progress tracking and error handling
5. Consider batch size optimization for memory efficiency

## Recent Progress (2025-07-20)

### RGBA to RGB Conversion Verified
- ✅ Examined Pokemon images - all have transparent backgrounds
- ✅ Confirmed white background is optimal for conversion (matches typical display context)
- ✅ Created `convert_to_rgb.py` script for batch conversion
- ✅ Successfully converted all 1025 Pokemon images to RGB format
- ✅ Verified conversion quality - colors preserved, no artifacts
- ✅ Conversion matches PIL's standard RGBA→RGB behavior

### Conversion Details
The RGBA to RGB conversion formula used:
```python
# For each pixel:
rgb = rgba[:3] * (alpha/255) + white_background * (1 - alpha/255)
```
This properly composites the image over white, handling transparency correctly.

## File Structure
```
.
├── generate_embeddings_daft.py  # Main script (WIP)
├── convert_to_rgb.py           # RGBA to RGB conversion script
├── requirements.txt             # Python dependencies
├── pokemon_artwork/             # Original RGBA images
├── pokemon_artwork_rgb/         # Converted RGB images
├── *.parquet                   # Output files (gitignored)
└── test_*.py                   # Test scripts (gitignored)
```

## Latest Updates (2025-07-20)

### Embeddings Script Updated
- ✅ Modified `generate_embeddings_daft.py` to use pre-converted RGB images
- ✅ Removed RGBA to RGB conversion logic from the UDF
- ✅ Successfully tested single image embedding generation
- ✅ Verified parquet output (3.8KB for single embedding)
- ✅ Confirmed 512-dimensional float32 embeddings are generated correctly

### Current Implementation Status
The script now:
1. Reads from `pokemon_artwork_rgb/` directory directly
2. Processes images without conversion overhead
3. Generates normalized CLIP embeddings
4. Saves to parquet format successfully

**Note**: Currently configured to process only 1 image for testing. Ready to scale to full dataset.