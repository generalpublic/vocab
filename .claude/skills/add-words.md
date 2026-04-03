---
name: add-words
description: Add and fully enrich new vocabulary words. Triggers when user lists words to add to the vocab database.
---

# Add Words — Enriched Vocabulary Addition

Add one or more words to `vocab_db.json` with full enrichment in a single step.

## When to trigger

- User says `/add-words` followed by a list of words
- User says "add these words" or "new words:" followed by a list
- User lists words separated by spaces, commas, or newlines with clear intent to add them to vocab

## Reference Files

- **Database:** `c:\Users\dseki\Desktop\All Claude Projects\Vocab\vocab_db.json`
- **Schema reference:** Use any existing enriched entry as the template (all 509 current words are enriched)

## Process

### Step 1 — Parse and Deduplicate

1. Read `vocab_db.json`
2. Extract all words from the user's input (handle spaces, commas, newlines, numbered lists)
3. For each word, check if it already exists in the database (case-insensitive)
4. Report duplicates immediately: `"⊘ Skipped: [word] — already exists"`

### Step 2 — Enrich Each New Word

For each new word, generate a complete entry matching this exact schema:

```json
{
  "word": "Wordname",
  "pos": ["noun"],
  "pronunciation": "WORD-name",
  "definition": "clear, precise definition covering primary senses",
  "register": ["formal", "literary"],
  "tags": ["category1", "category2"],
  "enriched": true,
  "examples": [
    {
      "context": "essay",
      "sentence": "Example sentence using the word correctly.",
      "why": "Explanation of why this usage is correct and precise."
    },
    {
      "context": "social media",
      "sentence": "...",
      "why": "..."
    },
    {
      "context": "professional",
      "sentence": "...",
      "why": "..."
    }
  ],
  "misuses": [
    {
      "wrong": "Incorrect usage sentence.",
      "problem": "Why this is wrong.",
      "use_instead": "better word choices"
    },
    {
      "wrong": "...",
      "problem": "...",
      "use_instead": "..."
    }
  ],
  "related": [
    {
      "word": "RelatedWord",
      "distinction": "How it differs from the target word."
    },
    {
      "word": "...",
      "distinction": "..."
    }
  ],
  "triggers": [
    "When/why to reach for this word — situation 1",
    "When/why to reach for this word — situation 2"
  ],
  "synonyms": [
    "drop-in replacement word 1",
    "drop-in replacement word 2"
  ],
  "date_added": "YYYY-MM-DD"
}
```

**Enrichment rules:**
- `pos`: Use full names — "noun", "verb", "adjective", "adverb". Multiple if applicable.
- `pronunciation`: ALL-CAPS syllable stress format (e.g., "eh-FEM-er-ul")
- `definition`: Precise, covering primary senses. Not a dictionary dump — write it for someone who needs to use it correctly.
- `register`: Choose from: formal, informal, literary, technical, academic, colloquial, neutral, slang
- `tags`: 2-4 semantic categories (e.g., "emotion", "time", "power", "cognition")
- `examples`: Minimum 3, across different contexts (essay, social media, professional, creative writing, casual). Each must include `why` explaining the precision of usage.
- `misuses`: Minimum 2. Show common ways people use the word wrong. Include `use_instead` alternatives.
- `related`: Minimum 2. Show words that are close but distinct. The `distinction` field is critical — explain the difference.
- `triggers`: Minimum 2. Describe the situations where this word is the right choice.
- `synonyms`: 2-4 true drop-in replacements — words you could swap into a sentence without changing meaning. NOT associative concepts (those are tags) or near-synonyms with important distinctions (those are related). These must be interchangeable.
- `date_added`: Today's date in ISO format.

### Step 3 — Insert and Save

1. Insert each new entry alphabetically into the `words` array
2. Update `meta.word_count` to the new total
3. Update `meta.last_updated` to today's date
4. Write the full database back to `vocab_db.json`

### Step 4 — Summary

Print a summary:
```
✓ Added [N] words: Word1, Word2, Word3
  Total: [count] words (all enriched)

⊘ Skipped [N] duplicates: Word4, Word5
```

## Quality Standards

- Every example sentence must sound like something a real person would write — not a textbook
- Misuses must be mistakes real people actually make, not strawmen
- Triggers should help the user recognize situations where the word fits — not just restate the definition
- Related words must include meaningful distinctions, not just "similar meaning"
- Match the tone and quality of existing enriched entries in the database
