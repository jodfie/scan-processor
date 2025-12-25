# Utility Bill Metadata Extraction

You are extracting metadata from a **utility bill** (electric, gas, water, internet, phone, etc.).

## Required Fields

- **date**: Bill date or due date (YYYY-MM-DD format)
- **provider**: Utility company name (e.g., "Duke Energy", "AT&T", "Spectrum")
- **type**: Type of utility (electric, gas, water, sewer, internet, cable, phone)
- **amount**: Total amount due (number only, e.g., 145.67)
- **due_date**: Payment due date (YYYY-MM-DD format)
- **account_number**: Last 4 digits only (masked for privacy, e.g., "****5678")

## Optional Fields

- **service_address**: Address being served (if different from billing)
- **billing_period**: Billing period (e.g., "Dec 1 - Dec 31, 2025")
- **usage**: Usage amount (kWh for electric, therms for gas, GB for internet)
- **previous_balance**: Previous balance if any
- **payment_status**: paid, unpaid, overdue
- **autopay_enabled**: true/false if autopay is mentioned
- **notes**: Any additional important details

## Privacy & Security

- **NEVER include full account numbers** - use masked format: `****5678`
- **NEVER include full credit card numbers**
- **NEVER include SSN or sensitive IDs**

## Utility Types

- **electric**: Electricity (Duke Energy, etc.)
- **gas**: Natural gas (Piedmont Natural Gas, etc.)
- **water**: Water/sewer
- **internet**: Internet service
- **cable**: Cable TV
- **phone**: Phone service (mobile or landline)
- **combined**: Multiple services in one bill

## Output Format (JSON)

```json
{
  "date": "2025-12-20",
  "provider": "Duke Energy",
  "type": "electric",
  "amount": 145.67,
  "due_date": "2026-01-10",
  "account_number": "****5678",
  "service_address": "123 Main St",
  "billing_period": "Nov 15 - Dec 15, 2025",
  "usage": "850 kWh",
  "previous_balance": 0.00,
  "payment_status": "unpaid",
  "autopay_enabled": true,
  "notes": "Usage higher than average month"
}
```

## Examples

### Electric Bill

```json
{
  "date": "2025-12-20",
  "provider": "Duke Energy",
  "type": "electric",
  "amount": 145.67,
  "due_date": "2026-01-10",
  "account_number": "****5678",
  "billing_period": "Nov 15 - Dec 15, 2025",
  "usage": "850 kWh",
  "payment_status": "unpaid"
}
```

### Internet Bill

```json
{
  "date": "2025-12-18",
  "provider": "Spectrum",
  "type": "internet",
  "amount": 89.99,
  "due_date": "2026-01-05",
  "account_number": "****1234",
  "billing_period": "Dec 1 - Dec 31, 2025",
  "usage": "Unlimited",
  "autopay_enabled": true,
  "payment_status": "autopay"
}
```

### Water/Sewer

```json
{
  "date": "2025-12-15",
  "provider": "Durham Water Management",
  "type": "water",
  "amount": 67.23,
  "due_date": "2026-01-10",
  "account_number": "****9012",
  "billing_period": "Nov 1 - Nov 30, 2025",
  "usage": "4,500 gallons",
  "payment_status": "unpaid"
}
```

Now extract metadata from the utility bill and provide your response in the JSON format specified above.
