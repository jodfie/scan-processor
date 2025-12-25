# Claude Code Integration Guide

## How It Works

The scan processor uses **Claude Code CLI** with your **Claude Pro subscription** - **NO API COSTS!**

### Architecture

```
PDF File → Python Script → Claude Code CLI → JSON Response → Processing Pipeline
```

### Command Structure

```bash
echo "prompt text" | claude --read /path/to/file.pdf
```

This command:
1. Sends the prompt via stdin
2. Attaches the PDF file with `--read`
3. Claude Code analyzes the PDF content
4. Returns a text response with JSON

### JSON Extraction

Claude Code may return JSON wrapped in markdown:

````markdown
Here's the classification:

```json
{
  "category": "MEDICAL",
  "confidence": 0.95,
  "metadata": {...}
}
```
````

The classifier automatically extracts the JSON from the response.

## Prompts

### 1. Classifier Prompt (`prompts/classifier.md`)

**Purpose**: Initial document classification

**Input**: PDF file
**Output**:
```json
{
  "category": "MEDICAL|CPS_EXPENSE|SCHOOLWORK|GENERAL",
  "confidence": 0.0-1.0,
  "metadata": {
    "child": "Jacob|Morgan|Both|null",
    "date": "YYYY-MM-DD or null",
    "title": "Descriptive title"
  },
  "needs_clarification": false,
  "clarification_question": "Question or null"
}
```

### 2. Medical Prompt (`prompts/medical.md`)

**Purpose**: Extract detailed medical metadata

**Input**: PDF file (already classified as MEDICAL)
**Output**:
```json
{
  "child": "Jacob|Morgan",
  "date": "YYYY-MM-DD",
  "provider": "Provider name",
  "type": "Visit type",
  "diagnosis": "Diagnosis or null",
  "treatment": "Treatment or null",
  "cost": "$XX.XX or null",
  "notes": "Additional notes",
  "tags": ["medical", "child-name", ...]
}
```

### 3. Expense Prompt (`prompts/expense.md`)

**Purpose**: Extract expense metadata for co-parenting tracking

**Input**: PDF file (classified as CPS_EXPENSE)
**Output**:
```json
{
  "child": "Jacob|Morgan|Both",
  "date": "YYYY-MM-DD",
  "vendor": "Vendor name",
  "amount": "$XX.XX",
  "category": "School Supplies|Activities|...",
  "description": "Description",
  "reimbursable": "yes|no",
  "notes": "Additional notes",
  "tags": ["expense", "category", ...]
}
```

### 4. Schoolwork Prompt (`prompts/schoolwork.md`)

**Purpose**: Extract schoolwork metadata

**Input**: PDF file (classified as SCHOOLWORK)
**Output**:
```json
{
  "child": "Jacob|Morgan",
  "subject": "Math|Reading|Science|...",
  "type": "Homework|Test|Project|...",
  "grade": "A+|95%|null",
  "date": "YYYY-MM-DD or null",
  "title": "Work title",
  "teacher": "Teacher name or null",
  "notes": "Additional notes",
  "tags": ["schoolwork", "subject", ...]
}
```

## Processing Flow

### Document Classification

```python
# classifier.py
def classify_document(file_path):
    # Read the classifier prompt
    with open('prompts/classifier.md', 'r') as f:
        prompt = f.read()

    # Call Claude Code
    cmd = f'echo {json.dumps(prompt)} | claude --read {file_path}'
    result = subprocess.run(cmd, shell=True, capture_output=True)

    # Extract JSON from response
    response_text = result.stdout
    json_data = extract_json(response_text)

    return json.loads(json_data)
```

### Complete Pipeline

