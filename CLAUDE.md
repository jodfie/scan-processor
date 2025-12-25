# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**scan-processor** is a personal R&D document processing system that uses Claude Code CLI for intelligent document classification and metadata extraction. This is the development sandbox for testing ALL document types (CPS + personal), while the CoParentingSystem scanner remains the production-ready, deployable product.

**Key Technologies:**
- Python 3.x
- Claude Code CLI (subprocess execution pattern)
- SQLite for processing history
- Paperless-NGX integration
- Obsidian vault (BasicMemory format)
- Flask web UI at scanui.redleif.dev
- Systemd file watcher (inotifywait)

## Recent Changes (2025-12-25)

### Category Expansion: 4 → 29 Categories

The system was expanded from 4 categories to 29 categories to support comprehensive personal document management:

**Previous (4 categories)**:
- MEDICAL → CPS-MEDICAL
- CPS_EXPENSE → CPS-EXPENSE
- SCHOOLWORK → CPS-SCHOOLWORK
- GENERAL → GENERAL

**Current (29 categories)**:

**CPS Categories (6)** - Children-related documents:
1. CPS-MEDICAL - Children's medical records, bills, EOBs
2. CPS-EXPENSE - Children's expenses (school, activities)
3. CPS-SCHOOLWORK - Children's schoolwork, report cards
4. CPS-CUSTODY - Custody schedule, visitation
5. CPS-COMMUNICATION - Communication with co-parent
6. CPS-LEGAL - Court orders, custody decree

**Personal Categories (23)** - Your personal documents:

*Financial & Expenses*:
- PERSONAL-EXPENSE, RECEIPT, INVOICE, TAX-DOCUMENT, BANK-STATEMENT, INVESTMENT

*Medical & Health*:
- PERSONAL-MEDICAL, PRESCRIPTION, INSURANCE

*Housing & Property*:
- MORTGAGE, UTILITY, LEASE, HOME-MAINTENANCE, PROPERTY-TAX

*Automotive*:
- AUTO-INSURANCE, AUTO-MAINTENANCE, AUTO-REGISTRATION

*Legal & Contracts*:
- CONTRACT, LEGAL-DOCUMENT

*Travel*:
- TRAVEL-BOOKING, TRAVEL-RECEIPT

*Other*:
- GENERAL, REFERENCE

### Naming Convention Change

**CRITICAL**: All categories now use **dash-based naming** (not underscores):

✅ Correct:
- `CPS-MEDICAL`
- `PERSONAL-EXPENSE`
- `AUTO-MAINTENANCE`

❌ Incorrect (old):
- `CPS_MEDICAL`
- `PERSONAL_EXPENSE`
- `AUTO_MAINTENANCE`

## Architecture

### Processing Pipeline

```
1. File arrives in incoming/
   ↓
2. classifier.md determines category (29 options)
   ↓
3. Category-specific extractor runs (medical.md, utility.md, etc.)
   ↓
4. Dual-vault routing based on is_cps_related flag
   ↓
5. BasicMemory note created in appropriate vault
   ↓
6. Upload to Paperless-NGX with hierarchical tags
   ↓
7. Move to completed/ directory
```

### Dual-Vault Routing

The system routes documents to **two separate Obsidian vaults**:

#### CPS Vault
- **Path**: `/home/jodfie/vault/jodys-brain/CoparentingSystem/`
- **Categories**: CPS-MEDICAL, CPS-EXPENSE, CPS-SCHOOLWORK, CPS-CUSTODY, CPS-COMMUNICATION, CPS-LEGAL
- **Structure**:
  - `60-medical/{child}/YYYY-MM-DD-{description}.md`
  - `40-expenses/YYYY-MM-DD-{vendor}.md`
  - `50-schoolwork/{child}/`

#### Personal Vault
- **Path**: `/home/jodfie/vault/jodys-brain/Personal/`
- **Categories**: PERSONAL-MEDICAL, PERSONAL-EXPENSE, UTILITY, AUTO-*
- **Structure**:
  - `Medical/YYYY-MM-DD-{provider}-{type}.md`
  - `Expenses/{category}/YYYY-MM-DD-{vendor}.md`
  - `Utilities/{type}/YYYY-MM-DD-{provider}-{type}.md`
  - `Automotive/{type}/YYYY-MM-DD-{provider}-{type}.md`

### Claude Code CLI Integration

The system uses a **subprocess pattern** to call Claude Code:

