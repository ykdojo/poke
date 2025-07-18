let pokemonData = [];

// Load Pokemon data
async function loadPokemonData() {
    try {
        const response = await fetch('pokemon_data.csv');
        const csvText = await response.text();
        pokemonData = parseCSV(csvText);
        displayPokemon();
    } catch (error) {
        console.error('Error loading Pokemon data:', error);
    }
}

// Parse CSV data
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
    
    return lines.slice(1).map(line => {
        const values = line.match(/(".*?"|[^,]+)/g).map(v => v.replace(/"/g, '').trim());
        const pokemon = {};
        headers.forEach((header, index) => {
            pokemon[header] = values[index] || '';
        });
        return pokemon;
    });
}

// Display Pokemon in grid
function displayPokemon() {
    const grid = document.getElementById('pokemon-grid');
    grid.innerHTML = '';
    
    pokemonData.forEach(pokemon => {
        const card = createPokemonCard(pokemon);
        grid.appendChild(card);
    });
}

// Create a Pokemon card element
function createPokemonCard(pokemon) {
    const card = document.createElement('div');
    card.className = 'pokemon-card';
    
    // Format ID with leading zeros
    const paddedId = pokemon.ID.padStart(4, '0');
    
    // Create form display
    const formDisplay = pokemon.Form && pokemon.Form.trim() 
        ? ` (${pokemon.Form.trim()})` 
        : '';
    
    // Create type badges
    const type1Badge = pokemon.Type1 ? 
        `<span class="type-badge type-${pokemon.Type1.toLowerCase()}">${pokemon.Type1}</span>` : '';
    const type2Badge = pokemon.Type2 && pokemon.Type2.trim() ? 
        `<span class="type-badge type-${pokemon.Type2.toLowerCase()}">${pokemon.Type2}</span>` : '';
    
    card.innerHTML = `
        <img src="pokemon_artwork/${paddedId}.png" alt="${pokemon.Name}" loading="lazy">
        <div class="pokemon-name">${pokemon.Name}${formDisplay}</div>
        <div class="pokemon-types">
            ${type1Badge}
            ${type2Badge}
        </div>
    `;
    
    card.addEventListener('click', () => {
        // For now, just log the Pokemon data
        console.log('Clicked:', pokemon);
        // TODO: Show detailed view
    });
    
    return card;
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', loadPokemonData);