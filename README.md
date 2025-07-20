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
- ✅ Successfully generates CLIP embeddings for small datasets (≤100 images)
- ❌ Fails with larger datasets (≥500 images) due to multiprocessing issues
- Root cause: Incompatibility between Daft's multiprocessing and transformers' model loading

For detailed findings and troubleshooting, see `EMBEDDINGS_PROGRESS.md`.

## Sources
- Images: [PokeAPI/sprites](https://github.com/PokeAPI/sprites)
- Data: [lgreski/pokemonData](https://github.com/lgreski/pokemonData) (from PokemonDB.net)