-- Scan Processor Database Schema

-- Pending Documents Table
-- Stores documents awaiting clarification
CREATE TABLE IF NOT EXISTS pending_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    options TEXT,  -- JSON array of possible responses
    metadata TEXT,  -- JSON metadata extracted so far
    thumbnail_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    response TEXT
);

CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_pending_responded ON pending_documents(responded_at);
CREATE INDEX IF NOT EXISTS idx_pending_status ON pending_documents(response);

-- Processing History Table
-- Stores completed processing records
CREATE TABLE IF NOT EXISTS processing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,  -- success, failed, pending_clarification
    paperless_id INTEGER,
    basicmemory_path TEXT,
    processing_time_ms INTEGER,
    error_message TEXT,
    metadata TEXT,  -- JSON metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_created ON processing_history(created_at);
CREATE INDEX IF NOT EXISTS idx_history_status ON processing_history(status);
CREATE INDEX IF NOT EXISTS idx_history_category ON processing_history(category);
CREATE INDEX IF NOT EXISTS idx_history_filename ON processing_history(filename);

-- Statistics Table (Optional)
-- For caching statistics calculations
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    total_processed INTEGER DEFAULT 0,
    successful INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    pending INTEGER DEFAULT 0,
    category_medical INTEGER DEFAULT 0,
    category_expense INTEGER DEFAULT 0,
    category_schoolwork INTEGER DEFAULT 0,
    category_general INTEGER DEFAULT 0,
    avg_processing_time_ms INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_stats_date ON statistics(date);

-- Configuration Table (Optional)
-- For storing runtime configuration
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT OR IGNORE INTO config (key, value) VALUES ('version', '1.0.0');
INSERT OR IGNORE INTO config (key, value) VALUES ('initialized_at', datetime('now'));
