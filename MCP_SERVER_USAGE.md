# Scanner MCP Server - Usage Guide

## Overview

The Scanner MCP Server provides claude.ai with direct access to your Scanner UI document processing system. You can upload documents, view processing history, manage prompts, and re-process documents directly from claude.ai conversations.

---

## Connection Details

### Server URL
```
https://scanner-mcp.redleif.dev
```

### Authentication
**Bearer Token:**
```
SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k=
```

---

## Connecting from claude.ai

### Desktop App (Recommended)

1. Open Claude Desktop settings
2. Navigate to "Developer" → "MCP Servers"
3. Click "Add Server"
4. Configure:
   - **Name:** Scanner UI
   - **Type:** SSE (Server-Sent Events)
   - **URL:** `https://scanner-mcp.redleif.dev`
   - **Authentication:** Bearer Token
   - **Token:** `SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k=`

### Web Interface

Claude.ai web interface support for remote MCP servers may vary. Check the claude.ai documentation for current MCP integration capabilities.

---

## Available Tools (8)

### 1. scanner_upload_document
Upload a PDF document to Scanner UI for Claude Code processing.

**Parameters:**
- `file_path` (required): Absolute path to PDF file
- `source` (optional): Source identifier (default: "mcp")
- `paperless_id` (optional): Paperless document ID for UPDATE mode

**Example:**
```
Upload /path/to/document.pdf for processing
```

---

### 2. scanner_list_documents
List processed documents with filtering and pagination.

**Parameters:**
- `category` (optional): Filter by MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL
- `status` (optional): Filter by completed, processing, failed
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Max results (1-100, default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `response_format` (optional): 'json' or 'markdown' (default: json)

**Example:**
```
Show me the last 10 medical documents
```

---

### 3. scanner_get_document_details
Get complete details for a specific document including Claude Code logs.

**Parameters:**
- `document_id` (required): Database ID of the document
- `response_format` (optional): 'json' or 'markdown' (default: json)

**Returns:**
- Document metadata
- Classification and metadata extraction prompts/responses
- Files created (Paperless uploads, BasicMemory notes)
- Claude Code processing logs
- Error messages (if any)

**Example:**
```
Show me full details for document ID 23
```

---

### 4. scanner_list_prompts
List all available Claude Code prompts used for classification and metadata extraction.

**No parameters required**

**Example:**
```
What prompts are available?
```

---

### 5. scanner_get_prompt
Get the full content of a specific Claude Code prompt.

**Parameters:**
- `prompt_name` (required): Name of prompt (classify, medical, expense, schoolwork)

**Example:**
```
Show me the medical metadata extraction prompt
```

---

### 6. scanner_update_prompt
Update a Claude Code prompt with automatic backup.

**Parameters:**
- `prompt_name` (required): Name of prompt to update
- `content` (required): New prompt content

**Example:**
```
Update the classify prompt to include a new category for "LEGAL" documents
```

---

### 7. scanner_reprocess_document
Re-process an existing document with optional corrections.

**Parameters:**
- `document_id` (required): Database ID of document to reprocess
- `corrections` (optional): JSON object with corrections

**Example:**
```
Reprocess document 19 with the correction that it's for Morgan, not Jacob
```

---

### 8. scanner_health_check
Check if the MCP server and Scanner UI are healthy.

**No parameters required**

**Returns:**
- scanner_mcp: healthy/unhealthy
- database: healthy/unhealthy
- scanner_ui: healthy/unhealthy
- prompts_dir: healthy/unhealthy
- overall: healthy/degraded

**Example:**
```
Check the health status of the scanner system
```

---

## Example Workflows

### Workflow 1: Check Recent Documents
```
1. "Show me the last 5 documents processed"
   → Uses scanner_list_documents with limit=5

2. "Show me full details for document ID 23"
   → Uses scanner_get_document_details with document_id=23
```

### Workflow 2: Upload and Monitor
```
1. "Upload /path/to/receipt.pdf for processing"
   → Uses scanner_upload_document

2. "Check the health status"
   → Uses scanner_health_check to monitor processing

3. "Show me recent documents"
   → Uses scanner_list_documents to find the newly processed document
```

### Workflow 3: Prompt Management
```
1. "What prompts are available?"
   → Uses scanner_list_prompts

2. "Show me the medical prompt"
   → Uses scanner_get_prompt with prompt_name="medical"

3. "Update the medical prompt to ask for provider phone numbers"
   → Uses scanner_update_prompt with modifications
```

### Workflow 4: Document Re-processing
```
1. "Show me document 19"
   → Uses scanner_get_document_details

2. "Reprocess document 19 with the note that it's for Morgan"
   → Uses scanner_reprocess_document with corrections
```

---

## Database Schema

### processing_history Table
- `id`: Document database ID
- `filename`: Original PDF filename
- `category`: MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL
- `status`: success, failed, pending_clarification
- `paperless_id`: Paperless-NGX document ID (if uploaded)
- `basicmemory_path`: BasicMemory note path (if created)
- `processing_time_ms`: Processing duration in milliseconds
- `error_message`: Error details (if failed)
- `created_at`: Processing timestamp
- `classification_prompt`: Prompt sent to Claude Code
- `classification_response`: Classification result
- `metadata_prompt`: Metadata extraction prompt
- `metadata_response`: Extracted metadata
- `files_created`: JSON list of created files
- `corrections`: JSON with user corrections

---

## Security Notes

1. **Bearer Token**: Keep the token secure - it provides full access to Scanner UI operations
2. **HTTPS Only**: All communication is encrypted via HTTPS
3. **Read-Only Database**: The MCP server has read-only access to the database
4. **File Access**: Limited to configured directories (prompts, incoming, completed)

---

## Troubleshooting

### "Error: Database error"
- Database may be locked or corrupted
- Check scanner-mcp container logs: `docker logs scanner-mcp`

### "Error: File not found"
- File may have been moved or deleted
- Check the completed directory: `/home/jodfie/scan-processor/completed/`

### "Error: API request failed"
- Scanner UI may be down
- Check Scanner UI container: `docker logs scan-processor-ui`

### Connection Issues
- Verify the server is running: `curl https://scanner-mcp.redleif.dev/`
- Should return "Not Found" (this is expected - MCP uses specific endpoints)
- Check bearer token is correct

---

## Technical Details

- **Framework**: FastMCP (Python MCP SDK)
- **Transport**: Streamable HTTP (stateless, production-ready)
- **Authentication**: Bearer token via TokenVerifier
- **Port**: 8003 (internal), 443 (external via HTTPS)
- **Deployment**: Docker container with nginx reverse proxy
- **Monitoring**: Uptime Kuma integration

---

## Related Systems

- **Scanner UI**: https://scanui.redleif.dev - Web interface
- **Paperless-NGX**: https://paperless.redleif.dev - Document management
- **BasicMemory**: MCP server for note management

---

## Version History

- **v1.0** (2025-12-23): Initial release
  - 8 tools implemented
  - Bearer token authentication
  - Full database query support
  - Prompt management
  - Document re-processing
