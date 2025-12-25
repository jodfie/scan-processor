#!/usr/bin/env python3
"""
MCP Server for Scanner UI.

This server provides tools to interact with the Scanner UI document processing system,
including document upload, history viewing, prompt management, and re-processing capabilities.
"""

import os
import json
import sqlite3
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pathlib import Path
import shutil
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import TokenVerifier, AccessToken

# Initialize the MCP server with HTTP transport configuration
mcp = FastMCP(
    "scanner_mcp",
    stateless_http=True,
    json_response=True,
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8003")),
    streamable_http_path="/mcp"
)

# Environment configuration
SCANNER_UI_URL = os.getenv("SCANNER_UI_URL", "http://scanui:5001")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/queue/pending.db")
PROMPTS_DIR = os.getenv("PROMPTS_DIR", "/app/prompts")
INCOMING_DIR = os.getenv("INCOMING_DIR", "/app/incoming")
COMPLETED_DIR = os.getenv("COMPLETED_DIR", "/app/completed")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

# Bearer token verifier for authentication
class ScannerTokenVerifier(TokenVerifier):
    """Simple bearer token verification."""

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        """Verify the bearer token matches our configured token."""
        if not BEARER_TOKEN:
            # No authentication required if token not set
            return AccessToken(sub="anonymous", exp=None)

        if token == BEARER_TOKEN:
            return AccessToken(sub="scanner_ui_user", exp=None)

        return None

# Apply token verifier if token is configured
if BEARER_TOKEN:
    mcp.token_verifier = ScannerTokenVerifier()

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"

class DocumentStatus(str, Enum):
    """Document processing status."""
    COMPLETED = "completed"
    PROCESSING = "processing"
    FAILED = "failed"

class DocumentCategory(str, Enum):
    """Document categories."""
    MEDICAL = "MEDICAL"
    CPS_EXPENSE = "CPS_EXPENSE"
    SCHOOLWORK = "SCHOOLWORK"
    GENERAL = "GENERAL"

# Pydantic Models for Input Validation

class UploadDocumentInput(BaseModel):
    """Input model for document upload."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    file_path: str = Field(..., description="Path to PDF file to upload", min_length=1)
    source: str = Field(default="mcp", description="Source identifier (default: 'mcp')", max_length=50)
    paperless_id: Optional[int] = Field(default=None, description="Optional Paperless document ID for UPDATE mode", ge=1)

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path is safe and exists."""
        path = Path(v)
        if not path.is_file():
            raise ValueError(f"File does not exist: {v}")
        if path.suffix.lower() != '.pdf':
            raise ValueError("Only PDF files are supported")
        return str(path.absolute())

