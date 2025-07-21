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

This project demonstrates generating CLIP embeddings for Pokemon images using Daft, a distributed dataframe library. We encountered and solved interesting multiprocessing challenges that provide insights into how Daft handles user-defined functions (UDFs) at scale.

### The Journey: Debugging Daft's Multiprocessing

#### Initial Problem
We wanted to generate CLIP embeddings for 1025 Pokemon images using Daft's UDF feature. The initial implementation failed with mysterious errors when processing more than ~100 images.

#### Investigation Process

1. **First Discovery** ([commit 3582467](../../commit/3582467)): Created a test script to reproduce the issue. Found that Daft worked with 100 images but failed at 1025 with "Too many open files" error.

2. **Finding the Threshold** ([commit c115b42](../../commit/c115b42)): Through binary search, discovered the exact failure threshold was 128 images. Above this, Daft failed with `ImportError` in worker processes.

3. **First Fix Attempt** ([commit 3f3c908](../../commit/3f3c908)): Moving imports to module level fixed the ImportError but revealed a new threshold at 406/407 images with "meta tensor" errors.

4. **Deeper Investigation** ([commit 1da7f8d](../../commit/1da7f8d)): Implemented lazy loading and CPU-only inference, which pushed the threshold to 430 images but still failed on larger datasets.

5. **Root Cause Discovery**: Through detailed debugging, we discovered that Daft creates multiple UDF instances when processing larger datasets. These instances were trying to load the CLIP model simultaneously, causing race conditions in the transformers library.

6. **Final Solution** ([commit 8e7411f](../../commit/8e7411f)): Implemented thread-safe model loading with a global cache, successfully processing all 1025 images.

### The Solution

The issue was that when Daft scales up processing, it creates multiple UDF instances that can run in parallel threads within the same process. If these instances try to initialize heavy ML models simultaneously, it causes race conditions.

Our solution uses a thread-safe global model cache that ensures only one model is loaded per process, regardless of how many UDF instances Daft creates.

[View the final working code →](generate_embeddings_daft_fixed.py)

### Key Learnings

1. **Daft's Execution Model**: Below ~128 images, Daft runs in single-threaded mode. Above that, it spawns multiple UDF instances for parallelism.

2. **Model Loading Race Conditions**: ML frameworks like transformers aren't always thread-safe during model initialization.

3. **Thread-Safe Patterns**: The double-check locking pattern is crucial for efficient thread-safe lazy initialization.

### Running the Code

```bash
# Generate embeddings for all Pokemon
python generate_embeddings_daft_fixed.py 1025

# Test with different dataset sizes
python generate_embeddings_daft_fixed.py 100   # Single-threaded execution
python generate_embeddings_daft_fixed.py 500   # Multi-threaded execution
```


## Sources
- Images: [PokeAPI/sprites](https://github.com/PokeAPI/sprites)
- Data: [lgreski/pokemonData](https://github.com/lgreski/pokemonData) (from PokemonDB.net)