/**
 * VeriDoc API Client
 * Handles all communication with the backend API
 */

class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
    }

    /**
     * Make HTTP request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(response.status, errorData.message || response.statusText, errorData);
            }

            return await response.json();
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            console.error('API Request Error Details:', {
                url,
                endpoint,
                options,
                error: error.message,
                stack: error.stack
            });
            throw new ApiError(0, 'Network error or server unavailable', { originalError: error });
        }
    }

    /**
     * Get cached data or fetch if expired
     */
    async getCached(key, fetchFn, timeout = this.cacheTimeout) {
        const cached = this.cache.get(key);
        const now = Date.now();

        if (cached && (now - cached.timestamp) < timeout) {
            return cached.data;
        }

        const data = await fetchFn();
        this.cache.set(key, { data, timestamp: now });
        return data;
    }

    /**
     * Clear cache entry
     */
    clearCache(key) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
        }
    }

    /**
     * Get directory listing
     */
    async getFiles(path = '/', options = {}) {
        // Normalize path - remove leading slash for backend (except root)
        const normalizedPath = path === '/' ? '' : (path.startsWith('/') ? path.substring(1) : path);
        
        const params = new URLSearchParams({
            path: normalizedPath,
            include_hidden: options.includeHidden || false,
            sort_by: options.sortBy || 'name',
            sort_order: options.sortOrder || 'asc'
        });

        const cacheKey = `files:${params.toString()}`;
        
        return this.getCached(cacheKey, async () => {
            return this.request(`/files?${params}`);
        }, 10000); // Cache for 10 seconds
    }

    /**
     * Get file content
     */
    async getFileContent(path, options = {}) {
        // Normalize path - remove leading slash for backend
        const normalizedPath = path.startsWith('/') ? path.substring(1) : path;
        
        const params = new URLSearchParams({
            path: normalizedPath,
            page: options.page || 1,
            lines_per_page: options.linesPerPage || 1000,
            encoding: options.encoding || 'utf-8'
        });

        const cacheKey = `content:${params.toString()}`;
        
        return this.getCached(cacheKey, async () => {
            return this.request(`/file_content?${params}`);
        });
    }

    /**
     * Get file metadata
     */
    async getFileInfo(path) {
        // Normalize path - remove leading slash for backend
        const normalizedPath = path.startsWith('/') ? path.substring(1) : path;
        
        const params = new URLSearchParams({ path: normalizedPath });
        const cacheKey = `info:${normalizedPath}`;
        
        return this.getCached(cacheKey, async () => {
            return this.request(`/file_info?${params}`);
        });
    }

    /**
     * Search files and content
     */
    async search(query, options = {}) {
        const params = new URLSearchParams({
            q: query,
            type: options.type || 'both',
            path: options.path || '',
            extensions: options.extensions || '',
            limit: options.limit || 50
        });

        // Don't cache search results as they change frequently
        return this.request(`/search?${params}`);
    }

    /**
     * Health check
     */
    async health() {
        return this.request('/health');
    }
}

/**
 * Custom API Error class
 */
class ApiError extends Error {
    constructor(status, message, details = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }

    /**
     * Check if error is a specific type
     */
    is(status) {
        return this.status === status;
    }
}

/**
 * Performance monitoring for API calls
 */
class ApiPerformanceMonitor {
    constructor() {
        this.metrics = {
            requests: 0,
            totalTime: 0,
            errors: 0,
            slowRequests: 0,
            cache: {
                hits: 0,
                misses: 0
            }
        };
        this.slowThreshold = 1000; // 1 second
    }

    /**
     * Record API call metrics
     */
    recordCall(endpoint, duration, success = true) {
        this.metrics.requests++;
        this.metrics.totalTime += duration;
        
        if (!success) {
            this.metrics.errors++;
        }
        
        if (duration > this.slowThreshold) {
            this.metrics.slowRequests++;
            console.warn(`Slow API call: ${endpoint} took ${duration}ms`);
        }
    }

    /**
     * Record cache hit/miss
     */
    recordCache(hit) {
        if (hit) {
            this.metrics.cache.hits++;
        } else {
            this.metrics.cache.misses++;
        }
    }

    /**
     * Get performance statistics
     */
    getStats() {
        const avgTime = this.metrics.requests > 0 
            ? this.metrics.totalTime / this.metrics.requests 
            : 0;
        
        const errorRate = this.metrics.requests > 0 
            ? (this.metrics.errors / this.metrics.requests) * 100 
            : 0;
        
        const cacheHitRate = (this.metrics.cache.hits + this.metrics.cache.misses) > 0
            ? (this.metrics.cache.hits / (this.metrics.cache.hits + this.metrics.cache.misses)) * 100
            : 0;

        return {
            requests: this.metrics.requests,
            averageTime: Math.round(avgTime),
            errorRate: Math.round(errorRate * 100) / 100,
            slowRequests: this.metrics.slowRequests,
            cacheHitRate: Math.round(cacheHitRate * 100) / 100
        };
    }

    /**
     * Reset metrics
     */
    reset() {
        this.metrics = {
            requests: 0,
            totalTime: 0,
            errors: 0,
            slowRequests: 0,
            cache: {
                hits: 0,
                misses: 0
            }
        };
    }
}

// Create global instances
console.log('API: Creating global API client...');
window.apiClient = new ApiClient();
window.apiMonitor = new ApiPerformanceMonitor();
console.log('API: Global API client created');

// Wrap API client methods to add performance monitoring
const originalRequest = window.apiClient.request;
window.apiClient.request = async function(endpoint, options) {
    const startTime = performance.now();
    let success = true;
    
    try {
        const result = await originalRequest.call(this, endpoint, options);
        return result;
    } catch (error) {
        success = false;
        throw error;
    } finally {
        const duration = performance.now() - startTime;
        window.apiMonitor.recordCall(endpoint, duration, success);
    }
};

// Wrap getCached method to monitor cache performance
const originalGetCached = window.apiClient.getCached;
window.apiClient.getCached = async function(key, fetchFn, timeout) {
    const cached = this.cache.get(key);
    const now = Date.now();
    const isHit = cached && (now - cached.timestamp) < timeout;
    
    window.apiMonitor.recordCache(isHit);
    
    return originalGetCached.call(this, key, fetchFn, timeout);
};