```python
# Create temp file with prompt
tmp_path = tempfile.mkstemp(suffix='.txt', prefix='claude_prompt_')

# Write prompt: "Analyze this PDF: /path/to/file.pdf"
with open(tmp_path, 'w') as f:
    f.write(prompt_text)

# Execute: cat prompt.txt | claude --print --add-dir /path/to/repo
cmd = f'cat {tmp_path} | claude --print --add-dir {scan_dir}'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

# Parse JSON from response
json_text = extract_json(result.stdout)
data = json.loads(json_text)
```

This pattern allows Claude to:
- Analyze PDF files using vision
- Have repository context via `--add-dir`
- Return structured JSON metadata
- Log all interactions to SQLite

## Directory Structure

```
/home/jodfie/scan-processor/
├── prompts/                    # Markdown prompt templates
│   ├── classifier.md           # Universal classifier (29 categories)
│   ├── medical.md              # CPS medical metadata extraction
│   ├── expense.md              # CPS expense metadata extraction
│   ├── schoolwork.md           # CPS schoolwork metadata extraction
│   ├── personal-medical.md     # Personal medical extraction (NEW)
│   ├── personal-expense.md     # Personal expense extraction (NEW)
│   ├── utility.md              # Utility bill extraction (NEW)
│   └── auto.md                 # Automotive document extraction (NEW)
├── scripts/                    # Python processing scripts
│   ├── classifier.py           # Document classification orchestrator
│   ├── basicmemory.py          # Obsidian note creator (dual-vault)
│   ├── process.py              # Main processing orchestrator
│   ├── paperless.py            # Paperless-NGX client
│   ├── notifier.py             # Notification system
│   └── watch.py                # File watcher daemon
├── scanui/                     # Flask web UI
│   ├── app.py                  # Main Flask app
│   ├── templates/              # Jinja2 templates
│   └── static/                 # CSS, JS, images
├── queue/                      # Processing queue
│   ├── incoming/               # New documents arrive here
│   ├── processing/             # Currently processing
│   ├── completed/              # Successfully processed
│   ├── failed/                 # Failed processing
│   └── pending.db              # SQLite database
├── CLAUDE.md                   # This file (project context)
├── CATEGORY_EXPANSION_SUMMARY.md  # Details on 29-category system
└── README.md                   # User-facing documentation
```

## Key Files Modified Today (2025-12-25)

### prompts/classifier.md
- **Status**: Completely rewritten (386 lines)
- **Changes**: Expanded from 4 to 29 categories with dash-based naming
- **New Fields**: Added `is_cps_related` flag for vault routing

### prompts/personal-medical.md
- **Status**: NEW FILE (150 lines)
- **Purpose**: Extract personal (adult) medical metadata
- **Fields**: provider, specialty, diagnosis, treatment, cost, type

### prompts/personal-expense.md
- **Status**: NEW FILE (140 lines)
- **Purpose**: Extract personal expense metadata
- **Fields**: vendor, amount, category, payment_method, description

### prompts/utility.md
- **Status**: NEW FILE (130 lines)
- **Purpose**: Extract utility bill metadata
- **Fields**: provider, type, amount, due_date, account_number (masked)

### prompts/auto.md
- **Status**: NEW FILE (180 lines)
- **Purpose**: Extract automotive document metadata
- **Fields**: type, provider, amount, vehicle, mileage, service_description

### scripts/classifier.py
**Changes Made**:
1. Added 4 new prompt file references in `__init__()`:
   - `self.personal_medical_prompt`
   - `self.personal_expense_prompt`
   - `self.utility_prompt`
   - `self.auto_prompt`

2. Updated `_get_prompt_type()` to recognize new prompts

3. Added 4 new extraction methods:
   - `extract_personal_medical_metadata()`
   - `extract_personal_expense_metadata()`
   - `extract_utility_metadata()`
   - `extract_auto_metadata()`

### scripts/basicmemory.py
**Changes Made**:
1. Updated `__init__()` for dual-vault support:
   - Added `personal_path` parameter
   - Added `personal_template_dir` path
   - Auto-creates Personal vault if missing

2. Added 4 new note creation methods:
   - `create_personal_medical_note()` → `Personal/Medical/`
   - `create_personal_expense_note()` → `Personal/Expenses/{category}/`
   - `create_utility_note()` → `Personal/Utilities/{type}/`
   - `create_auto_note()` → `Personal/Automotive/{type}/`

