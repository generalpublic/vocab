---
name: write
description: Unified writing orchestrator — sequences mode-detect, write-as-me or coach, and de-slop into one workflow for any writing task.
---

# Write — Unified Orchestrator

Single entry point for any writing task. Sequences the right skills in the right order based on what you need.

## When to trigger

- User says `/write` followed by a brief or topic
- User says "I need to write..." or "help me write..." or "write something about..."

## Reference Files

This skill reads through the sub-skills it invokes. No direct file reads needed — it orchestrates.

## Input

User provides a writing brief. Can be as simple as "Substack post about morning routines" or as detailed as "800-word serious essay on why most productivity advice is garbage, for my Substack audience."

## Process

### Step 1 — Mode Detection

Run the `/mode-detect` logic on the user's brief:
- Extract audience, platform, purpose, topic, stakes
- Recommend mode + humor dial + format + length
- Present the recommendation and **wait for user confirmation** before proceeding

Output to user:
```
**Mode:** [recommendation]
**Humor dial:** [0-10] — [reason]
**Format:** [suggestion]
**Length:** ~[word count]

Does this feel right, or do you want to adjust?
```

Do not proceed until the user confirms or adjusts.

### Step 2 — Draft or Coach?

Ask the user:
```
Two paths:
1. **You draft** — write it yourself, then I'll run /coach to review and push you to improve
2. **I draft** — I'll write it in your voice via /write-as-me, then we'll clean it up

Which one?
```

If the user says "just write it" or "you do it" → path 2 (write-as-me).
If the user says "I'll write it" or provides a draft → path 1 (coach).
If the user says "give me a starting point" → path 2 at raw refinement, then user edits, then coach.

### Step 3a — User drafts (Coach path)

1. User writes their draft (or pastes it)
2. Run `/coach` on the draft with the confirmed mode
3. Present coaching feedback
4. User revises based on feedback (optional second round of coaching)
5. Proceed to Step 4

### Step 3b — AI drafts (Write-as-me path)

1. Ask refinement level: `raw`, `polished`, or `elevated`
   - Default to `polished` if user doesn't specify
2. Run `/write-as-me` with the confirmed mode + refinement + format + length
3. Present the draft
4. User can request revisions or accept
5. Proceed to Step 4

### Step 4 — De-slop Audit

Run `/de-slop` on the final draft — **regardless of which path produced it.**

- Even /write-as-me output gets audited. Defense in depth.
- Even user-written drafts get checked for unconscious AI patterns (especially if user uses AI tools elsewhere).
- If slop score is 0-2: note it's clean, move on.
- If slop score is 3+: present the flags and offer to clean them up.

### Step 5 — Final Output

Present the finished piece with:

```
## Final Draft — [mode] mode, [humor dial]/10 humor

[The draft text]

---

**Stats:**
- Word count: ~[count]
- Slop score: [X] flags ([Clean/Suspicious/etc.])
- Vocab words used: [list, or "none"]
- Refinement level: [raw/polished/elevated, or "user-drafted"]

**Vocab opportunities:** [1-3 places where a vocab word could naturally replace a weaker word, if any — don't force it]
```

### Step 6 — Log (if writing_log.json exists)

Append to `c:\Users\dseki\Desktop\All Claude Projects\Vocab\writing_log.json`:
```json
{
  "date": "[today]",
  "mode": "[mode]",
  "humor_dial": [0-10],
  "format": "[format]",
  "word_count": [count],
  "path": "[coach or write-as-me]",
  "refinement": "[level or user-drafted]",
  "slop_score": [flags],
  "vocab_used": ["word1", "word2"],
  "topic": "[brief summary]"
}
```

If the file doesn't exist, create it as an array `[]` and add the first entry.

### Step 6b — Auto-log vocab usage

For each word in `vocab_used` from the entry above, also append to `c:\Users\dseki\Desktop\All Claude Projects\Vocab\usage_log.json`:

```json
{
  "WordName": [
    {"date": "[today]", "where": "/write — [topic]"}
  ]
}
```

If the word already has entries, append to its array. If not, create a new key. This closes the loop between writing and usage tracking — no manual `vocab used <word>` needed.

## Flow Summary

```
Brief → Mode-detect → Confirm → Draft (coach or write-as-me) → De-slop → Final → Log
```

No duplicated logic. Each step uses the existing skill's full capability.
