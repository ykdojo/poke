let pokemonData = [];
let filteredPokemonData = [];

// Load Pokemon data
async function loadPokemonData() {
    try {
        const response = await fetch('pokemon_data.csv');
        const csvText = await response.text();
        pokemonData = parseCSV(csvText);
        filteredPokemonData = [...pokemonData];
        displayPokemon();
        initializeSearch();
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

// Generation boundaries
const generationBoundaries = [
    { gen: 1, start: 1, end: 151, name: 'Kanto' },
    { gen: 2, start: 152, end: 251, name: 'Johto' },
    { gen: 3, start: 252, end: 386, name: 'Hoenn' },
    { gen: 4, start: 387, end: 493, name: 'Sinnoh' },
    { gen: 5, start: 494, end: 649, name: 'Unova' },
    { gen: 6, start: 650, end: 721, name: 'Kalos' },
    { gen: 7, start: 722, end: 809, name: 'Alola' },
    { gen: 8, start: 810, end: 905, name: 'Galar' },
    { gen: 9, start: 906, end: 1025, name: 'Paldea' }
];

// Display Pokemon in grid
function displayPokemon() {
    const grid = document.getElementById('pokemon-grid');
    grid.innerHTML = '';
    
    let currentGen = 1;
    
    filteredPokemonData.forEach((pokemon, index) => {
        const pokemonId = parseInt(pokemon.ID);
        
        // Check if we need to add a generation separator
        const genBoundary = generationBoundaries.find(g => g.start === pokemonId);
        if (genBoundary) {
            const separator = document.createElement('div');
            separator.className = 'generation-separator';
            separator.innerHTML = `<span>Generation ${genBoundary.gen} - ${genBoundary.name}</span>`;
            grid.appendChild(separator);
            currentGen = genBoundary.gen;
        }
        
        const card = createPokemonCard(pokemon);
        card.setAttribute('data-index', index);
        card.setAttribute('data-generation', currentGen);
        grid.appendChild(card);
    });
    
    // Initialize minimap after displaying Pokemon
    initializeMinimap();
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
        showPokemonDetail(pokemon);
    });
    
    return card;
}

// Show Pokemon detail view
function showPokemonDetail(pokemon) {
    const detailView = document.getElementById('pokemon-detail');
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
    
    detailView.innerHTML = `
        <div class="detail-content">
            <button class="close-button" onclick="closePokemonDetail()">&times;</button>
            
            <div class="detail-header">
                <img src="pokemon_artwork/${paddedId}.png" alt="${pokemon.Name}" class="detail-image">
                <div class="detail-info">
                    <h2>${pokemon.Name}${formDisplay}</h2>
                    <div class="detail-types">
                        ${type1Badge}
                        ${type2Badge}
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">HP:</span>
                            <span>${pokemon.HP}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Attack:</span>
                            <span>${pokemon.Attack}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Defense:</span>
                            <span>${pokemon.Defense}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Sp. Attack:</span>
                            <span>${pokemon['Sp. Atk']}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Sp. Defense:</span>
                            <span>${pokemon['Sp. Def']}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Speed:</span>
                            <span>${pokemon.Speed}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="similar-section">
                <h3>Visually Similar Pokemon</h3>
                <p class="similarity-note">Based on artwork appearance only - not stats, types, or abilities</p>
                <div class="similar-grid" id="similar-grid">
                    <!-- Similar Pokemon will be populated here -->
                </div>
            </div>
        </div>
    `;
    
    detailView.classList.remove('hidden');
    
    // Load similar Pokemon
    loadSimilarPokemon(parseInt(pokemon.ID));
    
    // Close on background click
    detailView.addEventListener('click', (e) => {
        if (e.target === detailView) {
            closePokemonDetail();
        }
    });
}