### scripts/process.py
**Changes Made**:
1. Updated `_extract_metadata()`:
   - Changed from 4 categories to 29 categories
   - Updated to dash-based naming (CPS-MEDICAL not CPS_MEDICAL)
   - Routes to new extraction methods

2. Updated `_create_basicmemory_note()`:
   - Implements dual-vault routing
   - CPS categories → CoparentingSystem vault
   - Personal categories → Personal vault

## Development Commands

### Testing Classification

```bash
# Test universal classifier
cd /home/jodfie/scan-processor
python3 scripts/classifier.py completed/sample-medical-bill.pdf

# Test classifier initialization (shows all prompts)
python3 scripts/classifier.py
```

### Testing BasicMemory Note Creation

```bash
# Test in dry-run mode (no files created)
python3 -c "
from scripts.basicmemory import BasicMemoryNoteCreator
b = BasicMemoryNoteCreator(dry_run=True)

# Test CPS medical note
metadata = {
    'child': 'Jacob',
    'date': '2024-01-15',
    'provider': 'Pediatric Clinic',
    'type': 'Well Child Visit',
    'cost': '25.00'
}
path = b.create_medical_note(metadata)
print(f'Would create: {path}')

# Test personal medical note
metadata = {
    'date': '2024-01-15',
    'provider': 'Family Doctor',
    'type': 'office-visit'
}
path = b.create_personal_medical_note(metadata)
print(f'Would create: {path}')
"
```

### Full Processing Pipeline

```bash
# Dev mode (no Paperless upload, BasicMemory dry-run)
python3 scripts/process.py incoming/document.pdf --dev

# Production mode
python3 scripts/process.py incoming/document.pdf
```

## Common Development Patterns

### Adding a New Category

1. **Create prompt file**: `prompts/new-category.md`
2. **Add to classifier.md**: Add to category list
3. **Add extraction method** in `classifier.py`
4. **Add note creation method** in `basicmemory.py`
5. **Update routing** in `process.py`

### Testing New Categories

```bash
# 1. Test prompt manually
cat prompts/new-category.md | claude --print --add-file sample.pdf

# 2. Test extraction method
python3 -c "
from scripts.classifier import DocumentClassifier
c = DocumentClassifier()
result = c.extract_new_category_metadata('sample.pdf')
print(result)
"

# 3. Test note creation (dry-run)
python3 -c "
from scripts.basicmemory import BasicMemoryNoteCreator
b = BasicMemoryNoteCreator(dry_run=True)
path = b.create_new_category_note(metadata)
"

# 4. Test full pipeline (dev mode)
python3 scripts/process.py sample.pdf --dev
```

## Relationship to CoParentingSystem

This scan-processor is the **R&D sandbox** for testing features before porting to the production CoParentingSystem scanner.

**Development Strategy**:
- scan-processor: Personal system handling ALL document types (CPS + personal)
- CoParentingSystem scanner: Public deployable product (generalized, CPS-focused)

**When to Port Features**:
If you improve something in scan-processor that would benefit CPS scanner:
1. Document the improvement in `CATEGORY_EXPANSION_SUMMARY.md`
2. Create a note in CoParentingSystem scanner's backlog
3. Consider generalization (remove personal-specific logic)

## Environment Variables

```bash
# Paperless-NGX
export PAPERLESS_BASE_URL="http://paperless.local:8000"
export PAPERLESS_TOKEN="your-api-token-here"

# Paths (auto-detected, but can override)
export SCAN_PROCESSOR_BASE="/home/jodfie/scan-processor"
export CPS_VAULT_PATH="/home/jodfie/vault/jodys-brain/CoparentingSystem"
export PERSONAL_VAULT_PATH="/home/jodfie/vault/jodys-brain/Personal"
```

## Common Pitfalls

1. **Category Naming**: Always use dashes, not underscores
   - ✅ `CPS-MEDICAL`
   - ❌ `CPS_MEDICAL`

2. **Vault Paths**: Ensure both vaults exist before running
   ```bash
   mkdir -p ~/vault/jodys-brain/CoparentingSystem
   mkdir -p ~/vault/jodys-brain/Personal
   ```

3. **Claude Code CLI**: Must be authenticated with Pro subscription
   ```bash
   claude auth status
   ```

## Next Steps

### Pending Tasks
- [ ] Test new categories with sample documents
- [ ] Verify dual-vault routing works correctly
- [ ] Test all 4 new extraction methods
- [ ] Document improvements for CPS scanner integration
- [ ] Create sample documents for each category

