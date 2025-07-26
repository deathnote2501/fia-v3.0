/**
 * FIA v3.0 - API Utilities
 * JavaScript ES6 utilities for backend communication
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * API client with common functionality
 */
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Make HTTP request
     * @param {string} endpoint 
     * @param {object} options 
     * @returns {Promise}
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorMessage = `HTTP error! status: ${response.status}`;
                
                // Try to get detailed error message from response
                try {
                    const errorData = await response.json();
                    console.error('API Error Details:', errorData);
                    
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
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
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