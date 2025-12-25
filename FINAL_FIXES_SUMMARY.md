# Final Fixes Summary - Template Paths & Claude Logging

## Date: December 21, 2025

## Issues Fixed

### 1. ✅ Claude Classifier Output Not Showing

**Problem**: Clicking "View Claude Logs" button showed "No Claude Logs Available" because the classifier wasn't logging interactions to the database.

**Solution**: Updated `classifier.py` to log all Claude Code interactions to the `claude_code_logs` table.

**Changes Made**:

#### `/home/jodfie/scan-processor/scripts/classifier.py`

1. **Added database support** (Lines 10-11):
```python
import sqlite3
from pathlib import Path
```

2. **Updated `__init__`** to accept `db_path` parameter (Line 17):
```python
def __init__(self, prompts_dir=None, db_path=None):
    self.prompts_dir = Path(prompts_dir or '/home/jodfie/scan-processor/prompts')
    self.db_path = Path(db_path or '/home/jodfie/scan-processor/queue/pending.db')
```

3. **Added logging to `_call_claude_code`** (Lines 94-130):
   - Logs successful calls with prompt and response content
   - Logs failures with error messages
   - Stores confidence scores when available

4. **Added helper methods**:
   - `_get_prompt_type()` - Determines prompt type from filename (Lines 303-315)
   - `_log_claude_interaction()` - Logs to database (Lines 317-350)

**Result**: All Claude Code interactions are now logged to the database with:
- Full prompt content
- Full response content
- Confidence scores
- Success/failure status
- Error messages (if any)

---

### 2. ✅ BasicMemory Templates Wrong Path

**Problem**: BasicMemory note creation failed because templates were being looked for in wrong location:
- Looking for: `/home/jodfie/Vault/jodys-brain/CoparentingSystem/Medical/_Template_Medical.md`
- Actually at: `/home/jodfie/vault/jodys-brain/Templates/CoparentingSystem/Template-Medical.md`

**Differences**:
- Case: `Vault` → `vault`
- Location: `CoparentingSystem/Medical/_Template_Medical.md` → `Templates/CoparentingSystem/Template-Medical.md`
- Naming: `_Template_Medical.md` → `Template-Medical.md`

**Solution**: Updated `basicmemory.py` to use correct template paths from the vault.

**Changes Made**:

#### `/home/jodfie/scan-processor/scripts/basicmemory.py` (Lines 15-26)

**Before**:
```python
def __init__(self, cps_path=None, dry_run=False):
    self.dry_run = dry_run
    self.cps_path = Path(cps_path or '/home/jodfie/Vault/jodys-brain/CoparentingSystem')

    if not self.dry_run and not self.cps_path.exists():
        raise ValueError(f"CPS path does not exist: {self.cps_path}")

    self.medical_template_path = self.cps_path / "Medical" / "_Template_Medical.md"
    self.expense_template_path = self.cps_path / "Expenses" / "_Template_Expense.md"
```

**After**:
```python
def __init__(self, cps_path=None, dry_run=False):
    self.dry_run = dry_run
    self.cps_path = Path(cps_path or '/home/jodfie/vault/jodys-brain/CoparentingSystem')

    # Template paths are in the Templates directory
    self.template_dir = Path('/home/jodfie/vault/jodys-brain/Templates/CoparentingSystem')

    if not self.dry_run and not self.cps_path.exists():
        raise ValueError(f"CPS path does not exist: {self.cps_path}")

    self.medical_template_path = self.template_dir / "Template-Medical.md"
    self.expense_template_path = self.template_dir / "Template-Expense.md"
```

**Result**: BasicMemory note creation now works correctly:
```
✓ BasicMemory note created: /home/jodfie/vault/jodys-brain/CoparentingSystem/Medical/2025-05-15_Morgan_Pediatric-Savannah---Wendi-Martin-NP.md
```

---

## Testing Results

### Test Document: `20251220_220605_Morgan_5-15-25_PedSav_Care_Plan.pdf`

**Processing Result**:
```
✓ Classification result: MEDICAL (98% confidence)
✓ Medical metadata extracted
  Child: Morgan
  Provider: Pediatric Savannah - Wendi Martin, NP
✓ Uploaded to Paperless (ID: DRY_RUN_12345)
✓ BasicMemory note created
✓ Processing completed in 45.88s
```

**Claude Logs Stored**: 2 interactions
1. **Classifier** (prompt_type: classifier)
   - Confidence: 0.98
   - Success: ✓
   - Full prompt and response logged

2. **Medical Metadata** (prompt_type: medical)
   - Confidence: null (not applicable)
   - Success: ✓
   - Full prompt and response logged

**API Test**:
```bash
curl "https://scanui.redleif.dev/api/claude-logs/20251220_220605_Morgan_5-15-25_PedSav_Care_Plan.pdf"

Response:
{
  "count": 2,
  "filename": "...",
  "has_logs": true,
  "logs": [
    {
      "prompt_type": "classifier",
      "prompt_file": "classifier.md",
      "prompt_content": "[FULL CLASSIFIER PROMPT]",
      "response_content": "[FULL CLAUDE RESPONSE]",
      "confidence": 0.98,
      "success": true,
      "created_at": "2025-12-21 03:13:00"
    },
    {
      "prompt_type": "medical",
      ...
    }
  ]
}
```

