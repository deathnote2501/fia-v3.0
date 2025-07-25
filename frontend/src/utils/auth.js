/**
 * FIA v3.0 - Authentication Utilities
 * Handle JWT tokens and authentication state
 */

class AuthManager {
    constructor() {
        this.tokenKey = 'fia_auth_token';
        this.userKey = 'fia_user_data';
    }

    /**
     * Store authentication token
     * @param {string} token 
     */
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    /**
     * Get authentication token
     * @returns {string|null}
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * Remove authentication token
     */
    clearToken() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    /**
     * Store user data
     * @param {object} userData 
     */
    setUser(userData) {
        localStorage.setItem(this.userKey, JSON.stringify(userData));
    }

    /**
     * Get user data
     * @returns {object|null}
     */
    getUser() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        // Check if token is expired
        try {
            const payload = this.parseJWT(token);
            const currentTime = Date.now() / 1000;
            return payload.exp > currentTime;
        } catch (error) {
            console.error('Invalid token:', error);
            this.clearToken();
            return false;
        }
    }

    /**
     * Parse JWT token
     * @param {string} token 
     * @returns {object}
     */
    parseJWT(token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    }

    /**
     * Get authorization header
     * @returns {object}
     */
    getAuthHeader() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    /**
     * Login user
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise}
     */
    async login(email, password) {
        try {
            const response = await apiClient.post('/api/auth/login', {
                email,
                password
            });

            if (response.access_token) {
                this.setToken(response.access_token);
                if (response.user) {
                    this.setUser(response.user);
                }
                return { success: true, user: response.user };
            }

            return { success: false, message: 'Invalid credentials' };
        } catch (error) {
            console.error('Login error:', error);
            return { 
                success: false, 
                message: error.message || 'Login failed. Please try again.' 
            };
        }
    }

    /**
     * Register user
     * @param {object} userData 
     * @returns {Promise}
     */
    async register(userData) {
        try {
            const response = await apiClient.post('/api/auth/register', userData);

            if (response.access_token) {
                this.setToken(response.access_token);
                if (response.user) {
                    this.setUser(response.user);
                }
                return { success: true, user: response.user };
            }

            return { success: false, message: 'Registration failed' };
        } catch (error) {
            console.error('Registration error:', error);
            return { 
                success: false, 
                message: error.message || 'Registration failed. Please try again.' 
            };
        }
    }

    /**
     * Logout user
     */
    logout() {
        this.clearToken();
        window.location.href = '/frontend/public/login.html';
    }

    /**
     * Redirect if not authenticated
     * @param {string} redirectUrl 
     */
    requireAuth(redirectUrl = '/frontend/public/login.html') {
        if (!this.isAuthenticated()) {
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    }

    /**
     * Redirect if already authenticated
     * @param {string} redirectUrl 
     */
    redirectIfAuthenticated(redirectUrl = '/frontend/public/trainer.html') {
        if (this.isAuthenticated()) {
            window.location.href = redirectUrl;
            return true;
        }
        return false;
    }

    /**
     * Update user profile
     * @param {object} profileData 
     * @returns {Promise}
     */
    async updateProfile(profileData) {
        try {
            const response = await apiClient.post('/api/auth/profile', profileData, {
                headers: this.getAuthHeader()
            });

            if (response.user) {
                this.setUser(response.user);
                return { success: true, user: response.user };
            }

            return { success: false, message: 'Profile update failed' };
        } catch (error) {
            console.error('Profile update error:', error);
            return { 
                success: false, 
                message: error.message || 'Profile update failed. Please try again.' 
            };
        }
    }
}

// Create global auth manager instance
const authManager = new AuthManager();

// Override API client to include auth headers
const originalRequest = apiClient.request;
apiClient.request = async function(endpoint, options = {}) {
    // Add auth headers if user is authenticated
    if (authManager.isAuthenticated()) {
        options.headers = {
            ...options.headers,
            ...authManager.getAuthHeader()
        };
    }

    try {
        return await originalRequest.call(this, endpoint, options);
    } catch (error) {
        // Handle 401 Unauthorized
        if (error.message.includes('401')) {
            authManager.clearToken();
            if (!window.location.pathname.includes('login.html')) {
                window.location.href = '/frontend/public/login.html';
            }
        }
        throw error;
    }
};

// Export for use in other modules
window.authManager = authManager;