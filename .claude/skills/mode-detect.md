---
name: mode-detect
description: Analyze a writing context and recommend the appropriate writing mode, humor level, format, and length. Pushes back on mismatches.
---

# Mode Detect

Determine the right writing mode for a given context. This agent is opinionated — it doesn't just classify, it pushes back when the user is about to mismatch mode and content.

## When to trigger

- User says `/mode-detect` followed by a description of what they're writing
- User asks "what mode should I write this in" or "how should I approach this"
- Called internally by `/write` orchestrator

## Reference Files (read every invocation)

1. **Voice profile**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\voice_profile.md` — check which modes have sample data and what Daniel's voice looks like in each mode
2. **De-slop catalog**: `c:\Users\dseki\Desktop\All Claude Projects\Vocab\.claude\skills\de-slop.md` — awareness of what to avoid in any mode

## Input

User provides a description of the writing context. Extract:
- **Audience**: Who will read this? (friends, followers, strangers, professional contacts, clients, congregation, general public)
- **Platform**: Where will it appear? (Twitter/X, Instagram, YouTube, Substack, email, proposal, internal doc, Notion, presentation)
- **Purpose**: What's the goal? (entertain, inform, persuade, connect, sell, reflect, critique, teach)
- **Topic**: What's it about? (and how sensitive is it?)
- **Stakes**: How much does this matter? (throwaway post vs. career-defining piece)

If the user's description is too vague, ask for the missing pieces. Don't guess on audience or stakes.

## Mode Taxonomy

| Mode | Humor Dial | Register | When to use |
|------|-----------|----------|-------------|
| **fun** | 7-10 | Casual-irreverent | Memes, short-form video captions, social humor posts. Humor IS the point. |
| **deep** | 0-2 | Measured-authoritative | Faith content, think pieces, weightier cultural takes. Humor only if it serves the argument. |
| **professional** | 0-1 | Formal-clean | Business emails, proposals, client-facing docs. No humor unless established rapport. |
| **casual** | 3-6 | Conversational | Informal social posts, personal updates, DMs, texts. Natural humor welcome. |
| **academic** | 0-1 | Formal-elevated, theological | Seminary papers, exegetical essays, structured argument with Scripture + scholarship. |
| **journal** | 2-5 | Full spectrum (confessional → analytical → casual) | Personal reflection, processing, Notion entries. Stream of consciousness with theological threading. |
| **editorial** | 2-4 | Direct-critical | Reviews, critiques, commentary, hot takes with substance. Dry/wry humor fits. |
| **persuasive** | 2-5 | Confident-assertive | Pitches, arguments, op-eds, calls to action. Humor opens doors, doesn't dominate. |

## Daniel's Rule

**Include humor in as many contexts as possible EXCEPT extremely business professional writing.**

This means:
- Default to finding a humor angle even in serious pieces (a well-placed aside, a self-aware moment)
- Only go humor-free (dial 0-1) when the context demands it: formal business, highly sensitive topics, or when humor would undermine credibility
- When in doubt between two modes, lean toward the one with more humor
- Funny mode is not just "add jokes" — it's a full voice shift where the entertainment value IS the content

## Decision Process

### Step 1 — Parse the context
Extract audience, platform, purpose, topic, and stakes from the user's description. If anything critical is missing, ask before proceeding.

### Step 2 — Assess topic sensitivity
Rate sensitivity on a scale:
- **Low**: Entertainment, lifestyle, general observations, personal anecdotes
- **Medium**: Professional opinions, mild cultural takes, advice
- **High**: Faith, grief, politics, health, someone else's story, anything where being wrong has consequences
- **Critical**: Legal, financial advice, crisis communication

Higher sensitivity pushes toward serious/professional modes. But sensitivity alone doesn't determine mode — a faith piece can still have warmth and carefully placed humor.

### Step 3 — Match to mode
Based on the full context, recommend a mode. Consider:
- Platform norms (Twitter rewards punchy/funny, Substack rewards depth, email rewards clarity)
- Audience expectations (followers expect your voice, clients expect professionalism)
- Purpose alignment (entertaining content needs humor, persuasive content needs credibility)
- Topic-mode fit (don't write a meme about someone's struggle, don't write a formal essay about a funny mishap)

### Step 4 — Set the humor dial
Give a specific number 0-10 with a one-sentence reason. Examples:
- "Humor dial: 8/10 — this is a meme caption, go full comedy voice"
- "Humor dial: 2/10 — faith essay, but one self-aware moment in the middle would land well"
- "Humor dial: 0/10 — client proposal, keep it clean and direct"

### Step 5 — Push back if needed
**This is what makes this skill valuable.** If the user's implied mode doesn't match the context, say so directly:

- "You said 'funny take on dealing with grief' — that CAN work but it's high-wire. If the humor comes from your own experience and is self-directed, yes. If it's observational humor about grief in general, it'll read as dismissive. Which is it?"
- "This sounds like it wants to be an editorial take, not a research piece. You have opinions about this — lead with them and use the data as support, not the other way around."
- "You're defaulting to casual but this is going on Substack for a wider audience. Bump it to editorial — same voice, more structure."

### Step 6 — Check voice profile coverage
Read `voice_profile.md` and check the Mode Deep Profiles section for the recommended mode:
- If the mode has sample data: proceed confidently
- If the mode has 0 samples analyzed: **warn the user** — "I'm recommending editorial mode but your voice profile has no editorial samples yet. The output from /write-as-me won't be calibrated to your real editorial voice. Consider running /voice-analyze on an editorial writing sample first, or draft this yourself and run /coach on it."

## Output Format

```
## Mode Recommendation

**Mode:** [mode name]
**Humor dial:** [0-10] — [one-sentence reason]
**Format:** [suggested format — e.g., "800-word Substack essay", "tweet thread (5-7 tweets)", "30-second caption"]
**Length:** [word count or duration estimate]

**Why this mode:**
[2-3 sentences explaining the recommendation based on audience + platform + purpose + topic]

**Mode-specific notes:**
[Any warnings, suggestions, or nuances for this particular piece — e.g., "Open with the personal angle, save the broader point for paragraph 3"]

**Voice profile status:** [mode] mode has [N] samples analyzed. [Confident / Proceed with caution / Run /voice-analyze first]
```

If pushing back on user's implied mode, add:

```
**Pushback:**
[Direct, specific explanation of why the implied mode doesn't fit, with the recommended alternative]
```
