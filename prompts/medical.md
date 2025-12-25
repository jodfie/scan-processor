# Medical Document Metadata Extraction

You are extracting detailed metadata from a medical document for a co-parenting system. The document has already been classified as MEDICAL.

## Children Information

- **Jacob** (born 2019)
- **Morgan** (born 2017)
- Co-parent: Stephanie

## Extraction Requirements

Extract the following information from the medical document:

1. **child**: Which child (Jacob or Morgan)
2. **date**: Date of service/visit (YYYY-MM-DD)
3. **provider**: Doctor name, clinic name, or healthcare provider
4. **type**: Type of visit or service (e.g., "Well Child Visit", "Sick Visit", "Dental Checkup", "Vaccination", "Prescription", "EOB")
5. **diagnosis**: Diagnosis or reason for visit (if available)
6. **treatment**: Treatment provided or prescribed (if available)
7. **cost**: Total cost, copay, or amount due (include $ and cents, e.g., "$25.00")
8. **notes**: Any additional relevant information

## Output Format

Respond with a JSON object in this exact format:

```json
{
  "child": "Jacob|Morgan",
  "date": "YYYY-MM-DD",
  "provider": "Provider name",
  "type": "Visit type",
  "diagnosis": "Diagnosis or null",
  "treatment": "Treatment or null",
  "cost": "$XX.XX or null",
  "notes": "Additional notes or empty string",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["medical", "child-name", "provider-type"]
}
```

## Clarification Rules

Set `needs_clarification` to `true` if:

1. You cannot determine which child
2. The date is missing or unclear
3. Key information is illegible or missing

## Tags Guidelines

Include relevant tags from this list:
- "medical", "dental", "vision"
- "checkup", "sick-visit", "vaccination", "prescription"
- "emergency", "urgent-care", "specialist"
- child name in lowercase (e.g., "jacob", "morgan")

## Examples

### Example 1: Well Child Visit

```json
{
  "child": "Jacob",
  "date": "2025-12-15",
  "provider": "Pediatric Associates - Dr. Smith",
  "type": "Well Child Visit",
  "diagnosis": "Healthy - routine checkup",
  "treatment": "Routine examination, growth measurements",
  "cost": "$25.00",
  "notes": "Next visit scheduled for 6 months",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["medical", "jacob", "checkup", "pediatric"]
}
```

### Example 2: Dental Visit

```json
{
  "child": "Morgan",
  "date": "2025-11-20",
  "provider": "Bright Smiles Dental",
  "type": "Dental Cleaning",
  "diagnosis": "No cavities found",
  "treatment": "Routine cleaning and fluoride treatment",
  "cost": "$0.00",
  "notes": "Covered by insurance, no copay",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["dental", "morgan", "checkup", "preventive"]
}
```

### Example 3: EOB (Explanation of Benefits)

```json
{
  "child": "Jacob",
  "date": "2025-10-05",
  "provider": "Children's Hospital - Dr. Johnson",
  "type": "EOB - Sick Visit",
  "diagnosis": "Upper respiratory infection",
  "treatment": "Prescribed amoxicillin",
  "cost": "$35.00",
  "notes": "Insurance paid $85.00, patient responsibility $35.00",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["medical", "jacob", "sick-visit", "eob"]
}
```

Now analyze the medical document and extract the metadata in the JSON format specified above.
