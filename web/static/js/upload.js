// File Upload Handler with Drag-and-Drop

document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const browseButton = document.getElementById('browse-button');
    const uploadProgress = document.getElementById('upload-progress');
    const progressList = document.getElementById('progress-list');

    // Browse button click
    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Drag and drop handlers
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    // Make entire upload zone clickable
    uploadZone.addEventListener('click', (e) => {
        if (e.target === uploadZone || e.target.closest('#upload-zone')) {
            fileInput.click();
        }
    });
});

function handleFiles(files) {
    if (files.length === 0) return;

    const uploadProgress = document.getElementById('upload-progress');
    const progressList = document.getElementById('progress-list');

    // Show progress area
    uploadProgress.classList.remove('hidden');

    // Process each file
    Array.from(files).forEach(file => {
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showToast(`${file.name} is not a PDF file`, 'error');
            return;
        }

        // Validate file size (50MB max)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            showToast(`${file.name} is too large (max 50MB)`, 'error');
            return;
        }

        uploadFile(file);
    });
}

function uploadFile(file) {
    const progressList = document.getElementById('progress-list');

    // Create progress item
    const progressId = 'progress-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const progressItem = document.createElement('div');
    progressItem.id = progressId;
    progressItem.className = 'bg-gray-700 rounded-lg p-4';
    progressItem.innerHTML = `
        <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-white font-medium">${file.name}</span>
            <span class="text-xs text-gray-400">${formatFileSize(file.size)}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width: 0%"></div>
        </div>
        <div class="mt-2 text-xs text-gray-400">
            <span class="status">Uploading...</span>
        </div>
    `;

    progressList.appendChild(progressItem);

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);

    // Create XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest();

    // Progress event
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            const progressBar = progressItem.querySelector('.progress-bar-fill');
            progressBar.style.width = percentComplete + '%';
        }
    });

    // Load event (completion)
    xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);

            // Update progress item
            const progressBar = progressItem.querySelector('.progress-bar-fill');
            progressBar.style.width = '100%';
            progressBar.style.background = 'var(--success)';

            const status = progressItem.querySelector('.status');
            status.textContent = 'Upload complete';
            status.className = 'status text-green-400';

            showToast(`${file.name} uploaded successfully`, 'success');

            // Add to recent uploads
            addToRecentUploads(file.name, response);

            // Check if dev mode is enabled and trigger immediate processing
            const devModeToggle = document.getElementById('dev-mode-toggle');
            if (devModeToggle && devModeToggle.checked) {
                status.textContent = 'Upload complete - Processing in dev mode...';
                processDocument(response.filename, true, progressItem);
            } else {
                // Remove progress item after delay (only if not processing immediately)
                setTimeout(() => {
                    progressItem.style.opacity = '0';
                    setTimeout(() => progressItem.remove(), 300);
                }, 5000);
            }

        } else {
            // Error
            const progressBar = progressItem.querySelector('.progress-bar-fill');
            progressBar.style.background = 'var(--error)';

            const status = progressItem.querySelector('.status');
            status.textContent = 'Upload failed';
            status.className = 'status text-red-400';

            showToast(`Failed to upload ${file.name}`, 'error');

            // Log to error service
            if (window.errorLogService) {
                const responseText = xhr.responseText;
                let responseData = null;
                try {
                    responseData = JSON.parse(responseText);
                } catch (e) {
                    responseData = { raw: responseText };
                }
                window.errorLogService.logApiError('/api/upload', xhr.status, xhr.statusText, responseData);
            }
        }
    });

    // Error event
    xhr.addEventListener('error', () => {
        const progressBar = progressItem.querySelector('.progress-bar-fill');
        progressBar.style.background = 'var(--error)';

        const status = progressItem.querySelector('.status');
        status.textContent = 'Upload error';
        status.className = 'status text-red-400';

        showToast(`Error uploading ${file.name}`, 'error');

        // Log to error service
        if (window.errorLogService) {
            window.errorLogService.logApiError('/api/upload', 0, 'Network Error', {
                filename: file.name,
                fileSize: file.size
            });
        }
    });

    // Send request
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function addToRecentUploads(filename, response) {
    const recentUploads = document.getElementById('recent-uploads');
    if (!recentUploads) return;

    // Clear "no recent uploads" message
    if (recentUploads.querySelector('p')) {
        recentUploads.innerHTML = '';
    }

    const uploadItem = document.createElement('div');
    uploadItem.className = 'bg-gray-700 rounded p-3 flex items-center justify-between';
    uploadItem.innerHTML = `
        <div>
            <div class="text-white text-sm font-medium">${filename}</div>
            <div class="text-gray-400 text-xs mt-1">Just now - Queued for processing</div>
        </div>
        <div>
            <span class="px-2 py-1 text-xs rounded bg-blue-900 text-blue-300">Processing</span>
        </div>
    `;

    recentUploads.insertBefore(uploadItem, recentUploads.firstChild);

    // Keep only last 5 uploads
    while (recentUploads.children.length > 5) {
        recentUploads.removeChild(recentUploads.lastChild);
    }
}

