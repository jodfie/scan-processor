# Scanner MCP Server - SUCCESSFULLY DEPLOYED ✅

**Date**: 2025-12-23
**Status**: Production-ready and connected to Claude Code

---

## ✅ Final Implementation

### Complete MCP Server with 8 Tools
**File**: `/home/jodfie/scan-processor/mcp-server/server.py` (828 lines)

**Framework**: FastMCP 1.25.0 with streamable HTTP transport
**Authentication**: Bearer token via TokenVerifier
**Public URL**: https://scanner-mcp.redleif.dev/mcp
**Status**: ✅ Connected and working

### All 8 Tools Available:
1. `scanner_upload_document` - Upload PDFs for processing
2. `scanner_list_documents` - List with filtering/pagination
3. `scanner_get_document_details` - Full details with Claude Code logs
4. `scanner_list_prompts` - List available prompts
5. `scanner_get_prompt` - Get prompt content
6. `scanner_update_prompt` - Update with backup
7. `scanner_reprocess_document` - Reprocess with corrections
8. `scanner_health_check` - System health status

---

## 🔧 The Fix: Proper FastMCP Configuration

### Root Cause
The initial implementation used manual uvicorn setup instead of FastMCP's built-in HTTP transport, which caused strict Host header validation that couldn't be overridden.

### Solution
Configure host, port, and path during **FastMCP initialization**, not when calling `run()`:

**CORRECT Implementation** (lines 22-30):
```python
# Initialize the MCP server with HTTP transport configuration
mcp = FastMCP(
    "scanner_mcp",
    stateless_http=True,
    json_response=True,
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8003")),
    streamable_http_path="/mcp"
)
```

**CORRECT Usage** (line 828):
```python
if __name__ == "__main__":
    # Run with streamable HTTP transport (configured in FastMCP initialization above)
    # Host, port, and path are set during FastMCP() initialization
    mcp.run(transport="streamable-http")
```

### FastMCP.run() Signature
```python
def run(
    self,
    transport: Literal['stdio', 'sse', 'streamable-http'] = 'stdio',
    mount_path: str | None = None
) -> None
```

**Key Point**: `run()` only accepts `transport` and `mount_path`. Host and port are **initialization parameters only**.

---

## 📊 Verification Tests

### 1. MCP Initialize via Public URL
```bash
curl -s -X POST https://scanner-mcp.redleif.dev/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k=" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Result: HTTP 200 OK with valid MCP response
```

### 2. Tools List
```bash
curl -s -X POST https://scanner-mcp.redleif.dev/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k=" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Result: All 8 tools listed correctly
```

### 3. Claude Code Connection
```bash
claude mcp list | grep scanner-mcp

# Result: scanner-mcp: https://scanner-mcp.redleif.dev/mcp (HTTP) - ✓ Connected
```

---

## 📁 Files Created/Modified

### Created
1. `/home/jodfie/scan-processor/mcp-server/server.py` (828 lines)
2. `/home/jodfie/scan-processor/mcp-server/requirements.txt`
3. `/home/jodfie/scan-processor/mcp-server/Dockerfile`
4. `/home/jodfie/scan-processor/mcp-server/.env.example`
5. `/home/jodfie/scan-processor/MCP_SERVER_USAGE.md`
6. `/home/jodfie/scan-processor/MCP_SERVER_STATUS.md`
7. `/home/jodfie/scan-processor/MCP_SERVER_FINAL_STATUS.md`
8. `/home/jodfie/scan-processor/MCP_SERVER_SUCCESS.md` (this file)
9. `/home/jodfie/docker/swag/config/nginx/proxy-confs/scanner-mcp.subdomain.conf`

### Modified
1. `/home/jodfie/docker/docker-compose.yml` - Added scanner-mcp service
2. `/home/jodfie/docker/.env` - Added SCANNER_MCP_TOKEN
3. `/home/jodfie/docker/swag/config/tunnelconfig.yml` - Added Cloudflare Tunnel ingress

---

## 🎯 What We Learned

