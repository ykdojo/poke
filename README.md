# Pokemon Browser

Interactive Pokemon browser with all 1025 Pokemon, featuring visual similarity search powered by CLIP embeddings.

## Setup

### Using UV (Recommended - faster for ML dependencies)
```bash
# Install UV if you haven't already
# See: https://github.com/astral-sh/uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

uv pip install -r requirements.txt
```

### Using pip
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Run Web Interface
```bash
python3 serve.py
# Open http://localhost:8000
```

## Project Structure
- `pokemon_artwork/` - Original artwork (475x475 RGBA PNG)
- `pokemon_artwork_rgb/` - RGB-converted images for CLIP processing
- `pokemon_data.csv` - Names, types, stats
- `requirements.txt` - Python dependencies
- `convert_to_rgb.py` - Utility to convert RGBA images to RGB

## Pokemon Embeddings with Daft

This project includes experiments with generating CLIP embeddings for Pokemon images using Daft.

### Key Findings
- ✅ Successfully processes all 1025 Pokemon images with thread-safe model loading
- ❌ Original code failed due to race conditions when Daft created multiple UDF instances

### The Root Cause
When processing larger datasets, Daft creates multiple UDF instances for parallel processing. If these instances try to load the CLIP model simultaneously, it causes race conditions in the transformers library, resulting in "meta tensor" errors.

### The Solution
The fix uses thread-safe model loading with a global cache:
1. **Single model per process**: Only one model is loaded regardless of UDF instances
2. **Thread-safe loading**: Uses threading.Lock() to prevent simultaneous loads
3. **Process-aware cache**: Separate cache entry per process ID for multiprocessing

### Complete Fix
```python
# Thread-safe global model cache
_model_lock = threading.Lock()
_model_cache = {}

def get_clip_model():
    """Thread-safe model loading."""
    pid = os.getpid()
    
    if pid in _model_cache:
        return _model_cache[pid]['model'], _model_cache[pid]['processor']
    
    with _model_lock:
        # Double-check pattern
        if pid in _model_cache:
            return _model_cache[pid]['model'], _model_cache[pid]['processor']
        
        # Load model once per process
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model.eval()
        
        _model_cache[pid] = {'model': model, 'processor': processor}
        
    return _model_cache[pid]['model'], _model_cache[pid]['processor']
```

### Testing Results
```bash
# Works with all 1025 images!
python test_parquet_issue.py 1025  # ✅ Works (~15 seconds)
```


## Sources
- Images: [PokeAPI/sprites](https://github.com/PokeAPI/sprites)
- Data: [lgreski/pokemonData](https://github.com/lgreski/pokemonData) (from PokemonDB.net)