function processDocument(filename, devMode, progressItem) {
    // Call the process API endpoint
    fetch('/api/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: filename,
            dev_mode: devMode
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update progress item
            const status = progressItem.querySelector('.status');
            status.textContent = '✓ Processing complete';
            status.className = 'status text-green-400';

            // Display results
            displayProcessingResult(data.result, filename);

            showToast(`Processing complete: ${filename}`, 'success');

            // Remove progress item after delay
            setTimeout(() => {
                progressItem.style.opacity = '0';
                setTimeout(() => progressItem.remove(), 300);
            }, 3000);
        } else {
            // Error
            const status = progressItem.querySelector('.status');
            status.textContent = '✗ Processing failed';
            status.className = 'status text-red-400';

            showToast(`Processing failed: ${data.error}`, 'error');

            // Log to error service
            if (window.errorLogService) {
                window.errorLogService.logApiError('/api/process', 200, 'Processing Failed', {
                    filename: filename,
                    error: data.error,
                    devMode: devMode
                });
            }
        }
    })
    .catch(error => {
        const status = progressItem.querySelector('.status');
        status.textContent = '✗ Processing error';
        status.className = 'status text-red-400';

        showToast(`Error processing ${filename}`, 'error');
        console.error('Processing error:', error);

        // Log to error service
        if (window.errorLogService) {
            window.errorLogService.logApiError('/api/process', 0, error.message, {
                filename: filename,
                devMode: devMode
            });
        }
    });
}

function displayProcessingResult(result, filename) {
    const resultsContainer = document.getElementById('processing-results');
    const resultsContent = document.getElementById('results-content');

    if (!resultsContainer || !resultsContent) return;

    // Show results container
    resultsContainer.classList.remove('hidden');

    // Create result item
    const resultItem = document.createElement('div');
    resultItem.className = 'bg-gray-800 rounded-lg p-4 border border-gray-700';

    const statusIcon = result.status === 'success' ? '✅' : '❌';
    const statusClass = result.status === 'success' ? 'text-green-400' : 'text-red-400';

    let content = `
        <div class="flex items-start justify-between mb-3">
            <div>
                <div class="text-white font-semibold">${statusIcon} ${filename}</div>
                <div class="${statusClass} text-sm">${result.status.toUpperCase()}</div>
            </div>
            <div class="text-xs text-gray-500">${new Date().toLocaleTimeString()}</div>
        </div>
    `;

    if (result.status === 'success') {
        content += `
            <div class="space-y-2 text-sm">
                <div class="flex items-center space-x-2">
                    <span class="text-gray-400">Category:</span>
                    <span class="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs">${result.category}</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-gray-400">Paperless ID:</span>
                    <span class="text-white">${result.paperless_id || 'DRY_RUN'}</span>
                </div>
                ${result.basicmemory_path ? `
                <div class="flex items-start space-x-2">
                    <span class="text-gray-400">BasicMemory:</span>
                    <span class="text-white text-xs">${result.basicmemory_path}</span>
                </div>
                ` : ''}
                <div class="flex items-center space-x-2">
                    <span class="text-gray-400">Processing Time:</span>
                    <span class="text-white">${(result.processing_time_ms / 1000).toFixed(2)}s</span>
                </div>
            </div>
        `;
    } else {
        content += `
            <div class="text-red-400 text-sm">
                <div class="font-semibold mb-1">Error:</div>
                <div class="bg-gray-900 p-2 rounded text-xs">${result.error || 'Unknown error'}</div>
            </div>
        `;
    }

    resultItem.innerHTML = content;
    resultsContent.insertBefore(resultItem, resultsContent.firstChild);

    // Keep only last 10 results
    while (resultsContent.children.length > 10) {
        resultsContent.removeChild(resultsContent.lastChild);
    }
}
