---
name: voice-analyze
description: Analyze a writing sample and update Daniel's voice profile. Accepts a file path, pasted text, or project folder.
---

# Voice Analyze

Analyze a piece of Daniel Kim's writing and update the voice profile.

## Reference Files (read every invocation)

1. **Voice profile**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\voice_profile.md` — read first. If it doesn't exist, create it from the template at the bottom of this skill.
2. **Peterson essay guide**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\Reference Files\Essay_Writing_Guide - Jordan Peterson.docx` — the full original. Extract the text and reference its principles when identifying gaps.
3. **Human writing style guide**: `c:\Users\dseki\Desktop\All Claude Projects\Resume Builder\human_writing_style_guide.md` — absorb AI-tell avoidance rules into the profile.
4. **Vocab DB**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\vocab_db.json` — check if the sample naturally uses any of these 509 words.
5. **Analysis log**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\analysis_log.md` — append results after analysis.

## Input

User provides one of:
- A file path to a writing sample
- Text pasted directly in the message
- A project folder path (scan for .md, .txt, .docx files containing prose)

## Process

### Step 1 — Load current profile
Read `voice_profile.md`. If this is the first run (file doesn't exist or is the empty template), note that all sections will be populated from scratch.

### Step 2 — Read the sample
Read the provided writing. Identify the apparent **mode**:
- **fun** — humor-forward, entertainment-oriented (memes, short-form, social humor)
- **deep** — think piece, argument-driven, reflective, faith content
- **academic** — formal essays, exegetical papers, structured theological argument
- **casual** — conversational, low-stakes, stream of thought, texts, informal posts
- **professional** — self-evals, business docs, corporate communication
- **journal** — personal reflection, processing, Notion entries, stream of consciousness
- **editorial** — feedback, critique, revision notes, commentary

Note the format (social caption, email draft, essay, script, guide, etc.) and approximate word count.

### Step 3 — Analyze across 12 dimensions

For each dimension, **quote specific examples from the text** (don't just describe — show the evidence):

| # | Dimension | What to measure |
|---|-----------|----------------|
| 1 | **Sentence rhythm** | Measure actual sentence lengths (word count) in 2-3 representative paragraphs. Calculate range, mean, and note the pattern — does he alternate short/long, cluster similar lengths, or vary unpredictably? |
| 2 | **Vocabulary tendencies** | Words/phrases used 2+ times. Unusual or distinctive word choices. Register level (formal/neutral/casual). Any words from vocab_db.json that appear naturally. Crutch words or filler patterns. |
| 3 | **Tone register** | Where on formal-to-casual spectrum. Does it stay consistent or shift within the piece? Where do shifts happen and why? |
| 4 | **Structural habits** | Opening approach (hook type). Section organization (headers? numbered lists? free-flowing?). Paragraph lengths. Closing approach. |
| 5 | **Rhetorical moves** | How does he persuade? Stats/data? Personal experience? Authority citation? Direct address to reader? Analogies? Contrasts? |
| 6 | **Humor patterns** | Types of humor present: irony, self-deprecation, absurdism, exaggeration, deadpan, sarcasm. Where does humor appear — openings, asides, throughout? What triggers it? |
| 7 | **What he avoids** | Note the *absence* of certain constructions, words, or approaches. Compare against AI-tell banned list from human_writing_style_guide.md. |
| 8 | **Openings** | First sentence and first paragraph. Type: question, statistic, direct claim, story, provocation, context-setting, personal anecdote. |
| 9 | **Closings** | Last paragraph. Type: call to action, summary, punchline, open question, callback, trailing thought. |
| 10 | **Transitions** | How he moves between ideas — abrupt jumps, structural (headers/breaks), connective words, thematic threading. Note specific transition words/phrases used. |
| 11 | **Argumentation** | Claim-evidence structure. How he handles counterarguments. Confidence level — does he hedge or assert? How does he handle uncertainty? |
| 12 | **Peterson gaps** | Where would Peterson's principles most improve this specific sample? Reference the actual guide. Focus on: precision of word choice, ruthless editing opportunities, paragraph focus, sentence length variation, hedging vs. asserting, structural organization. |

### Step 4 — Classify each finding

For every observation, mark it:

- **PRESERVE** — Authentically good. This is Daniel's voice working well. Protect this in all refinement levels.
- **REFINE** — Has potential but could be sharper. At "polished" refinement, this gets tightened. The underlying instinct is right; the execution needs work.
- **ROUGH** — Undermines his own goals. Unclear thinking, sloppy construction, or habits that weaken impact. At "polished" and above, these get addressed. Tag which Peterson principle applies.

### Step 5 — Update voice_profile.md

Edit `voice_profile.md`:
- **First analysis**: Populate all sections from scratch based on this single sample. Mark observations as "single-sample" confidence.
- **Subsequent analyses**: Merge new observations with existing ones.
  - Patterns seen across multiple samples: strengthen confidence, note consistency
  - Patterns that contradict previous observations: note the contradiction, investigate if it's mode-specific
  - New patterns not previously documented: add them
  - Never overwrite — accumulate and synthesize
- Update the metadata: sample count, source list, last updated date
- If the sample reveals a new mode not yet in the Tone Register table, add a row

**Per-mode deep profile (critical):** In addition to the cross-mode sections and summary table, populate the **Mode Deep Profiles** section for the detected mode:
- Fill in the mode's subsection under "## Mode Deep Profiles" with specific observations from this sample
- Include: register & humor dial, sentence rhythm differences from baseline, vocabulary register notes, structural patterns, 2-3 quoted examples, and PRESERVE/REFINE items specific to this mode
- If the mode subsection already has content from a prior analysis, merge — don't overwrite. Strengthen confirmed patterns, note contradictions, add new observations.
- The summary table row and the deep profile subsection should be consistent — the table is the quick reference, the subsection is the detail.

### Step 6 — Append to analysis_log.md

Append an entry:
```
## [DATE] — [Source filename or description]
**Mode:** [detected mode]
**Format:** [format type]
**Word count:** ~[count]
**Top 3 findings:**
1. [finding + PRESERVE/REFINE/ROUGH]
2. [finding + PRESERVE/REFINE/ROUGH]
3. [finding + PRESERVE/REFINE/ROUGH]
**New patterns:** [any patterns not previously in the profile, or "none"]
**Vocab words found naturally:** [list, or "none"]
```

### Step 7 — Output summary to user

Print:
1. **Mode detected** and format
2. **3 strongest voice markers** found in this sample (with quoted evidence)
3. **2 most impactful Peterson refinement opportunities** (with before/after example of how a specific sentence could improve)
4. **Vocab words** from vocab_db.json that appeared naturally (if any)
5. **Profile update summary** — what changed in the voice profile

---

## Voice Profile Template

If `voice_profile.md` doesn't exist, create it with this structure:

```markdown
# Daniel Kim — Writing Voice Profile
**Last updated:** [date]
**Samples analyzed:** 0
**Analysis sources:** (none yet)

---

## Core Voice Signature
What makes Daniel sound like Daniel — the non-negotiable characteristics that must be present at every refinement level.

(Populated by /voice-analyze)

## Sentence Rhythm
Cadence patterns, short/long mixing, punctuation habits.

(Populated by /voice-analyze)

## Vocabulary Tendencies
Gravitational words/phrases, register range, technical comfort zones, crutch words.

(Populated by /voice-analyze)

## Tone Register by Mode

| Mode | Register | Humor Dial (0-10) | Key Markers | Samples Analyzed |
|------|----------|-------------------|-------------|-----------------|
| Funny | | | | 0 |
| Serious | | | | 0 |
| Research | | | | 0 |
| Casual | | | | 0 |
| Professional | | | | 0 |
| Editorial | | | | 0 |
| Persuasive | | | | 0 |

## Mode Deep Profiles

(Each mode gets a full subsection populated by /voice-analyze as samples are analyzed. See the live voice_profile.md for the full template structure.)

## Structural Habits
Opening approaches, section organization, paragraph patterns, closing approaches.

(Populated by /voice-analyze)

## Rhetorical Moves
Persuasion patterns, evidence usage, argument construction, appeal balance.

(Populated by /voice-analyze)

## Humor Patterns
Types deployed, frequency, placement, strategic vs. natural.

(Populated by /voice-analyze)

## What He Avoids
Absent constructions, tonal no-go zones, AI-tell words (from human_writing_style_guide.md).

(Populated by /voice-analyze)

---

## Strengths to Preserve
Authentically good patterns that define his voice. These survive all refinement levels.

(Populated by /voice-analyze)

## Rough Edges to Refine
Patterns that undermine his goals. Each tagged with the Peterson principle that addresses it.

| Rough Edge | Peterson Principle | Refinement Direction |
|------------|-------------------|---------------------|
| (Populated by /voice-analyze) | | |

## Vocab Integration Notes
- Words from vocab_db.json that naturally fit his existing patterns
- Words that would stretch his voice productively
- Words to avoid forcing (wrong register)

(Populated by /voice-analyze and refined over time by /write-as-me feedback)
```
