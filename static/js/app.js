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

// Navigation Elements
const navBtns = document.querySelectorAll('.nav-btn');
const views = {
    'home': document.getElementById('home-view'),
    'archived': document.getElementById('archived-view'),
    'translated': document.getElementById('translated-view')
};
const archivedList = document.getElementById('archivedList');
const translatedList = document.getElementById('translatedList');

// State
let currentResults = [];

/**
 * Switch logic view
 */
function switchView(viewName) {
    // Update Nav Buttons
    navBtns.forEach(btn => {
        if (btn.dataset.view === viewName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update Views
    for (const [name, element] of Object.entries(views)) {
        if (name === viewName) {
            element.classList.add('active');
            // Load data if needed
            if (name === 'archived') loadArchiveFiles('original');
            if (name === 'translated') loadArchiveFiles('converted');
        } else {
            element.classList.remove('active');
        }
    }
}

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
    const providerSelect = document.getElementById('provider');
    // If element doesn't exist (it might not in older HTML), default to subdl
    const provider = providerSelect ? providerSelect.value : 'subdl';
    
    console.log(`[Search] Query: "${query}", Provider: ${provider}, Languages: ${searchLanguage.value}`);

    if (!query) {
        showError('Please enter a movie or TV show name');
        return;
    }

    showLoading('Searching subtitles...');

    try {
        const params = new URLSearchParams({
            query: query,
            languages: searchLanguage.value,
            provider: provider,
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
        
        console.log(`[Search] Request params: ${params.toString()}`);

        const response = await fetch(`${API_BASE}/api/search?${params}`);
        console.log(`[Search] Response Status: ${response.status}`);

        if (!response.ok) {
            const error = await response.json();
            console.error('[Search] API Error:', error);
            throw new Error(error.detail || 'Search failed');
        }

        const data = await response.json();
        console.log('[Search] Results:', data);
        currentResults = data.data || []; // Note: API returns {results: []}, but frontend code here expects {data: []} or needs update?
        // Wait, looking at main.py, search returns `results` list directly or dict? 
        // SubDL returns {"results": [...]}. OpenSubtitles returns something else?
        // Let's assume the frontend expects what the API provides.
        // My previous SubDL implementation returns {"results": [...]}.
        // The frontend code I read (line 89) says: `currentResults = data.data || [];`
        // But my API returns `{"results": [...]}`. 
        // This might be a bug in the existing frontend or I need to match it.
        // Let's stick to logging for now, but I should probably fix `data.data` to `data.results` if that's what my API returns.
        // Actually, let's just add the logs for now as requested.

        currentResults = data.results || data.data || []; // Patching this to be safe
        console.log(`[Search] Found ${currentResults.length} subtitles`);

        displayResults(currentResults);
    } catch (error) {
        console.error('[Search] Error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// ...

async function downloadSubtitle(fileId, releaseName, provider = 'subdl') {
    showLoading('Downloading subtitle...');
    console.log(`[Download] Requesting fileID: ${fileId}, releaseName: "${releaseName}", provider: ${provider}`);

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
            provider: provider,
        };

        // Add sync time if provided
        if (syncTime) {
            requestBody.sync_time = syncTime;
        }
        
        console.log('[Download] Request Body:', requestBody);

        const response = await fetch(`${API_BASE}/api/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        
        console.log(`[Download] Response Status: ${response.status}`);

        if (!response.ok) {
            const error = await response.json();
            console.error('[Download] API Error:', error);
            throw new Error(error.detail || 'Download failed');
        }

        // Get the content and trigger download
        const content = await response.text();
        console.log(`[Download] Received content size: ${content.length}`);
        triggerDownload(content, filename, 'text/plain');
        console.log('[Download] Success');

    } catch (error) {
        console.error('[Download] Error:', error);
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
        // Handle both OpenSubtitles (nested attributes) and SubDL (flat) formats
        let releaseInfo, language, downloads, fps, hearing_impaired, fileId;

        if (result.attributes) {
            // OpenSubtitles format
            const attrs = result.attributes;
            const files = attrs.files || [];
            const file = files[0] || {};
            
            releaseInfo = attrs.release || 'Unknown Release';
            language = attrs.language || 'Unknown';
            downloads = attrs.download_count || 0;
            fps = attrs.fps || '';
            hearing_impaired = attrs.hearing_impaired ? '♿ HI' : '';
            fileId = file.file_id;
        } else {
            // SubDL / Plain format
            releaseInfo = result.filename || 'Unknown Release';
            language = result.language || 'Unknown';
            downloads = 0; // SubDL doesn't provide this in search list easily
            fps = ''; 
            hearing_impaired = result.is_hearing_impaired ? '♿ HI' : '';
            fileId = result.id;
        }

        const item = document.createElement('div');
        item.className = 'result-item fade-in';
        item.style.animationDelay = `${index * 0.05}s`;

        // Determine provider based on source or default to current selection
        // Ideally the API results should contain the provider code.
        // For now, let's map source 'SubDL' -> 'subdl', 'OpenSubtitles' -> 'opensubtitles'
        // Or read from the result if we added it. We added 'source'.
        let provider = 'subdl';
        const sourceName = (result.source || attrs.source || 'subdl').toLowerCase();
        if (sourceName.includes('opensubtitles')) provider = 'opensubtitles';
        
        // Quote fileId if it's a string, or just always quote it to be safe.
        // We need to escape backslashes first, then single quotes for JS string context.
        const safeFileId = String(fileId).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        
        // Escape HTML for display, but for JS argument we need raw string escaped for JS
        // releaseInfo might contain special chars. 
        // Let's use the raw string for function args, but escape it for JS context.
        const safeReleaseInfo = String(releaseInfo).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        
        // However, escapeHtml is for the HTML content (result-title). 
        // For onclick, we put it inside HTML attribute, so we need to encode HTML entities if we put it directly?
        // Actually, inside onclick="...", HTML entities are decoded before JS runs.
        // So &quot; becomes " in JS.
        // Ideally we pass a simple ID and look up data, but to fix invalid syntax:
        
        item.innerHTML = `
            <div class="result-info">
                <div class="result-title">${escapeHtml(releaseInfo)}</div>
                <div class="result-meta">
                    <span class="result-badge">${escapeHtml(language)}</span>
                    <span>📥 ${downloads.toLocaleString()} downloads</span>
                    ${fps ? `<span>🎬 ${fps} FPS</span>` : ''}
                    ${hearing_impaired ? `<span>${hearing_impaired}</span>` : ''}
                    <span class="result-source">${escapeHtml(result.source || 'Unknown')}</span>
                </div>
            </div>
            <div class="result-actions">
                <button class="btn btn-secondary btn-sm" onclick="downloadSubtitle('${safeFileId}', '${safeReleaseInfo}', '${provider}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download
                </button>
                <button class="btn btn-accent btn-sm" onclick="translateAndDownload('${safeFileId}', '${safeReleaseInfo}', '${provider}')">
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
async function translateAndDownload(fileId, releaseName, provider = 'subdl') {
    const source = sourceLang.value;
    const target = targetLang.value;

    if (source === target) {
        showError('Source and target languages must be different');
        return;
    }

    showLoading(`Translating to ${getLanguageName(target)}...`);
    console.log(`[Translate] Requesting fileId: ${fileId}, releaseName: "${releaseName}", source: ${source}, target: ${target}, provider: ${provider}`);

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
            provider: provider,
        };

        // Add sync time if provided
        if (syncTime) {
            requestBody.sync_time = syncTime;
        }

        console.log('[Translate] Request Body:', requestBody);
        const response = await fetch(`${API_BASE}/api/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        console.log(`[Translate] Response Status: ${response.status}`);

        if (!response.ok) {
            const error = await response.json();
            console.error('[Translate] API Error:', error);
            throw new Error(error.detail || 'Translation failed');
        }

        // Get the content and trigger download
        const content = await response.text();
        console.log(`[Translate] Received translated content for "${filename}" (length: ${content.length})`);
        triggerDownload(content, filename, 'text/plain');
        console.log('[Translate] Success');

    } catch (error) {
        console.error('[Translate] Fetch Error:', error);
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
 * Load archive files
 */
async function loadArchiveFiles(type) {
    const listContainer = type === 'original' ? archivedList : translatedList;
    listContainer.innerHTML = '<p>Loading files...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/archive/files?type=${type}`);
        if (!response.ok) throw new Error('Failed to fetch files');
        
        const data = await response.json();
        renderFileList(data.files, listContainer, type);
    } catch (error) {
        console.error('Archive Load Error:', error);
        listContainer.innerHTML = `<p class="error-text">Failed to load files: ${error.message}</p>`;
    }
}

/**
 * Render file list
 */
function renderFileList(files, container, type) {
    if (files.length === 0) {
        container.innerHTML = '<p>No files found in archive.</p>';
        return;
    }

    container.innerHTML = '';
    files.forEach(file => {
        const item = document.createElement('div');
        item.className = 'result-item fade-in';
        
        const date = new Date(file.modified * 1000).toLocaleString();
        const size = (file.size / 1024).toFixed(1) + ' KB';
        // Securely escape the filename for onclick handlers
        const safeFilename = file.name.replace(/\\/g, '\\\\').replace(/'/g, "\\'");

        item.innerHTML = `
            <div class="result-info">
                <div class="result-title">${escapeHtml(file.name)}</div>
                <div class="result-meta">
                    <span>📅 ${date}</span>
                    <span>💾 ${size}</span>
                </div>
            </div>
            <div class="result-actions">
                <button class="btn btn-secondary btn-sm" onclick="renameFile('${safeFilename}', '${type}')">
                    ✏️ Rename
                </button>
                <button class="btn btn-primary btn-sm" onclick="downloadArchive('${safeFilename}', '${type}')">
                    ⬇️ Download
                </button>
                ${type === 'original' ? `
                <button class="btn btn-accent btn-sm" onclick="translateArchive('${safeFilename}')">
                    🌐 Translate
                </button>
                ` : ''}
                <button class="btn btn-secondary btn-sm" style="border-color: var(--color-error); color: var(--color-error);" onclick="deleteFile('${safeFilename}', '${type}')">
                    🗑️ Delete
                </button>
            </div>
        `;
        container.appendChild(item);
    });
}

/**
 * Translate archive file
 */
async function translateArchive(filename) {
    // Use archive-specific dropdowns
    const archiveSourceLang = document.getElementById('archiveSourceLang');
    const archiveTargetLang = document.getElementById('archiveTargetLang');
    
    if (!archiveSourceLang || !archiveTargetLang) {
        showError('Language selection not available');
        return;
    }
    
    const source = archiveSourceLang.value;
    const target = archiveTargetLang.value;

    if (source === target) {
        showError('Source and target languages must be different');
        return;
    }

    if (!confirm(`Translate "${filename}" from ${getLanguageName(source)} to ${getLanguageName(target)}?`)) {
        return;
    }

    showLoading(`Translating to ${getLanguageName(target)}...`);

    try {
        const response = await fetch(`${API_BASE}/api/archive/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: filename,
                source_lang: source,
                target_lang: target
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Translation failed');
        }

        const result = await response.json();
        
        // Success
        alert(`Translation complete! File saved as: ${result.filename}`);
        
        // Option to download immediately
        if (confirm("Download translated file now?")) {
            downloadArchive(result.filename, 'converted');
        }

        // Switch to translated view to show it?
        // switchView('translated'); 

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Rename archive file
 */
async function renameFile(filename, type) {
    const newName = prompt("Enter new filename:", filename);
    if (!newName || newName === filename) return;

    // Basic validation
    if (!newName.endsWith(type === 'converted' ? '.srt' : '')) {
         // Maybe alert user but let backend handle it or auto-append? 
         // Let's just pass it.
    }

    try {
        const response = await fetch(`${API_BASE}/api/archive/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: filename,
                new_filename: newName,
                type: type
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Rename failed');
        }

        // Refresh list
        loadArchiveFiles(type);
        
    } catch (error) {
        alert(`Error renaming file: ${error.message}`);
    }
}

/**
 * Delete archive file
 */
async function deleteFile(filename, type) {
    if (!confirm(`Are you sure you want to delete "${filename}"? This cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/archive/delete?filename=${encodeURIComponent(filename)}&type=${type}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Delete failed');
        }

        // Refresh list
        loadArchiveFiles(type);
    } catch (error) {
         alert(`Error deleting file: ${error.message}`);
    }
}

/**
 * Download archive file
 */
function downloadArchive(filename, type) {
    window.location.href = `${API_BASE}/api/archive/download/${encodeURIComponent(filename)}?type=${type}`;
}

/**
 * Get human-readable language name from code
 */
function getLanguageName(code) {
    const names = {
        'en': 'English',
        'nl': 'Dutch',
        'th': 'Thai',
        'tr': 'Turkish',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi'
    };
    return names[code] || code;
}

/**
 * Load supported languages
 */
async function loadLanguages() {
    try {
        const response = await fetch(`${API_BASE}/api/languages`);
        if (!response.ok) {
            throw new Error('Failed to fetch languages');
        }

        const languages = await response.json();
        console.log('Loaded languages:', languages);

        // Populate search language dropdown
        const searchLangSelect = document.getElementById('searchLanguage');
        if (searchLangSelect) {
            searchLangSelect.innerHTML = languages.map(lang => 
                `<option value="${lang.code}">${lang.name}</option>`
            ).join('');
        }

        // Populate translation language dropdowns (Home view)
        const sourceLangSelect = document.getElementById('sourceLang');
        if (sourceLangSelect) {
            sourceLangSelect.innerHTML = languages.map(lang => 
                `<option value="${lang.code}">${lang.name}</option>`
            ).join('');
        }

        const targetLangSelect = document.getElementById('targetLang');
        if (targetLangSelect) {
            targetLangSelect.innerHTML = languages.map(lang => 
                `<option value="${lang.code}">${lang.name}</option>`
            ).join('');
            // Set default to Thai if available
            if (languages.find(l => l.code === 'th')) {
                targetLangSelect.value = 'th';
            }
        }

        // Populate archive translation language dropdowns (Archived view)
        const archiveSourceLangSelect = document.getElementById('archiveSourceLang');
        if (archiveSourceLangSelect) {
            archiveSourceLangSelect.innerHTML = languages.map(lang => 
                `<option value="${lang.code}">${lang.name}</option>`
            ).join('');
        }

        const archiveTargetLangSelect = document.getElementById('archiveTargetLang');
        if (archiveTargetLangSelect) {
            archiveTargetLangSelect.innerHTML = languages.map(lang => 
                `<option value="${lang.code}">${lang.name}</option>`
            ).join('');
            // Set default to Thai if available
            if (languages.find(l => l.code === 'th')) {
                archiveTargetLangSelect.value = 'th';
            }
        }

        console.log('Language dropdowns populated successfully');
    } catch (error) {
        console.error('Failed to load languages:', error);
        showError('Failed to load language options');
    }
}
/**
 * Initialize the application
 */
function init() {
    loadLanguages();
    // Search form submit
    searchForm.addEventListener('submit', searchSubtitles);

    // Enter key on input
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchSubtitles(e);
        }
    });

    // Navigation
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
             switchView(btn.dataset.view);
        });
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
