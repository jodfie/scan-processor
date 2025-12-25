# Sample Documents for Testing

This directory contains 48 realistic PDF samples for testing the scan-processor document classification and metadata extraction pipeline.

## Directory Structure

```
samples/
├── personal-medical/         (9 samples)
├── personal-expense/         (9 samples)
├── utility/                  (12 samples)
├── auto-insurance/           (6 samples)
├── auto-maintenance/         (6 samples)
└── auto-registration/        (6 samples)
```

---

## Personal Medical (9 samples)

### Medical Bills (3 samples)
**Files**: `medical-bill-01.pdf`, `medical-bill-02.pdf`, `medical-bill-03.pdf`
**Expected Category**: `PERSONAL-MEDICAL`
**Expected Metadata**:
- `provider`: Medical provider/clinic name
- `date`: Date of service
- `amount`: Total bill amount
- `type`: "medical_bill"

### Lab Results (2 samples)
**Files**: `lab-results-01.pdf`, `lab-results-02.pdf`
**Expected Category**: `PERSONAL-MEDICAL`
**Expected Metadata**:
- `provider`: Laboratory name
- `date`: Test date
- `type`: "lab_results"

### Doctor Visits (2 samples)
**Files**: `doctor-visit-01.pdf`, `doctor-visit-02.pdf`
**Expected Category**: `PERSONAL-MEDICAL`
**Expected Metadata**:
- `provider`: Doctor's name
- `date`: Visit date
- `type`: "visit_summary"

### Prescriptions (2 samples)
**Files**: `prescription-01.pdf`, `prescription-02.pdf`
**Expected Category**: `PERSONAL-MEDICAL`
**Expected Metadata**:
- `provider`: Prescribing physician
- `date`: Prescription date
- `medication`: Medication name
- `type`: "prescription"

---

## Personal Expense (9 samples)

### Restaurant Receipts (3 samples)
**Files**: `restaurant-receipt-01.pdf`, `restaurant-receipt-02.pdf`, `restaurant-receipt-03.pdf`
**Expected Category**: `PERSONAL-EXPENSE`
**Expected Metadata**:
- `vendor`: Restaurant name
- `date`: Receipt date
- `amount`: Total amount
- `category`: "dining"

### Amazon Invoices (2 samples)
**Files**: `amazon-invoice-01.pdf`, `amazon-invoice-02.pdf`
**Expected Category**: `PERSONAL-EXPENSE`
**Expected Metadata**:
- `vendor`: "Amazon"
- `date`: Order date
- `amount`: Total amount
- `category`: "online_shopping"

### Store Receipts (2 samples)
**Files**: `store-receipt-01.pdf`, `store-receipt-02.pdf`
**Expected Category**: `PERSONAL-EXPENSE`
**Expected Metadata**:
- `vendor`: Store name (Target, Walmart, etc.)
- `date`: Purchase date
- `amount`: Total amount
- `category`: "shopping"

### Service Invoices (2 samples)
**Files**: `service-invoice-01.pdf`, `service-invoice-02.pdf`
**Expected Category**: `PERSONAL-EXPENSE`
**Expected Metadata**:
- `vendor`: Service provider name
- `date`: Service date
- `amount`: Total amount
- `category`: "services"

---

## Utility (12 samples)

### Electric Bills (3 samples)
**Files**: `electric-bill-01.pdf`, `electric-bill-02.pdf`, `electric-bill-03.pdf`
**Expected Category**: `UTILITY`
**Expected Metadata**:
- `utility_type`: "electric"
- `provider`: Power company name
- `billing_date`: Billing date
- `due_date`: Payment due date
- `amount`: Amount due
- `account_number`: Account number

### Water Bills (2 samples)
**Files**: `water-bill-01.pdf`, `water-bill-02.pdf`
**Expected Category**: `UTILITY`
**Expected Metadata**:
- `utility_type`: "water"
- `provider`: Water company name
- `billing_date`: Billing date
- `due_date`: Payment due date
- `amount`: Amount due

### Gas Bills (2 samples)
**Files**: `gas-bill-01.pdf`, `gas-bill-02.pdf`
**Expected Category**: `UTILITY`
**Expected Metadata**:
- `utility_type`: "gas"
- `provider`: Gas company name
- `billing_date`: Billing date
- `due_date`: Payment due date
- `amount`: Amount due

### Internet Bills (3 samples)
**Files**: `internet-bill-01.pdf`, `internet-bill-02.pdf`, `internet-bill-03.pdf`
**Expected Category**: `UTILITY`
**Expected Metadata**:
- `utility_type`: "internet"
- `provider`: ISP name (Comcast, AT&T, etc.)
- `billing_date`: Billing date
- `due_date`: Payment due date
- `amount`: Amount due

### Phone Bills (2 samples)
**Files**: `phone-bill-01.pdf`, `phone-bill-02.pdf`
**Expected Category**: `UTILITY`
**Expected Metadata**:
- `utility_type`: "phone"
- `provider`: Wireless carrier name
- `billing_date`: Billing date
- `due_date`: Payment due date
- `amount`: Amount due

---

