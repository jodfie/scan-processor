// WebSocket Connection and Event Handling

let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// Initialize WebSocket connection
function initWebSocket() {
    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: maxReconnectAttempts
    });

    // Connection established
    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus('online');
        reconnectAttempts = 0;
        showToast('Connected to server', 'success');
    });

    // Connection lost
    socket.on('disconnect', (reason) => {
        console.log('WebSocket disconnected:', reason);
        updateConnectionStatus('offline');
        showToast('Connection lost', 'error');

        // Log to error service
        if (window.errorLogService) {
            window.errorLogService.logWebSocketError('disconnect', `Connection lost: ${reason}`, { reason });
        }
    });

    // Reconnection attempt
    socket.on('reconnect_attempt', () => {
        reconnectAttempts++;
        updateConnectionStatus('connecting');
        console.log(`Reconnection attempt ${reconnectAttempts}/${maxReconnectAttempts}`);
    });

    // Reconnection failed
    socket.on('reconnect_failed', () => {
        updateConnectionStatus('offline');
        showToast('Failed to reconnect. Please refresh the page.', 'error');

        // Log to error service
        if (window.errorLogService) {
            window.errorLogService.logWebSocketError('reconnect_failed',
                `Failed to reconnect after ${maxReconnectAttempts} attempts`,
                { attempts: reconnectAttempts, maxAttempts: maxReconnectAttempts });
        }
    });

    // Custom events
    socket.on('processing_started', (data) => {
        console.log('Processing started:', data);
        showToast(`Processing ${data.filename}`, 'info');
        updateRecentActivity(data);
    });

    socket.on('processing_completed', (data) => {
        console.log('Processing completed:', data);
        const status = data.status === 'success' ? 'success' : 'error';
        showToast(`Completed: ${data.filename}`, status);
        updateRecentActivity(data);
        updateStatistics();
    });

    socket.on('clarification_needed', (data) => {
        console.log('Clarification needed:', data);
        showToast(`Clarification needed: ${data.filename}`, 'warning');
        updatePendingCount();
    });

    socket.on('clarification_responded', (data) => {
        console.log('Clarification responded:', data);
        showToast(`Response submitted for ${data.filename}`, 'success');
        updatePendingCount();
    });

    socket.on('file_uploaded', (data) => {
        console.log('File uploaded:', data);
        showToast(`File uploaded: ${data.filename}`, 'success');
    });

    socket.on('error_occurred', (data) => {
        console.log('Error occurred:', data);
        showToast(`Error: ${data.error}`, 'error');

        // Log to error service
        if (window.errorLogService) {
            window.errorLogService.logWebSocketError('error_occurred', data.error, data);
        }
    });

    // Log streaming
    socket.on('log_update', (data) => {
        appendLog(data.line);
    });

    // Ping/pong for keep-alive
    setInterval(() => {
        if (socket && socket.connected) {
            socket.emit('ping');
        }
    }, 30000);

    socket.on('pong', (data) => {
        console.log('Pong received:', data.timestamp);
    });

    // Socket.IO error handler
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        if (window.errorLogService) {
            window.errorLogService.logWebSocketError('connect_error', error.message, { error: error.toString() });
        }
    });
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');

    if (!indicator || !text) return;

    indicator.className = 'w-3 h-3 rounded-full';

    switch (status) {
        case 'online':
            indicator.classList.add('bg-green-500');
            indicator.style.boxShadow = '0 0 8px rgba(16, 185, 129, 0.8)';
            text.textContent = 'Connected';
            text.className = 'text-sm text-green-400';
            break;
        case 'offline':
            indicator.classList.add('bg-red-500');
            indicator.style.boxShadow = 'none';
            text.textContent = 'Disconnected';
            text.className = 'text-sm text-red-400';
            break;
        case 'connecting':
            indicator.classList.add('bg-yellow-500');
            indicator.style.animation = 'pulse 1.5s infinite';
            text.textContent = 'Connecting...';
            text.className = 'text-sm text-yellow-400';
            break;
    }
}

// Show toast notification
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type} px-6 py-4 rounded-lg shadow-lg text-white flex items-center justify-between min-w-[300px]`;

    const icon = getToastIcon(type);

    toast.innerHTML = `
        <div class="flex items-center">
            <span class="text-2xl mr-3">${icon}</span>
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" class="ml-4 text-white opacity-75 hover:opacity-100">
            ✕
        </button>
    `;

    container.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return '✓';
        case 'error': return '✕';
        case 'warning': return '⚠';
        case 'info': return 'ℹ';
        default: return 'ℹ';
    }
}

// Update pending count in navigation
function updatePendingCount() {
    fetch('/health')
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }
            return res.json();
        })
        .then(data => {
            // Update all pending count badges (desktop and mobile)
            const badges = [
                document.getElementById('pending-count-desktop'),
                document.getElementById('pending-count-mobile'),
                document.getElementById('pending-count') // Legacy
            ];

            badges.forEach(badge => {
                if (badge && data.queue_depth !== undefined) {
                    badge.textContent = data.queue_depth;
                }
            });
        })
        .catch(err => {
            console.error('Error updating pending count:', err);
            if (window.errorLogService) {
                window.errorLogService.logApiError('/health', 0, err.message);
            }
        });
}

// Update recent activity (dashboard)
function updateRecentActivity(data) {
    // This would be implemented on the dashboard page
    console.log('Update recent activity:', data);
}

// Update statistics (dashboard)
function updateStatistics() {
    // This would refresh dashboard statistics
    console.log('Update statistics');
}

// Append log line to viewer
function appendLog(line) {
    const logViewer = document.getElementById('log-viewer');
    if (!logViewer) return;

    const logLine = document.createElement('div');
    logLine.textContent = line;
    logViewer.appendChild(logLine);

    // Auto-scroll to bottom
    logViewer.scrollTop = logViewer.scrollHeight;

    // Limit lines to 500
    while (logViewer.children.length > 500) {
        logViewer.removeChild(logViewer.firstChild);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    updatePendingCount();

    // Update pending count every 30 seconds
    setInterval(updatePendingCount, 30000);
});