// Load and display similar Pokemon
function loadSimilarPokemon(pokemonId) {
    const similarGrid = document.getElementById('similar-grid');
    
    // Show loading state while embeddings load
    if (!embeddingsLoaded) {
        similarGrid.innerHTML = '<div class="loading-message">Loading similarity data...</div>';
        
        // Check again after a short delay
        setTimeout(() => loadSimilarPokemon(pokemonId), 500);
        return;
    }
    
    // Find similar Pokemon
    const similarPokemon = findSimilarPokemon(pokemonId, 6);
    
    // Clear the grid
    similarGrid.innerHTML = '';
    
    // Display each similar Pokemon
    similarPokemon.forEach(({ id, similarity }) => {
        const pokemon = pokemonData.find(p => parseInt(p.ID) === id);
        if (!pokemon) return;
        
        const paddedId = pokemon.ID.padStart(4, '0');
        const similarityPercent = Math.round(similarity * 100);
        
        const similarCard = document.createElement('div');
        similarCard.className = 'similar-card';
        similarCard.innerHTML = `
            <img src="pokemon_artwork/${paddedId}.png" alt="${pokemon.Name}" loading="lazy">
            <div class="similar-name">${pokemon.Name}</div>
            <div class="similarity-score">${similarityPercent}% similar</div>
        `;
        
        // Make it clickable to view that Pokemon
        similarCard.addEventListener('click', () => {
            showPokemonDetail(pokemon);
        });
        
        similarGrid.appendChild(similarCard);
    });
}

// Close Pokemon detail view
function closePokemonDetail() {
    const detailView = document.getElementById('pokemon-detail');
    detailView.classList.add('hidden');
}

