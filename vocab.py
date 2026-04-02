#!/usr/bin/env python3
"""
Vocabulary Mastery System — unified CLI.

Usage:
    python vocab.py search <term>
    python vocab.py define <word>
    python vocab.py browse [--register <reg>] [--tag <tag>]
    python vocab.py random
    python vocab.py stats
    python vocab.py quiz
    python vocab.py flash [-n N] [--weak] [--new] [--word <word>]
    python vocab.py daily [-n N] [--style <style>]
    python vocab.py wotd
    python vocab.py used <word> [--where <context>]
    python vocab.py progress
    python vocab.py suggest [--mode <mode>]
    python vocab.py review
    python vocab.py challenge [--mode <mode>]
    python vocab.py writing-progress
"""
import argparse
import json
import random
import sys
import textwrap
import subprocess
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import os
import shutil
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).parent
DB_PATH = BASE / "vocab_db.json"
FLASH_PATH = BASE / "flashcard_progress.json"
PROMPTS_PATH = BASE / "prompts_log.json"
USAGE_PATH = BASE / "usage_log.json"
VOICE_PROFILE_PATH = BASE / "voice_profile.md"
WRITING_LOG_PATH = BASE / "writing_log.json"
NAS_VOCAB_DIR = Path("Z:/Claude Projects/Vocab")

# ─── helpers ────────────────────────────────────────────────────────────────

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    db["meta"]["last_updated"] = str(date.today())
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def sync_to_nas():
    """Copy vocab_db.json and prompts_log.json to NAS for cross-project access."""
    if not NAS_VOCAB_DIR.exists():
        return  # NAS unreachable, skip silently
    for src in [DB_PATH, PROMPTS_PATH]:
        if src.exists():
            shutil.copy2(src, NAS_VOCAB_DIR / src.name)

def load_json(path, default=None):
    if default is None:
        default = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def wrap(text, indent=4, width=72):
    prefix = " " * indent
    return textwrap.fill(text, width=width, initial_indent=prefix, subsequent_indent=prefix)

def divider(char="─", width=50):
    return char * width


def get_active_version():
    db = load_db()
    return db["meta"].get("active_version", 1)

def filter_by_version(words, version=None):
    """Filter words by version number. None = all versions."""
    if version is None:
        return words
    return [w for w in words if w.get("version", 1) == version]

def smart_select(words, n, flash_data=None, usage_data=None, prompts_log=None, register_filter=None):
    """Select words prioritizing weak, due, unused, and stale words over random."""
    if flash_data is None:
        flash_data = load_json(FLASH_PATH)
    if usage_data is None:
        usage_data = load_json(USAGE_PATH)
    if prompts_log is None:
        prompts_log = load_json(PROMPTS_PATH, default=[])

    # optional register filter
    if register_filter:
        filtered = [w for w in words if any(r in register_filter for r in w.get("register", []))]
        if len(filtered) >= n:
            words = filtered

    today = str(date.today())

    # build prompted-dates map
    prompted_dates = {}
    for entry in (prompts_log if isinstance(prompts_log, list) else []):
        for wname in entry.get("words", []):
            prompted_dates[wname] = entry["date"]

    scored = []
    for w in words:
        name = w["word"]
        score = 0.0

        # flashcard signals
        if name not in flash_data:
            score += 3  # never drilled
        else:
            fd = flash_data[name]
            avg = fd.get("avg_score", 3)
            if avg <= 2:
                score += 4  # weak
            elif avg <= 3:
                score += 1  # mediocre
            if fd.get("next_due", "2099-01-01") <= today:
                score += 2  # overdue

        # never used in real writing
        if name not in usage_data:
            score += 2

        # staleness — not recently prompted
        if name not in prompted_dates:
            score += 1
        else:
            days_ago = (date.today() - date.fromisoformat(prompted_dates[name])).days
            if days_ago > 14:
                score += 1

        score += random.uniform(0, 0.5)  # tiebreaker
        scored.append((score, w))

    scored.sort(key=lambda x: -x[0])
    return [w for _, w in scored[:n]]

def print_entry(entry, full=True):
    w = entry["word"]
    pron = f"  ({entry['pronunciation']})" if entry.get("pronunciation") else ""
    pos = ", ".join(entry["pos"]) if entry["pos"] else ""
    reg = ", ".join(entry.get("register", [])) or ""

    ver = f"V{entry.get('version', 1)}"
    print(f"\n{divider()}")
    print(f"  {w}{pron}  [{ver}]")
    if pos:
        print(f"  [{pos}]" + (f"  |  register: {reg}" if reg else ""))
    print(divider())

    print(f"\n  DEFINITION:")
    print(wrap(entry["definition"]))

    if not full:
        if not entry.get("enriched"):
            print(f"\n  [skeleton — not yet enriched]")
        print()
        return

    if entry.get("tags"):
        print(f"\n  TAGS: {', '.join(entry['tags'])}")

    if entry.get("triggers"):
        print(f"\n  REACH FOR THIS WORD WHEN:")
        for t in entry["triggers"]:
            print(f"    → {t}")

    if entry.get("examples"):
        print(f"\n  EXAMPLES:")
        for i, ex in enumerate(entry["examples"], 1):
            ctx = f"[{ex['context']}]" if ex.get("context") else ""
            print(f"    {i}. {ctx} \"{ex['sentence']}\"")
            if ex.get("why"):
                print(wrap(f"WHY: {ex['why']}", indent=7))

    if entry.get("misuses"):
        print(f"\n  COMMON MISUSES:")
        for m in entry["misuses"]:
            print(f"    ✗ \"{m['wrong']}\"")
            print(wrap(f"→ {m['problem']}", indent=6))
            if m.get("use_instead"):
                print(wrap(f"Use instead: {m['use_instead']}", indent=6))

    if entry.get("related"):
        print(f"\n  RELATED WORDS:")
        for r in entry["related"]:
            print(f"    • {r['word']}: {r['distinction']}")

    if not entry.get("enriched"):
        print(f"\n  [skeleton — not yet enriched]")
    print()


# ─── commands ───────────────────────────────────────────────────────────────

def cmd_search(args):
    db = load_db()
    words = filter_by_version(db["words"], getattr(args, 'version', None))
    term = args.term.lower()
    results = []
    for w in words:
        score = 0
        word_lower = w["word"].lower()
        if term == word_lower:
            score = 1.0
        elif term in word_lower:
            score = 0.9
        elif term in w["definition"].lower():
            score = 0.7
        else:
            s = similarity(term, word_lower)
            if s > 0.5:
                score = s * 0.6
            else:
                # check tags
                for tag in w.get("tags", []):
                    if term in tag.lower():
                        score = 0.5
                        break
        if score > 0:
            results.append((score, w))

    results.sort(key=lambda x: -x[0])
    if not results:
        print(f"No results for '{args.term}'")
        return

    print(f"\nResults for '{args.term}' ({len(results)} matches):\n")
    for score, w in results[:15]:
        enriched = "●" if w.get("enriched") else "○"
        pos = ", ".join(w["pos"]) if w["pos"] else ""
        defn = w["definition"][:60] + ("..." if len(w["definition"]) > 60 else "")
        print(f"  {enriched} {w['word']:<20} [{pos}]  {defn}")
    if len(results) > 15:
        print(f"\n  ... and {len(results) - 15} more")


