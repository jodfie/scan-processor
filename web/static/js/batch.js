// Batch Operations Handler

document.addEventListener('DOMContentLoaded', () => {
    const selectAllBtn = document.getElementById('select-all');
    const selectNoneBtn = document.getElementById('select-none');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const approveAllBtn = document.getElementById('approve-all-btn');
    const reclassifyBtn = document.getElementById('reclassify-btn');
    const deleteBtn = document.getElementById('delete-btn');

    // Select All button
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            const checkboxes = document.querySelectorAll('.doc-checkbox');
            checkboxes.forEach(cb => cb.checked = true);
            updateSelectedCount();
        });
    }

    // Select None button
    if (selectNoneBtn) {
        selectNoneBtn.addEventListener('click', () => {
            const checkboxes = document.querySelectorAll('.doc-checkbox');
            checkboxes.forEach(cb => cb.checked = false);
            updateSelectedCount();
        });
    }

    // Select All checkbox in table header
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            const checkboxes = document.querySelectorAll('.doc-checkbox');
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            updateSelectedCount();
        });
    }

    // Individual checkboxes
    const docCheckboxes = document.querySelectorAll('.doc-checkbox');
    docCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            updateSelectedCount();
            updateSelectAllCheckbox();
        });
    });

    // Approve All button
    if (approveAllBtn) {
        approveAllBtn.addEventListener('click', () => {
            const selectedIds = getSelectedDocIds();

            if (selectedIds.length === 0) {
                showToast('Please select at least one document', 'warning');
                return;
            }

            if (!confirm(`Approve ${selectedIds.length} document(s)?`)) {
                return;
            }

            performBatchAction('approve_all', selectedIds);
        });
    }

    // Reclassify button
    if (reclassifyBtn) {
        reclassifyBtn.addEventListener('click', () => {
            const selectedIds = getSelectedDocIds();

            if (selectedIds.length === 0) {
                showToast('Please select at least one document', 'warning');
                return;
            }

            if (!confirm(`Re-classify ${selectedIds.length} document(s)?`)) {
                return;
            }

            performBatchAction('reclassify', selectedIds);
        });
    }

    // Delete button
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            const selectedIds = getSelectedDocIds();

            if (selectedIds.length === 0) {
                showToast('Please select at least one document', 'warning');
                return;
            }

            if (!confirm(`Delete ${selectedIds.length} document(s)? This action cannot be undone.`)) {
                return;
            }

            performBatchAction('delete', selectedIds);
        });
    }
});

function getSelectedDocIds() {
    const checkboxes = document.querySelectorAll('.doc-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.dataset.docId);
}

function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.doc-checkbox:checked').length;
    const countElement = document.getElementById('selected-count');

    if (countElement) {
        countElement.textContent = selectedCount;
    }
}

function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    if (!selectAllCheckbox) return;

    const allCheckboxes = document.querySelectorAll('.doc-checkbox');
    const checkedCheckboxes = document.querySelectorAll('.doc-checkbox:checked');

    if (checkedCheckboxes.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCheckboxes.length === allCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

function performBatchAction(action, docIds) {
    // Show loading state
    showToast('Processing...', 'info');

    // Prepare form data
    const formData = new FormData();
    formData.append('action', action);
    docIds.forEach(id => {
        formData.append('doc_ids[]', id);
    });

    // Send request
    fetch('/batch', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast(data.message || 'Operation completed successfully', 'success');

                // Reload page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast(data.error || 'Operation failed', 'error');

                // Log to error service
                if (window.errorLogService) {
                    window.errorLogService.logApiError('/batch', 200, 'Batch Operation Failed', {
                        action: action,
                        docIds: docIds,
                        error: data.error
                    });
                }
            }
        })
        .catch(error => {
            console.error('Batch operation error:', error);
            showToast('Error performing batch operation', 'error');

            // Log to error service
            if (window.errorLogService) {
                window.errorLogService.logApiError('/batch', 0, error.message, {
                    action: action,
                    docIds: docIds
                });
            }
        });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+A or Cmd+A to select all
    if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        const checkboxes = document.querySelectorAll('.doc-checkbox');
        if (checkboxes.length > 0) {
            e.preventDefault();
            checkboxes.forEach(cb => cb.checked = true);
            updateSelectedCount();
        }
    }

    // Escape to deselect all
    if (e.key === 'Escape') {
        const checkboxes = document.querySelectorAll('.doc-checkbox');
        checkboxes.forEach(cb => cb.checked = false);
        updateSelectedCount();
    }
});
