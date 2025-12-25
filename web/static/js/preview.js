// PDF Preview Handler using PDF.js

let pdfDoc = null;
let pageNum = 1;
let pageRendering = false;
let pageNumPending = null;
let scale = 1.5;

// Initialize PDF viewer
function initPdfViewer(pdfPath) {
    if (!pdfPath) {
        console.error('No PDF path provided');
        return;
    }

    // Set worker path
    if (typeof pdfjsLib !== 'undefined') {
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    }

    // Load PDF document
    const loadingTask = pdfjsLib.getDocument(pdfPath);
    loadingTask.promise.then((pdf) => {
        pdfDoc = pdf;
        document.getElementById('page-count').textContent = pdf.numPages;

        // Initial page render
        renderPage(pageNum);

        // Set up navigation buttons
        setupNavigation();
    }).catch((error) => {
        console.error('Error loading PDF:', error);
        const canvas = document.getElementById('pdf-canvas');
        if (canvas) {
            canvas.parentElement.innerHTML = '<p class="text-red-400">Error loading PDF: ' + error.message + '</p>';
        }
    });
}

// Render specific page
function renderPage(num) {
    pageRendering = true;

    // Get page
    pdfDoc.getPage(num).then((page) => {
        const canvas = document.getElementById('pdf-canvas');
        const ctx = canvas.getContext('2d');

        const viewport = page.getViewport({ scale: scale });

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        // Render PDF page
        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };

        const renderTask = page.render(renderContext);

        renderTask.promise.then(() => {
            pageRendering = false;
            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }
        });
    });

    // Update page number display
    document.getElementById('page-num').textContent = num;
}

// Queue page render if currently rendering
function queueRenderPage(num) {
    if (pageRendering) {
        pageNumPending = num;
    } else {
        renderPage(num);
    }
}

// Previous page
function onPrevPage() {
    if (pageNum <= 1) {
        return;
    }
    pageNum--;
    queueRenderPage(pageNum);
}

// Next page
function onNextPage() {
    if (pageNum >= pdfDoc.numPages) {
        return;
    }
    pageNum++;
    queueRenderPage(pageNum);
}

// Setup navigation buttons
function setupNavigation() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');

    if (prevBtn) {
        prevBtn.addEventListener('click', onPrevPage);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', onNextPage);
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            onPrevPage();
        } else if (e.key === 'ArrowRight') {
            onNextPage();
        }
    });
}

// Zoom controls
function zoomIn() {
    scale += 0.25;
    queueRenderPage(pageNum);
}

function zoomOut() {
    if (scale > 0.5) {
        scale -= 0.25;
        queueRenderPage(pageNum);
    }
}

// Fit to width
function fitToWidth() {
    const canvas = document.getElementById('pdf-canvas');
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth - 32; // padding

    if (pdfDoc) {
        pdfDoc.getPage(pageNum).then((page) => {
            const viewport = page.getViewport({ scale: 1 });
            scale = containerWidth / viewport.width;
            queueRenderPage(pageNum);
        });
    }
}

// Export functions for external use
window.initPdfViewer = initPdfViewer;
window.zoomIn = zoomIn;
window.zoomOut = zoomOut;
window.fitToWidth = fitToWidth;
