#!/usr/bin/env python3
"""
Scan Processor Web UI
Advanced Flask application for managing document scan processing
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import requests
import yaml

# Configuration
# When running in Docker, paths are relative to /app
# When running standalone, paths are relative to scan-processor/web
if Path('/app/config').exists():
    # Running in Docker - all directories mounted under /app
    BASE_DIR = Path('/app')  # Base directory for DocumentProcessor
    CONFIG_PATH = Path('/app/config/config.yaml')
    DB_PATH = Path('/app/queue/pending.db')
    INCOMING_DIR = Path('/app/incoming')
    PROCESSING_DIR = Path('/app/processing')
    COMPLETED_DIR = Path('/app/completed')
    FAILED_DIR = Path('/app/failed')
    LOGS_DIR = Path('/app/logs')
    UPLOAD_DIR = Path('/app/static/uploads')
    SCRIPTS_DIR = Path('/app/scripts')  # Scripts mounted at /app/scripts
else:
    # Running standalone
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
    DB_PATH = BASE_DIR / "queue" / "pending.db"
    INCOMING_DIR = BASE_DIR / "incoming"
    PROCESSING_DIR = BASE_DIR / "processing"
    COMPLETED_DIR = BASE_DIR / "completed"
    FAILED_DIR = BASE_DIR / "failed"
    LOGS_DIR = BASE_DIR / "logs"
    UPLOAD_DIR = Path(__file__).parent / "static" / "uploads"
    SCRIPTS_DIR = BASE_DIR / "scripts"

# Ensure directories exist
for directory in [INCOMING_DIR, PROCESSING_DIR, COMPLETED_DIR, FAILED_DIR, LOGS_DIR, UPLOAD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Add scripts directory to path for importing DocumentProcessor
sys.path.insert(0, str(SCRIPTS_DIR))

# Import DocumentProcessor
try:
    from process import DocumentProcessor
    PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import DocumentProcessor: {e}")
    PROCESSOR_AVAILABLE = False

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Socket.IO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Load configuration
def load_config():
    """Load YAML configuration"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

config = load_config()

# Database helpers
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database if needed"""
    conn = get_db()
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_documents'")
    if not cursor.fetchone():
        # Create tables from schema
        schema_path = BASE_DIR / "queue" / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
        else:
            # Create basic schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    category TEXT NOT NULL,
                    question TEXT NOT NULL,
                    options TEXT,
                    metadata TEXT,
                    thumbnail_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    responded_at TIMESTAMP,
                    response TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    paperless_id INTEGER,
                    basicmemory_path TEXT,
                    processing_time_ms INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Routes
@app.route('/')
def dashboard():
    """Main dashboard with real-time processing status"""
    conn = get_db()
    cursor = conn.cursor()

    # Get statistics
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
               SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
               AVG(processing_time_ms) as avg_time
        FROM processing_history
        WHERE created_at > datetime('now', '-24 hours')
    """)
    stats = dict(cursor.fetchone())

    # Get recent activity
    cursor.execute("""
        SELECT * FROM processing_history
        ORDER BY created_at DESC
        LIMIT 20
    """)
    recent = [dict(row) for row in cursor.fetchall()]

    # Get pending count
    cursor.execute("SELECT COUNT(*) as count FROM pending_documents WHERE response IS NULL")
    pending_count = cursor.fetchone()['count']

    conn.close()

    return render_template('dashboard.html',
                         stats=stats,
                         recent=recent,
                         pending_count=pending_count)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Manual file upload interface"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Check for paperless_id (UPDATE mode)
        paperless_id = request.form.get('paperless_id')
        source = request.form.get('source', 'manual')

        # Save file to incoming directory
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = INCOMING_DIR / unique_filename

        file.save(str(filepath))

        # Save metadata if paperless_id provided (for file watcher)
        if paperless_id:
            metadata_path = filepath.with_suffix('.meta.json')
            metadata = {
                'paperless_id': paperless_id,
                'source': source,
                'timestamp': timestamp,
                'original_filename': file.filename
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"Saved metadata for UPDATE mode: {metadata_path}")

        # Broadcast upload event via WebSocket
        upload_event = {
            'filename': unique_filename,
            'timestamp': timestamp,
            'source': source
        }
        if paperless_id:
            upload_event['paperless_id'] = paperless_id
            upload_event['mode'] = 'update'

        socketio.emit('file_uploaded', upload_event)

        response_data = {
            'success': True,
            'filename': unique_filename,
            'message': 'File uploaded successfully and queued for processing'
        }

        if paperless_id:
            response_data['mode'] = 'update'
            response_data['paperless_id'] = paperless_id
            response_data['message'] = f'File uploaded and queued for UPDATE of Paperless document {paperless_id}'

        return jsonify(response_data)

    return render_template('upload.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for file upload"""
    return upload()

@app.route('/api/process', methods=['POST'])
def api_process():
    """Process a document immediately with optional dev mode"""
    if not PROCESSOR_AVAILABLE:
        return jsonify({'error': 'DocumentProcessor not available'}), 500

    data = request.get_json()
    filename = data.get('filename')
    dev_mode = data.get('dev_mode', False)

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    # Check if file exists in incoming directory
    filepath = INCOMING_DIR / filename
    if not filepath.exists():
        return jsonify({'error': f'File not found: {filename}'}), 404

    try:
        # Initialize processor with dev mode
        processor = DocumentProcessor(base_dir=BASE_DIR, dev_mode=dev_mode)

        # Process the document
        result = processor.process_document(str(filepath))

        # Emit processing result via WebSocket
        socketio.emit('processing_completed', {
            'filename': filename,
            'status': result.get('status'),
            'category': result.get('category'),
            'dev_mode': dev_mode
        })

        return jsonify({
            'success': True,
            'result': result,
            'dev_mode': dev_mode
        })

    except Exception as e:
        error_msg = str(e)

        # Emit error via WebSocket
        socketio.emit('error_occurred', {
            'filename': filename,
            'error': error_msg
        })

        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/pending')
def pending():
    """List documents needing clarification"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM pending_documents
        WHERE response IS NULL
        ORDER BY created_at DESC
    """)
    pending_docs = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('pending.html', pending_docs=pending_docs)

