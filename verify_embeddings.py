#!/usr/bin/env python3
"""Verify the generated Pokemon embeddings"""

import numpy as np

# Load the saved embeddings
ids = np.load("pokemon_ids.npy")
embeddings = np.load("pokemon_embeddings.npy")

print("=== Embeddings Verification ===")
print(f"Number of Pokemon IDs: {len(ids)}")
print(f"Embeddings shape: {embeddings.shape}")
print(f"Data type: {embeddings.dtype}")
print(f"ID range: {ids.min()} to {ids.max()}")

# Check if all IDs are present
expected_ids = set(range(1, 1026))
actual_ids = set(ids)
missing_ids = expected_ids - actual_ids
extra_ids = actual_ids - expected_ids

print(f"\nMissing IDs: {missing_ids if missing_ids else 'None'}")
print(f"Extra IDs: {extra_ids if extra_ids else 'None'}")

# Check normalization
norms = np.linalg.norm(embeddings, axis=1)
print(f"\nNormalization check:")
print(f"  Min norm: {norms.min():.6f}")
print(f"  Max norm: {norms.max():.6f}")
print(f"  All normalized: {np.allclose(norms, 1.0)}")

# Test similarity with evolution lines
print("\n=== Testing Similarity ===")

# Find indices for test Pokemon
bulbasaur_idx = np.where(ids == 1)[0][0]
ivysaur_idx = np.where(ids == 2)[0][0]
venusaur_idx = np.where(ids == 3)[0][0]
charmander_idx = np.where(ids == 4)[0][0]
charizard_idx = np.where(ids == 6)[0][0]

# Compute similarities
def cosine_similarity(a, b):
    return np.dot(a, b)

print("\nBulbasaur evolution line:")
print(f"  Bulbasaur-Ivysaur: {cosine_similarity(embeddings[bulbasaur_idx], embeddings[ivysaur_idx]):.4f}")
print(f"  Ivysaur-Venusaur: {cosine_similarity(embeddings[ivysaur_idx], embeddings[venusaur_idx]):.4f}")

print("\nCross-evolution comparison:")
print(f"  Bulbasaur-Charmander: {cosine_similarity(embeddings[bulbasaur_idx], embeddings[charmander_idx]):.4f}")
print(f"  Ivysaur-Charizard: {cosine_similarity(embeddings[ivysaur_idx], embeddings[charizard_idx]):.4f}")

# File sizes
import os
ids_size = os.path.getsize("pokemon_ids.npy") / 1024 / 1024
embeddings_size = os.path.getsize("pokemon_embeddings.npy") / 1024 / 1024

print(f"\n=== File Sizes ===")
print(f"pokemon_ids.npy: {ids_size:.2f} MB")
print(f"pokemon_embeddings.npy: {embeddings_size:.2f} MB")
print(f"Total: {ids_size + embeddings_size:.2f} MB")

print("\n✅ Embeddings verification complete!")