def cmd_define(args):
    db = load_db()
    term = args.word.lower()
    for w in db["words"]:
        if w["word"].lower() == term:
            print_entry(w, full=True)
            return
    # fuzzy fallback
    best = max(db["words"], key=lambda w: similarity(term, w["word"].lower()))
    if similarity(term, best["word"].lower()) > 0.6:
        print(f"  (Did you mean '{best['word']}'?)\n")
        print_entry(best, full=True)
    else:
        print(f"Word '{args.word}' not found.")


def cmd_browse(args):
    db = load_db()
    words = filter_by_version(db["words"], getattr(args, 'version', None))
    if args.register:
        words = [w for w in words if args.register.lower() in [r.lower() for r in w.get("register", [])]]
    if args.tag:
        words = [w for w in words if args.tag.lower() in [t.lower() for t in w.get("tags", [])]]
    if args.enriched_only:
        words = [w for w in words if w.get("enriched")]

    if not words:
        print("No words match the filter.")
        return

    page_size = 20
    total = len(words)
    page = 0
    while True:
        start = page * page_size
        end = min(start + page_size, total)
        print(f"\n{'─' * 50}")
        print(f"  Showing {start+1}-{end} of {total}")
        print(f"{'─' * 50}\n")
        for w in words[start:end]:
            enriched = "●" if w.get("enriched") else "○"
            pos = ", ".join(w["pos"]) if w["pos"] else ""
            defn = w["definition"][:55] + ("..." if len(w["definition"]) > 55 else "")
            print(f"  {enriched} {w['word']:<22} [{pos:<10}]  {defn}")

        if end >= total:
            print(f"\n  End of list.")
            break
        try:
            resp = input(f"\n  [Enter] next page  |  [q] quit  |  [word] define > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if resp.lower() == "q":
            break
        elif resp:
            # treat as a word to define
            for w in db["words"]:
                if w["word"].lower() == resp.lower():
                    print_entry(w, full=True)
                    break
        else:
            page += 1


def cmd_random(args):
    db = load_db()
    v = getattr(args, 'version', None)
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if not enriched:
        enriched = db["words"]
    w = random.choice(enriched)
    print_entry(w, full=True)


def cmd_stats(args):
    db = load_db()
    v = getattr(args, 'version', None)
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    skeletons = [w for w in words if not w.get("enriched")]

    # register distribution
    reg_counts = {}
    for w in words:
        for r in w.get("register", []):
            reg_counts[r] = reg_counts.get(r, 0) + 1

    # tag distribution
    tag_counts = {}
    for w in words:
        for t in w.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    # pos distribution
    pos_counts = {}
    for w in words:
        for p in w["pos"]:
            pos_counts[p] = pos_counts.get(p, 0) + 1

    print(f"\n{divider()}")
    print(f"  VOCABULARY DATABASE STATS")
    print(divider())
    print(f"\n  Total words:    {len(words)}")
    print(f"  Enriched:       {len(enriched)} ({len(enriched)*100//len(words)}%)")
    print(f"  Skeletons:      {len(skeletons)} ({len(skeletons)*100//len(words)}%)")

    # version breakdown
    versions = db["meta"].get("versions", {})
    active_v = db["meta"].get("active_version", 1)
    if versions:
        print(f"\n  VERSIONS (active: V{active_v}):")
        for vn in sorted(versions.keys(), key=int):
            vi = versions[vn]
            locked = "locked" if vi.get("locked") else "open"
            label = vi.get("label", "")
            count = vi.get("count", 0)
            marker = " ◀" if int(vn) == active_v else ""
            print(f"    V{vn}: {count}/500 ({locked}) — {label}{marker}")

    print(f"\n  PARTS OF SPEECH:")
    for p, c in sorted(pos_counts.items(), key=lambda x: -x[1]):
        print(f"    {p:<15} {c}")

    if reg_counts:
        print(f"\n  REGISTERS:")
        for r, c in sorted(reg_counts.items(), key=lambda x: -x[1]):
            print(f"    {r:<15} {c}")

    if tag_counts:
        print(f"\n  TOP TAGS:")
        for t, c in sorted(tag_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"    {t:<20} {c}")

    # flashcard progress
    flash = load_json(FLASH_PATH)
    if flash:
        attempted = len(flash)
        avg = sum(e.get("avg_score", 0) for e in flash.values()) / attempted if attempted else 0
        print(f"\n  FLASHCARD PROGRESS:")
        print(f"    Words attempted:  {attempted}")
        print(f"    Average score:    {avg:.1f}/5")

    # usage log
    usage = load_json(USAGE_PATH)
    if usage:
        print(f"\n  REAL-WORLD USAGE:")
        print(f"    Words used:       {len(usage)}")
        total_uses = sum(len(v) for v in usage.values())
        print(f"    Total uses:       {total_uses}")

    print()


def cmd_quiz(args):
    db = load_db()
    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched") and w.get("misuses") and w.get("examples")]
    if not enriched:
        print("No enriched words with examples and misuses available for quiz.")
        return

    score = 0
    total = 0
    n = min(args.n or 5, len(enriched))
    selected = random.sample(enriched, n)

    print(f"\n{divider('═')}")
    print(f"  QUIZ: Correct usage or misuse?")
    print(f"  {n} questions")
    print(divider('═'))

    for w in selected:
        total += 1
        # randomly pick correct example or misuse
        is_correct = random.choice([True, False])
        if is_correct:
            ex = random.choice(w["examples"])
            sentence = ex["sentence"]
        else:
            m = random.choice(w["misuses"])
            sentence = m["wrong"]

        print(f"\n  Word: {w['word']}")
        print(f"  Definition: {w['definition']}")
        print(f"\n  Sentence: \"{sentence}\"")
        try:
            ans = input(f"\n  Is this CORRECT or MISUSE? [c/m] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Quiz ended.")
            break

        if (ans.startswith("c") and is_correct) or (ans.startswith("m") and not is_correct):
            print(f"  ✓ Correct!")
            score += 1
        else:
            print(f"  ✗ Wrong!")

        if is_correct:
            print(f"  → This was CORRECT usage.")
            print(wrap(f"Why it works: {ex.get('why', '')}", indent=4))
        else:
            print(f"  → This was a MISUSE.")
            print(wrap(f"Problem: {m['problem']}", indent=4))
            print(wrap(f"Use instead: {m.get('use_instead', '')}", indent=4))

        print(f"  {'─' * 40}")

    print(f"\n  SCORE: {score}/{total}")
    if total > 0:
        pct = score * 100 // total
        if pct >= 80:
            print(f"  Excellent — you know your words.")
        elif pct >= 60:
            print(f"  Solid. Keep drilling the ones you missed.")
        else:
            print(f"  Room to grow. Focus on the misuse patterns.")
    print()


def cmd_flash(args):
    db = load_db()
    flash_data = load_json(FLASH_PATH)
    today = str(date.today())

    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if not enriched:
        print("No enriched words available for flashcards.")
        return

    # filter based on flags
    if args.weak:
        candidates = [w for w in enriched if w["word"] in flash_data and flash_data[w["word"]].get("avg_score", 5) <= 2]
        if not candidates:
            print("No weak words found (scored ≤2). Try --new or default mode.")
            return
    elif args.new:
        candidates = [w for w in enriched if w["word"] not in flash_data]
        if not candidates:
            print("All enriched words have been attempted. Try default mode.")
            return
    elif args.word:
        candidates = [w for w in enriched if w["word"].lower() == args.word.lower()]
        if not candidates:
            print(f"Word '{args.word}' not found or not enriched.")
            return
    else:
        # spaced repetition: prioritize overdue and low-scoring
        def sort_key(w):
            name = w["word"]
            if name not in flash_data:
                return (0, 0, random.random())  # never attempted = highest priority
            fd = flash_data[name]
            due = fd.get("next_due", "2000-01-01")
            avg = fd.get("avg_score", 3)
            overdue = 1 if due <= today else 0
            return (1 - overdue, avg, random.random())

        candidates = sorted(enriched, key=sort_key)

    n = min(args.n or 10, len(candidates))

    print(f"\n{'═' * 50}")
    print(f"  FLASHCARD DRILL — {n} cards")
    print(f"{'═' * 50}")

    for i, entry in enumerate(candidates[:n], 1):
        word = entry["word"]
        print(f"\n{'─' * 50}")
        print(f"  [{i}/{n}]  WORD:  {word}")
        print(f"{'─' * 50}")

        try:
            user_def = input(f"\n  1. What does it mean?\n  > ").strip()
            user_sent = input(f"\n  2. Use it in a sentence:\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Session ended.")
            break

        # reveal
        print(f"\n{'─' * 50}")
        print(f"  REVEAL")
        print(f"{'─' * 50}")

        print(f"\n  ACTUAL DEFINITION:")
        print(wrap(entry["definition"]))

        print(f"\n  YOUR DEFINITION:")
        print(wrap(user_def if user_def else "(skipped)"))

        if entry.get("examples"):
            print(f"\n  CORRECT EXAMPLES:")
            for ex in entry["examples"][:2]:
                ctx = f"[{ex['context']}] " if ex.get("context") else ""
                print(f"    • {ctx}\"{ex['sentence']}\"")
                if ex.get("why"):
                    print(wrap(f"WHY: {ex['why']}", indent=6))

        if entry.get("misuses"):
            print(f"\n  COMMON MISUSES:")
            for m in entry["misuses"]:
                print(f"    ✗ \"{m['wrong']}\"")
                print(wrap(f"→ {m['problem']}", indent=6))

        print(f"\n  YOUR SENTENCE:")
        print(wrap(user_sent if user_sent else "(skipped)"))

        print(f"\n{'─' * 50}")
        print(f"  Rate your sentence (1-5):")
        print(f"    1 = wrong usage    — used incorrect meaning or context")
        print(f"    2 = forced/awkward — right meaning but sounds shoehorned")
        print(f"    3 = passable       — correct but a simpler word would work just as well")
        print(f"    4 = natural        — fits the sentence, a reader wouldn't notice it")
        print(f"    5 = nailed it      — the word is the BEST choice, irreplaceable")

        try:
            score_input = input(f"  > ").strip()
            score = int(score_input) if score_input.isdigit() and 1 <= int(score_input) <= 5 else 3
        except (EOFError, KeyboardInterrupt):
            score = 3

        # update progress
        if word not in flash_data:
            flash_data[word] = {"attempts": [], "avg_score": 0, "next_due": today}

        flash_data[word]["attempts"].append({
            "date": today,
            "sentence_score": score,
        })

        attempts = flash_data[word]["attempts"]
        flash_data[word]["avg_score"] = round(sum(a["sentence_score"] for a in attempts) / len(attempts), 1)

        # Track time-to-mastery: record first_seen and mastered_on
        if "first_seen" not in flash_data[word]:
            flash_data[word]["first_seen"] = today
        if flash_data[word]["avg_score"] >= 4.0 and "mastered_on" not in flash_data[word]:
            flash_data[word]["mastered_on"] = today
            first = flash_data[word]["first_seen"]
            days_to_master = (date.today() - date.fromisoformat(first)).days
            flash_data[word]["days_to_master"] = days_to_master
        elif flash_data[word]["avg_score"] < 4.0 and "mastered_on" in flash_data[word]:
            # Lost mastery -- reset
            del flash_data[word]["mastered_on"]
            if "days_to_master" in flash_data[word]:
                del flash_data[word]["days_to_master"]

        # spaced repetition
        if score <= 2:
            delta = 1
        elif score == 3:
            delta = 3
        elif score == 4:
            delta = 7
        else:
            delta = 14
        flash_data[word]["next_due"] = str(date.today() + timedelta(days=delta))

        print(f"  Recorded: {score}/5 — next due: {flash_data[word]['next_due']}")

    save_json(FLASH_PATH, flash_data)

    # Inflation detection: check score distribution across all attempts
    all_scores = []
    for wd, fd in flash_data.items():
        for a in fd.get("attempts", []):
            all_scores.append(a.get("sentence_score", 3))
    if len(all_scores) >= 20:
        high_pct = sum(1 for s in all_scores if s >= 4) / len(all_scores) * 100
        if high_pct >= 80:
            print(f"\n  ⚠ Score inflation warning: {high_pct:.0f}%% of all-time scores are 4-5.")
            print(f"    If most words feel easy, consider: are you stretching into harder contexts?")
            print(f"    A 4 means a reader wouldn't notice the word. A 5 means it's irreplaceable.")

    print(f"\n  Session saved. Run 'python vocab.py progress' to see your stats.\n")


SCENARIOS = {
    "punchy": [
        "Write a tweet thread (3 tweets) that makes people stop scrolling.",
        "Write a meme caption that lands without explaining the joke.",
        "Draft the first 3 sentences of a Substack post that hooks immediately.",
        "Write a short-form video caption that makes someone watch twice.",
        "Write a one-paragraph hot take that sounds effortless but is airtight.",
        "Rewrite a boring headline into something people would actually click.",
        "Write a cold open for a YouTube video -- the first 15 seconds, scripted.",
        "Write a reply-guy tweet that's funnier than the original post.",
    ],
    "persuasive": [
        "Write a Substack opening that makes the reader feel seen before you've made your point.",
        "Write a paragraph that changes someone's mind without them realizing it happened.",
        "Make an argument people instinctively disagree with, then make it undeniable in 150 words.",
        "Write the closing paragraph of an essay that leaves the reader unsettled in a productive way.",
        "Take a popular opinion and expose the lazy thinking behind it in 200 words.",
        "Write a single paragraph so persuasive it could be the entire post.",
        "Draft a newsletter intro that turns a personal anecdote into a universal insight.",
        "Write the paragraph where you pivot from story to argument. Make the seam invisible.",
    ],
    "measured": [
        "Write a reflection on something sacred that avoids both sentimentality and detachment.",
        "Describe a moment of conviction without preaching. Let the reader arrive there themselves.",
        "Write about doubt honestly, without performing vulnerability.",
        "Write a personal essay paragraph about a belief that costs you something to hold.",
        "Describe a conversation with God, a mentor, or your past self -- without quoting directly.",
        "Write about forgiveness without using the word forgiveness.",
        "Write a paragraph about loss that earns its weight -- no shortcuts to emotion.",
        "Reflect on a tradition you once rejected but now understand differently.",
    ],
    "craft": [
        "Rewrite this sentence three different ways, each with a different emotional temperature: 'He left without saying goodbye.'",
        "Write the same moment twice: once as a tweet, once as an essay paragraph. Same facts, different music.",
        "Write a 50-word paragraph. Then rewrite it at 25 words. Then at 10. All three must work.",
        "Describe a room in a way that reveals the person who lives there, without naming them.",
        "Write a transition between two unrelated ideas. Make the leap feel inevitable.",
        "Write a paragraph where every sentence is a different length. Read it aloud -- does it have rhythm?",
        "Take a cliche ('time heals all wounds') and rewrite it so it feels true again.",
        "Write a paragraph that builds tension using only short, declarative sentences.",
    ],
}

CONSTRAINTS = {
    "opening_hooks": [
        "Your first sentence must be under 6 words.",
        "Open with a question that sounds rhetorical but isn't.",
        "Start mid-action. No setup, no throat-clearing.",
        "Your opening line must be a contradiction.",
    ],
    "compression": [
        "Say it in under 100 words. Every word must earn its place.",
        "No adjectives. Rely on verbs and nouns only.",
        "Cut every sentence that doesn't change the reader's understanding.",
        "Use no word longer than two syllables.",
    ],
    "tonal_control": [
        "Start serious, end funny. The shift must feel earned, not forced.",
        "Write it deadpan. Zero exclamation marks, zero intensifiers.",
        "The tone must contradict the subject matter.",
        "Write it angry but calm. No raised voice.",
    ],
    "rhythm": [
        "Alternate between sentences under 8 words and over 20.",
        "No sentence may start with the same word as another.",
        "Three one-sentence paragraphs. Then one long one. Feel the shift.",
        "End three consecutive sentences on a stressed syllable.",
    ],
    "show_dont_tell": [
        "Never name the emotion. Make the reader feel it through action and detail.",
        "Replace every abstract noun with a concrete image.",
        "No opinion statements. Only observations that imply a stance.",
        "Describe a person entirely through what they do, never what they are.",
    ],
    "endings": [
        "Your last sentence must reframe everything before it.",
        "End on a single word. Make it land.",
        "The final line must be the shortest in the piece.",
        "End with an image, not a thought.",
    ],
}

SKILL_LABELS = {
    "opening_hooks": "Opening hooks",
    "compression": "Compression",
    "tonal_control": "Tonal control",
    "rhythm": "Rhythm & sentence variation",
    "show_dont_tell": "Showing vs telling",
    "endings": "Endings",
}

# Backward compatibility alias
PROMPT_STYLES = list(SCENARIOS.keys())


def cmd_daily(args):
    db = load_db()
    prompts_log = load_json(PROMPTS_PATH, default=[])
    today = str(date.today())

    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if not enriched:
        print("No enriched words available. Enrich some words first.")
        return

    n = args.n or 3
    n = min(n, len(enriched))

    selected = smart_select(enriched, n, prompts_log=prompts_log)

    style = args.style or random.choice(list(SCENARIOS.keys()))
    if style not in SCENARIOS:
        print(f"Unknown style. Available: {', '.join(SCENARIOS.keys())}")
        return

    scenario = random.choice(SCENARIOS[style])
    skill_key = random.choice(list(CONSTRAINTS.keys()))
    constraint = random.choice(CONSTRAINTS[skill_key])
    skill_label = SKILL_LABELS[skill_key]
    word_list = ", ".join(w["word"] for w in selected)
    prompt_text = f"{scenario} {constraint} Weave in: {word_list}."

    # build output
    output_lines = []
    output_lines.append(f"# Morning Writing — {today}")
    output_lines.append(f"**Style:** {style}")
    output_lines.append(f"**Skill focus:** {skill_label}")
    output_lines.append(f"**Words:** {word_list}")
    output_lines.append("")
    output_lines.append(f"## Prompt")
    output_lines.append(prompt_text)
    output_lines.append("")
    output_lines.append("## Quick Reference")
    for w in selected:
        output_lines.append(f"### {w['word']}")
        output_lines.append(f"**Definition:** {w['definition']}")
        if w.get("examples"):
            ex = w["examples"][0]
            output_lines.append(f"**Example:** \"{ex['sentence']}\"")
            if ex.get("why"):
                output_lines.append(f"*Why it works:* {ex['why']}")
        if w.get("misuses"):
            m = w["misuses"][0]
            output_lines.append(f"**Watch out:** ✗ \"{m['wrong']}\" — {m['problem']}")
        if w.get("triggers"):
            output_lines.append(f"**Reach for this when:** {w['triggers'][0]}")
        output_lines.append("")

    output_lines.append("## Your Writing")
    output_lines.append("(Write below)")
    output_lines.append("")

    full_output = "\n".join(output_lines)

    # print to terminal
    print(f"\n{'═' * 50}")
    print(f"  DAILY WRITING PROMPT — {today}")
    print(f"  Style: {style}  |  Skill: {skill_label}")
    print(f"{'═' * 50}")
    print(f"\n  {prompt_text}")
    print(f"\n  Words to use: {word_list}")
    print(f"\n{'─' * 50}")
    print(f"  QUICK REFERENCE:")
    for w in selected:
        print(f"\n  {w['word']}: {w['definition'][:80]}")
        if w.get("misuses"):
            m = w["misuses"][0]
            print(f"    ✗ Don't: \"{m['wrong'][:60]}...\"")
    print(f"{'─' * 50}")

    # copy to clipboard for Notion paste
    try:
        process = subprocess.Popen(["clip"], stdin=subprocess.PIPE, creationflags=0x08000000)
        process.communicate(full_output.encode("utf-16-le"))
        print(f"\n  ✓ Copied to clipboard — paste into Notion")
    except Exception:
        print(f"\n  (Could not copy to clipboard)")

    # log
    prompts_log.append({
        "date": today,
        "words": [w["word"] for w in selected],
        "style": style,
        "skill": skill_key,
        "constraint": constraint,
    })
    save_json(PROMPTS_PATH, prompts_log)
    sync_to_nas()
    print(f"  ✓ Logged to prompts_log.json\n")


def cmd_wotd(args):
    db = load_db()
    prompts_log = load_json(PROMPTS_PATH, default=[])
    today = str(date.today())

    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if not enriched:
        print("No enriched words available.")
        return

    # avoid recently shown
    recent_words = set()
    for entry in prompts_log[-14:]:
        recent_words.update(entry.get("words", []))

    candidates = [w for w in enriched if w["word"] not in recent_words]
    if not candidates:
        candidates = enriched

    word = random.choice(candidates)

    print(f"\n{'═' * 50}")
    print(f"  WORD OF THE DAY — {today}")
    print(f"{'═' * 50}")
    print_entry(word, full=True)

    # log
    prompts_log.append({
        "date": today,
        "words": [word["word"]],
        "style": "wotd",
    })
    save_json(PROMPTS_PATH, prompts_log)
    sync_to_nas()


def cmd_used(args):
    usage = load_json(USAGE_PATH)
    word = args.word
    where = args.where or "unspecified"
    today = str(date.today())

    # verify word exists
    db = load_db()
    found = any(w["word"].lower() == word.lower() for w in db["words"])
    if not found:
        print(f"Word '{word}' not in database. Add it first.")
        return

    # normalize key
    key = next(w["word"] for w in db["words"] if w["word"].lower() == word.lower())

    if key not in usage:
        usage[key] = []
    usage[key].append({"date": today, "where": where})
    save_json(USAGE_PATH, usage)
    print(f"  ✓ Logged: used '{key}' in {where} on {today}")
    print(f"  Total uses of '{key}': {len(usage[key])}")


def cmd_progress(args):
    db = load_db()
    flash = load_json(FLASH_PATH)
    usage = load_json(USAGE_PATH)
    prompts_log = load_json(PROMPTS_PATH, default=[])

    enriched_count = sum(1 for w in db["words"] if w.get("enriched"))
    total = len(db["words"])

    print(f"\n{'═' * 50}")
    print(f"  YOUR PROGRESS")
    print(f"{'═' * 50}")

    # enrichment
    bar_len = 30
    filled = int(enriched_count / total * bar_len) if total else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\n  ENRICHMENT:  [{bar}] {enriched_count}/{total} ({enriched_count*100//total}%)")

    # flashcard stats
    if flash:
        attempted = len(flash)
        scores = [e.get("avg_score", 0) for e in flash.values()]
        avg = sum(scores) / len(scores) if scores else 0
        weak = sum(1 for s in scores if s <= 2)
        strong = sum(1 for s in scores if s >= 4)
        due = sum(1 for e in flash.values() if e.get("next_due", "9999") <= str(date.today()))

        print(f"\n  FLASHCARDS:")
        print(f"    Words drilled:    {attempted}")
        print(f"    Average score:    {avg:.1f}/5")
        print(f"    Strong (≥4):      {strong}")
        print(f"    Weak (≤2):        {weak}")
        print(f"    Due today:        {due}")

        # Mastery analytics
        mastered = [w for w, fd in flash.items() if "mastered_on" in fd]
        if mastered:
            days_list = [fd["days_to_master"] for w, fd in flash.items() if "days_to_master" in fd]
            avg_days = sum(days_list) / len(days_list) if days_list else 0
            print(f"    Mastered (avg>=4): {len(mastered)}")
            if days_list:
                print(f"    Avg days to master: {avg_days:.0f}")

        # Inflation detection
        all_scores = []
        for wd, fd in flash.items():
            for a in fd.get("attempts", []):
                all_scores.append(a.get("sentence_score", 3))
        if len(all_scores) >= 20:
            high_pct = sum(1 for s in all_scores if s >= 4) / len(all_scores) * 100
            dist = {}
            for s in all_scores:
                dist[s] = dist.get(s, 0) + 1
            print(f"\n    Score distribution ({len(all_scores)} total ratings):")
            for s in sorted(dist.keys()):
                bar_s = "█" * (dist[s] * 20 // len(all_scores))
                print(f"      {s}: {bar_s} {dist[s]} ({dist[s]*100//len(all_scores)}%%)")
            if high_pct >= 80:
                print(f"    ⚠ {high_pct:.0f}%% rated 4-5 — possible inflation")
    else:
        print(f"\n  FLASHCARDS:  No sessions yet. Run: python vocab.py flash")

    # usage
    if usage:
        total_uses = sum(len(v) for v in usage.values())
        print(f"\n  REAL-WORLD USAGE:")
        print(f"    Unique words used:  {len(usage)}")
        print(f"    Total uses:         {total_uses}")
        # most used
        sorted_usage = sorted(usage.items(), key=lambda x: -len(x[1]))[:5]
        print(f"    Most used:")
        for word, uses in sorted_usage:
            print(f"      {word}: {len(uses)} times")
    else:
        print(f"\n  REAL-WORLD USAGE:  None logged yet. Run: python vocab.py used <word>")

    # writing streak
    if prompts_log:
        dates = sorted(set(e["date"] for e in prompts_log if e.get("style") != "wotd"), reverse=True)
        streak = 0
        check = date.today()
        for d in dates:
            if d == str(check):
                streak += 1
                check -= timedelta(days=1)
            elif d == str(check - timedelta(days=1)):
                check -= timedelta(days=1)
                streak += 1
                check -= timedelta(days=1)
            else:
                break
        print(f"\n  WRITING STREAK:  {streak} day{'s' if streak != 1 else ''}")
        print(f"    Total sessions:    {len([e for e in prompts_log if e.get('style') != 'wotd'])}")

    print()


# ─── suggest ───────────────────────────────────────────────────────────────

# Mode → register mapping for vocab suggestions
MODE_REGISTERS = {
    "fun": ["informal", "colloquial", "neutral"],
    "deep": ["formal", "literary", "neutral"],
    "professional": ["formal", "technical", "neutral"],
    "casual": ["informal", "neutral", "colloquial"],
    "academic": ["formal", "literary", "technical"],
    "journal": ["informal", "neutral", "literary"],
    "editorial": ["formal", "neutral", "literary"],
    "persuasive": ["formal", "neutral", "literary"],
}


def cmd_suggest(args):
    """Suggest vocab words appropriate for a given writing mode."""
    db = load_db()
    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if not enriched:
        print("No enriched words yet. Enrich some words first.")
        return

    mode = args.mode or "casual"
    target_registers = MODE_REGISTERS.get(mode, ["neutral"])

    picks = smart_select(enriched, 10, register_filter=target_registers)

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║  VOCAB SUGGESTIONS — {mode.upper():^14s}  ║")
    print(f"  ╚══════════════════════════════════════╝\n")

    for w in picks:
        regs = ", ".join(w.get("register", []))
        print(f"  • {w['word']:<20s} [{regs}]")
        defn = w.get("definition", "")
        if len(defn) > 70:
            defn = defn[:67] + "..."
        print(f"    {defn}")
        if w.get("triggers"):
            print(f"    → {w['triggers'][0]}")
        print()


def cmd_review(args):
    """Show words studied via flashcards but never used in real writing."""
    flash = load_json(FLASH_PATH, {})
    usage = load_json(USAGE_PATH, {})

    if not flash:
        print("No flashcard data yet. Run: python vocab.py flash")
        return

    studied_not_used = []
    for word, data in flash.items():
        if word not in usage:
            studied_not_used.append((word, data.get("avg_score", 0), data.get("attempts", 0)))

    if not studied_not_used:
        print("Every word you've studied has been used in real writing. Nice.")
        return

    # Sort by avg_score descending — words you know well but haven't used
    studied_not_used.sort(key=lambda x: -x[1])

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║   STUDIED BUT NEVER USED IN WRITING  ║")
    print(f"  ╚══════════════════════════════════════╝\n")
    print(f"  You've drilled these but never logged real-world usage.\n")

    for word, avg, attempts in studied_not_used:
        score_bar = "●" * int(avg) + "○" * (5 - int(avg))
        print(f"  • {word:<20s} [{score_bar}] {avg:.1f}/5  ({attempts} drills)")

    print(f"\n  Total: {len(studied_not_used)} words ready to use.")
    print(f"  Log usage with: python vocab.py used <word> --where \"context\"\n")


def cmd_challenge(args):
    """Generate a writing challenge: specific words + specific mode."""
    db = load_db()
    v = getattr(args, 'version', None) or get_active_version()
    words = filter_by_version(db["words"], v)
    enriched = [w for w in words if w.get("enriched")]
    if len(enriched) < 2:
        print("Need at least 2 enriched words for a challenge.")
        return

    mode = args.mode or random.choice(list(MODE_REGISTERS.keys()))
    target_registers = MODE_REGISTERS.get(mode, ["neutral"])

    picks = smart_select(enriched, min(3, len(enriched)), register_filter=target_registers)

    # Mode-appropriate format suggestions
    format_map = {
        "funny": ["meme caption", "tweet", "short-form video script", "Instagram caption"],
        "serious": ["essay paragraph", "Substack intro", "think piece opening"],
        "professional": ["email", "proposal paragraph", "LinkedIn post"],
        "casual": ["social post", "text to a friend", "journal entry"],
        "research": ["analysis brief", "data summary", "research note"],
        "editorial": ["hot take", "review paragraph", "commentary"],
        "persuasive": ["pitch paragraph", "argument opener", "call to action"],
    }
    fmt = random.choice(format_map.get(mode, ["short paragraph"]))

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║        WRITING CHALLENGE              ║")
    print(f"  ╚══════════════════════════════════════╝\n")
    print(f"  Mode:   {mode.upper()}")
    print(f"  Format: {fmt}")
    print(f"  Words:  {', '.join(w['word'] for w in picks)}\n")

    for w in picks:
        print(f"  ─── {w['word']} ───")
        print(f"  {w.get('definition', '')}")
        if w.get("triggers"):
            print(f"  Use when: {w['triggers'][0]}")
        if w.get("misuses"):
            m = w["misuses"][0]
            print(f"  ✗ Don't: {m.get('wrong', '')[:60]}")
        print()

    print(f"  Write a {fmt} using all {len(picks)} words.")
    print(f"  Log with: python vocab.py used <word> --where \"challenge\"\n")


def fuzzy_find(db, term, threshold=0.45):
    """Find the best matching word(s) in the database using multiple fuzzy strategies.
    Returns list of (score, entry) tuples, sorted best-first."""
    term_lower = term.lower().strip()
    results = []

    for w in db["words"]:
        word_lower = w["word"].lower()
        score = 0

        # exact match
        if term_lower == word_lower:
            score = 1.0
        # starts with same letters (handles partial typing)
        elif word_lower.startswith(term_lower) or term_lower.startswith(word_lower):
            score = 0.92
        # substring match
        elif term_lower in word_lower or word_lower in term_lower:
            score = 0.88
        else:
            # SequenceMatcher for typos
            seq_score = similarity(term_lower, word_lower)
            # also check with common letter swaps stripped
            stripped_term = term_lower.replace("ou", "o").replace("ei", "ie").replace("ious", "ous")
            stripped_word = word_lower.replace("ou", "o").replace("ei", "ie").replace("ious", "ous")
            alt_score = similarity(stripped_term, stripped_word)
            # check if same consonant skeleton (handles vowel confusion)
            consonants_term = "".join(c for c in term_lower if c not in "aeiou")
            consonants_word = "".join(c for c in word_lower if c not in "aeiou")
            cons_score = similarity(consonants_term, consonants_word) * 0.85
            score = max(seq_score, alt_score, cons_score)

        if score >= threshold:
            results.append((score, w))

    results.sort(key=lambda x: (-x[0], x[1]["word"].lower()))
    return results


def cmd_lookup(args):
    """Fuzzy word recall — handles misspellings, partial words, phonetic guesses."""
    db = load_db()
    term = args.term

    # exact match first
    for w in db["words"]:
        if w["word"].lower() == term.lower():
            print_entry(w, full=True)
            print_synonym_section(db, w)
            return

    # fuzzy search
    results = fuzzy_find(db, term)

    if not results:
        print(f"\n  No matches for '{term}'.")
        print(f"  Try: python vocab.py add {term}")
        return

    best_score, best = results[0]

    if best_score >= 0.75:
        # high confidence — show it directly
        if best["word"].lower() != term.lower():
            print(f"\n  → Showing: {best['word']}  (you typed: '{term}')")
        print_entry(best, full=True)
        print_synonym_section(db, best)
    elif best_score >= 0.5:
        # medium confidence — show top match + alternatives
        print(f"\n  Best match for '{term}':\n")
        print(f"  → {best['word']}  (confidence: {best_score:.0%})")
        print_entry(best, full=True)
        print_synonym_section(db, best)
        if len(results) > 1:
            print(f"  Other possibilities:")
            for score, w in results[1:4]:
                print(f"    • {w['word']:<20} ({score:.0%})")
            print()
    else:
        # low confidence — show candidates
        print(f"\n  No confident match for '{term}'. Did you mean:\n")
        for score, w in results[:5]:
            defn = w["definition"][:55] + ("..." if len(w["definition"]) > 55 else "")
            print(f"    • {w['word']:<20} ({score:.0%})  {defn}")
        print(f"\n  Use: python vocab.py lookup <word>  to see full entry")
        print(f"  Or:  python vocab.py add {term}     to add it as new\n")


def cmd_add(args):
    """Add one or more words to the database as skeletons."""
    db = load_db()
    existing = {w["word"].lower() for w in db["words"]}

    added = []
    skipped = []

    for word in args.words:
        word_title = word.strip().capitalize()
        if word_title.lower() in existing:
            skipped.append(word_title)
            continue

        new_entry = {
            "word": word_title,
            "pos": [],
            "pronunciation": None,
            "definition": "",
            "register": [],
            "tags": [],
            "enriched": False,
            "examples": [],
            "misuses": [],
            "related": [],
            "triggers": [],
            "date_added": str(date.today()),
        }

        # insert in alphabetical order
        inserted = False
        for i, w in enumerate(db["words"]):
            if w["word"].lower() > word_title.lower():
                db["words"].insert(i, new_entry)
                inserted = True
                break
        if not inserted:
            db["words"].append(new_entry)

        existing.add(word_title.lower())
        added.append(word_title)

    if added:
        db["meta"]["word_count"] = len(db["words"])
        db["meta"]["last_updated"] = str(date.today())
        save_db(db)
        sync_to_nas()

    print(f"\n  {'═' * 40}")
    if added:
        print(f"  ✓ Added {len(added)} word(s): {', '.join(added)}")
        print(f"    Total: {len(db['words'])} words")
        print(f"    Status: skeleton — run /add-words in Claude Code to enrich")
    if skipped:
        print(f"  ⊘ Skipped {len(skipped)} duplicate(s): {', '.join(skipped)}")
    if not added and not skipped:
        print(f"  No words provided.")
    print()


def cmd_sync(args):
    """Manually sync vocab data to NAS."""
    if not NAS_VOCAB_DIR.exists():
        print(f"  ✗ NAS not reachable at {NAS_VOCAB_DIR}")
        return
    sync_to_nas()
    print(f"  ✓ Synced vocab_db.json and prompts_log.json to NAS")


def cmd_words(args):
    """List every word in the database — just the words, nothing else."""
    db = load_db()
    v = getattr(args, 'version', None)
    filtered = filter_by_version(db["words"], v)
    words = [w["word"] for w in filtered]
    total = len(words)

    if args.alpha:
        # print in alphabetical columns
        cols = 4
        col_width = 22
        for i in range(0, total, cols):
            row = words[i:i+cols]
            print("  " + "".join(w.ljust(col_width) for w in row))
        print(f"\n  {total} words total")
    elif args.numbered:
        for i, w in enumerate(words, 1):
            print(f"  {i:>4}. {w}")
        print(f"\n  {total} words total")
    else:
        # default: compact columns
        cols = 5
        col_width = 18
        for i in range(0, total, cols):
            row = words[i:i+cols]
            print("  " + "".join(w.ljust(col_width) for w in row))
        print(f"\n  {total} words total")


def find_synonyms_in_db(db, target_entry):
    """Find all words in the database that are synonymous or closely related to the target.
    Uses multiple strategies: related words, shared tags, definition overlap, and cross-references."""
    target_word = target_entry["word"].lower()
    target_def = target_entry["definition"].lower()
    target_tags = set(t.lower() for t in target_entry.get("tags", []))
    target_pos = set(p.lower() for p in target_entry.get("pos", []))

    # collect explicitly listed related words
    explicit_related = {}
    for r in target_entry.get("related", []):
        explicit_related[r["word"].lower()] = r.get("distinction", "")

    # collect words that list THIS word as a related word
    reverse_related = {}
    for w in db["words"]:
        if w["word"].lower() == target_word:
            continue
        for r in w.get("related", []):
            if r["word"].lower() == target_word:
                reverse_related[w["word"].lower()] = r.get("distinction", "")

    # collect words with overlapping definitions (key synonym phrases)
    # extract key terms from target definition
    stop_words = {"a", "an", "the", "to", "of", "or", "and", "in", "is", "as", "by",
                  "for", "not", "with", "from", "that", "it", "be", "on", "at", "this",
                  "but", "are", "was", "has", "have", "been", "being", "its", "more",
                  "than", "also", "very", "often", "especially", "without", "one"}
    target_terms = set(t for t in target_def.split() if len(t) > 3 and t not in stop_words)

    definition_matches = {}
    for w in db["words"]:
        if w["word"].lower() == target_word:
            continue
        # must share at least one POS
        w_pos = set(p.lower() for p in w.get("pos", []))
        if target_pos and w_pos and not target_pos.intersection(w_pos):
            continue

        w_def = w["definition"].lower()
        w_terms = set(t for t in w_def.split() if len(t) > 3 and t not in stop_words)
        overlap = target_terms.intersection(w_terms)
        # also check if the target word appears in this word's definition or vice versa
        direct_ref = target_word in w_def or w["word"].lower() in target_def

        if len(overlap) >= 3 or direct_ref:
            definition_matches[w["word"].lower()] = w

    # collect words sharing 2+ tags AND same POS
    tag_matches = {}
    if target_tags and len(target_tags) >= 2:
        for w in db["words"]:
            if w["word"].lower() == target_word:
                continue
            w_pos = set(p.lower() for p in w.get("pos", []))
            if target_pos and w_pos and not target_pos.intersection(w_pos):
                continue
            w_tags = set(t.lower() for t in w.get("tags", []))
            shared = target_tags.intersection(w_tags)
            if len(shared) >= 2:
                tag_matches[w["word"].lower()] = w

    # also check "use_instead" fields in misuses — those are direct synonyms
    use_instead = {}
    for m in target_entry.get("misuses", []):
        alts = m.get("use_instead", "")
        for alt in alts.split(","):
            alt = alt.strip().lower()
            if alt:
                for w in db["words"]:
                    if w["word"].lower() == alt:
                        use_instead[w["word"].lower()] = w
                        break

    # merge all sources, avoiding duplicates
    all_synonyms = {}  # word_lower -> (entry, sources, distinction)

    for word_lower, distinction in explicit_related.items():
        entry = next((w for w in db["words"] if w["word"].lower() == word_lower), None)
        if entry:
            all_synonyms[word_lower] = (entry, ["related"], distinction)

    for word_lower, distinction in reverse_related.items():
        entry = next((w for w in db["words"] if w["word"].lower() == word_lower), None)
        if entry:
            if word_lower in all_synonyms:
                all_synonyms[word_lower] = (all_synonyms[word_lower][0], all_synonyms[word_lower][1] + ["cross-ref"], all_synonyms[word_lower][2] or distinction)
            else:
                all_synonyms[word_lower] = (entry, ["cross-ref"], distinction)

    for word_lower, entry in definition_matches.items():
        if word_lower in all_synonyms:
            all_synonyms[word_lower] = (all_synonyms[word_lower][0], all_synonyms[word_lower][1] + ["definition"], all_synonyms[word_lower][2])
        else:
            all_synonyms[word_lower] = (entry, ["definition"], "")

    for word_lower, entry in tag_matches.items():
        if word_lower in all_synonyms:
            all_synonyms[word_lower] = (all_synonyms[word_lower][0], all_synonyms[word_lower][1] + ["tags"], all_synonyms[word_lower][2])
        else:
            all_synonyms[word_lower] = (entry, ["tags"], "")

    for word_lower, entry in use_instead.items():
        if word_lower in all_synonyms:
            all_synonyms[word_lower] = (all_synonyms[word_lower][0], all_synonyms[word_lower][1] + ["alt-suggestion"], all_synonyms[word_lower][2])
        else:
            all_synonyms[word_lower] = (entry, ["alt-suggestion"], "")

    # sort by number of sources (more sources = stronger synonym match)
    sorted_syns = sorted(all_synonyms.items(), key=lambda x: -len(x[1][1]))
    return sorted_syns


def print_synonym_section(db, target_entry):
    """Print the synonym/related words section for a lookup."""
    synonyms = find_synonyms_in_db(db, target_entry)
    if not synonyms:
        return

    print(f"\n  {'═' * 46}")
    print(f"  SYNONYMS & RELATED IN YOUR DATABASE")
    print(f"  {'═' * 46}")

    for word_lower, (entry, sources, distinction) in synonyms:
        reg = ", ".join(entry.get("register", []))
        print(f"\n  ■ {entry['word']:<20} [{reg}]")

        # show definition
        defn = entry["definition"]
        if len(defn) > 80:
            defn = defn[:77] + "..."
        print(f"    Definition: {defn}")

        # show distinction if we have one
        if distinction:
            print(f"    ┌─ vs {target_entry['word']}:")
            print(wrap(distinction, indent=6))

        # check if the OTHER word's related list has a distinction for THIS word
        if not distinction:
            for r in entry.get("related", []):
                if r["word"].lower() == target_entry["word"].lower():
                    print(f"    ┌─ vs {target_entry['word']}:")
                    print(wrap(r["distinction"], indent=6))
                    break

        # show when to use THIS word instead
        if entry.get("triggers"):
            print(f"    → Use {entry['word']} when: {entry['triggers'][0]}")

    print(f"\n  {'─' * 46}")
    print(f"  {len(synonyms)} related word{'s' if len(synonyms) != 1 else ''} found in database")
    print()


def cmd_writing_progress(args):
    """Show writing progress trends from writing_log.json."""
    log = load_json(WRITING_LOG_PATH, [])
    if not log:
        print("No writing sessions logged yet.")
        print("Use /write to create content — sessions are logged automatically.")
        return

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║        WRITING PROGRESS               ║")
    print(f"  ╚══════════════════════════════════════╝\n")

    # Total pieces
    print(f"  Total pieces:     {len(log)}")

    # Mode distribution
    modes = {}
    for entry in log:
        m = entry.get("mode", "unknown")
        modes[m] = modes.get(m, 0) + 1
    print(f"\n  MODE DISTRIBUTION:")
    for m, count in sorted(modes.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {m:<14s} {bar} {count}")

    # Average slop score
    slop_scores = [e.get("slop_score", 0) for e in log if "slop_score" in e]
    if slop_scores:
        avg_slop = sum(slop_scores) / len(slop_scores)
        print(f"\n  AVG SLOP SCORE:   {avg_slop:.1f} flags")
        recent = slop_scores[-5:] if len(slop_scores) >= 5 else slop_scores
        recent_avg = sum(recent) / len(recent)
        print(f"  Last {len(recent)} pieces:    {recent_avg:.1f} flags")

    # Vocab usage across pieces
    all_vocab = []
    for entry in log:
        all_vocab.extend(entry.get("vocab_used", []))
    if all_vocab:
        unique = set(all_vocab)
        print(f"\n  VOCAB IN WRITING:")
        print(f"    Unique words used:  {len(unique)}")
        print(f"    Total insertions:   {len(all_vocab)}")

    # Draft path distribution
    paths = {}
    for entry in log:
        p = entry.get("path", "unknown")
        paths[p] = paths.get(p, 0) + 1
    if paths:
        print(f"\n  DRAFT METHOD:")
        for p, count in sorted(paths.items(), key=lambda x: -x[1]):
            print(f"    {p:<14s} {count}")

    # Recent pieces
    recent = log[-5:]
    print(f"\n  RECENT PIECES:")
    for entry in recent:
        d = entry.get("date", "?")
        m = entry.get("mode", "?")
        wc = entry.get("word_count", "?")
        topic = entry.get("topic", "untitled")
        if len(topic) > 40:
            topic = topic[:37] + "..."
        print(f"    {d}  [{m}]  ~{wc}w  {topic}")

    print()


# ─── main ───────────────────────────────────────────────────────────────────

def cmd_version_info(args):
    db = load_db()
    versions = db["meta"].get("versions", {})
    active_v = db["meta"].get("active_version", 1)

    print(f"\n{divider()}")
    print(f"  VERSION INFO")
    print(divider())
    print(f"\n  Active version: V{active_v}")
    print(f"  Total words: {db['meta'].get('word_count', len(db['words']))}")

    for vn in sorted(versions.keys(), key=int):
        vi = versions[vn]
        locked = "LOCKED" if vi.get("locked") else "OPEN"
        label = vi.get("label", "")
        count = vi.get("count", 0)
        marker = " ◀ YOU ARE HERE" if int(vn) == active_v else ""
        bar = "█" * (count // 10) + "░" * ((500 - count) // 10)
        print(f"\n  V{vn}: {label}")
        print(f"    {count}/500 [{locked}]{marker}")
        print(f"    [{bar}]")
    print()


def cmd_advance(args):
    db = load_db()
    active_v = db["meta"].get("active_version", 1)
    versions = db["meta"].get("versions", {})
    next_v = active_v + 1

    if str(next_v) not in versions:
        print(f"  No Version {next_v} exists yet. Stay on V{active_v} until new words are added.")
        return

    if versions[str(next_v)]["count"] == 0:
        print(f"  Version {next_v} has no words yet. Stay on V{active_v}.")
        return

    db["meta"]["active_version"] = next_v
    save_db(db)
    print(f"\n  Advanced to V{next_v}: {versions[str(next_v)].get('label', '')}")
    print(f"  Learning commands will now draw from V{next_v} ({versions[str(next_v)]['count']} words).")
    print(f"  Use --version {active_v} to revisit V{active_v} words.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Vocabulary Mastery System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", "-v", type=int, default=None,
                        help="Filter to a specific version (e.g., --version 2)")
    sub = parser.add_subparsers(dest="command")

    # version-info
    sub.add_parser("version-info", help="Show version summary and active version")

    # advance
    sub.add_parser("advance", help="Advance to the next version when ready")

    # search
    p = sub.add_parser("search", help="Search for a word")
    p.add_argument("term", help="Search term")

    # define
    p = sub.add_parser("define", help="Show full word entry")
    p.add_argument("word", help="Word to define")

    # browse
    p = sub.add_parser("browse", help="Browse words alphabetically")
    p.add_argument("--register", help="Filter by register (formal, literary, etc.)")
    p.add_argument("--tag", help="Filter by tag")
    p.add_argument("--enriched-only", action="store_true", help="Show only enriched words")

    # random
    sub.add_parser("random", help="Show a random enriched word")

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # quiz
    p = sub.add_parser("quiz", help="Correct-or-misuse quiz")
    p.add_argument("-n", type=int, default=5, help="Number of questions")

    # flash
    p = sub.add_parser("flash", help="Flashcard drill")
    p.add_argument("-n", type=int, help="Number of cards (default 10)")
    p.add_argument("--weak", action="store_true", help="Only weak words (≤2)")
    p.add_argument("--new", action="store_true", help="Only unattempted words")
    p.add_argument("--word", help="Drill a specific word")

    # daily
    p = sub.add_parser("daily", help="Morning writing prompt")
    p.add_argument("-n", type=int, help="Number of words (default 3)")
    p.add_argument("--style", choices=["punchy", "persuasive", "measured", "craft"])

    # wotd
    sub.add_parser("wotd", help="Word of the day")

    # used
    p = sub.add_parser("used", help="Log real-world usage of a word")
    p.add_argument("word", help="Word you used")
    p.add_argument("--where", help="Where you used it (e.g., 'Substack post')")

    # progress
    sub.add_parser("progress", help="Show your progress overview")

    # suggest
    p = sub.add_parser("suggest", help="Suggest vocab words for a writing mode")
    p.add_argument("--mode", choices=list(MODE_REGISTERS.keys()), help="Writing mode")

    # review
    sub.add_parser("review", help="Words studied but never used in real writing")

    # challenge
    p = sub.add_parser("challenge", help="Writing challenge with specific words + mode")
    p.add_argument("--mode", choices=list(MODE_REGISTERS.keys()), help="Writing mode")

    # writing-progress
    sub.add_parser("writing-progress", help="Show writing progress trends")

    # lookup
    p = sub.add_parser("lookup", help="Fuzzy word recall + synonyms — handles misspellings")
    p.add_argument("term", help="Word to look up (misspellings OK)")

    # add
    p = sub.add_parser("add", help="Add new words to the database")
    p.add_argument("words", nargs="+", help="Word(s) to add")

    # sync
    sub.add_parser("sync", help="Sync vocab data to NAS")

    # help
    sub.add_parser("help", help="Show all commands")

    # words
    p = sub.add_parser("words", help="List every word — just the words")
    p.add_argument("--alpha", action="store_true", help="Wider columns")
    p.add_argument("--numbered", action="store_true", help="Numbered list")

    args = parser.parse_args()

    if not args.command or args.command == "help":
        print(f"""
  ╔══════════════════════════════════════════════════════╗
  ║          VOCABULARY MASTERY SYSTEM                   ║
  ╚══════════════════════════════════════════════════════╝

  ─── LOOK UP & EXPLORE ───────────────────────────────
  lookup <word>          Fuzzy recall + synonyms (misspellings OK)
  define <word>          Full word entry
  search <term>          Search across words, definitions, tags
  words                  List every word (--numbered, --alpha)
  browse                 Page through words (--register, --tag)
  random                 Random enriched word, full context

  ─── LEARN & DRILL ───────────────────────────────────
  flash                  Flashcard drill (-n 5, --weak, --new, --word X)
  quiz                   Correct-or-misuse identification game
  wotd                   Word of the day

  ─── WRITE ───────────────────────────────────────────
  daily                  Morning writing prompt (-n 5, --style X)
  suggest                Vocab words for a writing mode (--mode X)
  challenge              Writing challenge with words + mode (--mode X)

  ─── TRACK ───────────────────────────────────────────
  used <word>            Log real-world usage (--where "context")
  progress               Full progress dashboard
  stats                  Database stats (counts, registers, tags)
  review                 Words studied but never used in writing
  writing-progress       Writing session trends

  ─── MANAGE ──────────────────────────────────────────
  add <word>             Add a new word to the database
  version-info           Show version summary + active version
  advance                Move to the next version when ready
  help                   Show this menu

  ─── GLOBAL FLAGS ────────────────────────────────────
  --version N / -v N     Filter any command to version N

  ────────────────────────────────────────────────────
  Examples:
    python vocab.py lookup pusillanimis
    python vocab.py flash -n 5 --weak
    python vocab.py daily --style persuasive
    python vocab.py used Visceral --where "Substack post"
    python vocab.py add Ephemeral
""")
        return

    commands = {
        "search": cmd_search,
        "define": cmd_define,
        "browse": cmd_browse,
        "random": cmd_random,
        "stats": cmd_stats,
        "quiz": cmd_quiz,
        "flash": cmd_flash,
        "daily": cmd_daily,
        "wotd": cmd_wotd,
        "used": cmd_used,
        "progress": cmd_progress,
        "suggest": cmd_suggest,
        "review": cmd_review,
        "challenge": cmd_challenge,
        "writing-progress": cmd_writing_progress,
        "lookup": cmd_lookup,
        "add": cmd_add,
        "sync": cmd_sync,
        "words": cmd_words,
        "version-info": cmd_version_info,
        "advance": cmd_advance,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
