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
    
    pokemonData.forEach((pokemon, index) => {
        const card = createPokemonCard(pokemon);
        card.setAttribute('data-index', index);
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
                <h3>Similar Pokemon</h3>
                <div class="similar-grid">
                    <div class="similar-placeholder">Similar Pokemon #1<br>(Coming Soon)</div>
                    <div class="similar-placeholder">Similar Pokemon #2<br>(Coming Soon)</div>
                    <div class="similar-placeholder">Similar Pokemon #3<br>(Coming Soon)</div>
                    <div class="similar-placeholder">Similar Pokemon #4<br>(Coming Soon)</div>
                    <div class="similar-placeholder">Similar Pokemon #5<br>(Coming Soon)</div>
                    <div class="similar-placeholder">Similar Pokemon #6<br>(Coming Soon)</div>
                </div>
            </div>
        </div>
    `;
    
    detailView.classList.remove('hidden');
    
    // Close on background click
    detailView.addEventListener('click', (e) => {
        if (e.target === detailView) {
            closePokemonDetail();
        }
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
        const cards = grid.children;
        
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
        
        // Calculate spacing for minimap
        const availableWidth = canvas.width - 10; // Leave some margin
        const dotSpacing = availableWidth / gridColumns;
        
        pokemonData.forEach((pokemon, index) => {
            if (index >= cards.length) return;
            
            const card = cards[index];
            const cardRect = card.getBoundingClientRect();
            const cardTop = cardRect.top + window.scrollY;
            
            // Scale position to minimap
            const y = cardTop * scale;
            
            // Calculate column position based on actual grid
            const col = index % gridColumns;
            const x = col * dotSpacing + dotSpacing / 2 + 5;
            
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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', loadPokemonData);