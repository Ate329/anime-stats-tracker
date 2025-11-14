// Global state
let manifest = [];
let selectedGenres = new Set(); // Changed from single genre to Set
let allGenres = []; // Store all available genres
let filterMode = 'OR'; // 'OR' or 'AND' filter mode
let allAnimeCache = []; // Cache all anime for reuse
let allAnimePromise = null; // Track in-flight data fetch
let showHentai = false; // Default OFF
let hideNotRated = true; // Default ON
let japaneseOnly = true; // Default ON (match main app)

/**
 * Load the manifest of all available seasons
 */
async function loadManifest() {
    try {
        const response = await fetch('data/manifest.json');
        if (!response.ok) {
            throw new Error('Failed to load manifest');
        }
        manifest = await response.json();
        await loadGenres();
    } catch (error) {
        console.error('Error loading manifest:', error);
        showError('Failed to load anime data. Please refresh the page.');
    }
}

/**
 * Load all anime across the manifest (with caching)
 */
async function loadAllAnimeData() {
    if (allAnimeCache.length > 0) {
        return allAnimeCache;
    }

    if (allAnimePromise) {
        return allAnimePromise;
    }

    if (!manifest || manifest.length === 0) {
        return [];
    }

    allAnimePromise = (async () => {
        try {
            const allAnimePromises = manifest.map(async (item) => {
                try {
                    const response = await fetch(`data/${item.year}/${item.season}.json`);
                    if (!response.ok) return [];
                    const seasonData = await response.json();
                    return seasonData.map(anime => ({
                        ...anime,
                        year: item.year,
                        season: item.season
                    }));
                } catch (error) {
                    console.error(`Error fetching ${item.year} ${item.season}:`, error);
                    return [];
                }
            });

            const allAnimeArrays = await Promise.all(allAnimePromises);
            allAnimeCache = allAnimeArrays.flat();
            return allAnimeCache;
        } finally {
            allAnimePromise = null;
        }
    })();

    return allAnimePromise;
}

/**
 * Load all genres from all anime
 */
async function loadGenres() {
    try {
        const genreCounts = new Map();
        const allAnime = await loadAllAnimeData();

        allAnime.forEach(anime => {
            if (anime.genres && Array.isArray(anime.genres)) {
                anime.genres.forEach(genre => {
                    if (genre && genre !== 'Hentai') { // Exclude Hentai from genre filters
                        genreCounts.set(genre, (genreCounts.get(genre) || 0) + 1);
                    }
                });
            }
        });

        // Get top 30 genres by frequency, then sort alphabetically
        allGenres = Array.from(genreCounts.entries())
            .sort((a, b) => b[1] - a[1]) // Sort by count desc
            .slice(0, 30)                // Take top 30
            .map(entry => entry[0])      // Get genre name
            .sort();                     // Sort alphabetically

        renderGenres();
    } catch (error) {
        console.error('Error loading genres:', error);
        showError('Failed to load genres. Please refresh the page.');
    }
}

/**
 * Render genre filter buttons
 */
function renderGenres() {
    const genreContainer = document.getElementById('genre-filters');
    if (!genreContainer) return;

    genreContainer.innerHTML = allGenres.map(genre => `
        <button 
            class="genre-btn px-3 py-1.5 rounded-lg text-sm transition-all"
            style="background-color: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color);"
            data-genre="${genre}">
            ${genre}
        </button>
    `).join('');

    // Add event listeners to genre buttons
    genreContainer.querySelectorAll('.genre-btn').forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('active');
            if (button.classList.contains('active')) {
                button.style.backgroundColor = 'var(--button-bg)';
                button.style.color = 'var(--button-text)';
            } else {
                button.style.backgroundColor = 'var(--bg-secondary)';
                button.style.color = 'var(--text-primary)';
            }
        });
    });
}

/**
 * Setup random anime picker
 *
 * This function is called when the DOM is ready
 */
async function setupRandomPicker() {
    // Note: loadGenres is called by loadManifest now, which should have completed.
    
    const getRandomAnimeButton = document.getElementById('get-random-anime');
    const getAnotherButton = document.getElementById('get-another-button');
    const backButton = document.getElementById('back-button');
    
    if (getRandomAnimeButton) {
        getRandomAnimeButton.addEventListener('click', () => {
            const anime = getRandomAnime();
            displayRandomAnime(anime);
        });
    }

    if (getAnotherButton) {
        getAnotherButton.addEventListener('click', () => {
            const anime = getRandomAnime();
            displayRandomAnime(anime);
        });
    }

    if (backButton) {
        backButton.addEventListener('click', () => {
            closeRandomResult();
        });
    }
}