// Initialize minimap
function initializeMinimap() {
    const canvas = document.getElementById('minimap-canvas');
    const ctx = canvas.getContext('2d');
    const minimap = document.getElementById('minimap');
    const viewport = document.querySelector('.minimap-viewport');
    
    // Set canvas size to match viewport height
    const updateCanvasSize = () => {
        const minmapContainer = document.getElementById('minimap');
        const containerHeight = minmapContainer.clientHeight - 20; // Account for padding
        canvas.width = 60;
        canvas.height = containerHeight;
        drawMinimap();
    };
    
    // Draw the minimap dots
    const drawMinimap = () => {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Calculate scaling to fit all Pokemon in the canvas height
        const totalHeight = document.documentElement.scrollHeight;
        const scale = canvas.height / totalHeight;
        
        // Calculate grid position for each Pokemon card
        const grid = document.getElementById('pokemon-grid');
        const allChildren = Array.from(grid.children);
        const cards = allChildren.filter(child => child.classList.contains('pokemon-card'));
        
        // Detect actual grid columns from the layout
        let gridColumns = 1;
        if (cards.length > 1) {
            const firstCardRect = cards[0].getBoundingClientRect();
            let columnsFound = 1;
            
            // Count cards in the first row
            for (let i = 1; i < cards.length; i++) {
                const cardRect = cards[i].getBoundingClientRect();
                if (Math.abs(cardRect.top - firstCardRect.top) < 5) {
                    columnsFound++;
                } else {
                    break;
                }
            }
            gridColumns = columnsFound;
        }
        
        // Calculate spacing for minimap - tighter columns
        const availableWidth = canvas.width - 20; // More margin for labels
        const dotSpacing = availableWidth / gridColumns * 0.8; // Tighter spacing
        
        // Map Pokemon data to their corresponding cards
        let cardIndex = 0;
        pokemonData.forEach((pokemon, dataIndex) => {
            if (cardIndex >= cards.length) return;
            
            const card = cards[cardIndex];
            if (!card || !card.hasAttribute('data-index') || 
                parseInt(card.getAttribute('data-index')) !== dataIndex) {
                return;
            }
            
            const cardRect = card.getBoundingClientRect();
            const cardTop = cardRect.top + window.scrollY;
            
            // Scale position to minimap
            const y = cardTop * scale;
            
            // Calculate column position based on actual grid
            const col = cardIndex % gridColumns;
            const x = col * dotSpacing + dotSpacing / 2 + 20; // Shift right for labels
            
            // Get type color
            const typeColors = {
                normal: '#A8A878', fire: '#F08030', water: '#6890F0', electric: '#F8D030',
                grass: '#78C850', ice: '#98D8D8', fighting: '#C03028', poison: '#A040A0',
                ground: '#E0C068', flying: '#A890F0', psychic: '#F85888', bug: '#A8B820',
                rock: '#B8A038', ghost: '#705898', dragon: '#7038F8', dark: '#705848',
                steel: '#B8B8D0', fairy: '#EE99AC'
            };
            
            const color = typeColors[pokemon.Type1.toLowerCase()] || '#999999';
            
            // Draw dot
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fill();
            
            cardIndex++;
        });
        
        // Draw generation separators on minimap
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.lineWidth = 1;
        ctx.font = '8px sans-serif';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        
        generationBoundaries.forEach((gen, index) => {
            // Find the card for the start of this generation
            const startIndex = pokemonData.findIndex(p => parseInt(p.ID) === gen.start);
            if (startIndex >= 0 && startIndex < cards.length) {
                const card = cards[startIndex];
                const cardRect = card.getBoundingClientRect();
                const cardTop = cardRect.top + window.scrollY;
                const y = cardTop * scale;
                
                // Draw line (except for Gen 1)
                if (index > 0) {
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(canvas.width, y);
                    ctx.stroke();
                }
                
                // Draw generation label
                const labelY = index === 0 ? y + 10 : y + 10;
                ctx.fillText(`G${gen.gen}`, 3, labelY); // Shortened to G1, G2, etc.
            }
        });
    };
    
    updateCanvasSize();
    
    // Update viewport on scroll
    function updateViewport() {
        const container = document.querySelector('.container');
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = window.scrollY / scrollHeight;
        const viewportHeight = (window.innerHeight / document.documentElement.scrollHeight) * canvas.height;
        
        viewport.style.height = Math.max(viewportHeight, 20) + 'px';
        viewport.style.top = (10 + scrollPercent * (canvas.height - viewportHeight)) + 'px';
    }
    
    // Combined click-to-jump and drag functionality
    canvas.addEventListener('mousedown', (e) => {
        const rect = canvas.getBoundingClientRect();
        const y = e.clientY - rect.top;
        const percent = y / canvas.height;
        const scrollTo = percent * (document.documentElement.scrollHeight - window.innerHeight);
        
        // Jump to clicked position
        window.scrollTo({ top: scrollTo, behavior: 'auto' });
        
        // Start dragging immediately
        isDragging = true;
        dragStartY = e.clientY;
        dragStartScrollY = scrollTo;
        viewport.classList.add('dragging');
        e.preventDefault();
    });
    
    // Make viewport draggable
    let isDragging = false;
    let dragStartY = 0;
    let dragStartScrollY = 0;
    
    viewport.addEventListener('mousedown', (e) => {
        isDragging = true;
        dragStartY = e.clientY;
        dragStartScrollY = window.scrollY;
        viewport.classList.add('dragging');
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        const deltaY = e.clientY - dragStartY;
        const canvasRect = canvas.getBoundingClientRect();
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollDelta = (deltaY / canvas.height) * scrollHeight;
        
        window.scrollTo({ top: dragStartScrollY + scrollDelta, behavior: 'auto' });
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            viewport.classList.remove('dragging');
        }
    });
    
    // Update viewport on scroll
    window.addEventListener('scroll', updateViewport);
    window.addEventListener('resize', () => {
        updateCanvasSize();
        updateViewport();
    });
    updateViewport();
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    
    // Search function
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            // If search is empty, show all Pokemon
            filteredPokemonData = [...pokemonData];
        } else {
            // Filter Pokemon by name
            filteredPokemonData = pokemonData.filter(pokemon => {
                const pokemonName = pokemon.Name.toLowerCase();
                const pokemonForm = pokemon.Form ? pokemon.Form.toLowerCase() : '';
                return pokemonName.includes(searchTerm) || pokemonForm.includes(searchTerm);
            });
        }
        
        // Re-display Pokemon with filtered data
        displayPokemon();
    }
    
    // Add event listeners
    searchButton.addEventListener('click', performSearch);
    
    // Allow search on Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Optional: Live search as user types (with debouncing)
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', loadPokemonData);