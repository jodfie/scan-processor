/**
 * Error Logging Service for ScanUI
 *
 * Captures and stores errors from various sources:
 * - Uncaught JavaScript errors
 * - Unhandled promise rejections
 * - Console.error calls
 * - API call failures
 * - WebSocket connection errors
 *
 * Provides formatted output for debugging with Claude Code
 */

class ErrorLogService {
    constructor() {
        this.errors = [];
        this.maxErrors = 50;
        this.listeners = [];
        this.init();
    }

    init() {
        // Capture uncaught errors
        window.addEventListener('error', (event) => {
            this.logError({
                type: 'uncaught',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error ? event.error.stack : null,
                timestamp: new Date().toISOString()
            });
        });

        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError({
                type: 'promise',
                message: event.reason ? event.reason.message || String(event.reason) : 'Unhandled Promise Rejection',
                stack: event.reason ? event.reason.stack : null,
                timestamp: new Date().toISOString()
            });
        });

        // Intercept console.error
        const originalConsoleError = console.error;
        console.error = (...args) => {
            this.logError({
                type: 'console',
                message: args.map(arg =>
                    typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
                ).join(' '),
                stack: new Error().stack,
                timestamp: new Date().toISOString()
            });
            originalConsoleError.apply(console, args);
        };
    }

    /**
     * Log an API error
     * @param {string} endpoint - The API endpoint that failed
     * @param {number} status - HTTP status code
     * @param {string} statusText - HTTP status text
     * @param {object} response - Response body if available
     */
    logApiError(endpoint, status, statusText, response = null) {
        this.logError({
            type: 'api',
            endpoint: endpoint,
            status: status,
            statusText: statusText,
            message: `API Error: ${status} ${statusText} - ${endpoint}`,
            response: response,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Log a WebSocket error
     * @param {string} event - The event type (connect, disconnect, error, etc.)
     * @param {string} message - Error message
     * @param {object} details - Additional details
     */
    logWebSocketError(event, message, details = {}) {
        this.logError({
            type: 'websocket',
            event: event,
            message: `WebSocket Error [${event}]: ${message}`,
            details: details,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Log a generic error
     * @param {object} error - Error object with type, message, etc.
     */
    logError(error) {
        // Add unique ID
        error.id = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Add to beginning of array (newest first)
        this.errors.unshift(error);

        // Trim to max size
        if (this.errors.length > this.maxErrors) {
            this.errors = this.errors.slice(0, this.maxErrors);
        }

        // Notify listeners
        this.notifyListeners();
    }

    /**
     * Get all errors
     * @returns {Array} All logged errors
     */
    getErrors() {
        return this.errors;
    }

    /**
     * Get error count
     * @returns {number} Number of errors
     */
    getErrorCount() {
        return this.errors.length;
    }

    /**
     * Clear all errors
     */
    clearErrors() {
        this.errors = [];
        this.notifyListeners();
    }

    /**
     * Remove a specific error by ID
     * @param {string} errorId - Error ID to remove
     */
    removeError(errorId) {
        this.errors = this.errors.filter(err => err.id !== errorId);
        this.notifyListeners();
    }

    /**
     * Add a listener for error count changes
     * @param {Function} callback - Called when errors change
     */
    addListener(callback) {
        this.listeners.push(callback);
    }

    /**
     * Notify all listeners
     */
    notifyListeners() {
        this.listeners.forEach(callback => callback(this.errors.length));
    }

    /**
     * Generate a formatted debugging prompt for Claude Code
     * @returns {string} Formatted prompt
     */
    generateClaudePrompt() {
        const appInfo = this.getAppInfo();
        const errorSummary = this.getErrorSummary();
        const detailedErrors = this.getDetailedErrors();

        return `# ScanUI Error Report for Debugging

## Application Context

**URL:** ${appInfo.url}
**User Agent:** ${appInfo.userAgent}
**Timestamp:** ${appInfo.timestamp}
**Screen Resolution:** ${appInfo.screenResolution}
**Viewport:** ${appInfo.viewport}

## Application Architecture

The ScanUI is a Flask-based document processing web application with:
- **Backend:** Flask + Flask-SocketIO
- **Frontend:** Vanilla JavaScript with WebSocket real-time updates
- **UI Framework:** Tailwind CSS (dark theme)
- **Key Components:**
  - File upload with drag-drop (upload.js)
  - Real-time WebSocket connection (websocket.js)
  - PDF preview with PDF.js (preview.js)
  - Batch operations (batch.js)
- **Main Files:**
  - Backend: app.py, websocket.py
  - Frontend: templates/base.html, static/js/*.js
  - Styling: static/css/style.css

${errorSummary}

${detailedErrors}

## What I Need Help With

I encountered ${this.errors.length} error(s) in the ScanUI application. Please analyze these errors and help me:

1. Identify the root cause of each error
2. Suggest fixes for the issues
3. Recommend any preventive measures to avoid similar errors
4. Point out any patterns or related issues

Please focus on practical, actionable solutions that I can implement immediately.
`;
    }

    /**
     * Get application information
     * @returns {object} App info
     */
    getAppInfo() {
        return {
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            screenResolution: `${window.screen.width}x${window.screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`
        };
    }

    /**
     * Get error summary
     * @returns {string} Summary markdown
     */
    getErrorSummary() {
        if (this.errors.length === 0) {
            return '## Error Summary\n\nNo errors logged.';
        }

        const byType = {};
        this.errors.forEach(err => {
            byType[err.type] = (byType[err.type] || 0) + 1;
        });

        let summary = '## Error Summary\n\n';
        summary += `**Total Errors:** ${this.errors.length}\n\n`;
        summary += '**By Type:**\n';
        Object.entries(byType).forEach(([type, count]) => {
            const icon = this.getTypeIcon(type);
            summary += `- ${icon} ${type}: ${count}\n`;
        });

        return summary;
    }

    /**
     * Get detailed error list
     * @returns {string} Detailed errors markdown
     */
    getDetailedErrors() {
        if (this.errors.length === 0) {
            return '';
        }

        let details = '\n## Detailed Error Log\n\n';

        this.errors.forEach((error, index) => {
            const icon = this.getTypeIcon(error.type);
            details += `### ${icon} Error #${index + 1}: ${error.type.toUpperCase()}\n\n`;
            details += `**Time:** ${new Date(error.timestamp).toLocaleString()}\n`;
            details += `**Message:** ${error.message}\n\n`;

            // Type-specific details
            if (error.type === 'api') {
                details += `**Endpoint:** ${error.endpoint}\n`;
                details += `**Status:** ${error.status} ${error.statusText}\n`;
                if (error.response) {
                    details += `**Response:**\n\`\`\`json\n${JSON.stringify(error.response, null, 2)}\n\`\`\`\n`;
                }
            } else if (error.type === 'websocket') {
                details += `**Event:** ${error.event}\n`;
                if (Object.keys(error.details).length > 0) {
                    details += `**Details:**\n\`\`\`json\n${JSON.stringify(error.details, null, 2)}\n\`\`\`\n`;
                }
            } else if (error.type === 'uncaught') {
                details += `**File:** ${error.filename}:${error.lineno}:${error.colno}\n`;
            }

            // Stack trace
            if (error.stack) {
                details += `\n**Stack Trace:**\n\`\`\`\n${error.stack}\n\`\`\`\n`;
            }

            details += '\n---\n\n';
        });

        return details;
    }

    /**
     * Get icon for error type
     * @param {string} type - Error type
     * @returns {string} Icon
     */
    getTypeIcon(type) {
        const icons = {
            'api': '🌐',
            'websocket': '🔌',
            'uncaught': '💥',
            'promise': '⚠️',
            'console': '📝'
        };
        return icons[type] || '❓';
    }

    /**
     * Copy Claude prompt to clipboard
     * @returns {Promise<boolean>} Success status
     */
    async copyClaudePrompt() {
        try {
            const prompt = this.generateClaudePrompt();
            await navigator.clipboard.writeText(prompt);
            return true;
        } catch (err) {
            console.warn('Failed to copy to clipboard:', err);
            return false;
        }
    }

    /**
     * Copy individual error to clipboard
     * @param {string} errorId - Error ID
     * @returns {Promise<boolean>} Success status
     */
    async copyError(errorId) {
        const error = this.errors.find(err => err.id === errorId);
        if (!error) {
            return false;
        }

        try {
            const text = `# ${error.type.toUpperCase()} Error\n\n` +
                        `**Time:** ${new Date(error.timestamp).toLocaleString()}\n` +
                        `**Message:** ${error.message}\n\n` +
                        (error.stack ? `**Stack:**\n\`\`\`\n${error.stack}\n\`\`\`\n` : '');
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.warn('Failed to copy error:', err);
            return false;
        }
    }
}

// Create global instance
window.errorLogService = new ErrorLogService();
