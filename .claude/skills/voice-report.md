---
name: voice-report
description: Generate or update a comprehensive Writing Voice Analysis report. Reads the current voice profile, optionally analyzes new writing samples, and exports a dated report to the Writing Profile Analysis folder.
---

# Voice Report

Generate a comprehensive, publication-ready Writing Voice Analysis document based on the current voice profile. Optionally incorporate new writing samples before generating.

## When to trigger

- User says `/voice-report`
- User asks for an updated writing analysis or voice profile report
- User provides new writing samples and wants the profile updated + a new report

## Reference Files (read every invocation)

1. **Voice profile**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\voice_profile.md` — the living profile. Primary source for the report.
2. **Analysis log**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\analysis_log.md` — history of what's been analyzed.
3. **Previous reports**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\Writing Profile Analysis\` — check for existing reports to understand format evolution.
4. **Vocab DB**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\vocab_db.json` — for vocab integration findings.
5. **Peterson essay guide**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\Reference Files\Essay_Writing_Guide - Jordan Peterson.docx` — for Peterson gap analysis.

## Input

User may provide:
- **No input** → Generate report from current voice profile as-is
- **New writing samples** (file paths or pasted text) → Run `/voice-analyze` on each sample first, update the profile, THEN generate the report
- **Specific focus** → "Focus on journal voice evolution" or "Compare my academic vs journal writing"

## Process

### Step 1 — Check for new samples

If the user provided new writing samples:
1. Run `/voice-analyze` on each sample (this updates voice_profile.md and analysis_log.md)
2. Re-read the updated voice_profile.md before proceeding

If no new samples, proceed with the current profile.

### Step 2 — Read the current voice profile

Read `voice_profile.md` thoroughly. This is the source of truth for all findings.

### Step 3 — Generate the report

Write a comprehensive Writing Voice Analysis document in markdown with the following structure:

```
# Daniel Kim — Writing Voice Analysis
## [Month Year]

### Corpus Summary
- Total samples analyzed: [count]
- Sources: [list]
- Modes covered: [list with sample counts]
- Total word count analyzed: ~[count]
- Date range: [earliest] to [latest]

### Overall Description
[2-3 paragraphs synthesizing who Daniel is as a writer across all modes. Pull from Core Voice Signature in the profile. This should read as a compelling portrait, not a list.]

### Cross-Cutting DNA
[The traits that appear in EVERY mode. Pull from Core Voice Signature. Each trait gets its own paragraph with quoted evidence.]

### Mode-by-Mode Analysis

#### Academic Writing
[Full analysis from the profile's Academic Mode deep profile. Include: sentence rhythm, vocabulary, tone, structure, rhetorical moves, Peterson gaps, vocab DB words found. Quote specific examples.]

#### Professional Writing
[Same structure as above, from Professional Mode deep profile.]

#### Journal Writing
[The most extensive section. Include the 15-year trajectory, the four sub-registers, the strongest passages, the humor patterns, the full PRESERVE/REFINE/ROUGH classification. This should be the heart of the document.]

[Add sections for any other modes that have been analyzed (Funny, Serious, Casual, etc.)]

### 15-Year Voice Trajectory
[Chronological arc from earliest writing to most recent. Year-by-year or era-by-era. Include quoted examples showing the evolution. This is unique to Daniel — most people don't have 15 years of writing to trace.]

### Strongest Passages
[Top 10 passages across the entire corpus, with the text quoted and a brief explanation of why each works.]

### Strengths to Preserve
[Numbered list with brief explanations. Pull from the profile.]

### Rough Edges to Refine
[Table format: Rough Edge | Where | Peterson Principle | Refinement Direction]

### Vocabulary Profile
[Natural vocabulary he already uses from vocab_db.json. Words that would stretch him productively. Words to avoid forcing. Register alignment notes.]

### Summary
[1-2 paragraph closing synthesis. What makes Daniel's writing distinctive. Where he's strongest. Where the biggest growth opportunities are.]
```

### Step 4 — Save as markdown

Save the report as:
`c:\Users\dseki\Desktop\All Claude Projects\Vocab\Writing Profile Analysis\Daniel_Kim_Writing_Voice_Analysis_[YYYY-MM-DD].md`

### Step 5 — Export to .docx

Use Python with the `python-docx` library to convert the markdown report to a properly formatted .docx file:
`c:\Users\dseki\Desktop\All Claude Projects\Vocab\Writing Profile Analysis\Daniel_Kim_Writing_Voice_Analysis_[YYYY-MM-DD].docx`

If `python-docx` is not installed, install it first (`pip install python-docx`).

The .docx should have:
- Title page: "Daniel Kim / Writing Voice Analysis / [Month Year]"
- Proper heading hierarchy (H1, H2, H3)
- Block quotes for quoted examples (indented, italic)
- Tables for the Rough Edges section
- Clean body font (Calibri or similar)

### Step 6 — Update the analysis log

Append to `analysis_log.md`:
```
## [DATE] — Voice Report Generated
**Report:** Daniel_Kim_Writing_Voice_Analysis_[YYYY-MM-DD].docx
**Corpus at time of report:** [sample count] samples, ~[word count] words
**Modes covered:** [list]
**New samples since last report:** [list, or "none — generated from existing profile"]
```

### Step 7 — Output to user

Tell the user:
- Report saved to [path]
- .docx exported to [path]
- What's new since the last report (if applicable)
- Any modes still empty that would improve future reports

## Notes

- Each report is a snapshot in time. Don't delete previous reports — they form a chronological record of profile evolution.
- The date in the filename ensures uniqueness and traceability.
- If the user asks to "update the analysis," this means: check for new samples, run /voice-analyze if needed, then generate a fresh report. Don't just re-export the old one.
