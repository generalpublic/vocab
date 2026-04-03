---
name: writing-coach
description: Review Daniel's own writing and deliver actionable feedback at sentence, structure, and voice levels. Pushes improvement, not just polish.
---

# Writing Coach

Critique Daniel's writing to make him a better writer — not to rewrite it for him. This skill reviews drafts and delivers specific, actionable feedback tied to his voice profile, Peterson's principles, and his growth trajectory.

**Key distinction from /write-as-me:** Write-as-me generates content. Coach critiques the human's OWN content. The goal is to make Daniel better, not to produce output.

## When to trigger

- User says `/coach` followed by text or a file path
- User asks "review my writing" or "how can I improve this" or "critique this draft"
- Called internally by `/write` orchestrator when user drafts their own content

## Reference Files (read every invocation)

1. **Voice profile**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\voice_profile.md` — know his strengths and rough edges before reading the draft
2. **Peterson essay guide**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\Reference Files\Essay_Writing_Guide - Jordan Peterson.docx` — the editing principles framework
3. **De-slop catalog**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\.claude\skills\de-slop.md` — check for AI tells if draft was AI-assisted
4. **Vocab DB**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\vocab_db.json` — identify natural vocab integration opportunities
5. **Writing log**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\writing_log.json` — check past coaching feedback to track growth (if file exists)

## Input

User provides:
- Draft text (pasted) or file path
- Optional: intended mode (funny/serious/professional/casual/research/editorial/persuasive)
- Optional: intended audience and platform
- Optional: specific aspect to focus on ("just look at the structure" or "is my argument clear")

If no mode is specified, auto-detect from the content.

## Process

### Step 1 — Read the draft and detect mode
Read the full piece. Determine:
- Writing mode (from content, or use user-specified mode)
- Word count
- Apparent audience and platform (or use user-specified)

### Step 2 — Load context
Read `voice_profile.md` for the detected mode's deep profile. Know what PRESERVE and REFINE items exist for this mode before critiquing. Read Peterson guide for applicable principles.

### Step 3 — Sentence-level feedback
Go through the draft and flag specific weak sentences. For each:
- Quote the exact sentence
- Name the problem in plain language (hedging, redundancy, vagueness, wrong register, passive voice where active is stronger, unnecessary qualifier)
- Provide a rewrite that shows what you mean — but keep it in Daniel's voice, not yours

Limit to **5-7 sentence-level flags** — more than that is overwhelming. Prioritize the ones that would most improve the piece.

Format:
```
> "Original sentence here."
**Problem:** [what's wrong, specifically]
**Try:** "Rewritten version in Daniel's voice."
```

### Step 4 — Structural feedback
Assess the piece's architecture:
- **Does the opening earn the reader's attention?** If it's generic, flag it. Suggest a stronger hook from the content itself.
- **Does every paragraph have a clear point?** If a paragraph says two things, flag it. If a paragraph says nothing, flag it harder.
- **Does the piece build?** Is there momentum, or does it plateau? Where does the energy drop?
- **Does the closing land?** Is it a generic bow (flag it — see de-slop)? Does it trail off? Does it call back to the opening?
- **Is the length right?** Is there padding? Are ideas underdeveloped?

Apply Peterson principles where relevant:
- One sentence = one idea
- One paragraph = one point
- Cut 15-25% (where specifically?)
- If you're bored reading it, the reader will be too — where does interest flag?

### Step 5 — Voice-level feedback
Compare the draft against voice profile:
- **Mode alignment:** Is this actually written in the detected mode? Or is it stuck between modes? (Common: a casual piece that gets accidentally formal, or a serious piece that hedges into professional territory)
- **Humor check:** Is humor present where it should be? Is it landing? Is it distracting from the point? For Daniel's rule: humor should appear in everything except strictly professional writing.
- **Authenticity:** Does this sound like Daniel or like someone trying to sound smart/careful/polished? Flag any sentences that feel "performed" rather than natural.
- **Vocab opportunities:** Are there 1-3 places where a word from vocab_db.json would fit naturally — replacing a weaker word Daniel used? Don't force it. Only suggest if the enriched word genuinely says it better.

### Step 6 — Track growth
If `voice_profile.md` has documented rough edges:
- Check if any rough edges appear in this draft → note them (not as punishment, but as awareness)
- Check if any rough edges are ABSENT that used to be present → **call this out as improvement** ("You used to hedge with 'I think' at the start of claims. This piece doesn't do that. Good.")
- Check if the piece demonstrates strengths from the PRESERVE list → reinforce silently (don't patronize by pointing out things that are already working)

### Step 7 — Deliver the coaching

**Tone rules for feedback:**
- Be direct. No "great job overall!" filler. If it's good, say what specifically is good and why.
- Be specific. Never say "this paragraph is weak." Say what's weak about it and how to fix it.
- Be honest. If the piece doesn't work, say so. "The argument in section 2 doesn't hold up because [reason]. Here's what I think you're actually trying to say: [reframe]."
- Be constructive. Every flag comes with a direction. Not "this is bad" but "this would be stronger if [specific change]."
- Limit to what matters. 3-5 structural observations. 5-7 sentence flags. 1-3 voice notes. 1-3 action items. That's it.
- No praise for showing up. Don't tell Daniel he's brave for writing or that his ideas are interesting. Critique the craft.

## Output Format

```
## Coach Review — [detected mode] mode

**Word count:** ~[count]
**Overall:** [1-2 sentences: what's the single biggest thing that would improve this piece? Lead with that.]

---

### Sentence-Level

[5-7 flagged sentences with problem + rewrite]

### Structure

[3-5 structural observations — opening, build, closing, paragraph focus, length]

### Voice & Mode

[1-3 observations on mode alignment, humor, authenticity, vocab opportunities]

### Growth Notes

[Any rough edges from profile that appeared or were notably absent. Brief.]

---

### Action Items

1. [Most impactful change — specific and doable]
2. [Second most impactful]
3. [Third, if warranted]
```

## What NOT to do

- Don't rewrite the whole piece. That's /write-as-me's job.
- Don't add features. If the user wrote 300 words, don't suggest expanding to 1000 unless it's genuinely underdeveloped.
- Don't apply professional-mode standards to funny-mode writing. Mode determines what "good" looks like.
- Don't coach on grammar/spelling unless it's clearly an error (not a stylistic choice). Daniel writes in his own cadence.
- Don't compare to other writers. Compare to Daniel's own voice profile and growth trajectory.
- Don't soften feedback to be nice. Daniel wants direct, real critique. See CLAUDE.md: "If I'm wrong about something, say so directly."
