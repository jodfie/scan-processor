#!/bin/bash
#
# Cleanup Temporary Files
# Removes orphaned Claude Code prompt temp files
#

set -e

echo "Scan Processor Cleanup"
echo "======================"
echo ""

# Clean up temp files older than 1 hour
echo "[1/3] Cleaning up old temp files..."
deleted_count=0

# Find and delete claude_prompt_* files older than 1 hour
for file in /tmp/claude_prompt_*.txt; do
    if [ -f "$file" ]; then
        # Check if file is older than 1 hour
        if [ $(find "$file" -mmin +60 -print 2>/dev/null) ]; then
            rm -f "$file"
            ((deleted_count++))
            echo "  ✓ Deleted: $(basename $file)"
        fi
    fi
done

if [ $deleted_count -eq 0 ]; then
    echo "  ✓ No old temp files to clean"
else
    echo "  ✓ Deleted $deleted_count temp file(s)"
fi
echo ""

# Clean up old files in completed directory (retention: 7 days)
echo "[2/3] Cleaning up old completed files (7-day retention)..."
COMPLETED_DIR="/home/jodfie/scan-processor/completed"
completed_count=0

if [ -d "$COMPLETED_DIR" ]; then
    completed_count=$(find "$COMPLETED_DIR" -name "*.pdf" -mtime +7 -type f | wc -l)

    if [ $completed_count -gt 0 ]; then
        find "$COMPLETED_DIR" -name "*.pdf" -mtime +7 -type f -delete
        echo "  ✓ Deleted $completed_count old file(s) from completed/"
    else
        echo "  ✓ No old completed files to clean"
    fi
else
    echo "  ⚠ Completed directory not found"
fi
echo ""

# Check disk space
echo "[3/3] Disk space check..."
SCAN_DIR="/home/jodfie/scan-processor"

if [ -d "$SCAN_DIR" ]; then
    du_output=$(du -sh "$SCAN_DIR" 2>/dev/null || echo "0K")
    echo "  Scan processor directory: $du_output"

    # Show breakdown
    for subdir in incoming processing completed failed; do
        if [ -d "$SCAN_DIR/$subdir" ]; then
            count=$(find "$SCAN_DIR/$subdir" -name "*.pdf" -type f 2>/dev/null | wc -l)
            size=$(du -sh "$SCAN_DIR/$subdir" 2>/dev/null | awk '{print $1}')
            echo "    $subdir: $count files ($size)"
        fi
    done

    echo ""
    echo "  Note: failed/ directory is NEVER auto-cleaned"
    echo "  Failed documents are preserved for review in web UI"
fi
echo ""

echo "======================"
echo "✓ Cleanup complete!"
echo "======================"
