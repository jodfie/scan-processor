# Co-Parenting Expense Metadata Extraction

You are extracting detailed metadata from an expense document for a co-parenting system. The document has already been classified as CPS-EXPENSE.

## Children Information

- **Jacob** (born 2019)
- **Morgan** (born 2017)
- Co-parent: Stephanie
- Custody: 50/50 split

## Extraction Requirements

Extract the following information from the expense document:

1. **child**: Which child (Jacob, Morgan, or Both)
2. **date**: Purchase/transaction date (YYYY-MM-DD)
3. **vendor**: Store or vendor name
4. **amount**: Total amount spent (include $ and cents, e.g., "$45.99")
5. **category**: Type of expense (see categories below)
6. **description**: Description of items purchased
7. **reimbursable**: Whether this should be split with co-parent ("yes" or "no")
8. **notes**: Any additional relevant information

## Expense Categories

Choose the most appropriate category:

- **School Supplies** - Notebooks, pens, backpacks, etc.
- **School Fees** - Tuition, activity fees, field trips
- **Activities** - Sports, music lessons, dance, clubs
- **Clothing** - Clothes, shoes, outerwear
- **Extracurricular** - Summer camps, special programs
- **Medical** - Over-the-counter medications, medical supplies
- **Childcare** - Daycare, babysitting
- **Birthday** - Birthday party costs
- **Other** - Anything else

## Reimbursement Rules

Set `reimbursable` to:

- **"yes"** if this is a shared expense that should be split 50/50
- **"no"** if this is covered by the parent who made the purchase

Typical reimbursable expenses:
- School supplies and fees
- Extracurricular activities
- Medical expenses (beyond insurance)
- Clothing (depending on agreement)

## Output Format

Respond with a JSON object in this exact format:

```json
{
  "child": "Jacob|Morgan|Both",
  "date": "YYYY-MM-DD",
  "vendor": "Vendor name",
  "amount": "$XX.XX",
  "category": "Category from list above",
  "description": "Description of items",
  "reimbursable": "yes|no",
  "notes": "Additional notes or empty string",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["expense", "category-tag", "child-name"]
}
```

## Clarification Rules

Set `needs_clarification` to `true` if:

1. You cannot determine which child
2. The amount is unclear or illegible
3. The purpose of the expense is ambiguous
4. You're unsure about reimbursability

## Tags Guidelines

Include relevant tags:
- "expense" (always)
- Category in lowercase (e.g., "school-supplies", "activities", "clothing")
- Child name in lowercase (e.g., "jacob", "morgan")
- "reimbursable" or "non-reimbursable"

## Examples

### Example 1: School Supplies

```json
{
  "child": "Morgan",
  "date": "2025-08-15",
  "vendor": "Target",
  "amount": "$45.99",
  "category": "School Supplies",
  "description": "Notebooks, pencils, folders, crayons for school year",
  "reimbursable": "yes",
  "notes": "Start of school year supplies",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["expense", "school-supplies", "morgan", "reimbursable"]
}
```

### Example 2: Soccer Registration

```json
{
  "child": "Jacob",
  "date": "2025-09-01",
  "vendor": "Little League Soccer",
  "amount": "$125.00",
  "category": "Activities",
  "description": "Fall soccer season registration",
  "reimbursable": "yes",
  "notes": "Season runs September-November",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["expense", "activities", "jacob", "reimbursable", "sports"]
}
```

### Example 3: Clothing Purchase

```json
{
  "child": "Both",
  "date": "2025-10-20",
  "vendor": "Old Navy",
  "amount": "$78.50",
  "category": "Clothing",
  "description": "Winter jackets and gloves for both kids",
  "reimbursable": "yes",
  "notes": "Needed for cold weather",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["expense", "clothing", "jacob", "morgan", "reimbursable"]
}
```

### Example 4: Birthday Party

```json
{
  "child": "Morgan",
  "date": "2025-06-15",
  "vendor": "Party City",
  "amount": "$95.00",
  "category": "Birthday",
  "description": "Birthday party supplies and decorations",
  "reimbursable": "no",
  "notes": "Morgan's 8th birthday party",
  "needs_clarification": false,
  "clarification_question": null,
  "tags": ["expense", "birthday", "morgan", "non-reimbursable"]
}
```

Now analyze the expense document and extract the metadata in the JSON format specified above.
