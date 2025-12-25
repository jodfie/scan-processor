# Auto Maintenance/Registration Metadata Extraction

You are extracting metadata from an **automotive document** (maintenance, registration, insurance, repair, etc.).

## Required Fields

- **date**: Service date or document date (YYYY-MM-DD format)
- **type**: Document type (oil-change, repair, registration, insurance, inspection, other)
- **provider**: Service provider or agency (e.g., "Jiffy Lube", "NC DMV", "State Farm")
- **amount**: Total cost (number only, 0.00 if not applicable)

## Optional Fields

- **vehicle**: Vehicle description (e.g., "2018 Honda Accord", "Black SUV")
- **mileage**: Odometer reading at service
- **service_description**: Description of service performed
- **parts**: Parts replaced or installed
- **next_service_date**: When next service is due
- **next_service_mileage**: Mileage when next service is due
- **registration_expiration**: Registration expiration date (YYYY-MM-DD)
- **inspection_expiration**: Inspection expiration date (YYYY-MM-DD)
- **policy_number**: Insurance policy number (if insurance doc)
- **coverage**: Insurance coverage details
- **payment_method**: How paid
- **warranty**: Warranty information
- **notes**: Additional relevant details

## Document Types

### Maintenance & Repair
- **oil-change**: Oil change service
- **tire-service**: Tire rotation, replacement, repair
- **brake-service**: Brake pads, rotors, etc.
- **battery**: Battery replacement
- **alignment**: Wheel alignment
- **diagnostic**: Diagnostic service
- **repair**: General repairs
- **tune-up**: Engine tune-up
- **fluid-service**: Transmission fluid, coolant, etc.
- **other-service**: Other maintenance

### Official Documents
- **registration**: Vehicle registration renewal
- **title**: Vehicle title document
- **inspection**: State safety/emissions inspection
- **insurance**: Auto insurance policy or card
- **accident-report**: Accident/incident report

## Output Format (JSON)

```json
{
  "date": "2025-12-20",
  "type": "oil-change",
  "provider": "Jiffy Lube",
  "amount": 45.99,
  "vehicle": "2018 Honda Accord",
  "mileage": 75234,
  "service_description": "Full synthetic oil change",
  "parts": ["Oil filter", "5 quarts synthetic oil"],
  "next_service_date": "2026-03-20",
  "next_service_mileage": 78234,
  "payment_method": "credit-card",
  "notes": "Tire pressure checked, all fluids topped off"
}
```

## Examples

### Oil Change

```json
{
  "date": "2025-12-20",
  "type": "oil-change",
  "provider": "Jiffy Lube",
  "amount": 45.99,
  "vehicle": "2018 Honda Accord",
  "mileage": 75234,
  "service_description": "Synthetic oil change",
  "parts": ["Oil filter", "5qt synthetic oil"],
  "next_service_mileage": 78234,
  "payment_method": "credit-card"
}
```

### Tire Replacement

```json
{
  "date": "2025-12-15",
  "type": "tire-service",
  "provider": "Discount Tire",
  "amount": 487.50,
  "vehicle": "2018 Honda Accord",
  "mileage": 75100,
  "service_description": "4 new tires installed",
  "parts": ["4 Michelin tires", "tire disposal"],
  "warranty": "60,000 mile warranty",
  "payment_method": "credit-card"
}
```

### Brake Service

```json
{
  "date": "2025-11-30",
  "type": "brake-service",
  "provider": "Meineke",
  "amount": 325.00,
  "vehicle": "2018 Honda Accord",
  "mileage": 74800,
  "service_description": "Front brake pads and rotors",
  "parts": ["Front brake pads", "Front rotors"],
  "warranty": "12 months / 12,000 miles",
  "payment_method": "credit-card"
}
```

### Vehicle Registration

```json
{
  "date": "2025-12-01",
  "type": "registration",
  "provider": "NC DMV",
  "amount": 38.75,
  "vehicle": "2018 Honda Accord",
  "registration_expiration": "2026-12-31",
  "payment_method": "credit-card",
  "notes": "Registration renewed online"
}
```

### State Inspection

```json
{
  "date": "2025-11-20",
  "type": "inspection",
  "provider": "ABC Auto Center",
  "amount": 30.00,
  "vehicle": "2018 Honda Accord",
  "mileage": 74500,
  "inspection_expiration": "2026-11-30",
  "payment_method": "cash",
  "notes": "Passed safety and emissions"
}
```

### Auto Insurance

```json
{
  "date": "2025-12-01",
  "type": "insurance",
  "provider": "State Farm",
  "amount": 145.00,
  "vehicle": "2018 Honda Accord",
  "policy_number": "****5678",
  "coverage": "Full coverage, $500 deductible",
  "notes": "Monthly premium, auto-pay"
}
```

### Repair

```json
{
  "date": "2025-12-10",
  "type": "repair",
  "provider": "Honda Dealership Service",
  "amount": 285.50,
  "vehicle": "2018 Honda Accord",
  "mileage": 74900,
  "service_description": "Replace alternator belt",
  "parts": ["Serpentine belt", "belt tensioner"],
  "warranty": "90 days / 3,000 miles",
  "payment_method": "credit-card"
}
```

Now extract metadata from the automotive document and provide your response in the JSON format specified above.
