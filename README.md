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
- ✅ Successfully generates CLIP embeddings for datasets up to 406 images (with original code)
- ✅ Can process 407+ images with lazy loading and CPU-only inference
- ❌ Still fails at higher image counts (exact threshold TBD)

### The Fix
The meta tensor error can be avoided by:
1. Moving imports to module level
2. Using lazy model loading in the UDF's `__call__` method
3. Keeping the model on CPU (avoiding device transfers that trigger meta tensor issues)

With these changes, the script can process at least 407 images successfully.

### Original Error (Fixed)
When processing more than 406 images with the original code, the script failed with:
```
NotImplementedError: Cannot copy out of meta tensor; no data! Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to() when moving module from meta to a different device.
```

This occurred because transformers uses "meta" tensors for memory efficiency, which can't be moved to devices in Daft's worker processes.

### Testing the Fix
```bash
# Original code: fails at 407 images
# Fixed code with lazy loading + CPU: works at 407 images
python test_parquet_issue.py 407  # ✅ Works (~10 seconds)

# But still fails at higher counts (exact threshold TBD)
python test_parquet_issue.py 1025 # ❌ UDFException
```


## Sources
- Images: [PokeAPI/sprites](https://github.com/PokeAPI/sprites)
- Data: [lgreski/pokemonData](https://github.com/lgreski/pokemonData) (from PokemonDB.net)