### Future Enhancements
- [ ] OCR for scanned documents
- [ ] Duplicate detection
- [ ] Multi-page PDF splitting
- [ ] Mobile app integration
- [ ] Email attachment monitoring

---

## Pipeline Architecture Details

**DocumentProcessor (`scripts/process.py`)**: Main orchestrator with state machine pattern
- Auto-detects container (`/app`) vs host (`/home/jodfie/scan-processor`) environment
- Supports three modes: normal processing, dev mode (`--dev`), and update mode (`--paperless-id`)
- Moves files through directory states: `incoming/` → `processing/` → `completed/`|`failed/`
- Logs all prompts/responses to SQLite for re-processing and audit trail

**Claude Code Integration (`scripts/classifier.py`)**: Subprocess wrapper for Claude Code CLI
- Creates temporary prompt files with auto-cleanup (`tempfile.mkstemp`)
- Command: `cat prompt.txt | claude --print --add-dir {scan_dir}`
- Supports correction injection: appends user notes to prompts for re-processing
- Parses JSON responses with error recovery (strips markdown code blocks)
- Logs all interactions to `claude_code_logs` table with timestamps

**Dual Environment Support**: Code detects runtime environment automatically
- Docker: `/app/*` paths with mounted volumes
- Standalone: `/home/jodfie/scan-processor/*` paths
- Pattern: `Path('/app').exists()` checks throughout codebase

---

## Critical Implementation Patterns

### Error Handling
Always use try/except with specific error messages:
- Paperless uploads: Catch HTTPError, ConnectionError, Timeout
- Claude Code calls: Catch subprocess.TimeoutExpired, CalledProcessError
- File operations: Catch OSError, PermissionError
- Database: Catch sqlite3.Error with connection cleanup

### Authentication
Token-based for external services, no user auth for web UI:
- Paperless: Bearer token in Authorization header (`Token {api_token}`)
- Pushover: App token + user key in POST payload
- Flask: Secret key for session management only (no login system)
- Web UI assumes network-level access control (reverse proxy/firewall)

### Database Access
Always use context managers for SQLite connections:
```python
with sqlite3.connect(db_path) as conn:
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    cursor = conn.cursor()
    # ... operations ...
    conn.commit()  # Auto-rollback on exception
```

### File Movement
Use shutil.move() not os.rename() (cross-filesystem safe):
```python
shutil.move(str(source_path), str(dest_path))  # Handles different filesystems
```

---

## Available MCP Servers & Capabilities

When working with Claude Code in this repository, you have access to these MCP servers:

### Active MCP Servers (via `claude mcp list`)

**Serena** (`plugin:serena:serena`) - ✓ Connected
- Advanced code intelligence and semantic analysis
- Symbol-based editing (find_symbol, replace_symbol_body, insert_after_symbol)
- Cross-reference analysis (find_referencing_symbols)
- Pattern-based search (search_for_pattern)
- Memory management (write_memory, read_memory, list_memories)
- Shell command execution (execute_shell_command)
- Project management (activate_project, get_current_config)

**Playwright** (`plugin:playwright:playwright`) - ✓ Connected
- Browser automation for testing web UI
- Useful for: Testing web interface at https://scanui.redleif.dev
- Commands: browser_navigate, browser_click, browser_snapshot, browser_take_screenshot

**Greptile** (`plugin:greptile:greptile`) - ✓ Connected
- Code review and PR management
- Custom context for code analysis
- Merge request operations
- Comment analysis and tracking

**Monica CRM** (`monica-crm`) - ✓ Connected
- Contact management via self-hosted Monica instance
- Could be useful for: Managing co-parenting contacts, document metadata linking
- URL: https://monica-mcp.redleif.dev/mcp

### MCP Servers Requiring Authentication

**Figma** (`plugin:figma:figma`) - ⚠ Needs authentication
- Design-to-code workflows (not currently needed for this project)

**Linear** (`plugin:linear:linear`) - ⚠ Needs authentication
- Project management integration (not currently configured)

### MCP Servers Unavailable

**GitHub** (`plugin:github:github`) - ✗ Failed to connect
**Figma Desktop** (`plugin:figma:figma-desktop`) - ✗ Failed to connect
**Laravel Boost** (`plugin:laravel-boost:laravel-boost`) - ✗ Failed to connect

### Using MCP Servers in This Project

**For Code Analysis**: Use Serena MCP for semantic code operations
```bash
# Example: Find all references to a function
# Serena provides tools like find_referencing_symbols, get_symbols_overview
```

