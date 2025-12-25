# iOS Shortcuts Integration Guide

Complete guide for uploading documents to the Scan Processor from your iPhone using the Shortcuts app.

> **📌 Note**: This is the detailed user-facing guide. For architecture and deployment details, see:
> `/home/jodfie/vault/jodys-brain/TechKB/10-projects/14-scan-processor/Scanner-UI-iOS-Upload-Integration.md`
>
> **⚡ Quick Start**: New to iOS Shortcuts? Start with [IOS_SHORTCUTS_QUICK_START.md](IOS_SHORTCUTS_QUICK_START.md)
>
> **🤔 Scan Processor vs Paperless App**: See [UPLOAD_WORKFLOW_COMPARISON.md](UPLOAD_WORKFLOW_COMPARISON.md) for workflow differences

---

## Overview

The Scan Processor provides a simple API endpoint that works perfectly with iOS Shortcuts. You can:

- **Scan documents** with your iPhone camera
- **Upload PDFs** from Files app
- **Share PDFs** from other apps directly to processing
- **Get instant confirmation** when upload succeeds
- **Automatic processing** starts immediately after upload

---

## Quick Start

### Endpoint Details

**URL**: `https://scanui.redleif.dev/api/upload`

**Method**: `POST`

**Content-Type**: `multipart/form-data`

**Body**: File field named `file` with your PDF

**Response**: JSON with upload confirmation

---

## Step-by-Step: Create iOS Shortcut

### Option 1: Scan Document and Upload

This shortcut lets you scan a document with your camera and upload it directly.

1. **Open Shortcuts App** on your iPhone
2. **Tap "+" to create new shortcut**
3. **Add these actions in order:**

#### Action 1: Scan Documents
- Search for "Scan Documents"
- Add the action
- This will use your camera to scan

#### Action 2: Get Name of Input
- Search for "Get Name"
- Add "Get Name of Scan Documents"
- This extracts the filename

#### Action 3: Set Variable
- Search for "Set Variable"
- Name it: `FileName`
- Set to: `Name`

#### Action 4: Format Date
- Search for "Format Date"
- Format: `Custom`
- Format String: `yyyyMMdd_HHmmss`
- This creates a timestamp

#### Action 5: Set Variable
- Name it: `Timestamp`
- Set to: `Formatted Date`

#### Action 6: Get File
- Search for "Get File"
- Select: `Scan Documents`

#### Action 7: Set Name
- Search for "Set Name"
- Rename to: `{Timestamp}_{FileName}.pdf`
- This creates: `20251221_171500_Document.pdf`

#### Action 8: Get URL
- Search for "URL"
- Type: `https://scanui.redleif.dev/api/upload`

#### Action 9: Get Contents of URL
- Search for "Get Contents of URL"
- **Method**: `POST`
- **Request Body**: `Form`
- **Add Field**:
  - **Key**: `file`
  - **Type**: `File`
  - **Value**: `Renamed File`

#### Action 10: Show Result (Optional)
- Search for "Show Result"
- Show: `Contents of URL`
- Displays success message

4. **Name your shortcut**: "Upload Scan to Processor"
5. **Save**

---

### Option 2: Upload Existing PDF

This shortcut lets you select a PDF from Files app and upload it.

1. **Open Shortcuts App**
2. **Create new shortcut**
3. **Add these actions:**

#### Action 1: Select File
- Search for "Select File"
- Add the action
- **File Types**: PDFs only

#### Action 2: Get Name
- Get Name of `Selected File`

#### Action 3: Format Date
- Format: `yyyyMMdd_HHmmss`

#### Action 4: Set Variable
- Name: `Timestamp`

#### Action 5: Rename File
- Rename `Selected File`
- To: `{Timestamp}_{Name}.pdf`

#### Action 6: Get Contents of URL
- **URL**: `https://scanui.redleif.dev/api/upload`
- **Method**: `POST`
- **Request Body**: `Form`
- **Add Field**:
  - **Key**: `file`
  - **Type**: `File`
  - **Value**: `Renamed File`