class ListDocumentsInput(BaseModel):
    """Input model for listing documents."""
    model_config = ConfigDict(str_strip_whitespace=True)

    category: Optional[DocumentCategory] = Field(default=None, description="Filter by category (MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL)")
    status: Optional[DocumentStatus] = Field(default=None, description="Filter by status (completed, processing, failed)")
    date_from: Optional[str] = Field(default=None, description="Start date filter (YYYY-MM-DD format)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    date_to: Optional[str] = Field(default=None, description="End date filter (YYYY-MM-DD format)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    limit: int = Field(default=50, description="Maximum results to return", ge=1, le=100)
    offset: int = Field(default=0, description="Results offset for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="Output format: 'json' or 'markdown'")

class GetDocumentDetailsInput(BaseModel):
    """Input model for getting document details."""
    model_config = ConfigDict(str_strip_whitespace=True)

    document_id: int = Field(..., description="Database ID of the document", ge=1)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON, description="Output format: 'json' or 'markdown'")

class GetPromptInput(BaseModel):
    """Input model for getting a prompt."""
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt_name: str = Field(..., description="Name of prompt (classify, medical, expense, schoolwork)", min_length=1, max_length=50)

    @field_validator('prompt_name')
    @classmethod
    def validate_prompt_name(cls, v: str) -> str:
        """Validate prompt name is alphanumeric."""
        if not v.replace('_', '').isalnum():
            raise ValueError("Prompt name must be alphanumeric with optional underscores")
        return v

class UpdatePromptInput(BaseModel):
    """Input model for updating a prompt."""
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt_name: str = Field(..., description="Name of prompt to update", min_length=1, max_length=50)
    content: str = Field(..., description="New prompt content", min_length=1)

    @field_validator('prompt_name')
    @classmethod
    def validate_prompt_name(cls, v: str) -> str:
        """Validate prompt name is alphanumeric."""
        if not v.replace('_', '').isalnum():
            raise ValueError("Prompt name must be alphanumeric with optional underscores")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt content cannot be empty or whitespace only")
        return v

class ReprocessDocumentInput(BaseModel):
    """Input model for reprocessing a document."""
    model_config = ConfigDict(str_strip_whitespace=True)

    document_id: int = Field(..., description="Database ID of document to reprocess", ge=1)
    corrections: Optional[Dict[str, Any]] = Field(default=None, description="Optional classification/metadata corrections as JSON object")

# Shared utility functions

def _get_db_connection() -> sqlite3.Connection:
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

async def _make_scanner_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    """Make an HTTP request to Scanner UI API."""
    url = f"{SCANNER_UI_URL}/{endpoint.lstrip('/')}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

def _handle_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID or path is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. Check authentication credentials."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}: {e.response.text}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The operation is taking longer than expected."
    elif isinstance(e, sqlite3.Error):
        return f"Error: Database error: {str(e)}"
    elif isinstance(e, FileNotFoundError):
        return f"Error: File not found: {str(e)}"
    return f"Error: {type(e).__name__}: {str(e)}"

# Tool implementations

@mcp.tool(
    name="scanner_upload_document",
    annotations={
        "title": "Upload Document to Scanner UI",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def scanner_upload_document(params: UploadDocumentInput) -> str:
    """
    Upload a PDF document to Scanner UI for processing.

    This tool uploads a document to the Scanner UI incoming directory where it will be
    automatically processed by Claude Code for classification and metadata extraction.
    If a paperless_id is provided, it will UPDATE the existing Paperless document
    instead of creating a new one.

    Args:
        params (UploadDocumentInput): Validated input parameters containing:
            - file_path (str): Absolute path to PDF file to upload
            - source (str): Source identifier (default: "mcp")
            - paperless_id (Optional[int]): Paperless document ID for UPDATE mode

    Returns:
        str: JSON-formatted response:
        Success: {"success": true, "message": "...", "filename": "..."}
        Error: "Error: <error message>"
    """
    try:
        file_path = Path(params.file_path)

        # Open and upload file via API
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            data = {'source': params.source}

            if params.paperless_id:
                data['paperless_id'] = str(params.paperless_id)

            # Upload to Scanner UI
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SCANNER_UI_URL}/api/upload",
                    files=files,
                    data=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()

        return json.dumps({
            "success": True,
            "message": result.get("message", "Document uploaded successfully"),
            "filename": result.get("filename", file_path.name)
        }, indent=2)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_list_documents",
    annotations={
        "title": "List Processed Documents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def scanner_list_documents(params: ListDocumentsInput) -> str:
    """
    List processed documents with optional filtering and pagination.

    This tool queries the Scanner UI database to retrieve a list of documents that have
    been processed, with support for filtering by category, status, and date range.
    Results are paginated for efficient retrieval.

    Args:
        params (ListDocumentsInput): Validated input parameters containing:
            - category (Optional[str]): Filter by category (MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL)
            - status (Optional[str]): Filter by status (completed, processing, failed)
            - date_from (Optional[str]): Start date (YYYY-MM-DD)
            - date_to (Optional[str]): End date (YYYY-MM-DD)
            - limit (int): Maximum results (1-100, default: 50)
            - offset (int): Pagination offset (default: 0)
            - response_format (str): Output format ('json' or 'markdown')

    Returns:
        str: JSON or Markdown formatted list of documents with pagination info

        JSON format:
        {
            "total": int,
            "count": int,
            "offset": int,
            "has_more": bool,
            "next_offset": int|null,
            "documents": [
                {
                    "id": int,
                    "filename": str,
                    "category": str,
                    "status": str,
                    "timestamp": str,
                    "paperless_id": int|null
                }
            ]
        }
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = """
            SELECT
                id, filename, category, status, created_at as timestamp,
                paperless_id
            FROM processing_history
            WHERE 1=1
        """
        params_list = []

        if params.category:
            query += " AND category = ?"
            params_list.append(params.category.value)

        if params.status:
            query += " AND status = ?"
            params_list.append(params.status.value)

        if params.date_from:
            query += " AND DATE(created_at) >= ?"
            params_list.append(params.date_from)

        if params.date_to:
            query += " AND DATE(created_at) <= ?"
            params_list.append(params.date_to)

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({query})"
        cursor.execute(count_query, params_list)
        total = cursor.fetchone()['total']

        # Add pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params_list.extend([params.limit, params.offset])

        cursor.execute(query, params_list)
        rows = cursor.fetchall()

        documents = [dict(row) for row in rows]
        count = len(documents)
        has_more = total > (params.offset + count)
        next_offset = (params.offset + count) if has_more else None

        conn.close()

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# Scanner UI - Processed Documents", ""]
            lines.append(f"**Total**: {total} documents | **Showing**: {count} | **Offset**: {params.offset}")
            lines.append("")

            for doc in documents:
                lines.append(f"## {doc['filename']}")
                lines.append(f"- **ID**: {doc['id']}")
                lines.append(f"- **Category**: {doc['category']}")
                lines.append(f"- **Status**: {doc['status']}")
                lines.append(f"- **Processed**: {doc['timestamp']}")
                if doc['paperless_id']:
                    lines.append(f"- **Paperless ID**: {doc['paperless_id']}")
                lines.append("")

            if has_more:
                lines.append(f"*Use offset={next_offset} to see more results*")

            return "\n".join(lines)
        else:
            return json.dumps({
                "total": total,
                "count": count,
                "offset": params.offset,
                "has_more": has_more,
                "next_offset": next_offset,
                "documents": documents
            }, indent=2)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_get_document_details",
    annotations={
        "title": "Get Document Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def scanner_get_document_details(params: GetDocumentDetailsInput) -> str:
    """
    Get full details for a specific document including Claude Code processing logs.

    This tool retrieves complete information about a processed document, including
    the classification and metadata extraction prompts/responses, files created,
    and any Claude Code logs.

    Args:
        params (GetDocumentDetailsInput): Validated input parameters containing:
            - document_id (int): Database ID of the document
            - response_format (str): Output format ('json' or 'markdown')

    Returns:
        str: JSON or Markdown formatted document details including:
        - Document metadata (filename, category, status, timestamps)
        - Classification prompt and response
        - Metadata extraction prompt and response
        - Files created (Paperless uploads, BasicMemory notes)
        - Claude Code processing logs
        - Any error messages
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # Get document details
        cursor.execute("""
            SELECT *
            FROM processing_history
            WHERE id = ?
        """, (params.document_id,))

        doc = cursor.fetchone()
        if not doc:
            conn.close()
            return f"Error: Document with ID {params.document_id} not found"

        doc_dict = dict(doc)

        # Get Claude Code logs
        cursor.execute("""
            SELECT prompt_type, prompt_file, confidence, success, error_message, created_at
            FROM claude_code_logs
            WHERE filename = ?
            ORDER BY created_at ASC
        """, (doc_dict['filename'],))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Parse files_created if it exists
        files_created = []
        if doc_dict.get('files_created'):
            try:
                files_created = json.loads(doc_dict['files_created'])
            except:
                pass

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# Document Details: {doc_dict['filename']}", ""]

            lines.append("## Overview")
            lines.append(f"- **ID**: {doc_dict['id']}")
            lines.append(f"- **Category**: {doc_dict['category']}")
            lines.append(f"- **Status**: {doc_dict['status']}")
            lines.append(f"- **Processed**: {doc_dict['created_at']}")
            lines.append(f"- **Processing Time**: {doc_dict.get('processing_time_ms', 0)}ms")
            if doc_dict.get('paperless_id'):
                lines.append(f"- **Paperless ID**: {doc_dict['paperless_id']}")
            if doc_dict.get('basicmemory_path'):
                lines.append(f"- **BasicMemory Note**: {doc_dict['basicmemory_path']}")
            lines.append("")

            if doc_dict.get('classification_response'):
                lines.append("## Classification Response")
                lines.append(f"```\n{doc_dict['classification_response']}\n```")
                lines.append("")

            if doc_dict.get('metadata_response'):
                lines.append("## Metadata Extraction Response")
                lines.append(f"```\n{doc_dict['metadata_response']}\n```")
                lines.append("")

            if files_created:
                lines.append("## Files Created")
                for file_info in files_created:
                    lines.append(f"- **{file_info.get('type', 'Unknown')}**: {file_info.get('path', 'N/A')}")
                lines.append("")

            if logs:
                lines.append("## Processing Logs")
                for log in logs:
                    lines.append(f"### {log['prompt_type'].upper()} - {log['created_at']}")
                    lines.append(f"- **File**: {log['prompt_file']}")
                    lines.append(f"- **Success**: {bool(log['success'])}")
                    if log['confidence']:
                        lines.append(f"- **Confidence**: {log['confidence']}")
                    if log['error_message']:
                        lines.append(f"- **Error**: {log['error_message']}")
                    lines.append("")

            if doc_dict.get('error_message'):
                lines.append("## Error")
                lines.append(f"```\n{doc_dict['error_message']}\n```")

            return "\n".join(lines)
        else:
            return json.dumps({
                "document": doc_dict,
                "files_created": files_created,
                "logs": logs
            }, indent=2, default=str)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_list_prompts",
    annotations={
        "title": "List Available Prompts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def scanner_list_prompts() -> str:
    """
    List all available Claude Code prompts.

    This tool scans the prompts directory and returns information about all available
    prompt files used for document classification and metadata extraction.

    Returns:
        str: JSON-formatted list of prompts:
        {
            "prompts": [
                {
                    "name": str,
                    "display_name": str,
                    "path": str,
                    "exists": bool,
                    "size": int,
                    "modified": str
                }
            ]
        }
    """
    try:
        prompts_path = Path(PROMPTS_DIR)
        prompts = []

        # Define expected prompts
        expected_prompts = {
            "classify": "Classification",
            "medical": "Medical Metadata",
            "expense": "Expense Metadata",
            "schoolwork": "Schoolwork Metadata"
        }

        for name, display_name in expected_prompts.items():
            file_path = prompts_path / f"{name}.md"

            prompt_info = {
                "name": name,
                "display_name": display_name,
                "path": str(file_path),
                "exists": file_path.exists()
            }

            if file_path.exists():
                stat = file_path.stat()
                prompt_info["size"] = stat.st_size
                prompt_info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            else:
                prompt_info["size"] = 0
                prompt_info["modified"] = None

            prompts.append(prompt_info)

        return json.dumps({"prompts": prompts}, indent=2)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_get_prompt",
    annotations={
        "title": "Get Prompt Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def scanner_get_prompt(params: GetPromptInput) -> str:
    """
    Get the content of a specific Claude Code prompt.

    This tool reads and returns the full content of a prompt file used for
    document classification or metadata extraction.

    Args:
        params (GetPromptInput): Validated input parameters containing:
            - prompt_name (str): Name of prompt (classify, medical, expense, schoolwork)

    Returns:
        str: JSON-formatted prompt information:
        {
            "name": str,
            "path": str,
            "size": int,
            "content": str
        }

        Or error message if prompt not found
    """
    try:
        prompt_path = Path(PROMPTS_DIR) / f"{params.prompt_name}.md"

        if not prompt_path.exists():
            return f"Error: Prompt '{params.prompt_name}' not found at {prompt_path}"

        content = prompt_path.read_text()
        stat = prompt_path.stat()

        return json.dumps({
            "name": params.prompt_name,
            "path": str(prompt_path),
            "size": stat.st_size,
            "content": content
        }, indent=2)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_update_prompt",
    annotations={
        "title": "Update Prompt Content",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def scanner_update_prompt(params: UpdatePromptInput) -> str:
    """
    Update a Claude Code prompt with automatic backup.

    This tool updates a prompt file with new content, creating a backup of the
    previous version before making changes. This is typically used through the
    Scanner UI web interface.

    Args:
        params (UpdatePromptInput): Validated input parameters containing:
            - prompt_name (str): Name of prompt to update
            - content (str): New prompt content (must not be empty)

    Returns:
        str: JSON-formatted response:
        Success: {"success": true, "message": "...", "backup_path": "..."}
        Error: "Error: <error message>"
    """
    try:
        # Use Scanner UI API for updates to ensure consistency
        result = await _make_scanner_request(
            f"/api/prompts/{params.prompt_name}",
            method="POST",
            json={"content": params.content}
        )

        return json.dumps({
            "success": result.get("success", False),
            "message": result.get("message", "Prompt updated"),
            "backup_path": result.get("backup_path", "")
        }, indent=2)

    except Exception as e:
        return _handle_error(e)

@mcp.tool(
    name="scanner_reprocess_document",
    annotations={
        "title": "Re-process Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def scanner_reprocess_document(params: ReprocessDocumentInput) -> str:
    """
    Re-process an existing document with optional corrections.

    This tool retrieves a previously processed document from the completed directory
    and copies it back to the incoming directory for re-processing. Optionally,
    corrections can be provided to guide the classification and metadata extraction.

    Args:
        params (ReprocessDocumentInput): Validated input parameters containing:
            - document_id (int): Database ID of document to reprocess
            - corrections (Optional[dict]): Classification/metadata corrections as JSON

    Returns:
        str: JSON-formatted response:
        Success: {
            "success": true,
            "message": "...",
            "original_filename": "...",
            "new_filename": "..."
        }
        Error: "Error: <error message>"
    """
    try:
        # Get document details from database
        conn = _get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT filename, category
            FROM processing_history
            WHERE id = ?
        """, (params.document_id,))

        doc = cursor.fetchone()
        conn.close()

        if not doc:
            return f"Error: Document with ID {params.document_id} not found in database"

        original_filename = doc['filename']

        # Look for file in completed directory
        completed_path = Path(COMPLETED_DIR) / original_filename

        if not completed_path.exists():
            return f"Error: Document file not found in completed directory: {original_filename}"

        # Generate new filename for incoming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_reprocess_{original_filename}"
        incoming_path = Path(INCOMING_DIR) / new_filename

        # Copy file to incoming directory
        shutil.copy2(completed_path, incoming_path)

        # If corrections provided, create metadata file
        if params.corrections:
            metadata_path = Path(INCOMING_DIR) / f"{new_filename}.corrections.json"
            with open(metadata_path, 'w') as f:
                json.dump(params.corrections, f, indent=2)

        return json.dumps({
            "success": True,
            "message": "Document queued for re-processing",
            "original_filename": original_filename,
            "new_filename": new_filename,
            "corrections_applied": bool(params.corrections)
        }, indent=2)

    except Exception as e:
        return _handle_error(e)

# Health check endpoint
@mcp.tool(
    name="scanner_health_check",
    annotations={
        "title": "Health Check",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def scanner_health_check() -> str:
    """
    Check if the MCP server and Scanner UI are healthy.

    Returns:
        str: JSON-formatted health status
    """
    health = {
        "scanner_mcp": "healthy",
        "database": "unknown",
        "scanner_ui": "unknown",
        "prompts_dir": "unknown"
    }

    # Check database
    try:
        conn = _get_db_connection()
        conn.close()
        health["database"] = "healthy"
    except:
        health["database"] = "unhealthy"

    # Check Scanner UI
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SCANNER_UI_URL}/", timeout=5.0)
            health["scanner_ui"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["scanner_ui"] = "unhealthy"

    # Check prompts directory
    try:
        prompts_path = Path(PROMPTS_DIR)
        health["prompts_dir"] = "healthy" if prompts_path.exists() else "unhealthy"
    except:
        health["prompts_dir"] = "unhealthy"

    health["overall"] = "healthy" if all(v == "healthy" for v in health.values()) else "degraded"

    return json.dumps(health, indent=2)

if __name__ == "__main__":
    # Run with streamable HTTP transport (configured in FastMCP initialization above)
    # Host, port, and path are set during FastMCP() initialization
    mcp.run(transport="streamable-http")
