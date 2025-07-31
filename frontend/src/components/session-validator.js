/**
 * FIA v3.0 - Session Validator Component
 * Handles session token validation and data retrieval
 */

export class SessionValidator {
    constructor() {
        console.log('🔑 [SESSION-VALIDATOR] SessionValidator initialized');
    }
    
    /**
     * Extract token from URL parameters
     * @returns {string|null} Token from URL or null if not found
     */
    extractTokenFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        console.log('🔍 [SESSION-VALIDATOR] Token extracted:', token ? 'Found' : 'Not found');
        return token;
    }
    
    /**
     * Validate session token with API
     * @param {string} token - Session token to validate
     * @returns {Promise<Object>} Session data from API
     * @throws {Error} If validation fails
     */
    async validateToken(token) {
        if (!token) {
            throw new Error('No session token provided');
        }
        
        console.log('🔄 [SESSION-VALIDATOR] Validating token with API...');
        
        try {
            const response = await fetch(`/api/session/${token}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Invalid or expired session token');
                }
                throw new Error('Unable to validate session. Please try again.');
            }
            
            const sessionData = await response.json();
            console.log('✅ [SESSION-VALIDATOR] Token validation successful');
            
            return sessionData;
            
        } catch (error) {
            if (error instanceof TypeError) {
                throw new Error('Unable to connect to the server. Please check your internet connection.');
            }
            console.error('❌ [SESSION-VALIDATOR] Token validation failed:', error);
            throw error;
        }
    }
    
    /**
     * Complete session validation workflow
     * @returns {Promise<{token: string, sessionData: Object}>} Validated session information
     * @throws {Error} If any step fails
     */
    async validateSession() {
        console.log('🚀 [SESSION-VALIDATOR] Starting session validation workflow');
        
        // Extract token from URL
        const token = this.extractTokenFromURL();
        if (!token) {
            throw new Error('Invalid session link - No session token found in the URL.');
        }
        
        // Validate token with API
        const sessionData = await this.validateToken(token);
        
        console.log('✅ [SESSION-VALIDATOR] Session validation workflow completed');
        return { token, sessionData };
    }
}