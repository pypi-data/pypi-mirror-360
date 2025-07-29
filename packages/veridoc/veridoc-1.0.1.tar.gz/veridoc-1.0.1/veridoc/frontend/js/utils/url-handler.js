/**
 * VeriDoc URL Handler
 * Manages URL-based navigation and deep linking
 */

class UrlHandler {
    constructor() {
        this.listeners = new Map();
        this.init();
    }

    /**
     * Initialize URL handler
     */
    init() {
        // Listen for popstate events (back/forward navigation)
        window.addEventListener('popstate', (e) => {
            this.handlePopState(e);
        });

        // Parse initial URL
        this.parseCurrentUrl();
    }

    /**
     * Parse current URL and extract parameters
     */
    parseCurrentUrl() {
        const params = this.getUrlParams();
        
        if (params.path) {
            this.emit('navigate', {
                path: params.path,
                line: params.line ? parseInt(params.line) : null,
                search: params.search
            });
        }
    }

    /**
     * Get URL parameters
     */
    getUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        return {
            path: urlParams.get('path'),
            line: urlParams.get('line'),
            search: urlParams.get('search'),
            type: urlParams.get('type'),
            extensions: urlParams.get('extensions'),
            limit: urlParams.get('limit')
        };
    }

    /**
     * Update URL without triggering navigation
     */
    updateUrl(params, replace = false) {
        const url = this.buildUrl(params);
        
        if (replace) {
            history.replaceState(params, '', url);
        } else {
            history.pushState(params, '', url);
        }
    }

    /**
     * Navigate to path and update URL
     */
    navigateTo(path, options = {}) {
        const params = {
            path,
            ...options
        };

        this.updateUrl(params);
        this.emit('navigate', params);
    }

    /**
     * Navigate to search results
     */
    searchFor(query, options = {}) {
        const params = {
            search: query,
            type: options.type || 'both',
            ...options
        };

        this.updateUrl(params);
        this.emit('search', params);
    }

    /**
     * Build URL from parameters
     */
    buildUrl(params) {
        const baseUrl = window.location.pathname;
        const searchParams = new URLSearchParams();

        // Add non-empty parameters
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                searchParams.set(key, value);
            }
        });

        const queryString = searchParams.toString();
        return queryString ? `${baseUrl}?${queryString}` : baseUrl;
    }

    /**
     * Handle browser back/forward navigation
     */
    handlePopState(e) {
        if (e.state) {
            this.emit('navigate', e.state);
        } else {
            this.parseCurrentUrl();
        }
    }

    /**
     * Get current navigation state
     */
    getCurrentState() {
        return this.getUrlParams();
    }

    /**
     * Clear URL parameters
     */
    clearUrl() {
        const baseUrl = window.location.pathname;
        history.replaceState({}, '', baseUrl);
    }

    /**
     * Check if current URL has specific parameter
     */
    hasParam(name) {
        const params = this.getUrlParams();
        return params[name] !== null;
    }

    /**
     * Get specific URL parameter
     */
    getParam(name) {
        const params = this.getUrlParams();
        return params[name];
    }

    /**
     * Register event listener
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    /**
     * Emit event to listeners
     */
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`URL handler event error (${event}):`, error);
                }
            });
        }
    }

    /**
     * Generate shareable URL for current state
     */
    getShareableUrl(params = null) {
        const urlParams = params || this.getUrlParams();
        return window.location.origin + this.buildUrl(urlParams);
    }

    /**
     * Copy current URL to clipboard
     */
    async copyCurrentUrl() {
        try {
            const url = this.getShareableUrl();
            await navigator.clipboard.writeText(url);
            return true;
        } catch (error) {
            console.error('Failed to copy URL:', error);
            return false;
        }
    }

    /**
     * Parse file path from various URL formats
     */
    parseFilePath(url) {
        try {
            const urlObj = new URL(url, window.location.origin);
            const params = new URLSearchParams(urlObj.search);
            return params.get('path');
        } catch (error) {
            // Try to extract path from hash or pathname
            if (url.includes('#')) {
                return url.split('#')[1];
            }
            return url;
        }
    }

    /**
     * Generate deep link to specific line in file
     */
    getLineUrl(path, lineNumber) {
        return this.getShareableUrl({
            path,
            line: lineNumber
        });
    }

    /**
     * Generate search URL
     */
    getSearchUrl(query, options = {}) {
        return this.getShareableUrl({
            search: query,
            type: options.type || 'both',
            ...options
        });
    }

    /**
     * Validate URL parameters
     */
    validateParams(params) {
        const errors = [];

        // Validate path
        if (params.path) {
            if (typeof params.path !== 'string') {
                errors.push('Path must be a string');
            } else if (params.path.includes('..')) {
                errors.push('Path cannot contain ".." segments');
            } else if (params.path.includes('\0')) {
                errors.push('Path cannot contain null bytes');
            }
        }

        // Validate line number
        if (params.line) {
            const lineNum = parseInt(params.line);
            if (isNaN(lineNum) || lineNum < 1) {
                errors.push('Line number must be a positive integer');
            }
        }

        // Validate search type
        if (params.type && !['filename', 'content', 'both'].includes(params.type)) {
            errors.push('Search type must be "filename", "content", or "both"');
        }

        // Validate limit
        if (params.limit) {
            const limit = parseInt(params.limit);
            if (isNaN(limit) || limit < 1 || limit > 1000) {
                errors.push('Limit must be between 1 and 1000');
            }
        }

        return errors;
    }

    /**
     * Sanitize URL parameters
     */
    sanitizeParams(params) {
        const sanitized = {};

        // Sanitize path
        if (params.path) {
            sanitized.path = params.path
                .replace(/\.\./g, '')
                .replace(/\0/g, '')
                .replace(/\/+/g, '/')
                .replace(/^\/+/, '');
        }

        // Sanitize line number
        if (params.line) {
            const lineNum = parseInt(params.line);
            if (!isNaN(lineNum) && lineNum > 0) {
                sanitized.line = lineNum;
            }
        }

        // Sanitize search query
        if (params.search) {
            sanitized.search = params.search
                .replace(/\0/g, '')
                .trim()
                .slice(0, 1000); // Limit length
        }

        // Sanitize type
        if (params.type && ['filename', 'content', 'both'].includes(params.type)) {
            sanitized.type = params.type;
        }

        // Sanitize extensions
        if (params.extensions) {
            sanitized.extensions = params.extensions
                .replace(/[^a-zA-Z0-9,\.]/g, '')
                .split(',')
                .filter(ext => ext.length > 0)
                .slice(0, 20) // Limit number of extensions
                .join(',');
        }

        // Sanitize limit
        if (params.limit) {
            const limit = parseInt(params.limit);
            if (!isNaN(limit) && limit > 0 && limit <= 1000) {
                sanitized.limit = limit;
            }
        }

        return sanitized;
    }
}

// Export for use in other modules
window.UrlHandler = UrlHandler;