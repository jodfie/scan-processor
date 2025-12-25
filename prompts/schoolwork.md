# Schoolwork Document Metadata Extraction

You are extracting metadata from a schoolwork document for a co-parenting system. The document has already been classified as SCHOOLWORK.

## Children Information

- **Jacob** (born 2019) - Currently in kindergarten/1st grade
- **Morgan** (born 2017) - Currently in 2nd/3rd grade
- Co-parent: Stephanie

## Extraction Requirements

Extract the following information from the schoolwork document:

1. **child**: Which child (Jacob or Morgan)
2. **subject**: Subject area (Math, Reading, Science, Social Studies, Art, etc.)
3. **type**: Type of work (see types below)
4. **grade**: Grade/score received (if visible, e.g., "A+", "95%", "Excellent")
5. **date**: Date on document or completion date (YYYY-MM-DD)
6. **title**: Title or description of the work
7. **teacher**: Teacher name (if visible)
8. **notes**: Any additional notes

## Schoolwork Types

Choose the most appropriate type:

- **Homework** - Daily homework assignments
- **Test** - Tests and quizzes
- **Project** - Class projects
- **Report Card** - Progress reports and report cards
- **Artwork** - Art projects and drawings
- **Writing** - Creative writing, essays
- **Worksheet** - Completed worksheets
- **Certificate** - Awards and certificates
- **Progress Report** - Academic progress updates
- **Other** - Anything else

## Output Format

Respond with a JSON object in this exact format:

```json
{
  "child": "Jacob|Morgan",
  "subject": "Subject name",
  "type": "Type from list above",
  "grade": "Grade/score or null",
  "date": "YYYY-MM-DD or null",
  "title": "Work title or description",
  "teacher": "Teacher name or null",
  "notes": "Additional notes or empty string",
  "tags": ["schoolwork", "subject-tag", "child-name"]
}
```

## Tags Guidelines

Include relevant tags:
- "schoolwork" (always)
- Subject in lowercase (e.g., "math", "reading", "science", "art")
- Type in lowercase (e.g., "homework", "test", "project")
- Child name in lowercase (e.g., "jacob", "morgan")
- Grade level if apparent (e.g., "grade-1", "grade-2")
- Special achievements (e.g., "honor-roll", "award", "perfect-score")

## No Clarification Needed

For schoolwork, we generally don't need clarification. Just extract what you can from the document. If the child cannot be determined, try to infer from:
- Age-appropriate content
- Grade level
- Handwriting maturity
- Teacher name (if you know which child has which teacher)

## Examples

### Example 1: Math Homework

```json
{
  "child": "Jacob",
  "subject": "Math",
  "type": "Homework",
  "grade": "100%",
  "date": "2025-12-10",
  "title": "Addition and Subtraction Practice",
  "teacher": "Mrs. Johnson",
  "notes": "Excellent work! All problems correct.",
  "tags": ["schoolwork", "math", "homework", "jacob", "grade-1", "perfect-score"]
}
```

### Example 2: Report Card

```json
{
  "child": "Morgan",
  "subject": "All Subjects",
  "type": "Report Card",
  "grade": null,
  "date": "2025-11-15",
  "title": "Q2 Report Card - 3rd Grade",
  "teacher": "Mr. Williams",
  "notes": "Excellent progress in all areas. Honor roll.",
  "tags": ["schoolwork", "report-card", "morgan", "grade-3", "honor-roll"]
}
```

### Example 3: Science Project

```json
{
  "child": "Morgan",
  "subject": "Science",
  "type": "Project",
  "grade": "A",
  "date": "2025-10-28",
  "title": "Volcano Model - How Volcanoes Erupt",
  "teacher": "Mr. Williams",
  "notes": "Creative project with detailed explanation",
  "tags": ["schoolwork", "science", "project", "morgan", "grade-3"]
}
```

### Example 4: Artwork

```json
{
  "child": "Jacob",
  "subject": "Art",
  "type": "Artwork",
  "grade": null,
  "date": "2025-12-05",
  "title": "Family Portrait Drawing",
  "teacher": "Ms. Davis",
  "notes": "Beautiful colors and detail",
  "tags": ["schoolwork", "art", "jacob", "grade-1", "artwork"]
}
```

### Example 5: Spelling Test

```json
{
  "child": "Jacob",
  "subject": "Reading/Spelling",
  "type": "Test",
  "grade": "18/20",
  "date": "2025-12-12",
  "title": "Weekly Spelling Test",
  "teacher": "Mrs. Johnson",
  "notes": "Good improvement from last week",
  "tags": ["schoolwork", "reading", "spelling", "test", "jacob", "grade-1"]
}
```

Now analyze the schoolwork document and extract the metadata in the JSON format specified above.