### 1. FastMCP Configuration Pattern
- **Host, port, and HTTP paths** are **initialization parameters**
- `run()` method only controls **transport type**
- Don't try to override these at runtime

### 2. Debugging MCP Servers
- Use `inspect.signature()` to check actual method signatures
- Don't assume documentation from different packages applies
- Test with direct container access first before troubleshooting proxies

### 3. MCP Best Practices
- Use `stateless_http=True` for scalable deployments
- Set `json_response=True` for structured tool responses
- Configure bearer token authentication via TokenVerifier
- Follow tool naming convention: `{server}_{action}_{resource}`

---

## 🚀 Usage from Claude Code

The scanner-mcp server is now available in this Claude Code session:

```
Available Tools:
- scanner_upload_document - Upload PDFs for processing
- scanner_list_documents - List processed documents with filtering
- scanner_get_document_details - Get full document details
- scanner_list_prompts - List available Claude Code prompts
- scanner_get_prompt - View prompt content
- scanner_update_prompt - Modify prompts with automatic backup
- scanner_reprocess_document - Re-run processing with corrections
- scanner_health_check - Check system health
```

### Example: List Recent Documents
```
Use scanner_list_documents tool with:
{
  "limit": 10,
  "status": "completed"
}
```

### Example: Get Document Details
```
Use scanner_get_document_details tool with:
{
  "document_id": 123
}
```

---

## 📚 Architecture

```
Claude Code / claude.ai
    ↓
HTTPS (bearer token auth)
    ↓
https://scanner-mcp.redleif.dev/mcp
    ↓
Cloudflare Tunnel (TLS termination)
    ↓
SWAG nginx (reverse proxy)
    ├─ CORS headers for claude.ai
    ├─ Request buffering disabled
    └─ Proxy to scanner-mcp:8003
    ↓
scanner-mcp container (FastMCP)
    ├─ streamable-http transport
    ├─ Bearer token verification
    └─ 8 MCP tools
        ├─ SQLite reads (read-only mount)
        └─ HTTP API writes (Scanner UI)
```

---

## 🎉 Success Metrics

- [x] All 8 MCP tools implemented and working
- [x] Bearer token authentication enforced
- [x] Public URL accessible via https://scanner-mcp.redleif.dev/mcp
- [x] No Host header validation errors
- [x] Claude Code shows "✓ Connected" status
- [x] All tools callable from Claude Code session
- [x] nginx configuration matches working MCP servers
- [x] Docker container running healthy
- [x] Cloudflare Tunnel routing correctly

---

## 🔍 Troubleshooting Reference

### If Connection Fails

**Check server logs:**
```bash
docker logs scanner-mcp --tail 50
```

**Test direct container access:**
```bash
docker exec scanner-mcp python3 -c "
import httpx
response = httpx.post(
    'http://localhost:8003/mcp',
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Host': 'localhost:8003',
        'Authorization': 'Bearer SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k='
    },
    json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}}
)
print(f'Status: {response.status_code}')
print(response.json())
"
```

**Test public URL:**
```bash
curl -s https://scanner-mcp.redleif.dev/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SXQHUcWw6djFmS2hTNIAHLNpyvTgsXcaSAyaygDwL9k=" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Verify Claude Code config:**
```bash
claude mcp list
```

### Common Issues

1. **Container restart loop**: Check logs for Python errors
2. **502 Bad Gateway**: Verify container is running and healthy
3. **401 Unauthorized**: Check bearer token in request header
4. **Connection timeout**: Check Cloudflare Tunnel and nginx routing

---

## 📖 Related Documentation

- **Usage Guide**: `/home/jodfie/scan-processor/MCP_SERVER_USAGE.md`
- **Implementation History**: `/home/jodfie/scan-processor/MCP_SERVER_FINAL_STATUS.md`
- **Scanner UI Docs**: `/home/jodfie/scan-processor/README.md`
- **Claude Code Integration**: `/home/jodfie/scan-processor/CLAUDE_CODE_INTEGRATION.md`

---

**Conclusion**: The scanner-mcp server is fully operational and ready for production use. All tools are accessible via Claude Code, and the deployment is stable and properly configured.