**For Web UI Testing**: Use Playwright MCP
```python
# Can automate testing of:
# - File upload flow
# - Pending clarifications UI
# - Processing history display
# - Real-time WebSocket updates
```

**For Code Reviews**: Use Greptile MCP
```bash
# Review changes to processing pipeline
# Track custom patterns and conventions
```

---

## Recommended Claude Code Plugins for This Project

Out of 811+ available plugins across 10 marketplaces, these are most relevant for scan-processor development:

### Currently Installed & Active (19 plugins)

**Core Plugins** (pre-installed):
- **`hookify`** - Create hooks to prevent unwanted behaviors
- **`feature-dev`** - Guided feature development with architecture focus
- **`pr-review-toolkit`** - Comprehensive PR review using specialized agents
- **`code-review`** - Code review for pull requests
- **`commit-commands`** - Git commit helpers (`/commit`, `/commit-push-pr`)
- **`frontend-design`** - Production-grade frontend interfaces
- **`explanatory-output-style`** - Educational insights mode (CURRENTLY ACTIVE)

**Newly Installed** (2025-12-25):
- ✅ **`python-expert`** - Python 3.12+ with async, performance optimization
- ✅ **`test-writer-fixer`** - Automated test generation and fixing
- ✅ **`backend-architect`** - Scalable API design patterns
- ✅ **`database-performance-optimizer`** - SQLite query optimization
- ✅ **`debugger`** - Advanced debugging workflows
- ✅ **`codebase-documenter`** - Automated documentation generation
- ✅ **`security-guidance`** - Security vulnerability scanning
- ✅ **`ui-designer`** - User interface design and implementation
- ✅ **`performance-benchmarker`** - Performance testing and optimization
- ✅ **`api-error-handler`** - API error handling for Paperless/Pushover
- ✅ **`api-test-automation`** - Automated API integration testing
- ✅ **`devops-automation-pack`** - DevOps automation workflows

### Plugin Usage Examples

**Python Development**:
```bash
"Use python-expert to optimize the async processing in scripts/process.py"
```

**Testing**:
```bash
"Use test-writer-fixer to generate comprehensive tests for scripts/classifier.py"
```

**API Integration**:
```bash
"Use backend-architect to review my Paperless API integration in scripts/paperless.py"
"Use api-error-handler to improve error handling in paperless.py and notify.py"
```

**Database Optimization**:
```bash
"Use database-performance-optimizer to analyze and improve the processing_history table queries"
```

**Security Review**:
```bash
"Use security-guidance to audit file upload handling in web/app.py"
```

**Documentation**:
```bash
"Use codebase-documenter to generate updated documentation for the processing pipeline"
```

**UI Enhancement**:
```bash
"Use ui-designer to enhance the Flask web UI at web/templates/dashboard.html"
```

### How to Install Additional Plugins

```bash
# Install a specific plugin
claude plugin install <plugin-name>

# Install from specific marketplace
claude plugin install <plugin-name>@<marketplace-name>

# List installed plugins
/plugin  # Opens interactive menu

# Update all plugins
claude plugin update
```

### Marketplace Distribution (10 total)

**Official Marketplaces**:
- **claude-plugins-official**: Official Anthropic plugins (including MCP integrations)
- **claude-code-plugins**: Core development plugins
- **claude-code-workflows**: Workflow automation plugins
- **anthropic-agent-skills**: Agent-based skills

**Community Marketplaces**:
- **dotclaude-plugins**: Community plugins
- **cc-marketplace**: Extended marketplace
- **claude-code-plugins-plus** 🆕: Enhanced plugin collection (jeremylongshore)
- **severity1-marketplace** 🆕: Specialized workflows (severity1)
- **ando-marketplace** 🆕: Plugin marketplace (kivilaid)
- **feedmob-claude-plugins** 🆕: Feed-mob plugins (feed-mob)

### Additional Recommended Plugins (from 811 available)

- `changelog-generator` - Auto-generate changelogs from commits
- `data-scientist` - Document metadata analysis
- `api-integration-specialist` - External service integration best practices
- `audit` - Code audit and quality checks
- `unit-test-generator` - Generate comprehensive unit tests
- `monitoring-observability-specialist` - System monitoring
- `api-monitoring-dashboard` - Monitor API integrations (from claude-code-plugins-plus)
- `database-documentation-gen` - Database schema documentation (from claude-code-plugins-plus)

---

**Last Updated**: 2025-12-25
**Status**: Code complete - ready for testing
**Version**: 2.0 (29-category system with dual-vault routing)