/**
 * Get a random anime from the manifest, applying filters
 */
function getRandomAnime() {
    const selectedGenres = new Set(
        Array.from(document.querySelectorAll('#genre-filters .genre-btn.active'))
            .map(btn => btn.dataset.genre)
    );

    const filteredAnime = allAnimeCache.filter(anime => {
        // Genre filter
        if (selectedGenres.size > 0) {
            if (!anime.genres || !anime.genres.some(genre => selectedGenres.has(genre))) {
                return false;
            }
        }
        return true;
    });

    if (filteredAnime.length === 0) {
        return null; // No anime matched criteria
    }

    const randomIndex = Math.floor(Math.random() * filteredAnime.length);
    return filteredAnime[randomIndex];
}

/**
 * Display the randomly selected anime in a card format
 * @param {object} anime - The anime object to display
 */
function displayRandomAnime(anime) {
    const resultSection = document.getElementById('result-section');
    const pickerSection = document.getElementById('picker-section');

    if (!anime) {
        resultSection.innerHTML = '<p class="text-center text-red-500">No anime found matching your criteria. Please try again with different filters.</p>';
        resultSection.classList.remove('hidden');
        pickerSection.classList.add('hidden');
        return;
    }

    // Populate the placeholder elements
    document.getElementById('anime-image').src = anime.image_url || 'https://via.placeholder.com/400x600?text=No+Image';
    document.getElementById('anime-image').alt = anime.title || 'Anime Poster';
    document.getElementById('anime-season').textContent = `${capitalize(anime.season)} ${anime.year}`;
    
    const episodesEl = document.getElementById('anime-episodes');
    if (anime.episodes) {
        episodesEl.textContent = `${anime.episodes} episodes`;
        episodesEl.classList.remove('hidden');
    } else {
        episodesEl.classList.add('hidden');
    }

    document.getElementById('anime-title').textContent = anime.title || 'Title not available';

    const scoreContainer = document.getElementById('anime-score-container');
    const scoreEl = document.getElementById('anime-score');
    if (anime.score) {
        scoreEl.textContent = anime.score.toFixed(2);
        scoreContainer.classList.remove('hidden');
    } else {
        scoreContainer.classList.add('hidden');
    }
    
    const ratingContainer = document.getElementById('anime-rating-container');
    const ratingEl = document.getElementById('anime-rating');
    if (anime.rating) {
        ratingEl.textContent = anime.rating;
        ratingContainer.classList.remove('hidden');
    } else {
        ratingContainer.classList.add('hidden');
    }

    document.getElementById('anime-synopsis').textContent = anime.synopsis || 'No synopsis available.';
    
    const studio = Array.isArray(anime.studios) ? anime.studios.map(s => s.name).join(', ') : (anime.studios?.name || 'Unknown');
    document.getElementById('anime-studio').textContent = studio;

    document.getElementById('anime-source').textContent = anime.source || 'Unknown';
    document.getElementById('anime-genres').textContent = anime.genres && anime.genres.length > 0 ? anime.genres.join(', ') : 'None';
    document.getElementById('anime-themes').textContent = anime.themes && anime.themes.length > 0 ? anime.themes.join(', ') : 'None';

    // Show the result section and hide the picker
    resultSection.classList.remove('hidden');
    pickerSection.classList.add('hidden');
}

/**
 * Close random anime result and return to picker
 */
function closeRandomResult() {
    const resultSection = document.getElementById('result-section');
    const pickerSection = document.getElementById('picker-section');

    resultSection.classList.add('hidden');
    pickerSection.classList.remove('hidden');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Show error message
 */
function showError(message) {
    const resultCard = document.getElementById('random-result-card');
    resultCard.innerHTML = `
        <div class="text-center py-16 rounded-xl" style="background-color: var(--bg-secondary); border: 2px solid var(--border-color);">
            <div class="text-6xl mb-4">❌</div>
            <p class="text-2xl font-bold mb-2" style="color: var(--text-primary);">Error</p>
            <p class="text-lg" style="color: var(--text-secondary);">${message}</p>
        </div>
    `;
}

/**
 * Capitalize first letter of a string
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    await loadManifest();
    setupRandomPicker();
});

