/**
 * Subtitle Converter - Frontend Application
 */

// API Base URL
const API_BASE = '';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('query');
const searchLanguage = document.getElementById('searchLanguage');
const yearInput = document.getElementById('year');
const seasonInput = document.getElementById('season');
const episodeInput = document.getElementById('episode');
const sourceLang = document.getElementById('sourceLang');
const targetLang = document.getElementById('targetLang');
const resultsCard = document.getElementById('resultsCard');
const resultsContainer = document.getElementById('resultsContainer');
const resultCount = document.getElementById('resultCount');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const searchBtn = document.getElementById('searchBtn');
const syncTimeInput = document.getElementById('syncTime');

// State
let currentResults = [];

/**
 * Show loading overlay
 */
function showLoading(text = 'Loading...') {
    loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

/**
 * Show an error message
 */
function showError(message) {
    hideLoading();
    alert(`Error: ${message}`);
}

/**
 * Search for subtitles
 */
async function searchSubtitles(event) {
    event.preventDefault();

    const query = queryInput.value.trim();
    if (!query) {
        showError('Please enter a movie or TV show name');
        return;
    }

    showLoading('Searching subtitles...');

    try {
        const params = new URLSearchParams({
            query: query,
            languages: searchLanguage.value,
        });

        if (yearInput.value) {
            params.append('year', yearInput.value);
        }
        if (seasonInput.value) {
            params.append('season', seasonInput.value);
        }
        if (episodeInput.value) {
            params.append('episode', episodeInput.value);
        }

        const response = await fetch(`${API_BASE}/api/search?${params}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Search failed');
        }

        const data = await response.json();
        currentResults = data.data || [];

        displayResults(currentResults);
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Display search results
 */
function displayResults(results) {
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultCount.textContent = 'No results found';
        resultsContainer.innerHTML = `
            <div class="info-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>No subtitles found. Try adjusting your search terms or language.</span>
            </div>
        `;
        resultsCard.style.display = 'block';
        resultsCard.classList.add('fade-in');
        return;
    }

    resultCount.textContent = `${results.length} subtitles found`;

    results.forEach((result, index) => {
        const attrs = result.attributes || {};
        const files = attrs.files || [];
        const file = files[0] || {};

        const item = document.createElement('div');
        item.className = 'result-item fade-in';
        item.style.animationDelay = `${index * 0.05}s`;

        const releaseInfo = attrs.release || 'Unknown Release';
        const language = attrs.language || 'Unknown';
        const downloads = attrs.download_count || 0;
        const fps = attrs.fps || '';
        const hearing_impaired = attrs.hearing_impaired ? '♿ HI' : '';
        const fileId = file.file_id;

        item.innerHTML = `
            <div class="result-info">
                <div class="result-title">${escapeHtml(releaseInfo)}</div>
                <div class="result-meta">
                    <span class="result-badge">${escapeHtml(language)}</span>
                    <span>📥 ${downloads.toLocaleString()} downloads</span>
                    ${fps ? `<span>🎬 ${fps} FPS</span>` : ''}
                    ${hearing_impaired ? `<span>${hearing_impaired}</span>` : ''}
                </div>
            </div>
            <div class="result-actions">
                <button class="btn btn-secondary btn-sm" onclick="downloadSubtitle(${fileId}, '${escapeHtml(releaseInfo)}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download
                </button>
                <button class="btn btn-accent btn-sm" onclick="translateAndDownload(${fileId}, '${escapeHtml(releaseInfo)}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04z"/>
                    </svg>
                    Translate
                </button>
            </div>
        `;

        resultsContainer.appendChild(item);
    });

    resultsCard.style.display = 'block';
    resultsCard.classList.add('fade-in');
}

/**
 * Download a subtitle file
 */
async function downloadSubtitle(fileId, releaseName) {
    showLoading('Downloading subtitle...');

    try {
        const syncTime = syncTimeInput.value.trim();
        let filename = sanitizeFilename(releaseName);
        if (syncTime) {
            filename += '_synced';
        }
        filename += '.srt';

        const requestBody = {
            file_id: fileId,
            filename: filename,
        };

        // Add sync time if provided
        if (syncTime) {
            requestBody.sync_time = syncTime;
        }

        const response = await fetch(`${API_BASE}/api/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Download failed');
        }

        // Get the content and trigger download
        const content = await response.text();
        triggerDownload(content, filename, 'text/plain');

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Translate and download a subtitle file
 */
async function translateAndDownload(fileId, releaseName) {
    const source = sourceLang.value;
    const target = targetLang.value;

    if (source === target) {
        showError('Source and target languages must be different');
        return;
    }

    showLoading(`Translating to ${getLanguageName(target)}...`);

    try {
        const syncTime = syncTimeInput.value.trim();
        let filename = sanitizeFilename(releaseName) + `_${target}`;
        if (syncTime) {
            filename += '_synced';
        }
        filename += '.srt';

        const requestBody = {
            file_id: fileId,
            source_lang: source,
            target_lang: target,
            filename: filename,
        };

        // Add sync time if provided
        if (syncTime) {
            requestBody.sync_time = syncTime;
        }

        const response = await fetch(`${API_BASE}/api/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Translation failed');
        }

        // Get the content and trigger download
        const content = await response.text();
        triggerDownload(content, filename, 'text/plain');

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Trigger a file download
 */
function triggerDownload(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Sanitize filename
 */
function sanitizeFilename(name) {
    return name
        .replace(/[<>:"/\\|?*]/g, '')
        .replace(/\s+/g, '_')
        .substring(0, 100);
}

/**
 * Escape HTML entities
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Get language name from code
 */
function getLanguageName(code) {
    const languages = {
        'en': 'English',
        'th': 'Thai',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
    };
    return languages[code] || code;
}

/**
 * Initialize the application
 */
function init() {
    // Search form submit
    searchForm.addEventListener('submit', searchSubtitles);

    // Enter key on input
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchSubtitles(e);
        }
    });

    // Add subtle animations on page load
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + index * 100);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