---

## User Experience Improvements

### Before:
1. ❌ Claude logs button showed "No Claude Logs Available"
2. ❌ No way to see what Claude saw or how it classified
3. ❌ BasicMemory note creation failed with template not found
4. ❌ Templates in wrong location

### After:
1. ✅ Claude logs show full interaction transcript
2. ✅ Can see exact prompts sent to Claude Code
3. ✅ Can see Claude's full responses with reasoning
4. ✅ See confidence scores for each interaction
5. ✅ BasicMemory notes created successfully with proper templates
6. ✅ Templates loaded from correct vault location

---

## Side Panel Features (Now Working!)

When clicking **"View Claude Logs"** on a pending document:

```
┌────────────────────────────────────────┐
│ CLASSIFIER              98% ✓ Success  │
│ Prompt: classifier.md                   │
├────────────────────────────────────────┤
│ 📝 Prompt Sent                    [▼]  │
│   [Click to expand - shows full        │
│    classifier prompt with categories,  │
│    rules, examples]                    │
├────────────────────────────────────────┤
│ 💬 Claude Response                [▼]  │
│   [Click to expand - shows full        │
│    classification result with          │
│    category, confidence, metadata,     │
│    and reasoning]                      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ MEDICAL                     ✓ Success  │
│ Prompt: medical.md                      │
├────────────────────────────────────────┤
│ 📝 Prompt Sent                    [▼]  │
│ 💬 Claude Response                [▼]  │
│   [Shows extracted medical metadata:   │
│    child, date, provider, diagnosis,   │
│    treatment, notes, tags]             │
└────────────────────────────────────────┘
```

---

## Database Schema Used

### `claude_code_logs` Table

```sql
CREATE TABLE claude_code_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    prompt_type TEXT NOT NULL,      -- 'classifier', 'medical', 'expense', 'schoolwork'
    prompt_file TEXT NOT NULL,       -- e.g., 'classifier.md', 'medical.md'
    prompt_content TEXT NOT NULL,    -- Full prompt text
    response_content TEXT NOT NULL,  -- Full Claude response
    confidence REAL,                 -- Classification confidence (0.0-1.0)
    success BOOLEAN DEFAULT 1,       -- Success flag
    error_message TEXT,              -- Error message if failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_history_id INTEGER,
    FOREIGN KEY (processing_history_id) REFERENCES processing_history(id)
);
```

---

## Files Modified

1. **`/home/jodfie/scan-processor/scripts/classifier.py`**
   - Added database logging support
   - Added `_log_claude_interaction()` method
   - Added `_get_prompt_type()` helper
   - Logs all successful and failed Claude Code calls

2. **`/home/jodfie/scan-processor/scripts/basicmemory.py`**
   - Fixed template directory paths
   - Changed from `Vault` to `vault` (case)
   - Changed from `CoparentingSystem/Medical/_Template_Medical.md` to `Templates/CoparentingSystem/Template-Medical.md`

---

## Benefits

### For Debugging:
- ✅ See exact prompts sent to Claude Code
- ✅ See Claude's complete responses
- ✅ Understand classification reasoning
- ✅ Debug low-confidence classifications
- ✅ Review error messages when failures occur

### For Transparency:
- ✅ Full audit trail of AI classifications
- ✅ Confidence scores visible
- ✅ Can verify AI accuracy
- ✅ Can improve prompts based on responses

### For Development:
- ✅ Test prompt improvements
- ✅ Compare classification results
- ✅ Analyze false positives/negatives
- ✅ Optimize confidence thresholds

---

## Example Claude Log Content

### Classifier Prompt (excerpt):
```
# Document Classification Prompt

You are a document classifier for a co-parenting document management system.

## Categories

1. **MEDICAL** - Medical records, bills, EOBs...
2. **CPS_EXPENSE** - Co-parenting expenses...
3. **SCHOOLWORK** - Children's schoolwork...
4. **GENERAL** - Any other document...

[Full prompt with examples and guidelines...]
```

### Claude Response (excerpt):
```json
{
  "category": "MEDICAL",
  "confidence": 0.98,
  "metadata": {
    "child": "Morgan",
    "date": "2025-05-15",
    "title": "Pediatric Visit - Fever/Abdominal Pain"
  },
  "needs_clarification": false
}
```

Plus Claude's reasoning:
```
★ Insight ─────────────────────────────────
Document Classification Analysis:
- High Confidence Indicators: Structured clinical data
- Child Identification: Filename and patient demographics
- Date Extraction: DOS field provides canonical date
──────────────────────────────────────────────────────
```

---

## Next Processing Will Show:

When you process the next document, the Claude logs will automatically:
1. **Capture** all prompts and responses
2. **Store** in database with confidence scores
3. **Display** in side panel when viewing pending documents
4. **Enable** full transparency into classification decisions

---

## Status

✅ **All Fixed and Tested**

- Claude logging: **Working**
- Template paths: **Fixed**
- Side panel: **Displaying logs**
- API endpoint: **Returning data**
- Database: **Storing interactions**

**Version**: v1.2
**Date**: December 21, 2025 03:15