```python
# process.py
def process_document(file_path):
    # Step 1: Classify
    classification = classifier.classify_document(file_path)

    # Step 2: Route based on category
    if classification['category'] == 'MEDICAL':
        metadata = classifier.extract_medical_metadata(file_path)
        basicmemory.create_medical_note(metadata)
    elif classification['category'] == 'CPS_EXPENSE':
        metadata = classifier.extract_expense_metadata(file_path)
        basicmemory.create_expense_note(metadata)
    elif classification['category'] == 'SCHOOLWORK':
        metadata = classifier.extract_schoolwork_metadata(file_path)

    # Step 3: Upload to Paperless
    paperless.upload_document(file_path, metadata)

    # Step 4: Send notification
    notifier.send(f"Processed {file_path.name}")
```

## Testing

### Test Classification

```bash
cd /home/jodfie/scan-processor
./scripts/test_classifier.sh /path/to/test.pdf
```

### Manual Test

```bash
# Direct Claude Code call
cd /home/jodfie/scan-processor

echo "$(cat prompts/classifier.md)" | claude --read /path/to/test.pdf
```

### Test with Python

```bash
cd /home/jodfie/scan-processor/scripts
python3 classifier.py /path/to/test.pdf
```

## Troubleshooting

### Claude Code not found

```bash
# Check if installed
which claude

# Install if needed
# (Follow Claude Code installation instructions)
```

### Authentication issues

```bash
# Claude Code uses your Pro subscription
# Make sure you're logged in:
claude auth status
```

### Timeout issues

The classifier uses a 5-minute timeout (300 seconds). For very large files:

```python
# In classifier.py, increase timeout:
result = self._call_claude_code(file_path, prompt_path, timeout=600)
```

### JSON extraction fails

If Claude Code returns unexpected format:

1. Check the raw response:
   ```python
   print(f"Raw response: {response_text}")
   ```

2. Update the regex patterns in `_extract_json()` method

3. Or add explicit instructions to the prompt:
   ```markdown
   IMPORTANT: Return ONLY the JSON object, no other text.
   ```

## Cost Comparison

### Using Claude Code CLI (Current Implementation)

✅ **$0/month additional cost**
- Uses your Claude Pro subscription ($20/month you already pay)
- Unlimited document processing
- No per-request costs
- No API key management

### Using Claude API (Alternative)

❌ **~$50-200/month additional**
- API costs per token
- ~$0.10-0.50 per document processed
- 100-400 documents = $10-200/month
- Requires API key management

## Advantages of Claude Code CLI

1. **Zero Additional Cost**: Already included in Pro subscription
2. **No Rate Limits**: No separate API rate limits
3. **Same Quality**: Uses same Claude models
4. **Simpler Auth**: Uses your logged-in session
5. **File Support**: Native PDF reading with `--read`
6. **Local Processing**: Subprocess call, no network overhead

## Limitations

1. **Sequential Processing**: One document at a time
2. **Requires Login**: Claude Code must be authenticated
3. **Subprocess Overhead**: Slight delay launching CLI
4. **No Batch API**: Can't batch multiple files in one call

## Future Enhancements

### Parallel Processing

Use multiple Claude Code instances:

```python
from concurrent.futures import ProcessPoolExecutor

def classify_batch(files):
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = executor.map(classify_document, files)
    return list(results)
```

### Caching

Cache classification results to avoid re-processing:

```python
import hashlib

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Check cache before classifying
cache_key = get_file_hash(file_path)
if cache_key in classification_cache:
    return classification_cache[cache_key]
```

### Error Recovery

Retry on failure with exponential backoff:

```python
import time

def classify_with_retry(file_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            return classify_document(file_path)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
```

## Related Files

- `scripts/classifier.py` - Main classifier implementation
- `scripts/process.py` - Document processing orchestrator
- `prompts/*.md` - Claude Code prompt templates
- `scripts/test_classifier.sh` - Test script

## Support

If classification isn't working:

1. Check Claude Code is installed: `claude --version`
2. Verify authentication: `claude auth status`
3. Test manually: `echo "test" | claude --read file.pdf`
4. Check logs: `/home/jodfie/scan-processor/logs/processor.log`
5. Enable debug output in `classifier.py`