#### Action 7: Show Notification
- Title: "Upload Complete"
- Body: `Contents of URL`

4. **Name**: "Upload PDF to Processor"
5. **Save**

---

### Option 3: Share Sheet Integration

Add to iOS Share Sheet to upload PDFs from any app.

1. **Create shortcut** (same as Option 2)
2. **Instead of "Select File"**, use **"Receive Input"**:
   - Search for "Receive Input"
   - Add as first action
   - Input Type: `Files`
   - Replace "Selected File" references with "Shortcut Input"

3. **Enable in Share Sheet**:
   - Tap shortcut settings (⋯)
   - Toggle **"Show in Share Sheet"**
   - Toggle **"Accept Files"** and select PDFs

4. **Usage**: From any app with a PDF, tap Share → Your Shortcut

---

## Example Response

### Successful Upload

```json
{
  "success": true,
  "filename": "20251221_171500_Morgan_Doctor_Visit.pdf",
  "message": "File uploaded successfully and queued for processing"
}
```

### Error Response

```json
{
  "error": "Only PDF files are allowed"
}
```

---

## File Naming Best Practices

The system works best with descriptive filenames. The Shortcut automatically adds a timestamp, but you can customize the filename:

**Recommended Format**: `YYYYMMDD_HHMMSS_[Child]_[Description].pdf`

**Examples**:
- `20251221_171500_Morgan_Doctor_Visit.pdf`
- `20251221_090000_Jacob_School_Report_Card.pdf`
- `20251221_143000_Medical_Bill_Prescription.pdf`

**Why Timestamps Matter**:
- Prevents filename conflicts
- Maintains chronological order
- Helps with processing history

---

## Advanced: Custom Metadata

You can add metadata by customizing the filename in your Shortcut:

### Ask for Child Name

Add this before the "Rename" action:

1. **Ask for Input**
   - Prompt: "Which child is this for?"
   - Input Type: `Text`
   - Default: Leave blank or set common names

2. **Set Variable**
   - Name: `ChildName`
   - Value: `Provided Input`

3. **Update Rename Action**
   - New format: `{Timestamp}_{ChildName}_{Name}.pdf`

### Ask for Category

1. **Choose from Menu**
   - Prompt: "What type of document?"
   - Options:
     - Medical
     - Expense
     - Schoolwork
     - General

2. **Set Variable**
   - Name: `Category`

3. **Update Rename**
   - Format: `{Timestamp}_{ChildName}_{Category}_{Name}.pdf`
   - Example: `20251221_171500_Morgan_Medical_Visit.pdf`

---

## Processing Pipeline

Once uploaded via Shortcut:

1. **File lands** in `incoming/` directory
2. **File watcher detects** new PDF (< 1 second)
3. **Claude Code classifies** document (5-15 seconds)
4. **Metadata extracted** based on category (10-20 seconds)
5. **Uploaded to Paperless** with tags (2-5 seconds)
6. **BasicMemory note created** (if medical/expense)
7. **Pushover notification sent** (if important)
8. **File moved** to `completed/`

**Total time**: 30-120 seconds from iPhone upload to completion

---

## Monitoring Upload Status

### Via Web UI

1. **Dashboard**: https://scanui.redleif.dev
   - Shows real-time processing status
   - File appears immediately after upload

2. **History Page**: https://scanui.redleif.dev/history
   - View all processed documents
   - See classification results
   - Review extracted metadata

3. **Pending Page**: https://scanui.redleif.dev/pending
   - Documents needing clarification
   - Respond with additional info

### Via Pushover Notifications

For **MEDICAL** and **CPS_EXPENSE** documents, you'll receive:

- **Title**: Document category and child name
- **Message**: Key details (provider, amount, date)
- **Link**: Direct link to Paperless document

---

## Troubleshooting

