# Category Expansion Summary - 29-Category System

## Overview

The scan-processor has been expanded from **4 categories** to **29 categories** to support both co-parenting (CPS) and personal document processing. This enables the system to be a comprehensive personal document management R&D platform while maintaining the CPS focus for production deployment.

## Category Naming Convention

**CRITICAL CHANGE**: All categories now use **dash-based naming** instead of underscores.

- ✅ `CPS-MEDICAL` (dash-based)
- ❌ `CPS_MEDICAL` (old underscore-based)

This applies to ALL 29 categories.

## Categories (29 Total)

### CPS Categories (6) - Children-related documents

1. **CPS-MEDICAL** - Children's medical records, bills, EOBs
2. **CPS-EXPENSE** - Children's expenses (school, activities, etc.)
3. **CPS-SCHOOLWORK** - Children's schoolwork, report cards
4. **CPS-CUSTODY** - Custody schedule, visitation, exchanges
5. **CPS-COMMUNICATION** - Communication with co-parent
6. **CPS-LEGAL** - Court orders, custody decree updates

### Personal Categories (23) - Your personal documents

**Financial & Expenses**:
7. PERSONAL-EXPENSE
8. RECEIPT
9. INVOICE
10. TAX-DOCUMENT
11. BANK-STATEMENT
12. INVESTMENT

**Medical & Health**:
13. PERSONAL-MEDICAL
14. PRESCRIPTION
15. INSURANCE

**Housing & Property**:
16. MORTGAGE
17. UTILITY
18. LEASE
19. HOME-MAINTENANCE
20. PROPERTY-TAX

**Automotive**:
21. AUTO-INSURANCE
22. AUTO-MAINTENANCE
23. AUTO-REGISTRATION

**Legal & Contracts**:
24. CONTRACT
25. LEGAL-DOCUMENT

**Travel**:
26. TRAVEL-BOOKING
27. TRAVEL-RECEIPT

**Other**:
28. GENERAL
29. REFERENCE

## Dual-Vault Architecture

The system now routes documents to **two separate vaults** based on category:

### CPS Vault
- **Path**: `/home/jodfie/vault/jodys-brain/CoparentingSystem/`
- **Categories**: CPS-MEDICAL, CPS-EXPENSE, CPS-SCHOOLWORK, CPS-CUSTODY, CPS-COMMUNICATION, CPS-LEGAL
- **Directory Structure**:
  - `60-medical/{child}/YYYY-MM-DD-{description}.md`
  - `40-expenses/YYYY-MM-DD-{vendor}.md`
  - `50-schoolwork/{child}/` (TBD)

### Personal Vault
- **Path**: `/home/jodfie/vault/jodys-brain/Personal/`
- **Categories**: PERSONAL-MEDICAL, PERSONAL-EXPENSE, UTILITY, AUTO-*
- **Directory Structure**:
  - `Medical/YYYY-MM-DD-{provider}-{type}.md`
  - `Expenses/{category}/YYYY-MM-DD-{vendor}.md`
  - `Utilities/{type}/YYYY-MM-DD-{provider}-{type}.md`
  - `Automotive/{type}/YYYY-MM-DD-{provider}-{type}.md`

## Files Modified

### 1. Prompt Templates (prompts/)

**Updated Existing Files**:
- `classifier.md` - Expanded from 4 to 29 categories, added `is_cps_related` flag
- `medical.md` - Changed CPS_MEDICAL → CPS-MEDICAL
- `expense.md` - Changed CPS_EXPENSE → CPS-EXPENSE
- `schoolwork.md` - Changed CPS_SCHOOLWORK → CPS-SCHOOLWORK

**New Prompt Files**:
- `utility.md` (130 lines) - Utility bill metadata extraction
- `personal-medical.md` (150 lines) - Personal (adult) medical records
- `personal-expense.md` (140 lines) - Personal spending receipts
- `auto.md` (180 lines) - Automotive documents (maintenance, registration, insurance)

### 2. Python Code (scripts/)

#### classifier.py
**Changes**:
- Added prompt file references: `personal_medical_prompt`, `personal_expense_prompt`, `utility_prompt`, `auto_prompt`
- Updated `_get_prompt_type()` to recognize new prompt types
- **Added 4 new extraction methods**:
  - `extract_personal_medical_metadata()`
  - `extract_personal_expense_metadata()`
  - `extract_utility_metadata()`
  - `extract_auto_metadata()`

