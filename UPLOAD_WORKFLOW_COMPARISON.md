# Upload Workflow Comparison

Guide to understanding the different ways to upload documents and when to use each method.

---

## 📊 Two Upload Paths

### Path 1: Scan Processor (Intelligent Processing)
**Endpoint**: `https://scanui.redleif.dev/api/upload`

**What Happens**:
```
iPhone Scan
    ↓
Upload to scanui.redleif.dev
    ↓
Claude Code Classifier (5-15 sec)
    ↓
Category Determination (MEDICAL, CPS_EXPENSE, SCHOOLWORK, GENERAL)
    ↓
Metadata Extraction (10-20 sec)
    ↓
├─→ Paperless-NGX (with intelligent tags)
├─→ BasicMemory Note (for MEDICAL & CPS_EXPENSE)
└─→ Pushover Notification (for important docs)
    ↓
Complete (30-120 seconds total)
```

### Path 2: Paperless Mobile App (Direct Upload)
**App**: Paperless Mobile (iOS App Store)

**What Happens**:
```
iPhone Scan
    ↓
Paperless Mobile App
    ↓
Direct Upload to Paperless
    ↓
Complete (< 5 seconds)
```

**Limitations**:
- ❌ No Claude Code classification
- ❌ No automatic BasicMemory notes
- ❌ No intelligent metadata extraction
- ❌ No Pushover notifications
- ⚠️ Manual tagging required
- ⚠️ Manual categorization

---

## 🎯 When to Use Each Method

### Use Scan Processor (scanui.redleif.dev) When:

✅ **Medical Documents**
- Automatically creates BasicMemory notes in `60-medical/{child}/`
- Extracts provider, date, diagnosis, treatment
- Sends notification with key details
- Tags with provider, child name, medical

✅ **Co-Parenting Expenses**
- Creates BasicMemory notes in `40-expenses/`
- Extracts amount, vendor, date, category
- Sends notification for expense tracking
- Tags with expense, child name, category

✅ **Important Documents Needing Processing**
- School records requiring categorization
- Bills needing metadata extraction
- Documents you want in both Paperless AND BasicMemory

✅ **When You Want Notifications**
- Medical visits → Get notified immediately
- Expenses → Track co-parenting costs
- Important documents → Don't miss anything

### Use Paperless Mobile App When:

✅ **Quick Archival**
- Random receipts you just want stored
- Non-critical documents
- Documents that don't need BasicMemory notes

✅ **Simple Storage**
- Already know the tags/category
- Don't need intelligent classification
- Don't need notifications

✅ **Immediate Upload**
- Need document in Paperless ASAP
- Don't want to wait 30-120 seconds for processing
- Speed over intelligence

✅ **Network/Service Issues**
- Scan processor is down
- Claude Code unavailable
- Backup upload method

---

## 📱 Comparison Table

| Feature | Scan Processor | Paperless App |
|---------|---------------|---------------|
| **Upload Speed** | 30-120 seconds | < 5 seconds |
| **Classification** | ✅ Automatic (Claude Code) | ❌ Manual only |
| **Metadata Extraction** | ✅ Automatic | ❌ Manual only |
| **BasicMemory Notes** | ✅ Yes (medical/expense) | ❌ No |
| **Notifications** | ✅ Yes (important docs) | ❌ No |
| **Paperless Storage** | ✅ Yes | ✅ Yes |
| **Intelligent Tagging** | ✅ Yes | ⚠️ Manual |
| **Setup Complexity** | Medium (iOS Shortcut) | Easy (Just install app) |
| **Internet Required** | Yes | Yes |
| **Authentication** | None (public endpoint) | Yes (login required) |

---

## 🔀 Hybrid Workflow (Recommended)

Use **both** methods for different purposes:

### Primary: Scan Processor
For **all important documents**:
- Medical records
- Bills and expenses
- School documents
- Anything needing tracking/notes

**How**: Use iOS Shortcut (see [IOS_SHORTCUTS_QUICK_START.md](IOS_SHORTCUTS_QUICK_START.md))

### Backup: Paperless App
For **quick archival**:
- Random receipts
- Non-urgent documents
- When scan processor is unavailable

**How**: Install Paperless Mobile app from App Store

---

## 📲 Paperless Mobile App Setup

If you want the direct upload option as a backup:

### Installation

1. **Download App**
   - iOS: Search "Paperless Mobile" in App Store
   - Or use official Paperless-NGX mobile app

2. **Configure Connection**
   - Server URL: `https://paperless.redleif.dev`
   - Username: Your Paperless username
   - Password: Your Paperless password
   - Or use API token from Paperless settings

3. **Upload Documents**
   - Tap camera icon
   - Take photo or select file
   - Add tags (manual)
   - Upload

### Limitations

**No Intelligent Processing**:
- You must manually select tags
- You must manually add metadata
- No BasicMemory notes created
- No notifications sent