@app.route('/prompts')
def prompts():
    """View and edit Claude Code prompts"""
    prompts_dir = BASE_DIR / 'prompts'

    # Get list of all prompt files
    prompt_files = {
        'classifier': prompts_dir / 'classifier.md',
        'medical': prompts_dir / 'medical.md',
        'expense': prompts_dir / 'expense.md',
        'schoolwork': prompts_dir / 'schoolwork.md'
    }

    # Check which files exist
    available_prompts = {}
    for name, path in prompt_files.items():
        if path.exists():
            available_prompts[name] = {
                'name': name,
                'display_name': name.replace('_', ' ').title(),
                'path': str(path),
                'exists': True
            }
        else:
            available_prompts[name] = {
                'name': name,
                'display_name': name.replace('_', ' ').title(),
                'path': str(path),
                'exists': False
            }

    return render_template('prompts.html', prompts=available_prompts)

@app.route('/api/prompts/<prompt_name>', methods=['GET'])
def get_prompt(prompt_name):
    """Get prompt content"""
    prompts_dir = BASE_DIR / 'prompts'
    prompt_path = prompts_dir / f'{prompt_name}.md'

    if not prompt_path.exists():
        return jsonify({'error': 'Prompt file not found'}), 404

    try:
        with open(prompt_path, 'r') as f:
            content = f.read()
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts/<prompt_name>', methods=['POST'])
def update_prompt(prompt_name):
    """Update prompt content"""
    prompts_dir = BASE_DIR / 'prompts'
    prompt_path = prompts_dir / f'{prompt_name}.md'

    data = request.get_json()
    content = data.get('content', '')

    if not content:
        return jsonify({'error': 'No content provided'}), 400

    try:
        # Create backup
        if prompt_path.exists():
            backup_path = prompts_dir / f'{prompt_name}.md.backup'
            with open(prompt_path, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)

        # Write new content
        with open(prompt_path, 'w') as f:
            f.write(content)

        return jsonify({'success': True, 'message': 'Prompt updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/respond/<int:doc_id>', methods=['GET', 'POST'])
def respond(doc_id):
    """Respond to clarification question with manual classification"""
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get form data
        category = request.form.get('category')
        response_text = request.form.get('response', '')

        # Build metadata based on category
        metadata = {}

        if category == 'MEDICAL':
            metadata = {
                'child': request.form.get('child_name', ''),
                'provider': request.form.get('provider', ''),
                'visit_date': request.form.get('visit_date', '')
            }
        elif category == 'CPS_EXPENSE':
            metadata = {
                'child': request.form.get('expense_child', ''),
                'amount': request.form.get('amount', ''),
                'expense_type': request.form.get('expense_type', '')
            }
        elif category == 'SCHOOLWORK':
            metadata = {
                'child': request.form.get('school_child', ''),
                'document_type': request.form.get('school_type', '')
            }

        # Clean up empty values
        metadata = {k: v for k, v in metadata.items() if v}

        # Update pending document with response and metadata
        cursor.execute("""
            UPDATE pending_documents
            SET response = ?,
                category = ?,
                metadata = ?,
                responded_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (response_text, category, json.dumps(metadata), doc_id))

        conn.commit()

        # Get document info
        cursor.execute("SELECT * FROM pending_documents WHERE id = ?", (doc_id,))
        doc = dict(cursor.fetchone())

        conn.close()

        # Broadcast response event
        socketio.emit('clarification_responded', {
            'doc_id': doc_id,
            'filename': doc['filename'],
            'category': category,
            'response': response_text
        })

        # TODO: Trigger continued processing with manual classification
        # For now, just mark as responded - can be processed manually or via automation

        return redirect(url_for('pending'))

    # GET request - show form
    cursor.execute("SELECT * FROM pending_documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()

    if not doc:
        conn.close()
        return "Document not found", 404

    doc = dict(doc)
    conn.close()

    return render_template('respond.html', doc=doc)

@app.route('/preview/<int:doc_id>')
def preview(doc_id):
    """Preview document with metadata"""
    conn = get_db()
    cursor = conn.cursor()

    # Try pending documents first
    cursor.execute("SELECT * FROM pending_documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()

    if not doc:
        # Try processing history
        cursor.execute("SELECT * FROM processing_history WHERE id = ?", (doc_id,))
        doc = cursor.fetchone()

    if not doc:
        conn.close()
        return "Document not found", 404

    doc = dict(doc)

    # Find the file
    filename = doc['filename']
    for directory in [PROCESSING_DIR, COMPLETED_DIR, FAILED_DIR, INCOMING_DIR]:
        filepath = directory / filename
        if filepath.exists():
            doc['filepath'] = str(filepath)
            break

    conn.close()

    return render_template('preview.html', doc=doc)

@app.route('/file/<path:filename>')
def serve_file(filename):
    """Serve PDF file for preview"""
    # Check all directories
    for directory in [PROCESSING_DIR, COMPLETED_DIR, FAILED_DIR, INCOMING_DIR]:
        filepath = directory / filename
        if filepath.exists():
            return send_file(str(filepath), mimetype='application/pdf')

    return "File not found", 404

@app.route('/history')
def history():
    """Processing history with filtering"""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM processing_history WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    query += " ORDER BY created_at DESC LIMIT 100"

    cursor.execute(query, params)
    history_items = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('history.html', history=history_items)

@app.route('/api/reprocess', methods=['POST'])
def api_reprocess():
    """API endpoint to re-process a document with corrections"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        corrections = data.get('corrections', {})

        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        # Find the document in completed directory
        completed_path = COMPLETED_DIR / filename
        if not completed_path.exists():
            return jsonify({'success': False, 'error': f'Document not found: {filename}'}), 404

        # Trigger re-processing with corrections
        import subprocess
        import json as json_module

        # Prepare corrections JSON for passing to process script
        corrections_json = json_module.dumps({
            'override_category': corrections.get('override_category'),
            'notes': corrections.get('notes'),
            'reason': corrections.get('reason')
        })

        # Call process.py with corrections parameter
        cmd = [
            'python3',
            str(SCRIPTS_DIR / 'process.py'),
            str(completed_path),
            '--corrections',
            corrections_json
        ]

        # Run in background
        env = os.environ.copy()
        subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return jsonify({
            'success': True,
            'message': f'Re-processing started for {filename}',
            'filename': filename
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/batch', methods=['GET', 'POST'])
def batch():
    """Batch operations interface"""
    if request.method == 'POST':
        action = request.form.get('action')
        doc_ids = request.form.getlist('doc_ids[]')

        conn = get_db()
        cursor = conn.cursor()

        if action == 'approve_all':
            # Approve all selected clarifications with default response
            for doc_id in doc_ids:
                cursor.execute("""
                    UPDATE pending_documents
                    SET response = 'Approved', responded_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (doc_id,))

            conn.commit()
            message = f"Approved {len(doc_ids)} documents"

        elif action == 'reclassify':
            # Mark for reclassification
            message = "Reclassification not yet implemented"

        else:
            conn.close()
            return jsonify({'error': 'Unknown action'}), 400

        conn.close()

        return jsonify({'success': True, 'message': message})

    # GET request - show batch interface
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM pending_documents
        WHERE response IS NULL
        ORDER BY created_at DESC
    """)
    pending_docs = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('batch.html', pending_docs=pending_docs)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check database connection
        conn = get_db()
        conn.close()

        # Check directories
        all_ok = all([
            INCOMING_DIR.exists(),
            PROCESSING_DIR.exists(),
            COMPLETED_DIR.exists(),
            FAILED_DIR.exists()
        ])

        # Get queue depth
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM pending_documents WHERE response IS NULL")
        queue_depth = cursor.fetchone()['count']
        conn.close()

        return jsonify({
            'status': 'ok' if all_ok else 'degraded',
            'queue_depth': queue_depth,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/logs')
def logs():
    """Live log viewer - shows recent processing activity"""
    lines = int(request.args.get('lines', 100))

    try:
        # Try to read from available log files in order of preference
        log_sources = [
            ('dev_mode_test.log', 'Development Mode Tests'),
            ('classifier_test.log', 'Classifier Tests'),
            ('manual_test.log', 'Manual Tests')
        ]

        log_lines = []
        log_source_name = None

        # Try each log file
        for log_file, source_name in log_sources:
            log_path = LOGS_DIR / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        all_lines = f.readlines()
                        if all_lines:
                            log_lines = all_lines[-lines:]
                            log_source_name = source_name
                            break
                except Exception:
                    continue

        # If no log files found, check recent processing history from database
        if not log_lines:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, filename, category, status, processing_time_ms, error_message
                FROM processing_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (lines,))

            history_logs = []
            for row in cursor.fetchall():
                timestamp = row[0]
                filename = row[1]
                category = row[2]
                status = row[3]
                proc_time = row[4]
                error = row[5]

                status_icon = '✓' if status == 'success' else '✗'
                time_str = f"{proc_time/1000:.1f}s" if proc_time else "N/A"

                log_line = f"[{timestamp}] {status_icon} {filename} - {category} ({time_str})"
                if error:
                    log_line += f"\n    ERROR: {error}"
                history_logs.append(log_line)

            conn.close()

            if history_logs:
                log_lines = history_logs
                log_source_name = 'Processing History (Database)'

        if log_lines:
            return jsonify({
                'logs': log_lines,
                'source': log_source_name or 'Application Logs',
                'count': len(log_lines)
            })
        else:
            # No logs available at all - return helpful message
            return jsonify({
                'logs': [
                    '=' * 60,
                    'No logs available yet',
                    '',
                    'Logs will appear here when:',
                    '  • Documents are processed',
                    '  • Development mode tests are run',
                    '  • Classification tests are performed',
                    '',
                    'Upload a document to get started!',
                    '=' * 60
                ],
                'source': 'System Message',
                'count': 10
            })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'logs': [
                'Error loading logs',
                '',
                f'Details: {str(e)}',
                '',
                'Check that the logs directory exists and is readable.'
            ],
            'source': 'Error',
            'count': 5
        }), 500

@app.route('/api/claude-logs/<filename>')
def claude_logs(filename):
    """Get Claude Code interaction logs for a specific file"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT prompt_type, prompt_file, prompt_content, response_content,
                   confidence, success, error_message, created_at
            FROM claude_code_logs
            WHERE filename = ?
            ORDER BY created_at ASC
        """, (filename,))

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'prompt_type': row[0],
                'prompt_file': row[1],
                'prompt_content': row[2],
                'response_content': row[3],
                'confidence': row[4],
                'success': bool(row[5]),
                'error_message': row[6],
                'created_at': row[7]
            })

        conn.close()

        if not logs:
            # If no logs found, try to extract from recent test logs
            # This is a fallback for documents processed before logging was added
            log_file = LOGS_DIR / 'dev_mode_test.log'
            if log_file.exists() and filename in log_file.read_text():
                return jsonify({
                    'filename': filename,
                    'logs': [],
                    'message': 'This document was processed before Claude logging was implemented. Check /logs for processing details.',
                    'has_logs': False
                })

            return jsonify({
                'filename': filename,
                'logs': [],
                'message': 'No Claude Code logs found for this document',
                'has_logs': False
            }), 404

        return jsonify({
            'filename': filename,
            'logs': logs,
            'count': len(logs),
            'has_logs': True
        })

    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# WebSocket handlers
@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    emit('connected', {'message': 'Connected to scan processor'})

@socketio.on('subscribe_logs')
def handle_log_subscription(data):
    """Client wants to receive log updates"""
    # TODO: Implement log streaming
    emit('log_subscribed', {'message': 'Subscribed to log updates'})

@socketio.on('ping')
def handle_ping():
    """Keep-alive ping"""
    emit('pong', {'timestamp': time.time()})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run with Socket.IO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
