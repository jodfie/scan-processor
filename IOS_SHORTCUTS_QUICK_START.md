# iOS Shortcuts - Quick Start

**5-Minute Setup Guide** for uploading scans from your iPhone to the Scan Processor.

> **🤔 Paperless App vs Scan Processor?** See [UPLOAD_WORKFLOW_COMPARISON.md](UPLOAD_WORKFLOW_COMPARISON.md) to understand which upload method to use when.

---

## 📱 What You'll Create

A Shortcut that lets you:
1. **Scan a document** with your iPhone camera
2. **Auto-upload** to your scan processor
3. **Get confirmation** it's being processed

**Total time**: Document processed in 30-120 seconds!

---

## 🚀 Quick Setup

### Step 1: Open Shortcuts App
On your iPhone, open the **Shortcuts** app (blue icon with white squares).

### Step 2: Create New Shortcut
1. Tap **"+"** in the top right
2. Tap **"Add Action"**

### Step 3: Add These 4 Actions

#### Action 1: Scan Documents
- Search: **"Scan Documents"**
- Tap to add
- This opens your camera to scan

#### Action 2: Format Date
- Search: **"Format Date"**
- Tap the date, select **"Current Date"**
- Tap format, select **"Custom"**
- Enter: `yyyyMMdd_HHmmss`

#### Action 3: Rename File
- Search: **"Rename"**
- Select **"Scan Documents"** from list
- Tap the filename field
- Clear it and add variables:
  - Tap **"Formatted Date"** (from Action 2)
  - Type: `_Document.pdf`
- Result: `20251221_173000_Document.pdf`

#### Action 4: Upload to Web
- Search: **"Get Contents of URL"**
- In **URL** field, type: `https://scanui.redleif.dev/api/upload`
- Tap **"Show More"**
- Change **Method** to: `POST`
- Change **Request Body** to: `Form`
- Tap **"Add new field"**:
  - **Key**: `file` (exactly, lowercase)
  - **Type**: `File`
  - **Value**: Select **"Renamed Item"** from list

### Step 4: Name and Save
1. Tap **"Done"**
2. Long-press the shortcut
3. Tap **"Rename"**
4. Name it: **"Upload Scan"**
5. Tap **"Done"**

---

## ✅ Test It!

1. **Run your shortcut**
2. **Scan a test document** (any piece of paper)
3. **Tap "Save"** after scanning
4. **Wait 2-3 seconds**
5. **Check**: https://scanui.redleif.dev

Your document should appear and start processing!

---

## 🎯 Using Your Shortcut

### From Home Screen
1. Tap the Shortcuts app
2. Tap "Upload Scan"
3. Scan → Done

### With Siri
1. **Add to Siri**:
   - Open Shortcuts app
   - Long-press "Upload Scan"
   - Tap "Add to Siri"
   - Record: "Upload a scan"

2. **Use it**: "Hey Siri, upload a scan"

### From Widget
1. Long-press home screen
2. Tap **"+"** (top left)
3. Search **"Shortcuts"**
4. Select widget size
5. Tap **"Add Widget"**
6. Long-press widget to configure
7. Select "Upload Scan"

---

## 📊 What Happens Next?

After upload:

1. ⚡ **Instant confirmation** (< 1 second)
2. 🤖 **Claude Code analyzes** document (5-15 seconds)
3. 🏷️ **Auto-categorizes** (Medical, Expense, Schoolwork, etc.)
4. 📝 **Extracts metadata** (date, provider, amount, etc.)
5. 📤 **Uploads to Paperless** with tags
6. 🔔 **Sends notification** (for medical/expenses)
7. ✅ **Processing complete!** (30-120 seconds total)

---

## 🛠️ Troubleshooting

### "No file provided" error
**Fix**: Check Action 4, make sure:
- Field name is exactly `file` (lowercase)
- Field type is `File` not `Text`
- Value is set to "Renamed Item"

### Upload works but nothing processes
**Check web UI**: https://scanui.redleif.dev
- File should appear immediately
- If stuck, file watcher may need restart

### Can't find "Get Contents of URL"
**Search tip**: Try typing just "URL" or "Get Contents"

---

## 🎨 Customize It

### Add Child Name

Before "Rename File" action:

1. Add **"Ask for Input"**
   - Prompt: "Child name?"
   - Type: Text

2. Add **"Set Variable"**
   - Name: `Child`
   - Value: `Provided Input`

3. Update **Rename** to:
   - `{Formatted Date}_{Child}_Document.pdf`

### Add Document Type

1. Add **"Choose from Menu"**
   - Prompt: "Document type?"
   - Options: Medical, Expense, School

2. Update **Rename** to include category

---

## 📖 Full Documentation

**Complete Guide**: [IOS_SHORTCUTS_INTEGRATION.md](IOS_SHORTCUTS_INTEGRATION.md)

Includes:
- Share Sheet integration
- Automation triggers
- Advanced metadata
- Full API reference
- Troubleshooting guide

**Architecture & Deployment**: See TechKB documentation at:
- `/home/jodfie/vault/jodys-brain/TechKB/10-projects/14-scan-processor/Scanner-UI-iOS-Upload-Integration.md`

**System Overview**: [CLAUDE.md](CLAUDE.md) and [README.md](README.md)

---

## 🔗 Quick Links

- **Web Dashboard**: https://scanui.redleif.dev
- **Upload Endpoint**: https://scanui.redleif.dev/api/upload
- **Processing History**: https://scanui.redleif.dev/history
- **Pending Items**: https://scanui.redleif.dev/pending

---

## 💡 Pro Tips

1. **Add to Lock Screen**: iOS 16+ lets you add shortcuts to lock screen
2. **Use Back Tap**: Settings → Accessibility → Touch → Back Tap → Triple Tap → Upload Scan
3. **Automate**: Create automation to run when you arrive home from doctor
4. **Share Sheet**: Enable "Show in Share Sheet" to upload from any app

---

## 📋 Quick Reference

| What | Value |
|------|-------|
| **URL** | `https://scanui.redleif.dev/api/upload` |
| **Method** | `POST` |
| **Field** | `file` |
| **Type** | PDF only, max 50MB |
| **Response** | < 1 second |
| **Processing** | 30-120 seconds |

---

**Questions?** Check the full guide: [IOS_SHORTCUTS_INTEGRATION.md](IOS_SHORTCUTS_INTEGRATION.md)

---

*Last Updated: 2025-12-21*
