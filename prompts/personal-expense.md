# Personal Expense Metadata Extraction

You are extracting metadata from a **personal expense receipt** (groceries, dining, shopping, entertainment, etc.).

**IMPORTANT**: This is for PERSONAL expenses only. If the expense is specifically for children (Jacob or Morgan), it should be classified as CPS_EXPENSE instead.

## Required Fields

- **date**: Purchase date (YYYY-MM-DD format)
- **vendor**: Store or merchant name (e.g., "Whole Foods", "Target", "Amazon")
- **amount**: Total amount spent (number only, e.g., 87.45)
- **category**: Spending category (see categories below)
- **payment_method**: How paid (credit-card, debit-card, cash, check, venmo, etc.)

## Optional Fields

- **description**: Brief description of purchase
- **items**: Major items purchased (if notable)
- **tax_amount**: Sales tax amount
- **tip_amount**: Tip/gratuity (for restaurants)
- **rewards_earned**: Points/cashback earned
- **notes**: Additional relevant details

## Spending Categories

- **groceries**: Grocery shopping (food for household)
- **dining**: Restaurants, fast food, takeout
- **entertainment**: Movies, concerts, events, streaming services
- **clothing**: Personal clothing purchases
- **electronics**: Electronics, gadgets, tech
- **home-goods**: Home decor, furniture, household items
- **personal-care**: Personal care items (toiletries, haircuts, etc.)
- **gifts**: Gifts for others
- **subscriptions**: Subscription services
- **fuel**: Gasoline for vehicle
- **other**: Other personal spending

## Payment Methods

- **credit-card**: Credit card
- **debit-card**: Debit card
- **cash**: Cash
- **check**: Check
- **venmo**: Venmo or similar P2P payment
- **paypal**: PayPal
- **apple-pay**: Apple Pay or similar mobile payment

## Output Format (JSON)

```json
{
  "date": "2025-12-20",
  "vendor": "Whole Foods",
  "amount": 87.45,
  "category": "groceries",
  "payment_method": "credit-card",
  "description": "Weekly grocery shopping",
  "items": ["produce", "meat", "dairy", "bread"],
  "tax_amount": 5.25,
  "rewards_earned": "87 points"
}
```

## Examples

### Grocery Shopping

```json
{
  "date": "2025-12-18",
  "vendor": "Whole Foods",
  "amount": 87.45,
  "category": "groceries",
  "payment_method": "credit-card",
  "description": "Weekly groceries",
  "items": ["produce", "meat", "dairy"],
  "tax_amount": 5.25
}
```

### Restaurant

```json
{
  "date": "2025-12-15",
  "vendor": "Olive Garden",
  "amount": 45.60,
  "category": "dining",
  "payment_method": "credit-card",
  "description": "Dinner out",
  "tax_amount": 3.20,
  "tip_amount": 9.00
}
```

### Clothing

```json
{
  "date": "2025-12-10",
  "vendor": "Target",
  "amount": 67.89,
  "category": "clothing",
  "payment_method": "debit-card",
  "description": "Work shirts and pants",
  "items": ["2 shirts", "1 pair pants"],
  "tax_amount": 4.50
}
```

### Gas

```json
{
  "date": "2025-12-20",
  "vendor": "Shell Station",
  "amount": 52.00,
  "category": "fuel",
  "payment_method": "credit-card",
  "description": "Gasoline",
  "notes": "15.2 gallons @ $3.42/gal"
}
```

### Subscription

```json
{
  "date": "2025-12-01",
  "vendor": "Netflix",
  "amount": 15.99,
  "category": "subscriptions",
  "payment_method": "credit-card",
  "description": "Monthly Netflix subscription",
  "notes": "Standard plan"
}
```

### Home Goods

```json
{
  "date": "2025-12-12",
  "vendor": "Home Depot",
  "amount": 134.76,
  "category": "home-goods",
  "payment_method": "credit-card",
  "description": "Light fixtures and paint",
  "items": ["2 light fixtures", "3 gallons paint"],
  "tax_amount": 9.50
}
```

Now extract metadata from the personal expense receipt and provide your response in the JSON format specified above.
