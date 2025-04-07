// log.js
// Utility class for displaying logs in the viewer

export class LogDisplay {
    /**
     * Constructor for the LogDisplay class
     * @param {string} logToggleButtonId - The ID of the button to toggle the log display
     * @param {string} logContainerId - The ID of the container to display the log content
     * @param {string} logContentId - The ID of the element to display the log content
     * @param {string} logStatusId - The ID of the element to display the log status
     * @param {string} copyLogButtonId - The ID of the button to copy the log content
     */
    constructor(
        logToggleButtonId,
        logContainerId,
        logContentId,
        logStatusId,
        copyLogButtonId
    ) {
        this.logToggleButtonId = logToggleButtonId;
        this.logContainerId = logContainerId;
        this.logContentId = logContentId;
        this.logStatusId = logStatusId;
        this.copyLogButtonId = copyLogButtonId;
        this.logData = [];

        // Get DOM elements
        this.logToggleButton = document.getElementById(logToggleButtonId);
        this.logContainer = document.getElementById(logContainerId);
        this.logContent = document.getElementById(logContentId);
        this.logStatus = document.getElementById(logStatusId);
        this.copyLogButton = document.getElementById(copyLogButtonId);
        
    }

    /**
     * Toggle log display
     */
    toggleLogDisplay() {
        if (this.logContainer.classList.contains('d-none')) {
            this.showLogContainer();
        } else {
            this.hideLogContainer();
        }
    }

    /**
     * Show log container and fetch logs
     */
    showLogContainer() {
        // Show the container
        this.logContainer.classList.remove('d-none');
        this.copyLogButton.classList.remove('d-none');
        
        // Change button text
        this.logToggleButton.textContent = 'Hide Log Details';
        
        // Fetch logs if we haven't already
        if (this.logData.length === 0) {
            this.fetchLogs();
        }
    }

    /**
     * Hide log container
     */
    hideLogContainer() {
        this.logContainer.classList.add('d-none');
        this.copyLogButton.classList.add('d-none');
        this.logToggleButton.textContent = 'Show Log Details';
    }

    /**
     * Fetch logs from the server
     */
    fetchLogs() {
        // Show loading status
        this.logStatus.textContent = 'Loading logs...';
        this.logStatus.classList.remove('d-none');
        
        // URL to fetch logs from
        let url = '/get_log_entries';
        
        // Add diagnostic logging
        console.log(`Fetching logs from: ${url}`);
        
        // Fetch logs
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch logs: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                this.logData = data;
                this.renderLogs();
                this.logStatus.classList.add('d-none');
            })
            .catch(error => {
                this.logContent.innerHTML = `<div class="text-danger">Error fetching logs: ${error.message}</div>`;
                this.logStatus.classList.add('d-none');
            });
    }

    /**
     * Render logs in the container
     */
    renderLogs() {
        if (!this.logData || this.logData.length === 0) {
            this.logContent.innerHTML = '<div class="text-info">No log entries found</div>';
            return;
        }
        
        // Format logs with color coding by level
        const logHtml = this.logData.map(log => {
            // Determine CSS class based on log level
            let levelClass = '';
            switch (log.level) {
                case 'CRITICAL':
                case 'ERROR':
                    levelClass = 'text-danger';
                    break;
                case 'WARNING':
                    levelClass = 'text-warning';
                    break;
                case 'INFO':
                    levelClass = 'text-info';
                    break;
                case 'DEBUG':
                    levelClass = 'text-secondary';
                    break;
                default:
                    levelClass = 'text-light';
            }
            
            // Format timestamp to be more readable
            const timestamp = new Date(log.timestamp).toLocaleString();
            
            // Format the log entry
            return `<div class="log-entry mb-1">
                <span class="log-timestamp text-muted">${timestamp}</span>
                <span class="log-level ${levelClass}">[${log.level}]</span>
                <span class="log-source text-primary">${log.source}</span>
                <span class="log-message">${this.formatLogMessage(log.message)}</span>
            </div>`;
        }).join('');
        
        this.logContent.innerHTML = logHtml;
        
        // Scroll to bottom to show the most recent logs
        this.logContent.scrollTop = this.logContent.scrollHeight;
    }

    /**
     * Format log message with highlighting for error patterns
     * @param {string} message - The log message
     * @returns {string} Formatted HTML for the message
     */
    formatLogMessage(message) {
        // Escape HTML to prevent XSS
        const escapedMessage = this.escapeHtml(message);
        
        // Highlight common error patterns
        return escapedMessage
            .replace(/Error/g, '<span class="text-danger">Error</span>')
            .replace(/Exception/g, '<span class="text-danger">Exception</span>')
            .replace(/Warning/g, '<span class="text-warning">Warning</span>')
            .replace(/(File ".+?", line \d+)/, '<span class="text-info">$1</span>');
    }

    /**
     * Escape HTML to prevent XSS attacks
     * @param {string} unsafe - Unsafe HTML string
     * @returns {string} Escaped HTML string
     */
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * Copy log content to clipboard
     */
    copyLogToClipboard() {
        // Create plain text version of logs
        const plainText = this.logData.map(log => {
            const timestamp = new Date(log.timestamp).toLocaleString();
            return `${timestamp} [${log.level}] ${log.source}: ${log.message}`;
        }).join('\n');
        
        // Copy to clipboard
        navigator.clipboard.writeText(plainText)
            .then(() => {
                // Show temporary success message
                const originalText = this.copyLogButton.textContent;
                this.copyLogButton.textContent = 'Copied!';
                setTimeout(() => {
                    this.copyLogButton.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy logs to clipboard:', err);
            });
    }
    
}