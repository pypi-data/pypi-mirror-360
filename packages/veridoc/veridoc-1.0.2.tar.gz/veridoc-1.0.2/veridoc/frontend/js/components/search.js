/**
 * VeriDoc Search Component
 * Global search functionality for files and content
 */

class SearchComponent {
    constructor(searchInput, apiClient) {
        this.searchInput = searchInput;
        this.api = apiClient;
        this.searchTimeout = null;
        this.currentQuery = '';
        this.searchResults = [];
        this.isSearching = false;
        
        this.init();
    }

    /**
     * Initialize search component
     */
    init() {
        this.createSearchResultsPanel();
        this.bindEvents();
    }

    /**
     * Create search results panel
     */
    createSearchResultsPanel() {
        // Remove existing panel
        const existing = document.getElementById('search-results-panel');
        if (existing) {
            existing.remove();
        }

        const panel = document.createElement('div');
        panel.id = 'search-results-panel';
        panel.className = 'search-results-panel';
        panel.style.display = 'none';
        
        panel.innerHTML = `
            <div class="search-results-header">
                <span class="search-results-title">Search Results</span>
                <button class="panel-btn" id="search-close">×</button>
            </div>
            <div class="search-results-content" id="search-results-content">
                <!-- Results will be populated here -->
            </div>
        `;

        document.body.appendChild(panel);
        this.resultsPanel = panel;
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        this.searchInput.addEventListener('keydown', (e) => {
            this.handleSearchKeydown(e);
        });

        this.searchInput.addEventListener('focus', () => {
            if (this.currentQuery && this.searchResults.length > 0) {
                this.showResults();
            }
        });

        // Clear button
        const clearBtn = document.getElementById('search-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Close button
        const closeBtn = document.getElementById('search-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hideResults();
            });
        }

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.resultsPanel.contains(e.target) && 
                !this.searchInput.contains(e.target)) {
                this.hideResults();
            }
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults();
            }
        });
    }

    /**
     * Handle search input changes
     */
    handleSearchInput(query) {
        // Clear existing timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.currentQuery = query.trim();

        // Show/hide clear button
        const clearBtn = document.getElementById('search-clear');
        if (clearBtn) {
            clearBtn.style.opacity = this.currentQuery ? '0.7' : '0';
        }

        if (!this.currentQuery) {
            this.hideResults();
            return;
        }

        // Debounce search
        this.searchTimeout = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, 300);
    }

    /**
     * Handle keyboard navigation in search
     */
    handleSearchKeydown(e) {
        const resultItems = this.resultsPanel.querySelectorAll('.search-result-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateResults(1, resultItems);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateResults(-1, resultItems);
                break;
            case 'Enter':
                e.preventDefault();
                const selected = this.resultsPanel.querySelector('.search-result-item.selected');
                if (selected) {
                    this.selectSearchResult(selected);
                }
                break;
            case 'Escape':
                e.preventDefault();
                this.hideResults();
                break;
        }
    }

    /**
     * Navigate through search results with keyboard
     */
    navigateResults(direction, resultItems) {
        if (resultItems.length === 0) return;

        const currentSelected = this.resultsPanel.querySelector('.search-result-item.selected');
        let newIndex = 0;

        if (currentSelected) {
            const currentIndex = Array.from(resultItems).indexOf(currentSelected);
            newIndex = currentIndex + direction;
            
            if (newIndex < 0) newIndex = resultItems.length - 1;
            if (newIndex >= resultItems.length) newIndex = 0;
            
            currentSelected.classList.remove('selected');
        }

        resultItems[newIndex].classList.add('selected');
        resultItems[newIndex].scrollIntoView({ block: 'nearest' });
    }

    /**
     * Perform search request
     */
    async performSearch(query) {
        if (this.isSearching) return;

        try {
            this.isSearching = true;
            this.showSearchingState();

            const results = await this.api.search(query, {
                type: 'both',
                limit: 50
            });

            this.searchResults = results.results || [];
            this.renderSearchResults(query, this.searchResults);
            this.showResults();

        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError(error);
        } finally {
            this.isSearching = false;
        }
    }

    /**
     * Render search results
     */
    renderSearchResults(query, results) {
        const content = document.getElementById('search-results-content');
        if (!content) return;

        if (results.length === 0) {
            content.innerHTML = `
                <div class="search-no-results">
                    <div class="search-no-results-icon">🔍</div>
                    <div class="search-no-results-text">No results found for "${this.escapeHtml(query)}"</div>
                </div>
            `;
            return;
        }

        const resultsHTML = `
            <div class="search-results-summary">
                Found ${results.length} result${results.length === 1 ? '' : 's'} for "${this.escapeHtml(query)}"
            </div>
            <div class="search-results-list">
                ${results.map((result, index) => this.renderSearchResult(result, index)).join('')}
            </div>
        `;

        content.innerHTML = resultsHTML;

        // Bind click events
        content.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSearchResult(item);
            });
        });
    }

    /**
     * Render individual search result
     */
    renderSearchResult(result, index) {
        const icon = this.getFileIcon(result.path);
        const fileName = result.path.split('/').pop();
        const directory = result.path.substring(0, result.path.lastIndexOf('/')) || '/';
        
        const snippet = result.snippet 
            ? this.highlightSearchTerms(result.snippet, this.currentQuery)
            : '';

        const lineInfo = result.line_number 
            ? `<span class="search-result-line">Line ${result.line_number}</span>`
            : '';

        return `
            <div class="search-result-item" data-path="${this.escapeHtml(result.path)}" data-line="${result.line_number || ''}" ${index === 0 ? 'class="selected"' : ''}>
                <div class="search-result-main">
                    <div class="search-result-icon">${icon}</div>
                    <div class="search-result-content">
                        <div class="search-result-title">
                            <span class="search-result-filename">${this.escapeHtml(fileName)}</span>
                            ${lineInfo}
                        </div>
                        <div class="search-result-path">${this.escapeHtml(directory)}</div>
                        ${snippet ? `<div class="search-result-snippet">${snippet}</div>` : ''}
                    </div>
                </div>
                <div class="search-result-meta">
                    <span class="search-result-type">${result.match_type}</span>
                    <span class="search-result-score">${Math.round(result.score * 100)}%</span>
                </div>
            </div>
        `;
    }

    /**
     * Show searching state
     */
    showSearchingState() {
        const content = document.getElementById('search-results-content');
        if (content) {
            content.innerHTML = `
                <div class="search-loading">
                    <div class="search-loading-spinner"></div>
                    <div class="search-loading-text">Searching...</div>
                </div>
            `;
        }
        this.showResults();
    }

    /**
     * Show search error
     */
    showSearchError(error) {
        const content = document.getElementById('search-results-content');
        if (content) {
            content.innerHTML = `
                <div class="search-error">
                    <div class="search-error-icon">⚠️</div>
                    <div class="search-error-text">Search failed: ${error.getUserMessage()}</div>
                </div>
            `;
        }
        this.showResults();
    }

    /**
     * Show search results panel
     */
    showResults() {
        if (this.resultsPanel) {
            this.resultsPanel.style.display = 'block';
            this.positionResultsPanel();
        }
    }

    /**
     * Hide search results panel
     */
    hideResults() {
        if (this.resultsPanel) {
            this.resultsPanel.style.display = 'none';
        }
    }

    /**
     * Position results panel relative to search input
     */
    positionResultsPanel() {
        if (!this.resultsPanel || !this.searchInput) return;

        const inputRect = this.searchInput.getBoundingClientRect();
        const panelHeight = Math.min(400, window.innerHeight * 0.6);
        
        this.resultsPanel.style.position = 'fixed';
        this.resultsPanel.style.top = `${inputRect.bottom + 5}px`;
        this.resultsPanel.style.left = `${inputRect.left}px`;
        this.resultsPanel.style.width = `${Math.max(400, inputRect.width)}px`;
        this.resultsPanel.style.maxHeight = `${panelHeight}px`;
        this.resultsPanel.style.zIndex = '1000';
    }

    /**
     * Handle search result selection
     */
    selectSearchResult(item) {
        const path = item.dataset.path;
        const line = item.dataset.line;

        // Emit selection event
        const event = new CustomEvent('search:select', {
            detail: {
                path,
                line: line ? parseInt(line) : null
            }
        });
        
        document.dispatchEvent(event);
        this.hideResults();
    }

    /**
     * Clear search
     */
    clearSearch() {
        this.searchInput.value = '';
        this.currentQuery = '';
        this.searchResults = [];
        this.hideResults();
        
        const clearBtn = document.getElementById('search-clear');
        if (clearBtn) {
            clearBtn.style.opacity = '0';
        }
    }

    /**
     * Highlight search terms in text
     */
    highlightSearchTerms(text, query) {
        if (!query || !text) return this.escapeHtml(text);

        const escapedQuery = this.escapeRegex(query);
        const regex = new RegExp(`(${escapedQuery})`, 'gi');
        
        return this.escapeHtml(text).replace(regex, '<mark>$1</mark>');
    }

    /**
     * Get file icon based on path
     */
    getFileIcon(path) {
        const extension = path.split('.').pop()?.toLowerCase();
        
        const iconMap = {
            'md': '📄', 'markdown': '📄', 'mdown': '📄', 'mkd': '📄',
            'mmd': '📊', 'mermaid': '📊',
            'py': '💻', 'js': '💻', 'ts': '💻', 'html': '💻', 'css': '💻',
            'json': '💻', 'yaml': '💻', 'yml': '💻', 'xml': '💻',
            'txt': '📋', 'text': '📋', 'log': '📋',
            'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️', 'gif': '🖼️', 'svg': '🖼️',
            'zip': '📦', 'tar': '📦', 'gz': '📦'
        };

        return iconMap[extension] || '📄';
    }

    /**
     * Focus search input
     */
    focus() {
        this.searchInput.focus();
    }

    /**
     * Set search query programmatically
     */
    setQuery(query) {
        this.searchInput.value = query;
        this.handleSearchInput(query);
    }

    /**
     * Get current search query
     */
    getQuery() {
        return this.currentQuery;
    }

    /**
     * Utility functions
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// CSS for search component
const searchCSS = `
    .search-results-panel {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 6px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        overflow: hidden;
    }

    .search-results-header {
        background: var(--bg-tertiary);
        border-bottom: 1px solid var(--border);
        padding: var(--spacing-sm) var(--spacing-md);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .search-results-title {
        font-size: var(--font-size-sm);
        font-weight: 600;
        color: var(--text-secondary);
    }

    .search-results-content {
        max-height: 350px;
        overflow-y: auto;
        padding: var(--spacing-sm);
    }

    .search-results-summary {
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border);
        margin-bottom: var(--spacing-sm);
    }

    .search-result-item {
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: 4px;
        cursor: pointer;
        transition: all var(--transition-fast);
        margin-bottom: 2px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .search-result-item:hover,
    .search-result-item.selected {
        background: var(--bg-tertiary);
    }

    .search-result-main {
        display: flex;
        align-items: flex-start;
        gap: var(--spacing-sm);
        flex: 1;
        min-width: 0;
    }

    .search-result-icon {
        font-size: 16px;
        margin-top: 2px;
        flex-shrink: 0;
    }

    .search-result-content {
        flex: 1;
        min-width: 0;
    }

    .search-result-title {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: 2px;
    }

    .search-result-filename {
        font-weight: 500;
        color: var(--text-accent);
    }

    .search-result-line {
        font-size: var(--font-size-xs);
        color: var(--accent-blue);
        background: rgba(0, 122, 204, 0.1);
        padding: 1px 4px;
        border-radius: 2px;
    }

    .search-result-path {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .search-result-snippet {
        font-size: var(--font-size-xs);
        color: var(--text-primary);
        background: var(--bg-primary);
        padding: 4px 6px;
        border-radius: 3px;
        border-left: 2px solid var(--accent-blue);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .search-result-snippet mark {
        background: var(--accent-yellow);
        color: var(--bg-primary);
        padding: 0 1px;
        border-radius: 1px;
    }

    .search-result-meta {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
        flex-shrink: 0;
        margin-left: var(--spacing-sm);
    }

    .search-result-type {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
        text-transform: capitalize;
    }

    .search-result-score {
        font-size: var(--font-size-xs);
        color: var(--accent-green);
        font-weight: 500;
    }

    .search-no-results,
    .search-error,
    .search-loading {
        text-align: center;
        padding: var(--spacing-xl);
        color: var(--text-secondary);
    }

    .search-no-results-icon,
    .search-error-icon {
        font-size: 32px;
        margin-bottom: var(--spacing-sm);
    }

    .search-loading-spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--border);
        border-top: 2px solid var(--accent-blue);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto var(--spacing-sm);
    }

    .search-error-icon {
        color: var(--accent-red);
    }
`;

// Inject CSS
const searchStyle = document.createElement('style');
searchStyle.textContent = searchCSS;
document.head.appendChild(searchStyle);

// Export for use in other modules
window.SearchComponent = SearchComponent;