// Pokemon Embeddings and Similarity Search

let pokemonEmbeddings = null;
let embeddingsLoaded = false;

// Load embeddings asynchronously
async function loadEmbeddings() {
    try {
        console.log('Loading Pokemon embeddings...');
        const response = await fetch('static/pokemon_embeddings.json');
        pokemonEmbeddings = await response.json();
        embeddingsLoaded = true;
        console.log(`Loaded embeddings for ${pokemonEmbeddings.length} Pokemon`);
    } catch (error) {
        console.error('Error loading embeddings:', error);
    }
}

// Compute cosine similarity between two embeddings
function cosineSimilarity(embedding1, embedding2) {
    // Since embeddings are already normalized (from CLIP), 
    // cosine similarity is just the dot product
    let dotProduct = 0;
    for (let i = 0; i < embedding1.length; i++) {
        dotProduct += embedding1[i] * embedding2[i];
    }
    return dotProduct;
}

// Find most similar Pokemon
function findSimilarPokemon(pokemonId, topK = 6) {
    if (!embeddingsLoaded || !pokemonEmbeddings) {
        console.warn('Embeddings not loaded yet');
        return [];
    }
    
    // Get the embedding for the target Pokemon
    const targetEmbedding = pokemonEmbeddings[pokemonId - 1];
    if (!targetEmbedding) {
        console.warn(`No embedding found for Pokemon ID ${pokemonId}`);
        return [];
    }
    
    // Calculate similarities with all other Pokemon
    const similarities = [];
    for (let i = 0; i < pokemonEmbeddings.length; i++) {
        if (i === pokemonId - 1) continue; // Skip self
        
        const similarity = cosineSimilarity(targetEmbedding, pokemonEmbeddings[i]);
        similarities.push({
            id: i + 1,
            similarity: similarity
        });
    }
    
    // Sort by similarity (descending) and take top K
    similarities.sort((a, b) => b.similarity - a.similarity);
    return similarities.slice(0, topK);
}

// Start loading embeddings when the script loads
loadEmbeddings();