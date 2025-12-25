# Personal Medical Record Metadata Extraction

You are extracting metadata from a **personal medical record** (for Jody, NOT for children Jacob or Morgan).

**IMPORTANT**: This is for ADULT medical records only. If the document is for a child (Jacob or Morgan), it should be classified as CPS-MEDICAL instead.

## Required Fields

- **date**: Date of medical service or document (YYYY-MM-DD format)
- **provider**: Medical provider name (e.g., "Dr. Sarah Smith", "Durham Regional Hospital")
- **type**: Visit type (office-visit, urgent-care, ER, specialist, lab, imaging, etc.)
- **specialty**: Medical specialty if applicable (primary-care, cardiology, orthopedics, etc.)

## Optional Fields

- **diagnosis**: Primary diagnosis or reason for visit
- **treatment**: Treatment provided or medications prescribed
- **cost**: Total cost or copay amount (number only)
- **insurance_used**: Insurance provider name
- **claim_number**: Insurance claim number (if present)
- **prescription**: Medications prescribed
- **follow_up**: Follow-up appointment info
- **lab_results**: Lab test results summary (if present)
- **notes**: Any additional important medical information

## Privacy & Security

- **Patient name should be Jody** (adult)
- **Do NOT include** SSN, full insurance ID, or other sensitive identifiers
- If the document shows a child's name (Jacob or Morgan), this is the WRONG prompt

## Visit Types

- **office-visit**: Routine doctor visit
- **urgent-care**: Urgent care visit
- **ER**: Emergency room visit
- **specialist**: Specialist consultation
- **lab**: Lab work
- **imaging**: X-ray, MRI, CT scan, etc.
- **telehealth**: Virtual visit
- **procedure**: Medical procedure
- **surgery**: Surgical procedure
- **follow-up**: Follow-up visit
- **annual-physical**: Annual checkup

## Medical Specialties

- **primary-care**: Family doctor, general practice
- **cardiology**: Heart specialist
- **orthopedics**: Bone/joint specialist
- **dermatology**: Skin specialist
- **gastroenterology**: Digestive system
- **neurology**: Neurological specialist
- **ophthalmology**: Eye specialist
- **ENT**: Ear, nose, throat
- **psychiatry**: Mental health
- **other**: Other specialties

## Output Format (JSON)

```json
{
  "date": "2025-12-20",
  "provider": "Dr. Sarah Smith",
  "type": "office-visit",
  "specialty": "primary-care",
  "diagnosis": "Annual physical exam",
  "treatment": "Routine checkup, labs ordered",
  "cost": 25.00,
  "insurance_used": "Blue Cross Blue Shield",
  "prescription": "None",
  "follow_up": "Return in 1 year",
  "notes": "Blood pressure normal, cholesterol slightly elevated"
}
```

## Examples

### Annual Physical

```json
{
  "date": "2025-12-18",
  "provider": "Dr. Michael Johnson",
  "type": "annual-physical",
  "specialty": "primary-care",
  "diagnosis": "Routine wellness exam",
  "treatment": "Physical exam, labs ordered",
  "cost": 25.00,
  "insurance_used": "BCBS",
  "follow_up": "1 year",
  "notes": "All vitals normal"
}
```

### Urgent Care

```json
{
  "date": "2025-12-10",
  "provider": "MedExpress Urgent Care",
  "type": "urgent-care",
  "specialty": "urgent-care",
  "diagnosis": "Upper respiratory infection",
  "treatment": "Prescribed amoxicillin 500mg",
  "cost": 50.00,
  "insurance_used": "BCBS",
  "prescription": "Amoxicillin 500mg, 3x daily for 10 days"
}
```

### Specialist Visit

```json
{
  "date": "2025-11-30",
  "provider": "Dr. Emily Chen - Cardiology Associates",
  "type": "specialist",
  "specialty": "cardiology",
  "diagnosis": "Routine cardiac follow-up",
  "treatment": "EKG performed, medication review",
  "cost": 40.00,
  "insurance_used": "BCBS",
  "follow_up": "6 months",
  "notes": "Heart rhythm normal, continue current medications"
}
```

### Lab Work

```json
{
  "date": "2025-12-05",
  "provider": "LabCorp",
  "type": "lab",
  "specialty": "lab",
  "diagnosis": "Annual bloodwork",
  "lab_results": "Cholesterol 210, glucose 95",
  "cost": 0.00,
  "insurance_used": "BCBS",
  "notes": "Cholesterol slightly elevated, discuss diet at next visit"
}
```

Now extract metadata from the personal medical record and provide your response in the JSON format specified above.