### Upload Fails with "No file provided"

**Cause**: File field not properly configured

**Fix**:
- Check "Get Contents of URL" action
- Verify field name is exactly `file` (lowercase)
- Ensure field type is `File` not `Text`

### Upload Fails with "Only PDF files allowed"

**Cause**: Non-PDF file or incorrect content type

**Fix**:
- Ensure you're uploading a PDF
- Check file extension is `.pdf`
- If scanning, ensure "Scan Documents" saves as PDF

### Upload Succeeds but No Processing

**Cause**: File watcher service may not be running

**Check**:
```bash
systemctl --user status scan-processor-watcher
```

**Restart if needed**:
```bash
systemctl --user restart scan-processor-watcher
```

### Network/SSL Errors

**Cause**: Device can't reach server or certificate issues

**Fix**:
- Verify you can access https://scanui.redleif.dev in Safari
- Check you're not on VPN blocking the domain
- Try disabling "Validate SSL" in Shortcut (not recommended for production)

### File Name Too Long

**Cause**: Very long original filename + timestamp

**Fix**:
- Shorten the original filename before upload
- Or modify Shortcut to truncate filename

---

## Testing Your Shortcut

### Test Upload

1. **Create test PDF**:
   - Use Notes app to create a simple note
   - Export/Print as PDF
   - Or scan a blank page

2. **Run your Shortcut**

3. **Check Web UI**:
   - Open https://scanui.redleif.dev
   - File should appear in processing
   - Should complete within 30-120 seconds

4. **Verify in History**:
   - Go to https://scanui.redleif.dev/history
   - Your test file should be listed
   - Click to expand and see classification

---

## Security Considerations

### Current Setup

- **HTTPS**: All traffic encrypted via Cloudflare + SWAG
- **No Authentication**: Public endpoint (anyone with URL can upload)
- **File Validation**: Only PDFs accepted, 50MB max
- **Processing Isolation**: Files processed in isolated directories

### Recommended for Production

If you need to restrict access:

1. **Add API Key**: Modify endpoint to require secret key
2. **IP Whitelist**: Restrict to your home/mobile IP
3. **VPN**: Use Tailscale to access only on VPN
4. **Basic Auth**: Add HTTP basic authentication in SWAG

**For personal/family use**: Current setup is fine. All PDFs are stored on your private server.

---

## Example Shortcuts

### Complete "Scan & Upload" Shortcut

```
1. Scan Documents
2. Get Name of [Scan Documents]
3. Set Variable [FileName] to [Name]
4. Format Date [Current Date] as "yyyyMMdd_HHmmss"
5. Set Variable [Timestamp] to [Formatted Date]
6. Get File [Scan Documents]
7. Set Name of [File] to "[Timestamp]_[FileName].pdf"
8. Get Contents of URL
   - URL: https://scanui.redleif.dev/api/upload
   - Method: POST
   - Request Body: Form
   - Fields:
     - file: [Renamed File]
9. Show Notification
   - Title: "Scan Uploaded"
   - Body: [Contents of URL]
```

### Complete "Upload PDF" Shortcut

```
1. Select File (PDFs only)
2. Get Name of [Selected File]
3. Format Date [Current Date] as "yyyyMMdd_HHmmss"
4. Set Variable [Timestamp] to [Formatted Date]
5. Rename [Selected File] to "[Timestamp]_[Name].pdf"
6. Get Contents of URL
   - URL: https://scanui.redleif.dev/api/upload
   - Method: POST
   - Request Body: Form
   - Fields:
     - file: [Renamed File]
7. Show Result [Contents of URL]
```

---

## Advanced Integration

### Siri Voice Commands

After creating your Shortcut:

1. **Add to Siri**:
   - Tap shortcut settings
   - "Add to Siri"
   - Record phrase: "Upload scan to processor" or "Process document"

2. **Usage**: "Hey Siri, upload scan to processor"

### Automation Triggers

