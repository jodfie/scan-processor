#!/bin/bash
#
# File Watcher for Scan Processor
# Monitors incoming/ directory and triggers processing for new files
#

set -e

# Configuration
# Detect if running in container or on host
if [ -d "/app/incoming" ]; then
    # Running in container
    BASE_DIR="/app"
else
    # Running on host
    BASE_DIR="/home/jodfie/scan-processor"
fi

INCOMING_DIR="$BASE_DIR/incoming"
PROCESSING_SCRIPT="$BASE_DIR/scripts/process.py"
LOG_FILE="$BASE_DIR/logs/watcher.log"

# Ensure log directory exists
mkdir -p "$BASE_DIR/logs"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if inotify-tools is installed
if ! command -v inotifywait &> /dev/null; then
    log "ERROR: inotify-tools not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y inotify-tools
fi

# Check if incoming directory exists
if [ ! -d "$INCOMING_DIR" ]; then
    log "ERROR: Incoming directory does not exist: $INCOMING_DIR"
    exit 1
fi

# Check if processing script exists
if [ ! -f "$PROCESSING_SCRIPT" ]; then
    log "ERROR: Processing script not found: $PROCESSING_SCRIPT"
    exit 1
fi

log "=========================================="
log "Scan Processor File Watcher Started"
log "=========================================="
log "Monitoring: $INCOMING_DIR"
log "Processing script: $PROCESSING_SCRIPT"
log "Log file: $LOG_FILE"
log ""

# Process any existing files in incoming directory
log "Checking for existing files..."
file_count=0
for file in "$INCOMING_DIR"/*.pdf "$INCOMING_DIR"/*.PDF; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        log "Found existing file: $filename"

        # Check for metadata file (UPDATE mode)
        metadata_file="${file%.pdf}.meta.json"
        extra_args=""

        if [ -f "$metadata_file" ]; then
            paperless_id=$(python3 -c "import json; print(json.load(open('$metadata_file')).get('paperless_id', ''))" 2>/dev/null)
            if [ -n "$paperless_id" ]; then
                log "📱 UPDATE MODE - Paperless ID: $paperless_id"
                extra_args="--paperless-id $paperless_id"
                rm -f "$metadata_file"
            fi
        fi

        python3 "$PROCESSING_SCRIPT" "$file" $extra_args >> "$LOG_FILE" 2>&1 &
        ((file_count++))
    fi
done

if [ $file_count -eq 0 ]; then
    log "No existing files found"
else
    log "Processing $file_count existing file(s)"
fi

log ""
log "Watching for new files..."
log "Press Ctrl+C to stop"
log ""

# Watch for new files
inotifywait -m "$INCOMING_DIR" -e create -e moved_to --format '%w%f' |
while read filepath; do
    # Only process PDF files
    if [[ "$filepath" =~ \.pdf$ ]] || [[ "$filepath" =~ \.PDF$ ]]; then
        filename=$(basename "$filepath")

        log "----------------------------------------"
        log "New file detected: $filename"

        # Wait a moment for file to be completely written
        sleep 2

        # Check if file still exists (wasn't moved/deleted)
        if [ ! -f "$filepath" ]; then
            log "File no longer exists, skipping"
            continue
        fi

        # Check for metadata file (UPDATE mode for Paperless iOS app uploads)
        metadata_file="${filepath%.pdf}.meta.json"
        extra_args=""

        if [ -f "$metadata_file" ]; then
            # Extract paperless_id from metadata
            paperless_id=$(python3 -c "import json; print(json.load(open('$metadata_file')).get('paperless_id', ''))" 2>/dev/null)

            if [ -n "$paperless_id" ]; then
                log "📱 UPDATE MODE detected - Paperless ID: $paperless_id"
                extra_args="--paperless-id $paperless_id"

                # Remove metadata file after reading
                rm -f "$metadata_file"
            fi
        fi

        # Trigger processing in background
        log "Triggering processing for: $filename $extra_args"

        python3 "$PROCESSING_SCRIPT" "$filepath" $extra_args >> "$LOG_FILE" 2>&1 &

        pid=$!
        log "Processing started (PID: $pid)"
    else
        log "Ignoring non-PDF file: $(basename "$filepath")"
    fi
done
