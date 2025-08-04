/**
 * FIA v3.0 - API Utilities
 * JavaScript ES6 utilities for backend communication
 */

// Use relative URLs - no need for CORS since frontend and API are on same server
const API_BASE_URL = '';

/**
 * Build API URL that respects HTTPS in production to avoid Mixed Content errors
 * @param {string} endpoint - API endpoint (e.g., '/api/trainings')
 * @returns {string} - Full URL with correct protocol
 */
function buildSecureApiUrl(endpoint) {
    // Force HTTPS in production to avoid Mixed Content errors
    if (window.location.protocol === 'https:' && window.location.hostname !== 'localhost') {
        // Production HTTPS - build absolute URL with HTTPS
        const baseUrl = `https://${window.location.hostname}`;
        const fullUrl = endpoint.startsWith('/') ? `${baseUrl}${endpoint}` : `${baseUrl}/${endpoint}`;
        
        // CRITICAL: Double-check URL is HTTPS (some servers/proxies force HTTP redirects)
        const finalUrl = fullUrl.replace(/^http:/, 'https:');
        console.log('🔒 [FORCE_HTTPS] Original:', fullUrl, '→ Final:', finalUrl);
        
        return finalUrl;
    } else {
        // Local development or HTTP - use relative URLs
        return endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    }
}

// Make buildSecureApiUrl available globally for other modules
window.buildSecureApiUrl = buildSecureApiUrl;

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
        // Use the global buildSecureApiUrl function
        const url = buildSecureApiUrl(endpoint);
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
            // CRITICAL: Force HTTPS even if URL got corrupted somewhere
            const secureUrl = url.replace(/^http:/, 'https:');
            if (secureUrl !== url) {
                console.log('🚨 [FORCE_HTTPS] URL corrected:', url, '→', secureUrl);
            }
            
            const response = await fetch(secureUrl, config);
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