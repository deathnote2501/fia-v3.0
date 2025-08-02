/**
 * FIA v3.0 - API Utilities
 * JavaScript ES6 utilities for backend communication
 */

// Auto-detect API base URL based on environment
const API_BASE_URL = (() => {
    // If running on Railway production
    if (window.location.hostname.includes('railway.app')) {
        return window.location.origin;
    }
    
    // If running on custom domain
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        return window.location.origin;
    }
    
    // Default to localhost for development
    return 'http://localhost:8000';
})();

/**
 * API client with common functionality
 */
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Make HTTP request with logging
     * @param {string} endpoint 
     * @param {object} options 
     * @returns {Promise}
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const startTime = performance.now();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        // 📤 Log API Request
        console.log(`📤 [API_CALL] [REQUEST] ${config.method || 'GET'} ${endpoint}`);
        if (config.body) {
            try {
                const payload = JSON.parse(config.body);
                console.log(`📋 [API_CALL] [PAYLOAD]`, payload);
            } catch (e) {
                console.log(`📋 [API_CALL] [RAW_BODY]`, config.body);
            }
        }

        try {
            const response = await fetch(url, config);
            const duration = performance.now() - startTime;
            
            // 📥 Log API Response
            console.log(`📥 [API_CALL] [RESPONSE] ${response.status} ${response.statusText} (${duration.toFixed(0)}ms)`);
            console.log(`🔗 [API_CALL] [URL] ${url}`);
            
            if (!response.ok) {
                let errorMessage = `HTTP error! status: ${response.status}`;
                
                // Try to get detailed error message from response
                try {
                    const errorData = await response.json();
                    console.log(`❌ [API_CALL] [ERROR]`, errorData);
                    
                    if (errorData.detail) {
                        // Handle Pydantic validation errors (detail is an array)
                        if (Array.isArray(errorData.detail)) {
                            const errors = errorData.detail.map(err => {
                                const field = err.loc ? err.loc.join('.') : 'unknown';
                                return `${field}: ${err.msg}`;
                            }).join(', ');
                            errorMessage = `Validation error: ${errors}`;
                        } else {
                            errorMessage = errorData.detail;
                        }
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                } catch (jsonError) {
                    // If response is not JSON, use status text
                    errorMessage = `${response.status} ${response.statusText}`;
                }
                
                throw new Error(errorMessage);
            }
            
            // Log successful response data (preview)
            const responseData = await response.json();
            const preview = JSON.stringify(responseData).substring(0, 200);
            console.log(`✅ [API_CALL] [DATA] ${preview}${preview.length >= 200 ? '...' : ''}`);
            
            return responseData;
        } catch (error) {
            const duration = performance.now() - startTime;
            console.log(`❌ [API_CALL] [FAILED] ${config.method || 'GET'} ${endpoint} (${duration.toFixed(0)}ms)`);
            console.error(`💥 [API_CALL] [EXCEPTION]`, error);
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} endpoint 
     * @returns {Promise}
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     * @param {string} endpoint 
     * @param {object} data 
     * @returns {Promise}
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * Check API health
     * @returns {Promise}
     */
    async healthCheck() {
        return this.get('/api/health');
    }
}

// Export API client instance
const apiClient = new APIClient();

// Make it available globally
window.apiClient = apiClient;