-- Add Claude Code interaction logs table
-- Stores prompts sent to and responses received from Claude Code

CREATE TABLE IF NOT EXISTS claude_code_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    prompt_type TEXT NOT NULL,  -- 'classifier', 'medical', 'expense', 'schoolwork'
    prompt_file TEXT NOT NULL,  -- e.g., 'classifier.md', 'medical.md'
    prompt_content TEXT NOT NULL,  -- The full prompt sent
    response_content TEXT NOT NULL,  -- The full response received
    confidence REAL,  -- Classification confidence if applicable
    success BOOLEAN DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_history_id INTEGER,  -- Link to processing_history table
    FOREIGN KEY (processing_history_id) REFERENCES processing_history(id)
);

CREATE INDEX IF NOT EXISTS idx_claude_logs_filename ON claude_code_logs(filename);
CREATE INDEX IF NOT EXISTS idx_claude_logs_prompt_type ON claude_code_logs(prompt_type);
CREATE INDEX IF NOT EXISTS idx_claude_logs_created ON claude_code_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_claude_logs_history ON claude_code_logs(processing_history_id);
