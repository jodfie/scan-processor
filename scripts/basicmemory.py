#!/usr/bin/env python3
"""
BasicMemory Note Creator
Creates notes in the CPS project from templates
"""

import os
from pathlib import Path
from datetime import datetime
import re

class BasicMemoryNoteCreator:
    """Create BasicMemory notes from templates"""

    def __init__(self, cps_path=None, personal_vault=None, dry_run=False):
        self.dry_run = dry_run

        # Auto-detect container vs host environment for CPS vault
        if cps_path is None:
            if Path('/app/vault/CoparentingSystem').exists():
                # Running in container (vault is mounted at /app/vault)
                cps_path = '/app/vault/CoparentingSystem'
                template_base = '/app/vault/Templates/CoparentingSystem'
            else:
                # Running on host
                cps_path = '/home/jodfie/vault/jodys-brain/CoparentingSystem'
                template_base = '/home/jodfie/vault/jodys-brain/Templates/CoparentingSystem'
        else:
            # If cps_path is provided, derive template path from it
            vault_base = Path(cps_path).parent
            template_base = vault_base / 'Templates' / 'CoparentingSystem'

        # Auto-detect container vs host environment for Personal vault
        if personal_vault is None:
            if Path('/app/vault/Personal').exists():
                # Running in container
                personal_vault = '/app/vault/Personal'
                personal_template_base = '/app/vault/Templates/Personal'
            else:
                # Running on host
                personal_vault = '/home/jodfie/vault/jodys-brain/Personal'
                personal_template_base = '/home/jodfie/vault/jodys-brain/Templates/Personal'
        else:
            # If personal_vault is provided, derive template path from it
            vault_base = Path(personal_vault).parent
            personal_template_base = vault_base / 'Templates' / 'Personal'

        # Use consistent naming: cps_vault and personal_vault
        self.cps_path = Path(cps_path)  # Keep for backwards compatibility
        self.cps_vault = Path(cps_path)  # New attribute name
        self.personal_path = Path(personal_vault)  # Keep for backwards compatibility
        self.personal_vault = Path(personal_vault)  # New attribute name
        
        self.template_dir = Path(template_base)
        self.personal_template_dir = Path(personal_template_base)

        if not self.dry_run:
            # Auto-create vaults if they don't exist
            if not self.cps_vault.exists():
                print(f"Warning: CPS vault does not exist: {self.cps_vault}")
                print(f"  Creating it now...")
                self.cps_vault.mkdir(parents=True, exist_ok=True)
            
            if not self.personal_vault.exists():
                print(f"Warning: Personal vault does not exist: {self.personal_vault}")
                print(f"  Creating it now...")
                self.personal_vault.mkdir(parents=True, exist_ok=True)

        # CPS templates
        self.medical_template_path = self.template_dir / "Template-Medical.md"
        self.expense_template_path = self.template_dir / "Template-Expense.md"
        
        # Personal templates (optional - will use fallback content if not found)
        self.personal_medical_template_path = self.personal_template_dir / "Template-Personal-Medical.md"
        self.personal_expense_template_path = self.personal_template_dir / "Template-Personal-Expense.md"
        self.utility_template_path = self.personal_template_dir / "Template-Utility.md"
        self.auto_template_path = self.personal_template_dir / "Template-Auto.md"

    def create_medical_note(self, metadata):
        """
        Create a medical note from template

        Args:
            metadata: Dictionary containing:
                - child: Child name (Jacob or Morgan)
                - date: Visit date (YYYY-MM-DD)
                - provider: Provider/clinic name
                - type: Visit type (checkup, sick visit, etc.)
                - diagnosis: Diagnosis or reason (optional)
                - treatment: Treatment provided (optional)
                - cost: Cost/copay (optional)
                - notes: Additional notes (optional)

        Returns:
            Path to created note
        """
        if not self.medical_template_path.exists():
            raise FileNotFoundError(f"Medical template not found: {self.medical_template_path}")

        # Read template
        with open(self.medical_template_path, 'r') as f:
            template = f.read()

        # Fill in template
        content = template

        # Replace placeholders - using uppercase to match template
        visit_type = metadata.get('type', metadata.get('visit_type', 'Medical Visit'))
        date_val = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))

        replacements = {
            # Basic info
            '{{DATE}}': date_val,
            '{{CHILD}}': metadata.get('child', ''),
            '{{PROVIDER}}': metadata.get('provider', ''),
            '{{VISIT_TYPE}}': visit_type,
            '{{TITLE}}': metadata.get('title', visit_type),

            # Appointment details
            '{{TIME}}': metadata.get('time', 'Not specified'),
            '{{SPECIALTY}}': metadata.get('specialty', 'Not specified'),
            '{{LOCATION}}': metadata.get('location', 'Not specified'),
            '{{ACCOMPANIED_BY}}': metadata.get('accompanied_by', 'Not specified'),
            '{{APPOINTMENT_TYPE}}': visit_type,

            # Medical details
            '{{CHIEF_COMPLAINT}}': metadata.get('chief_complaint', metadata.get('reason', 'Not specified')),
            '{{SYMPTOMS}}': metadata.get('symptoms', 'Not specified'),
            '{{SYMPTOM_DURATION}}': metadata.get('duration', 'Not specified'),
            '{{DIAGNOSIS}}': metadata.get('diagnosis', 'Not specified'),
            '{{ASSESSMENT}}': metadata.get('assessment', 'Not specified'),
            '{{SEVERITY}}': metadata.get('severity', 'Not specified'),
            '{{PROGNOSIS}}': metadata.get('prognosis', 'Not specified'),

            # Treatment
            '{{PRESCRIPTIONS}}': metadata.get('prescriptions', metadata.get('treatment', 'None')),
            '{{PRESCRIPTION}}': metadata.get('prescriptions', metadata.get('treatment', 'None')),
            '{{OTHER_TREATMENTS}}': metadata.get('other_treatments', 'None'),
            '{{RESTRICTIONS}}': metadata.get('restrictions', 'None'),

            # Follow-up
            '{{FOLLOW_UP_SCHEDULED}}': metadata.get('follow_up_scheduled', 'Not specified'),
            '{{FOLLOW_UP_DATE}}': metadata.get('follow_up_date', 'Not specified'),
            '{{FOLLOW_UP_REASON}}': metadata.get('follow_up_reason', 'Not specified'),
            '{{WARNING_SIGNS}}': metadata.get('warning_signs', 'Not specified'),
            '{{CALL_DOCTOR_IF}}': metadata.get('call_doctor_if', 'Not specified'),

            # History
            '{{PREVIOUS_CONDITIONS}}': metadata.get('previous_conditions', 'None noted'),
            '{{CURRENT_MEDICATIONS}}': metadata.get('current_medications', 'None'),
            '{{ALLERGIES}}': metadata.get('allergies', 'None known'),
            '{{RECENT_CHANGES}}': metadata.get('recent_changes', 'None'),

            # Exam
            '{{VITALS}}': metadata.get('vitals', 'Not recorded'),
            '{{EXAM_FINDINGS}}': metadata.get('exam_findings', 'Not specified'),
            '{{TESTS_PERFORMED}}': metadata.get('tests_performed', 'None'),

            # Communication
            '{{COMMUNICATION_METHOD}}': metadata.get('communication_method', 'Not specified'),
            '{{NOTIFICATION_TIME}}': metadata.get('notification_time', 'Not specified'),
            '{{INFORMATION_SHARED}}': metadata.get('information_shared', 'Not specified'),
            '{{OTHER_PARENT_RESPONSE}}': metadata.get('other_parent_response', 'Not specified'),
            '{{JOINT_DECISION_NOTES}}': metadata.get('joint_decision_notes', 'Not specified'),
            '{{COMMUNICATION_STATUS}}': metadata.get('communication_status', 'Pending'),

            # Costs
            '{{INSURANCE_USED}}': metadata.get('insurance_used', 'Not specified'),
            '{{COPAY_AMOUNT}}': metadata.get('copay', metadata.get('cost', '0.00')),
            '{{PAID_BY}}': metadata.get('paid_by', 'Not specified'),
            '{{ADDITIONAL_COSTS}}': metadata.get('additional_costs', 'None'),
            '{{REIMBURSEMENT_STATUS}}': metadata.get('reimbursement_status', 'Not applicable'),
            '{{EXPENSE_NOTE_LINK}}': metadata.get('expense_note_link', 'None'),

            # School
            '{{SCHOOL_NOTIFICATION_REQUIRED}}': metadata.get('school_notification_required', 'Not specified'),
            '{{SCHOOL_NOTIFIED_DATE}}': metadata.get('school_notified_date', 'Not specified'),
            '{{SCHOOL_INFO_PROVIDED}}': metadata.get('school_info_provided', 'Not specified'),

            # Child response
            '{{CHILD_DURING_VISIT}}': metadata.get('child_during_visit', 'Not recorded'),
            '{{CHILD_AFTER_VISIT}}': metadata.get('child_after_visit', 'Not recorded'),
            '{{CHILD_UNDERSTANDING}}': metadata.get('child_understanding', 'Not assessed'),
            '{{CHILD_EMOTIONAL_STATE}}': metadata.get('child_emotional_state', 'Not recorded'),

            # Documentation
            '{{PAPERLESS_ID}}': metadata.get('paperless_id', 'Not uploaded'),
            '{{SHA256_HASH}}': metadata.get('sha256', 'Not calculated'),
            '{{PHOTO_DESCRIPTION}}': metadata.get('photo_description', 'None'),

            # Tags
            '{{TAGS}}': metadata.get('tags', visit_type.lower()),

            # Evaluator notes placeholders
            '{{CUSTODY_FACTORS}}': 'To be determined',
            '{{RELEVANCE_EXPLANATION}}': 'To be determined',
            '{{RELEVANCE_SCORE}}': 'TBD',
            '{{CORROBORATION_LEVEL}}': 'To be determined',
            '{{EVIDENCE_STRENGTHS}}': 'To be determined',
            '{{EVIDENCE_WEAKNESSES}}': 'To be determined',
            '{{STRENGTH_SCORE}}': 'TBD',
            '{{DECREE_SECTION}}': 'To be determined',
            '{{COMPLIANCE_STATUS}}': 'To be determined',
            '{{COMPLIANCE_ANALYSIS}}': 'To be determined',
            '{{DECISION_MAKING_NOTES}}': 'To be determined',
            '{{ADMISSIBILITY_LEVEL}}': 'To be determined',
            '{{FOUNDATION_REQUIRED}}': 'To be determined',
            '{{HIPAA_NOTES}}': 'To be determined',

            # Related docs
            '{{PREVIOUS_VISITS}}': 'None linked',
            '{{RELATED_EXPENSES}}': 'None linked',
            '{{RELATED_COMMUNICATIONS}}': 'None linked',

            # Backwards compatibility - lowercase versions
            '{{date}}': date_val,
            '{{child}}': metadata.get('child', ''),
            '{{provider}}': metadata.get('provider', ''),
            '{{type}}': visit_type,
            '{{diagnosis}}': metadata.get('diagnosis', ''),
            '{{treatment}}': metadata.get('treatment', ''),
            '{{cost}}': metadata.get('cost', ''),
            '{{notes}}': metadata.get('notes', ''),
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))

        # Generate filename following CPS convention
        child = metadata.get('child', 'Unknown')
        date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Create brief description from diagnosis, visit type, or default
        # Priority: diagnosis > visit_type > "Medical-Visit"
        diagnosis = metadata.get('diagnosis', '').strip()
        visit_type = metadata.get('type', metadata.get('visit_type', '')).strip()

        # Use diagnosis if meaningful (not "Not specified" or empty)
        if diagnosis and diagnosis != 'Not specified':
            description = diagnosis
        elif visit_type and visit_type != 'Medical Visit':
            description = visit_type
        else:
            # Fallback: try chief complaint or default
            chief_complaint = metadata.get('chief_complaint', metadata.get('reason', '')).strip()
            if chief_complaint and chief_complaint != 'Not specified':
                description = chief_complaint
            else:
                description = 'Medical-Visit'

        # Clean and shorten description (max 50 chars)
        description_clean = re.sub(r'[^\w\s-]', '', description).strip()
        description_clean = re.sub(r'\s+', '-', description_clean)
        if len(description_clean) > 50:
            description_clean = description_clean[:50].rstrip('-')

        # CPS convention: YYYY-MM-DD-{Brief-Description}.md
        base_filename = f"{date_str}-{description_clean}.md"

        # Save to 60-medical/{child}/ following CPS structure
        child_folder = self.cps_path / "60-medical" / child.lower()

        # Ensure child folder exists
        if not self.dry_run:
            child_folder.mkdir(parents=True, exist_ok=True)

        # Check for collisions and add counter if needed
        note_path = child_folder / base_filename
        counter = 1
        while note_path.exists():
            filename_parts = base_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}-{counter}.{filename_parts[1]}"
            note_path = child_folder / filename
            counter += 1

        # DRY RUN MODE
        if self.dry_run:
            print("\n" + "="*60)
            print("🔧 BASICMEMORY DRY RUN - Would create medical note:")
            print("="*60)
            print(f"  Path: {note_path}")
            print(f"  Folder: 60-medical/{child.lower()}/")
            print(f"  Filename: {note_path.name}")
            print(f"\n  Metadata:")
            for key, value in metadata.items():
                print(f"    {key}: {value}")
            print(f"\n  Content preview (first 500 chars):")
            print(f"  {content[:500]}...")
            print("="*60 + "\n")
            return note_path

        # Write note
        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created medical note: {note_path}")

        return note_path

    def create_expense_note(self, metadata):
        """
        Create an expense note from template

        Args:
            metadata: Dictionary containing:
                - child: Child name (Jacob or Morgan)
                - date: Expense date (YYYY-MM-DD)
                - vendor: Vendor/store name
                - amount: Expense amount
                - category: Expense category (school, activities, clothing, etc.)
                - description: Description of expense
                - reimbursable: Whether this is reimbursable (yes/no)
                - notes: Additional notes (optional)

        Returns:
            Path to created note
        """
        if not self.expense_template_path.exists():
            raise FileNotFoundError(f"Expense template not found: {self.expense_template_path}")

        # Read template
        with open(self.expense_template_path, 'r') as f:
            template = f.read()

        # Fill in template
        content = template

        # Replace placeholders
        replacements = {
            '{{date}}': metadata.get('date', datetime.now().strftime('%Y-%m-%d')),
            '{{child}}': metadata.get('child', ''),
            '{{vendor}}': metadata.get('vendor', ''),
            '{{amount}}': metadata.get('amount', ''),
            '{{category}}': metadata.get('category', ''),
            '{{description}}': metadata.get('description', ''),
            '{{reimbursable}}': metadata.get('reimbursable', 'no'),
            '{{notes}}': metadata.get('notes', ''),
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))

        # Generate filename
        child = metadata.get('child', 'Unknown')
        date_str = metadata.get('date', datetime.now().strftime('%Y%m%d'))
        vendor = metadata.get('vendor', 'Expense')

        # Sanitize filename
        vendor_clean = re.sub(r'[^\w\s-]', '', vendor).strip().replace(' ', '-')
        filename = f"{date_str}_{child}_{vendor_clean}_Expense.md"

        # Create note
        note_path = self.cps_path / "Expenses" / filename

        # DRY RUN MODE
        if self.dry_run:
            print("\n" + "="*60)
            print("🔧 BASICMEMORY DRY RUN - Would create expense note:")
            print("="*60)
            print(f"  Path: {note_path}")
            print(f"  Filename: {filename}")
            print(f"\n  Metadata:")
            for key, value in metadata.items():
                print(f"    {key}: {value}")
            print(f"\n  Content preview (first 500 chars):")
            print(f"  {content[:500]}...")
            print("="*60 + "\n")
            return note_path

        # Ensure directory exists
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # Write note
        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created expense note: {note_path}")

        return note_path


    def create_personal_medical_note(self, metadata, source_filename=None):
        """
        Create a personal (adult) medical note

        Args:
            metadata: Dictionary containing:
                - date: Visit date (YYYY-MM-DD)
                - provider: Provider/clinic name
                - type: Visit type (office-visit, urgent-care, ER, etc.)
                - specialty: Medical specialty
                - diagnosis: Diagnosis or reason
                - treatment: Treatment provided
                - cost: Cost/copay
                - notes: Additional notes

        Returns:
            Path to created note
        """
        # Generate simple markdown note (template optional)
        date_val = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        provider = metadata.get('provider', 'Unknown Provider')
        visit_type = metadata.get('type', 'office-visit')
        
        # Build markdown content
        amount = metadata.get('amount', metadata.get('cost', 0.00))
        content = f"""---
date: {date_val}
provider: {provider}
type: {visit_type}
amount: {amount}
specialty: {metadata.get('specialty', '')}
category: PERSONAL-MEDICAL
tags: [medical, personal]
---

# Personal Medical - {provider}

**Date**: {date_val}
**Provider**: {provider}
**Type**: {visit_type}
**Specialty**: {metadata.get('specialty', 'N/A')}

## Diagnosis

{metadata.get('diagnosis', 'Not specified')}

## Treatment

{metadata.get('treatment', 'Not specified')}

## Cost

- **Amount**: ${metadata.get('cost', '0.00')}
- **Insurance**: {metadata.get('insurance_used', 'N/A')}

## Follow-up

{metadata.get('follow_up', 'None scheduled')}

## Notes

{metadata.get('notes', '')}
"""

        # Generate filename: YYYY-MM-DD-{provider}-{type}.md
        provider_clean = re.sub(r'[^\\w\\s-]', '', provider).strip().replace(' ', '-')
        type_clean = re.sub(r'[^\\w\\s-]', '', visit_type).strip().replace(' ', '-')
        base_filename = f"{date_val}-{provider_clean}-{type_clean}.md"

        # Save to Personal/Medical/
        medical_folder = self.personal_path / "Medical"

        if not self.dry_run:
            medical_folder.mkdir(parents=True, exist_ok=True)

        # Check for collisions
        note_path = medical_folder / base_filename
        counter = 1
        while note_path.exists():
            filename_parts = base_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}-{counter}.{filename_parts[1]}"
            note_path = medical_folder / filename
            counter += 1

        if self.dry_run:
            print(f"\\n{'='*60}")
            print(f"🔧 BASICMEMORY DRY RUN - Would create personal medical note:")
            print(f"{'='*60}")
            print(f"  Path: {note_path}")
            print(f"  Folder: Personal/Medical/")
            print(f"  Filename: {note_path.name}")
            print(f"{'='*60}\\n")
            return note_path

        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created personal medical note: {note_path}")
        return note_path

    def create_personal_expense_note(self, metadata, source_filename=None):
        """
        Create a personal expense note

        Args:
            metadata: Dictionary containing:
                - date: Purchase date (YYYY-MM-DD)
                - vendor: Store/merchant name
                - amount: Total amount
                - category: Spending category
                - payment_method: How paid
                - description: Brief description
                - notes: Additional notes

        Returns:
            Path to created note
        """
        date_val = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        vendor = metadata.get('vendor', 'Unknown Vendor')
        amount = metadata.get('amount', '0.00')
        category = metadata.get('category', 'other')

        # Build markdown content
        content = f"""---
date: {date_val}
vendor: {vendor}
amount: {amount}
category: PERSONAL-EXPENSE
subcategory: {category}
payment_method: {metadata.get('payment_method', '')}
tags: [expense, personal, {category}]
---

# Personal Expense - {vendor}

**Date**: {date_val}
**Vendor**: {vendor}
**Amount**: ${amount}
**Category**: {category}
**Payment Method**: {metadata.get('payment_method', 'N/A')}

## Description

{metadata.get('description', '')}

## Items

{metadata.get('items', 'N/A')}

## Notes

{metadata.get('notes', '')}
"""

        # Generate filename: YYYY-MM-DD-{vendor}.md
        vendor_clean = re.sub(r'[^\\w\\s-]', '', vendor).strip().replace(' ', '-')
        base_filename = f"{date_val}-{vendor_clean}.md"

        # Save to Personal/Expenses/{category}/
        expense_folder = self.personal_path / "Expenses" / category

        if not self.dry_run:
            expense_folder.mkdir(parents=True, exist_ok=True)

        note_path = expense_folder / base_filename
        counter = 1
        while note_path.exists():
            filename_parts = base_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}-{counter}.{filename_parts[1]}"
            note_path = expense_folder / filename
            counter += 1

        if self.dry_run:
            print(f"\\n{'='*60}")
            print(f"🔧 BASICMEMORY DRY RUN - Would create personal expense note:")
            print(f"{'='*60}")
            print(f"  Path: {note_path}")
            print(f"  Folder: Personal/Expenses/{category}/")
            print(f"  Filename: {note_path.name}")
            print(f"{'='*60}\\n")
            return note_path

        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created personal expense note: {note_path}")
        return note_path

    def create_utility_note(self, metadata, source_filename=None):
        """
        Create a utility bill note

        Args:
            metadata: Dictionary containing:
                - date: Bill date (YYYY-MM-DD)
                - provider: Utility company name
                - type: Utility type (electric, gas, water, etc.)
                - amount: Total amount due
                - due_date: Payment due date
                - account_number: Masked account number
                - notes: Additional notes

        Returns:
            Path to created note
        """
        date_val = metadata.get('date', metadata.get('billing_date', datetime.now().strftime('%Y-%m-%d')))
        provider = metadata.get('provider', 'Unknown Provider')
        utility_type = metadata.get('utility_type', metadata.get('type', 'utility'))
        amount = metadata.get('amount', '0.00')

        content = f"""---
date: {date_val}
provider: {provider}
utility_type: {utility_type}
amount: {amount}
due_date: {metadata.get('due_date', '')}
billing_date: {metadata.get('billing_date', date_val)}
account_number: {metadata.get('account_number', '')}
category: UTILITY
tags: [utility, {utility_type}]
---

# Utility Bill - {provider}

**Date**: {date_val}
**Provider**: {provider}
**Type**: {utility_type.title()}
**Amount Due**: ${amount}
**Due Date**: {metadata.get('due_date', 'N/A')}
**Account**: {metadata.get('account_number', 'N/A')}

## Billing Period

{metadata.get('billing_period', 'N/A')}

## Usage

{metadata.get('usage', 'N/A')}

## Payment Status

{metadata.get('payment_status', 'unpaid')}

## Notes

{metadata.get('notes', '')}
"""

        provider_clean = re.sub(r'[^\\w\\s-]', '', provider).strip().replace(' ', '-')
        base_filename = f"{date_val}-{provider_clean}-{utility_type}.md"

        utility_folder = self.personal_path / "Utilities" / utility_type

        if not self.dry_run:
            utility_folder.mkdir(parents=True, exist_ok=True)

        note_path = utility_folder / base_filename
        counter = 1
        while note_path.exists():
            filename_parts = base_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}-{counter}.{filename_parts[1]}"
            note_path = utility_folder / filename
            counter += 1

        if self.dry_run:
            print(f"\\n{'='*60}")
            print(f"🔧 BASICMEMORY DRY RUN - Would create utility note:")
            print(f"{'='*60}")
            print(f"  Path: {note_path}")
            print(f"  Folder: Personal/Utilities/{utility_type}/")
            print(f"  Filename: {note_path.name}")
            print(f"{'='*60}\\n")
            return note_path

        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created utility note: {note_path}")
        return note_path

    def create_auto_note(self, metadata, source_filename=None, category=None):
        """
        Create an automotive document note

        Args:
            metadata: Dictionary containing:
                - date: Service/document date (YYYY-MM-DD)
                - type: Document type (oil-change, registration, etc.)
                - provider: Service provider or agency
                - amount: Total cost
                - vehicle: Vehicle description
                - mileage: Odometer reading
                - notes: Additional notes
            source_filename: Original filename (optional)
            category: Category for routing (AUTO-INSURANCE, AUTO-MAINTENANCE, AUTO-REGISTRATION)

        Returns:
            Path to created note
        """
        date_val = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Determine auto type from category parameter or metadata
        if category:
            # Map category to subdirectory
            category_map = {
                'AUTO-INSURANCE': 'Insurance',
                'AUTO-MAINTENANCE': 'Maintenance',
                'AUTO-REGISTRATION': 'Registration',
            }
            auto_subdir = category_map.get(category, 'Other')
            auto_type = auto_subdir.lower()
        else:
            auto_type = metadata.get('type', 'other-service')
            auto_subdir = auto_type.replace('-', ' ').title().replace(' ', '')
        
        provider = metadata.get('provider', metadata.get('insurance_company', metadata.get('shop', 'Unknown Provider')))
        amount = metadata.get('amount', metadata.get('cost', metadata.get('fee', '0.00')))
        
        # Determine category for frontmatter
        auto_category = category if category else f"AUTO-{auto_type.upper().replace('-', '_')}"
        
        # Preserve all specific fields in frontmatter based on category
        frontmatter_fields = f"""date: {date_val}
type: {auto_type}
provider: {provider}
amount: {amount}
vehicle: {metadata.get('vehicle', '')}
category: {auto_category}
tags: [auto, {auto_type}]"""
        
        # Add category-specific fields
        if metadata.get('insurance_company'):
            frontmatter_fields += f"\ninsurance_company: {metadata.get('insurance_company', '')}"
        if metadata.get('policy_number'):
            frontmatter_fields += f"\npolicy_number: {metadata.get('policy_number', '')}"
        if metadata.get('service_type'):
            frontmatter_fields += f"\nservice_type: {metadata.get('service_type', '')}"
        if metadata.get('shop'):
            frontmatter_fields += f"\nshop: {metadata.get('shop', '')}"
        if metadata.get('cost'):
            frontmatter_fields += f"\ncost: {metadata.get('cost', 0.00)}"
        if metadata.get('mileage'):
            frontmatter_fields += f"\nmileage: {metadata.get('mileage', '')}"
        if metadata.get('registration_number'):
            frontmatter_fields += f"\nregistration_number: {metadata.get('registration_number', '')}"
        if metadata.get('vin'):
            frontmatter_fields += f"\nvin: {metadata.get('vin', '')}"
        if metadata.get('license_plate'):
            frontmatter_fields += f"\nlicense_plate: {metadata.get('license_plate', '')}"
        if metadata.get('fee'):
            frontmatter_fields += f"\nfee: {metadata.get('fee', 0.00)}"

        content = f"""---
{frontmatter_fields}
---

# Auto - {provider}

**Date**: {date_val}
**Type**: {auto_type.replace('-', ' ').title()}
**Provider**: {provider}
**Amount**: ${amount}
**Vehicle**: {metadata.get('vehicle', 'N/A')}
**Mileage**: {metadata.get('mileage', 'N/A')}

## Service Description

{metadata.get('service_description', metadata.get('service_type', 'N/A'))}

## Parts

{metadata.get('parts', 'N/A')}

## Next Service

- **Date**: {metadata.get('next_service_date', 'N/A')}
- **Mileage**: {metadata.get('next_service_mileage', 'N/A')}

## Warranty

{metadata.get('warranty', 'N/A')}

## Notes

{metadata.get('notes', '')}
"""

        provider_clean = re.sub(r'[^\w\s-]', '', provider).strip().replace(' ', '-')
        type_clean = re.sub(r'[^\w\s-]', '', auto_type).strip().replace(' ', '-')
        base_filename = f"{date_val}-{provider_clean}-{type_clean}.md"

        # Use Auto/ instead of Automotive/
        auto_folder = self.personal_path / "Auto" / auto_subdir

        if not self.dry_run:
            auto_folder.mkdir(parents=True, exist_ok=True)

        note_path = auto_folder / base_filename
        counter = 1
        while note_path.exists():
            filename_parts = base_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}-{counter}.{filename_parts[1]}"
            note_path = auto_folder / filename
            counter += 1

        if self.dry_run:
            print(f"\n{'='*60}")
            print(f"🔧 BASICMEMORY DRY RUN - Would create auto note:")
            print(f"{'='*60}")
            print(f"  Path: {note_path}")
            print(f"  Folder: Personal/Auto/{auto_subdir}/")
            print(f"  Filename: {note_path.name}")
            print(f"{'='*60}\n")
            return note_path

        with open(note_path, 'w') as f:
            f.write(content)

        print(f"✓ Created auto note: {note_path}")
        return note_path


if __name__ == '__main__':
    # Test note creation
    creator = BasicMemoryNoteCreator()

    print("Testing medical note creation...")
    medical_metadata = {
        'child': 'Jacob',
        'date': '2025-12-20',
        'provider': 'Pediatric Clinic',
        'type': 'Well Child Visit',
        'diagnosis': 'Healthy',
        'treatment': 'Routine checkup',
        'cost': '$25.00',
        'notes': 'Test note from scan processor'
    }

    try:
        medical_note = creator.create_medical_note(medical_metadata)
        print(f"✓ Medical note created: {medical_note}")
    except Exception as e:
        print(f"✗ Failed to create medical note: {e}")

    print("\nTesting expense note creation...")
    expense_metadata = {
        'child': 'Morgan',
        'date': '2025-12-20',
        'vendor': 'Target',
        'amount': '$45.99',
        'category': 'School Supplies',
        'description': 'Notebooks and pens',
        'reimbursable': 'yes',
        'notes': 'Test expense from scan processor'
    }

    try:
        expense_note = creator.create_expense_note(expense_metadata)
        print(f"✓ Expense note created: {expense_note}")
    except Exception as e:
        print(f"✗ Failed to create expense note: {e}")
