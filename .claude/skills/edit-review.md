---
name: edit-review
description: Typo and error review for journal entries. Catches misspellings, wrong words, missing words, doubled words — preserves voice and proper nouns.
---

# Edit Review — Journal Entry Proofreader

Catch typos and mechanical errors in journal entries without touching voice, tone, or style.

## When to trigger

- User says `/edit-review` followed by a file path or entry text
- After journal entries are finalized/imported into the system
- Automatically as the last step of any journal extraction or import workflow

## What to fix

1. **Misspellings** — "mentality" when "mentally" was meant, "incidences" vs "incidents"
2. **Wrong word** — "then" vs "than", "it's" vs "its", "form" vs "from", "the" vs "he"
3. **Missing words** — "not to afraid" → "not to be afraid"
4. **Extra/doubled words** — "don't don't", "you were you made"
5. **Verb form errors** — "witnessing" when "witnessed" was meant, "disobeys" vs "disobeyed"
6. **Compound word splits** — "part take" → "partake", "back in to" → "back into", "pay check" → "paycheck"

## What to leave alone

- **Proper nouns** — names of people, places, churches, brands, apps (Jiwon, TJ, Vivian, Moody, Talbot, etc.)
- **Intentional informal style** — lowercase "i", "lol", "cause" (for because), "gonna", "goin", slang, sentence fragments
- **Casual grammar** — run-on sentences, missing commas, stream-of-consciousness structure
- **Scripture quotes** — do not modify quoted Bible verses
- **Summarized/bracketed content** — text in `[brackets]` is editorial summary, not original writing
- **Words that feel like they could be names** — if unsure whether something is a typo or a proper noun, leave it

## Process

### Step 1 — Read the entries

Read the full file or text provided. Note entry boundaries (## headers).

### Step 2 — Scan each entry

For each entry, identify all typos per the categories above. Build a list:
```
Entry [#]: [title]
- "[old text]" → "[new text]" (reason)
```

### Step 3 — Present findings

Show the user the full list of proposed fixes grouped by entry. Wait for confirmation before applying.

Format:
```
## Edit Review — [filename]

Found [N] typos across [M] entries.

### Entry [#]: [title]
1. "[old]" → "[new]" — [brief reason]
2. ...

### Entry [#]: [title]
1. ...

Apply all? Or review individually?
```

### Step 4 — Apply fixes

On user confirmation, apply all edits. If user wants to review individually, walk through each one.

### Step 5 — Confirm

After applying, report:
```
Done. [N] fixes applied across [M] entries. [X] entries were clean.
```

## Integration

This skill should be invoked as the final step whenever:
- New journal entries are extracted from Notion/OneNote/Day One
- Entries are imported or appended to `journal_entries_chronological.md` or `2025_glory_journal_full.md`
- User manually requests a proofread pass