**Use Cases**:
- Quick receipt archival
- Backup when scan-processor is down
- Documents that don't need processing

---

## 🤔 Decision Flow

```
New document to upload?
    ↓
Is it medical or expense related?
    ├─ YES → Use Scan Processor (intelligent processing)
    │           - Gets BasicMemory note
    │           - Sends notification
    │           - Intelligent tagging
    │
    └─ NO → Does it need categorization/metadata?
              ├─ YES → Use Scan Processor
              │
              └─ NO → Either method works
                        - Scan Processor: Better tagging
                        - Paperless App: Faster upload
```

---

## 🔄 Re-processing Documents

### If You Uploaded via Paperless App

You can still trigger intelligent processing later:

1. **Download from Paperless**
   - Get document from Paperless-NGX
   - Save to iPhone

2. **Upload to Scan Processor**
   - Use iOS Shortcut
   - Upload via scanui.redleif.dev/api/upload

3. **Processing Happens**
   - Claude Code classifies
   - BasicMemory note created
   - Re-uploaded to Paperless with better tags

**Note**: This creates a duplicate in Paperless. Delete the original after verifying the new one has better metadata.

---

## 💡 Recommendations

### For Your Use Case (Co-Parenting System)

**Primary Method**: **Scan Processor via iOS Shortcuts**

**Why**:
- ✅ Medical documents → Automatic BasicMemory notes
- ✅ Expenses → Tracked in BasicMemory
- ✅ Notifications → Don't miss important docs
- ✅ Better organization → Intelligent tagging
- ✅ Less work → No manual categorization

**Secondary Method**: **Paperless App as Backup**

**Why**:
- ✅ Quick receipts → Not everything needs processing
- ✅ Redundancy → If scan-processor is down
- ✅ Simplicity → For family members who don't want shortcuts

---

## 📖 Documentation Links

### Scan Processor Setup
- **Quick Start**: [IOS_SHORTCUTS_QUICK_START.md](IOS_SHORTCUTS_QUICK_START.md)
- **Complete Guide**: [IOS_SHORTCUTS_INTEGRATION.md](IOS_SHORTCUTS_INTEGRATION.md)
- **System Overview**: [CLAUDE.md](CLAUDE.md)

### Paperless Mobile App
- **Official Docs**: https://docs.paperless-ngx.com/usage/#mobile-app
- **iOS App**: Search App Store for "Paperless Mobile"
- **Server**: https://paperless.redleif.dev

### Architecture
- **TechKB**: `/home/jodfie/vault/jodys-brain/TechKB/10-projects/14-scan-processor/Scanner-UI-iOS-Upload-Integration.md`

---

## 🎯 Quick Reference

| Document Type | Recommended Method | Why |
|---------------|-------------------|-----|
| **Medical Records** | Scan Processor | BasicMemory notes + notifications |
| **Medical Bills** | Scan Processor | Expense tracking + notifications |
| **CPS Expenses** | Scan Processor | BasicMemory tracking + categorization |
| **School Documents** | Scan Processor | Intelligent categorization |
| **Random Receipts** | Either (Paperless faster) | No processing needed |
| **Quick Archival** | Paperless App | Speed over intelligence |
| **Important Docs** | Scan Processor | Full processing pipeline |

---

## ❓ FAQ

### Can I use both methods?
**Yes!** They're complementary. Use scan-processor for important docs, Paperless app for quick archival.

### Will documents be duplicated?
**Only if you upload the same document twice.** Each method uploads to Paperless, so uploading via both would create a duplicate.

### Which is faster?
**Paperless App** (< 5 seconds) vs **Scan Processor** (30-120 seconds)

### Which is smarter?
**Scan Processor** - Automatic classification, metadata extraction, BasicMemory notes, notifications.

### What if scan-processor is down?
**Use Paperless App** as backup. You can always re-process later via scan-processor.

### Can I add the same document to both?
**Not recommended.** This creates duplicates in Paperless. Choose one method per document.

### Which tags are better?
**Scan Processor tags** - Automatically extracted from document content. **Paperless App tags** - Manual, whatever you select.

---

## 🚀 Getting Started

### Option 1: Scan Processor (Recommended)
1. **Set up iOS Shortcut** (5 minutes)
   - Follow [IOS_SHORTCUTS_QUICK_START.md](IOS_SHORTCUTS_QUICK_START.md)

2. **Scan a test document**
   - Run shortcut
   - Wait 30-120 seconds

3. **Check results**
   - View at https://scanui.redleif.dev/history
   - Check Paperless for document
   - Check BasicMemory for note (if medical/expense)

### Option 2: Paperless App (Backup)
1. **Download app** from App Store
2. **Configure** with https://paperless.redleif.dev
3. **Upload** documents directly

### Option 3: Both (Best)
Set up both, use scan-processor as primary, Paperless app as backup.

---

*Last Updated: 2025-12-21*
