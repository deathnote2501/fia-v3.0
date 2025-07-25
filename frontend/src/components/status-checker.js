/**
 * FIA v3.0 - Status Checker Component
 * Checks backend API status and updates UI
 */

class StatusChecker {
    constructor() {
        this.statusElement = document.getElementById('status-indicator');
        this.init();
    }

    /**
     * Initialize status checker
     */
    init() {
        this.checkStatus();
        // Check status every 30 seconds
        setInterval(() => this.checkStatus(), 30000);
    }

    /**
     * Check API status
     */
    async checkStatus() {
        try {
            this.updateStatus('checking', 'Checking...');
            
            const health = await apiClient.healthCheck();
            
            if (health.status === 'healthy') {
                this.updateStatus('healthy', 'API Online');
            } else {
                this.updateStatus('warning', 'API Issues');
            }
        } catch (error) {
            console.error('Status check failed:', error);
            this.updateStatus('offline', 'API Offline');
        }
    }

    /**
     * Update status indicator
     * @param {string} status - healthy, warning, offline, checking
     * @param {string} message - Status message
     */
    updateStatus(status, message) {
        if (!this.statusElement) return;

        const badgeClasses = {
            healthy: 'bg-success',
            warning: 'bg-warning',
            offline: 'bg-danger',
            checking: 'bg-secondary'
        };

        const icons = {
            healthy: 'bi-check-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            offline: 'bi-x-circle-fill',
            checking: 'bi-arrow-clockwise'
        };

        const badgeClass = badgeClasses[status] || 'bg-secondary';
        const icon = icons[status] || 'bi-question-circle';

        this.statusElement.innerHTML = `
            <span class="badge ${badgeClass}">
                <i class="bi ${icon} me-1"></i>
                ${message}
            </span>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StatusChecker();
});