Create automated uploads based on triggers:

1. **Open Shortcuts app → Automation tab**
2. **Create Personal Automation**
3. **Choose Trigger**:
   - When file added to specific iCloud folder
   - At specific time of day
   - When arriving/leaving location
   - When NFC tag scanned

4. **Add Action**: Run your upload shortcut

**Example**: Auto-upload PDFs when you arrive home from doctor's office.

---

## API Reference

### Upload Endpoint

**POST** `https://scanui.redleif.dev/api/upload`

**Headers**:
```
Content-Type: multipart/form-data
```

**Body** (multipart/form-data):
```
file: <PDF file>
```

**Success Response** (200):
```json
{
  "success": true,
  "filename": "20251221_171500_document.pdf",
  "message": "File uploaded successfully and queued for processing"
}
```

**Error Responses**:

**400 - No file provided**:
```json
{
  "error": "No file provided"
}
```

**400 - No file selected**:
```json
{
  "error": "No file selected"
}
```

**400 - Invalid file type**:
```json
{
  "error": "Only PDF files are allowed"
}
```

**413 - File too large**:
```
Request Entity Too Large (>50MB)
```

### cURL Example

```bash
curl -X POST https://scanui.redleif.dev/api/upload \
  -F "file=@/path/to/document.pdf"
```

### Python Example

```python
import requests

url = "https://scanui.redleif.dev/api/upload"
files = {"file": open("document.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

---

## Integration with Other Apps

### Scanbot / Scanner Pro

Many scanning apps support "Custom Upload" or "Webhooks":

1. **Configure custom endpoint**:
   - URL: `https://scanui.redleif.dev/api/upload`
   - Method: POST
   - Field name: `file`

2. **Automatic upload** after scanning

### Documents by Readdle

1. **Select PDF**
2. **Share → Shortcuts → Your Upload Shortcut**

### Apple Notes

1. **Create note with scan**
2. **Export as PDF**
3. **Share → Shortcuts → Your Upload Shortcut**

---

## Support

### Check Upload Status

**Web UI**: https://scanui.redleif.dev/history

**Logs**: Available in web UI under real-time dashboard

### Common Issues

| Issue | Solution |
|-------|----------|
| Upload timeout | Check internet connection, try smaller file |
| SSL certificate error | Update iOS, verify domain works in Safari |
| Processing never completes | Check file watcher service status |
| File not classified correctly | Review/reprocess from History page |

### Need Help?

- **Web UI**: https://scanui.redleif.dev
- **Documentation**: `/home/jodfie/scan-processor/`
- **Logs**: https://scanui.redleif.dev/logs

---

## Quick Reference Card

**Endpoint**: `https://scanui.redleif.dev/api/upload`

**Method**: POST

**Field**: `file` (PDF, max 50MB)

**Response Time**: < 1 second for upload, 30-120s for processing

**Monitoring**: https://scanui.redleif.dev

**Categories**: MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL

**Notifications**: Pushover (MEDICAL + CPS_EXPENSE only)

---

## Related Documentation

**In This Directory** (`/home/jodfie/scan-processor/`):
- **IOS_SHORTCUTS_QUICK_START.md** - 5-minute quick start guide
- **CLAUDE.md** - System architecture and overview
- **README.md** - General usage and deployment
- **WEB_UI_DEV_MODE.md** - Web interface features
- **PENDING_SCREEN_GUIDE.md** - Handling clarifications
- **DEVELOPMENT_MODE.md** - Testing and development

**In TechKB** (`/home/jodfie/vault/jodys-brain/TechKB/10-projects/14-scan-processor/`):
- **Scanner-UI-iOS-Upload-Integration.md** - Architecture overview and deployment details
- **Scan-Processor-Pipeline-Setup.md** - Complete Claude Code pipeline
- **Scan-Processor-n8n-Migration.md** - Future n8n orchestration plans

---

*Last Updated: 2025-12-21*
