# Enhanced Pending Screen Guide

## Overview

The pending screen now provides **inline document preview** with **metadata correction** capabilities when Claude Code classification fails.

**URL**: https://scanui.redleif.dev/pending

## Features

### ✅ Inline PDF Preview

- **Left side**: Full PDF viewer with page navigation
- **Right side**: Classification form with metadata fields
- Navigate pages with ← Prev / Next → buttons
- Download PDF button for offline viewing

### ✅ Manual Classification

When Claude Code fails to classify a document, you can:

1. **View the document** - See the PDF inline without opening a new window
2. **Select correct category** - Choose from:
   - 📋 **Medical** - Doctor visits, prescriptions, medical bills
   - 💰 **Co-Parenting Expense** - Shared expenses, receipts
   - 🎓 **Schoolwork** - Report cards, school documents
   - 📄 **General** - Other documents

3. **Enter metadata** - Category-specific fields appear based on selection:

   **Medical Documents:**
   - Child Name (e.g., Jacob, Morgan)
   - Provider/Doctor (e.g., Dr. Smith, Pediatric Associates)
   - Visit Date

   **Co-Parenting Expenses:**
   - Child Name
   - Amount (e.g., $45.99)
   - Expense Type (e.g., Sports, Medical, School)

   **Schoolwork:**
   - Child Name
   - Document Type (e.g., Report Card, Permission Slip)

4. **Add notes** - Optional additional information field
5. **Submit** - Saves classification and metadata for processing

## Example Workflow

### Scenario: Medical Document Failed to Classify

1. **Navigate to pending**: https://scanui.redleif.dev/pending
2. **Review the document**:
   - See PDF preview on left side
   - Read error: "Failed to classify with Claude Code. Please review manually."
3. **Manually classify**:
   - Select category: **Medical**
   - Metadata fields appear automatically
   - Fill in:
     - Child Name: `Morgan`
     - Provider: `Pediatric Savannah`
     - Visit Date: `2025-02-10`
4. **Add optional note**: "Care plan for upcoming visit"
5. **Click "Submit & Process"**
6. Document is updated and ready for processing

## Mobile Responsive

- Works on phones and tablets
- PDF viewer stacks on top of form on mobile
- Touch-friendly navigation buttons
- Full functionality on all devices

## Technical Details

### What Happens When You Submit

1. **Database Update**:
   - Category is updated to your selection
   - Metadata is stored as JSON
   - Response timestamp is recorded

2. **WebSocket Notification**:
   - Real-time broadcast to all connected clients
   - Dashboard updates automatically

3. **Processing Queue**:
   - Document is marked as responded
   - Can be reprocessed with correct classification
   - Metadata is used for Paperless tags and BasicMemory notes

### Metadata Format

Stored in database as JSON:

```json
{
  "child": "Morgan",
  "provider": "Pediatric Savannah",
  "visit_date": "2025-02-10"
}
```

## Common Issues

### "Error loading PDF"

**Problem**: PDF file not found or permissions issue

**Solution**:
- Check file exists in incoming/processing/completed/failed directories
- Verify Docker volume mounts are correct
- Restart container if needed

### Metadata fields not showing

**Problem**: JavaScript not loading or category not selected

**Solution**:
- Select a category from dropdown
- Fields appear automatically based on category
- Refresh page if JavaScript errors occur

### Changes not saving

**Problem**: Database write permissions

**Solution**:
- Already fixed with read-write volume mounts
- Check Docker logs if issues persist

## Tips

💡 **Preview first** - Always review the PDF before classifying

💡 **Use metadata** - Even if optional, metadata helps future searches

💡 **Skip button** - If unsure, skip and come back later

💡 **Download PDF** - For complex documents, download for closer inspection

💡 **Mobile friendly** - Review and classify from your phone/scanner

## Comparison: Old vs New

| Feature | Old Pending Screen | New Enhanced Screen |
|---------|-------------------|---------------------|
| **PDF Preview** | ❌ External link only | ✅ Inline viewer with pagination |
| **Metadata Entry** | ❌ Text-only response | ✅ Category-specific form fields |
| **Category Selection** | ❌ Not available | ✅ Dropdown with descriptions |
| **Mobile Support** | ⚠️ Basic | ✅ Fully responsive |
| **Visual Feedback** | ⚠️ Minimal | ✅ Color-coded, icons, badges |
| **User Experience** | ⚠️ Multiple clicks | ✅ Single page workflow |

## Next Steps

After submitting a manual classification:

1. **Automatic Reprocessing** (Future):
   - Document will be automatically reprocessed
   - Uses your manual classification
   - Metadata applied to Paperless and BasicMemory

2. **Manual Processing** (Current):
   - Run classifier with manual override
   - Process.py will use stored metadata
   - Upload to Paperless with correct tags

## Related Documentation

- **Main Guide**: `README.md`
- **Web UI Dev Mode**: `WEB_UI_DEV_MODE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Development Mode**: `DEVELOPMENT_MODE.md`

## Summary

The enhanced pending screen eliminates the need to:
- ❌ Open separate windows to preview PDFs
- ❌ Manually figure out what category a document belongs to
- ❌ Type metadata in a plain text field
- ❌ Switch between desktop and mobile for document review

Instead, you get:
- ✅ Everything in one screen
- ✅ Visual PDF preview with navigation
- ✅ Guided metadata entry with field validation
- ✅ Mobile-friendly responsive design
- ✅ Real-time updates via WebSocket

**Perfect for quickly triaging failed classifications!**
