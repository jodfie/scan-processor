#!/bin/bash
#
# Verify Claude Code Integration
# Shows exactly what commands will be executed
#

set -e

echo "=========================================="
echo "Claude Code Integration Verification"
echo "=========================================="
echo ""

# Check Claude Code CLI
echo "[1/4] Checking Claude Code CLI..."
if ! command -v claude &> /dev/null; then
    echo "  ✗ ERROR: Claude Code CLI not found"
    echo "  Please install Claude Code first"
    exit 1
fi

CLAUDE_PATH=$(which claude)
CLAUDE_VERSION=$(claude --version 2>&1 | head -1)
echo "  ✓ Found: $CLAUDE_PATH"
echo "  ✓ Version: $CLAUDE_VERSION"
echo ""

# Check prompts exist
echo "[2/4] Checking prompt files..."
PROMPTS_DIR="/home/jodfie/scan-processor/prompts"

for prompt in classifier.md medical.md expense.md schoolwork.md; do
    if [ -f "$PROMPTS_DIR/$prompt" ]; then
        size=$(wc -c < "$PROMPTS_DIR/$prompt")
        echo "  ✓ $prompt ($size bytes)"
    else
        echo "  ✗ Missing: $prompt"
        exit 1
    fi
done
echo ""

# Show command structure
echo "[3/4] Command structure that will be used..."
echo ""
echo "  STEP 1: Save prompt to temporary file"
echo "    /tmp/prompt_XXXXXX.txt"
echo ""
echo "  STEP 2: Pipe prompt through Claude Code with file"
echo "    cat /tmp/prompt_XXXXXX.txt | claude --read /path/to/document.pdf"
echo ""
echo "  STEP 3: Extract JSON from response"
echo "    - Searches for JSON in markdown code blocks"
echo "    - Or extracts raw JSON objects"
echo ""
echo "  STEP 4: Parse and return to processing pipeline"
echo ""

# Test authentication
echo "[4/4] Testing Claude Code authentication..."
if claude auth status &> /dev/null; then
    echo "  ✓ Authentication successful"
else
    echo "  ⚠ Warning: Authentication check failed"
    echo "  You may need to login: claude auth login"
fi
echo ""

echo "=========================================="
echo "✓ Integration Verification Complete!"
echo "=========================================="
echo ""
echo "To test with an actual PDF:"
echo "  ./scripts/test_classifier.sh /path/to/test.pdf"
echo ""
echo "To test manual command:"
echo "  cat prompts/classifier.md | claude --read /path/to/test.pdf"
echo ""