## Auto Insurance (6 samples)

### Insurance Policies (2 samples)
**Files**: `insurance-policy-01.pdf`, `insurance-policy-02.pdf`
**Expected Category**: `AUTO-INSURANCE`
**Expected Metadata**:
- `insurance_company`: Company name
- `policy_number`: Policy number
- `vehicle`: Year/Make/Model
- `effective_date`: Policy effective date
- `expiration_date`: Policy expiration date
- `premium`: Annual premium amount

### Declaration Pages (2 samples)
**Files**: `declaration-page-01.pdf`, `declaration-page-02.pdf`
**Expected Category**: `AUTO-INSURANCE`
**Expected Metadata**:
- `insurance_company`: Company name
- `policy_number`: Policy number
- `vehicle`: Year/Make/Model
- `coverages`: Coverage types and amounts

### Premium Notices (2 samples)
**Files**: `premium-notice-01.pdf`, `premium-notice-02.pdf`
**Expected Category**: `AUTO-INSURANCE`
**Expected Metadata**:
- `insurance_company`: Company name
- `policy_number`: Policy number
- `due_date`: Payment due date
- `amount`: Premium amount

---

## Auto Maintenance (6 samples)

### Oil Change Receipts (2 samples)
**Files**: `oil-change-01.pdf`, `oil-change-02.pdf`
**Expected Category**: `AUTO-MAINTENANCE`
**Expected Metadata**:
- `service_type`: "oil_change"
- `shop`: Service shop name
- `date`: Service date
- `vehicle`: Year/Make/Model
- `mileage`: Current mileage
- `cost`: Total cost

### Tire Service (2 samples)
**Files**: `tire-service-01.pdf`, `tire-service-02.pdf`
**Expected Category**: `AUTO-MAINTENANCE`
**Expected Metadata**:
- `service_type`: "tire_service"
- `shop`: Service shop name
- `date`: Service date
- `vehicle`: Year/Make/Model
- `cost`: Total cost

### General Service (2 samples)
**Files**: `general-service-01.pdf`, `general-service-02.pdf`
**Expected Category**: `AUTO-MAINTENANCE`
**Expected Metadata**:
- `service_type`: "general_service"
- `shop`: Service shop name
- `date`: Service date
- `vehicle`: Year/Make/Model
- `services`: List of services performed
- `cost`: Total cost

---

## Auto Registration (6 samples)

### Registration Renewals (3 samples)
**Files**: `registration-renewal-01.pdf`, `registration-renewal-02.pdf`, `registration-renewal-03.pdf`
**Expected Category**: `AUTO-REGISTRATION`
**Expected Metadata**:
- `registration_number`: Registration number
- `vehicle`: Year/Make/Model
- `vin`: Vehicle identification number
- `license_plate`: License plate number
- `renewal_date`: Renewal date
- `expiration_date`: Expiration date
- `fee`: Registration fee

### Inspection Certificates (3 samples)
**Files**: `inspection-certificate-01.pdf`, `inspection-certificate-02.pdf`, `inspection-certificate-03.pdf`
**Expected Category**: `AUTO-REGISTRATION`
**Expected Metadata**:
- `certificate_number`: Certificate number
- `vehicle`: Year/Make/Model
- `vin`: Vehicle identification number
- `inspection_date`: Inspection date
- `expiration_date`: Valid until date
- `station`: Inspection station name
- `result`: "PASS" or "FAIL"

---

## Usage in Tests

### Sample Classification Test Pattern
```python
def test_classify_personal_medical():
    sample_path = "samples/personal-medical/medical-bill-01.pdf"
    result = classifier.classify(sample_path)
    assert result['category'] == 'PERSONAL-MEDICAL'
    assert result['confidence'] > 0.8
```

### Sample Metadata Extraction Test Pattern
```python
def test_extract_utility_metadata():
    sample_path = "samples/utility/electric-bill-01.pdf"
    metadata = classifier.extract_metadata(sample_path, 'UTILITY')
    assert metadata['utility_type'] == 'electric'
    assert 'billing_date' in metadata
    assert 'amount' in metadata
```

### Sample Note Creation Test Pattern
```python
def test_create_personal_medical_note():
    sample_path = "samples/personal-medical/medical-bill-01.pdf"
    metadata = {...}  # Extract metadata first
    note_path = note_creator.create_personal_medical_note(metadata)
    assert note_path.exists()
    assert "Medical" in str(note_path)
```

---

## Generating New Samples

To generate additional samples:

```bash
# Generate all samples
python3 scripts/generate_samples.py --all

# Generate specific category
python3 scripts/generate_samples.py --category personal-medical --count 5

# Generate to custom directory
python3 scripts/generate_samples.py --all --output-dir samples-test/
```

---

## Notes

- All samples use **realistic but fake data** generated by the Faker library
- Amounts, dates, and identifiers are randomized for each generation
- Sample PDFs are text-based (not scanned images) for easier testing
- Each sample should produce consistent classification results
- Metadata extraction may vary slightly due to random data generation

**Generated**: 2025-12-25
**Total Samples**: 48 documents across 6 categories