#### basicmemory.py
**Changes**:
- Added dual-vault routing: `cps_path` AND `personal_path` parameters
- Added personal template directory support
- **Added 4 new note creation methods**:
  - `create_personal_medical_note()` → Personal/Medical/
  - `create_personal_expense_note()` → Personal/Expenses/{category}/
  - `create_utility_note()` → Personal/Utilities/{type}/
  - `create_auto_note()` → Personal/Automotive/{type}/

#### process.py
**Changes**:
- Updated `_extract_metadata()` to handle all 29 categories with dash-based naming
- Updated `_create_basicmemory_note()` to route to correct vault based on category

### 3. Documentation

#### CLAUDE.md
**Updated**:
- Lines 83-122: Document Categories section
- Added table showing 6 CPS + 23 personal categories
- Documented dash-based naming convention
- Updated directory structure to show new prompt files

## Technical Highlights

### Category Classification Flow

1. **Universal Classifier** (`prompts/classifier.md`)
   - Analyzes document
   - Returns category (one of 29)
   - Includes `is_cps_related` flag for routing
   - Provides metadata preview

2. **Category-Specific Extraction** (`prompts/{category}.md`)
   - Detailed metadata extraction
   - Category-specific fields
   - Privacy/security rules (account number masking, etc.)

3. **Dual-Vault Routing** (`basicmemory.py`)
   - CPS categories → CoparentingSystem vault
   - Personal categories → Personal vault
   - Automatic directory creation

4. **Paperless Upload** (`paperless.py`)
   - All categories upload to Paperless-NGX
   - Hierarchical tagging based on category
   - OCR text search

## Next Steps

### Testing Required
- [ ] Test classification with sample CPS documents
- [ ] Test classification with sample personal documents
- [ ] Verify dual-vault routing creates notes in correct locations
- [ ] Test all 4 new extraction methods
- [ ] Verify Paperless uploads work for all categories

### Potential Improvements for CPS Scanner
Based on this R&D work, these features could be ported to CoParentingSystem scanner:
1. Improved category-specific metadata extraction prompts
2. Enhanced error handling and fallback responses
3. Privacy features (account number masking)
4. Better structured markdown note templates

## Architecture Diagram

```
PDF Document
    ↓
classifier.md (29 categories)
    ↓
Category-specific extraction (medical.md, utility.md, etc.)
    ↓
is_cps_related flag check
    ↓
┌─────────────────┬─────────────────┐
│   CPS Vault     │  Personal Vault │
│                 │                 │
│ CPS-MEDICAL    │ PERSONAL-MEDICAL│
│ CPS-EXPENSE    │ PERSONAL-EXPENSE│
│ CPS-SCHOOLWORK │ UTILITY         │
│ (etc.)         │ AUTO-*          │
└─────────────────┴─────────────────┘
    ↓                   ↓
Paperless-NGX (all categories)
```

## Naming Consistency

### Old (Underscore-based)
- `CPS_MEDICAL`
- `CPS_EXPENSE`
- `CPS_SCHOOLWORK`
- `PERSONAL_MEDICAL`
- `PERSONAL_EXPENSE`

### New (Dash-based) ✅
- `CPS-MEDICAL`
- `CPS-EXPENSE`
- `CPS-SCHOOLWORK`
- `PERSONAL-MEDICAL`
- `PERSONAL-EXPENSE`
- `UTILITY`
- `AUTO-INSURANCE`
- `AUTO-MAINTENANCE`
- `AUTO-REGISTRATION`

## Summary Statistics

- **Prompts Created**: 4 new files (utility, personal-medical, personal-expense, auto)
- **Prompts Updated**: 5 files (classifier, medical, expense, schoolwork, CLAUDE.md)
- **Python Files Updated**: 3 files (classifier.py, basicmemory.py, process.py)
- **New Methods Added**: 8 methods (4 extraction + 4 note creation)
- **Lines of Code Modified**: ~600+ lines
- **Total Categories**: 29 (6 CPS + 23 personal)

---

**Implementation Date**: 2025-12-25
**Status**: Code Complete - Ready for Testing
**Next Milestone**: Sample document testing
