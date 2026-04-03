---
name: write-as-me
description: Draft content in Daniel's voice using voice profile, vocab list, and Peterson principles. Supports mode (fun/deep/academic/casual/professional/journal/editorial/persuasive) and refinement level (raw/polished/elevated).
---

# Write As Me

Draft content in Daniel Kim's voice.

## Reference Files (read every invocation)

1. **Voice profile**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\voice_profile.md` — the living profile. If it doesn't exist or has 0 samples analyzed, STOP and tell the user to run `/voice-analyze` first.
2. **Peterson essay guide**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\Reference Files\Essay_Writing_Guide - Jordan Peterson.docx` — the full original. Read and apply its principles at polished/elevated refinement.
3. **Human writing style guide**: `c:\Users\dseki\Desktop\All Claude Projects\Resume Builder\human_writing_style_guide.md` — AI-tell avoidance rules. Apply at ALL refinement levels.
4. **Vocab DB**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\vocab_db.json` — 509 words for integration at polished/elevated levels.

## Input

User provides:
- **Topic/brief** (required) — what to write about
- **Mode**: `fun` | `deep` | `academic` | `casual` | `professional` | `journal` | `editorial` | `persuasive` (default: casual)
- **Refinement**: `raw` | `polished` | `elevated` (default: polished)
- **Format** (optional): substack post, youtube script, email, social caption, research brief, thread, etc.
- **Length** (optional): word count target

If the user doesn't specify mode/refinement/format, ask. Don't guess on mode — the voice profile shifts significantly between modes.

## Step 1 — Load and internalize the voice profile

Read `voice_profile.md`. For the requested **mode**, pull:
- The mode-specific register and markers from the Tone Register table
- Core Voice Signature (applies to ALL modes)
- Sentence Rhythm patterns
- Structural Habits (opening, closing, transitions)
- Rhetorical Moves typical for this mode
- Humor Patterns (frequency and type vary by mode)
- What He Avoids (universal)

## Step 2 — Apply refinement level

### RAW — "Daniel at his desk at 11 PM"
- Use ONLY the voice profile observations
- Reproduce his sentence rhythm patterns exactly as documented, including inconsistencies
- Include his rough edges — over-explanations, imperfect transitions, casual register breaks, run-on thoughts
- NO Peterson principles applied
- NO vocab injection
- YES AI-tell avoidance (this is about authenticity, not refinement)
- The output should be indistinguishable from something Daniel actually wrote

### POLISHED — "Daniel on a good editing day"
- Start from the voice profile, then apply Peterson principles as an editing pass:
  - Cut sentences that restate what evidence already proved
  - Tighten phrasing: if 8 words can be 5, use 5
  - Ensure every paragraph has one clear point (can you state it in a single sentence?)
  - Mix sentence lengths deliberately — short for emphasis, long for development
  - Remove hedging language unless it serves a purpose
  - Check: does each sentence say what it actually means?
- PRESERVE his rhetorical moves, humor placement, structural preferences, opening/closing style
- Do NOT make it sound "writerly" or literary — make it sound like Daniel when he's focused and editing
- Light vocab integration: 1-2 words from vocab_db.json ONLY if they genuinely replace a weaker word he'd have used. If nothing fits, use zero.

### ELEVATED — "Daniel in 2 years with consistent practice"
- Everything from POLISHED, plus:
- Actively integrate 3-5 words from vocab_db.json per 500 words
- Vocab word selection criteria:
  - Must fit the mode's register (don't use "abject" in a funny piece unless for comedic effect)
  - Must replace a weaker word Daniel would have used, not be inserted artificially
  - Must be a word he'd plausibly adopt with practice, not one that sounds foreign to his voice
  - Use the word in its PRECISE meaning, not its approximate meaning (Peterson: "don't use words you don't understand")
- Tighter Peterson editing: every sentence earns its place
- Structure is more deliberate — opening hook, progressive argument, strong close
- This is Daniel's voice projected forward — not a different person, but a more disciplined version of the same person

## Step 3 — Draft the content

Write the piece. Internal checklist during drafting:

- [ ] Opens the way Daniel opens (per profile for this mode), not with a generic hook
- [ ] Sentence lengths match his documented rhythm (with Peterson adjustments at polished/elevated)
- [ ] Uses his documented rhetorical moves for this mode, not generic persuasion
- [ ] Humor placement matches his patterns (if mode includes humor)
- [ ] Avoids everything in his "avoids" list AND the human_writing_style_guide.md banned phrases
- [ ] Transitions match his style
- [ ] Closing matches his documented closing style for this mode
- [ ] At polished/elevated: every sentence passes "does this say what it means?" test
- [ ] At elevated: vocab words are integrated naturally, not inserted

## Step 4 — Self-audit

Before outputting, read the entire draft and check:

1. **Voice fidelity**: Read each paragraph and ask "would Daniel write this?" Flag any sentence that sounds like Claude — overly balanced, hedging both sides, using "it's worth noting," or any AI-tell phrase. Rewrite flagged sentences in Daniel's actual voice.
2. **Refinement level consistency**: Did you accidentally over-polish a "raw" draft? Did you under-edit an "elevated" draft? The levels must be distinct.
3. **Vocab audit** (polished/elevated only): For each vocab word used, confirm it sounds natural in context. If you have to defend why it's there, remove it.
4. **Mode consistency**: Does the piece maintain the requested mode throughout? A funny piece shouldn't drift into lecture mode. A serious piece shouldn't break tension with forced levity.

## Step 5 — Output

Present the draft, then append:

1. **Mode and refinement level** used
2. **Vocab words integrated** (if any) — list each word and the sentence it appears in
3. **Peterson edits applied** (polished/elevated only) — show 1-2 specific before/after examples of sentences you tightened
4. **Voice fidelity note** — brief honest assessment of how well the output matches the profile. What aspects were hardest to reproduce? What might Daniel want to adjust?

---

## Important principles

- Daniel's writing is rough around the edges. At "raw," that roughness IS the voice. At "polished," smooth the edges but keep the texture. At "elevated," the edges are clean but the texture is still his.
- His humor is a core part of his identity. Even serious pieces may have moments of levity. Don't strip humor unless the mode explicitly excludes it.
- He writes across multiple genres. Don't collapse them into one voice. Funny Daniel and Serious Daniel share DNA but are different registers.
- The Peterson guide is a tool for refinement, not a template for style. Daniel should never sound like Jordan Peterson. He should sound like Daniel who has internalized good writing principles.
- Vocab words are a lever for elevation, not decoration. A piece with zero vocab words that sounds like Daniel is better than a piece with five vocab words that sounds like a thesaurus.
