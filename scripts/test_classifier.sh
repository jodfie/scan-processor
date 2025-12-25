#!/bin/bash
#
# Test the Claude Code classifier integration
#

set -e

# Check if Claude Code CLI is installed
if ! command -v claude &> /dev/null; then
    echo "ERROR: Claude Code CLI not found"
    echo "Please install Claude Code first"
    exit 1
fi

echo "✓ Claude Code CLI found: $(which claude)"
echo ""

# Check if a test PDF was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <test.pdf>"
    echo ""
    echo "This will test the document classifier by:"
    echo "  1. Running classification on the PDF"
    echo "  2. Displaying the results"
    echo ""
    exit 1
fi

TEST_FILE="$1"

if [ ! -f "$TEST_FILE" ]; then
    echo "ERROR: File not found: $TEST_FILE"
    exit 1
fi

echo "Testing classifier on: $TEST_FILE"
echo "========================================"
echo ""

# Run the classifier
cd /home/jodfie/scan-processor/scripts
python3 classifier.py "$TEST_FILE"

echo ""
echo "========================================"
echo "Test complete!"
