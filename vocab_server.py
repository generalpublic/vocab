"""
Local vocab enrichment server.
Runs on http://localhost:9876 — dashboard calls POST /add-word to enrich + save.
Usage: python vocab_server.py
"""
import json
import os
import sys
import webbrowser
from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

import anthropic

BASE = Path(__file__).parent
DB_PATH = BASE / "vocab_db.json"

ENRICH_PROMPT = """You are a vocabulary enrichment engine. Given a word, produce a JSON object with this EXACT structure. Be precise, literary, and useful for a writer learning to deploy this word.

{
  "word": "Word",
  "pos": ["noun"],
  "pronunciation": "phonetic guide like pruh-NUN-see-AY-shun",
  "definition": "clear, precise definition",
  "register": ["formal"],
  "tags": ["concept1", "concept2", "concept3"],
  "enriched": true,
  "examples": [
    {"context": "essay", "sentence": "Full sentence.", "why": "Why this usage is correct."},
    {"context": "professional", "sentence": "...", "why": "..."},
    {"context": "creative writing", "sentence": "...", "why": "..."}
  ],
  "misuses": [
    {"wrong": "Incorrect sentence.", "problem": "Why wrong.", "use_instead": "Better word."},
    {"wrong": "...", "problem": "...", "use_instead": "..."}
  ],
  "related": [
    {"word": "related1", "distinction": "How it differs."},
    {"word": "related2", "distinction": "..."},
    {"word": "related3", "distinction": "..."}
  ],
  "triggers": [
    "Situation when you should reach for this word",
    "Another situation",
    "A third situation"
  ]
}

Rules:
- EXACTLY 3 examples, 2 misuses, 3 related words, 3 triggers
- register values: formal, academic, literary, general, informal, technical, archaic, poetic, legal
- tags: 2-4 lowercase conceptual tags
- pos: noun, verb, adjective, adverb, conjunction, preposition
- Examples should show the word used correctly in varied contexts
- Misuses should show genuine mistakes writers make with this word
- Related words should be real alternatives with clear distinctions
- Triggers describe WHEN a writer should reach for this word
- Output ONLY the JSON object, no markdown fences, no explanation

The word to enrich: """


def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    db["meta"]["last_updated"] = str(date.today())
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def enrich_word(word):
    """Call Claude to enrich a word. Returns the enriched dict or raises."""
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": ENRICH_PROMPT + word}],
    )
    text = resp.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
    return json.loads(text)


def add_word_to_db(enriched):
    """Add enriched word to vocab_db.json in the current open version."""
    db = load_db()
    existing = {w["word"].lower() for w in db["words"]}

    word_lower = enriched["word"].lower()
    if word_lower in existing:
        return None, f"'{enriched['word']}' already exists in the database."

    # Find current open version
    versions = db["meta"].get("versions", {})
    active_v = None
    for vn in sorted(versions.keys(), key=int):
        if not versions[vn].get("locked", False):
            active_v = int(vn)
            break

    if active_v is None:
        next_v = max(int(k) for k in versions.keys()) + 1
        versions[str(next_v)] = {"count": 0, "locked": False, "label": f"Version {next_v}"}
        active_v = next_v

    # Auto-advance if version is full
    if versions[str(active_v)]["count"] >= 500:
        versions[str(active_v)]["locked"] = True
        active_v += 1
        versions[str(active_v)] = {"count": 0, "locked": False, "label": f"Version {active_v}"}

    enriched["version"] = active_v
    enriched["date_added"] = str(date.today())

    db["words"].append(enriched)
    versions[str(active_v)]["count"] += 1
    db["meta"]["word_count"] = len(db["words"])
    save_db(db)

    return enriched, None


class VocabHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/add-word":
            self._handle_add_word()
        else:
            self.send_error(404)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "":
            self.path = "/vocab_dashboard.html"
        super().do_GET()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _handle_add_word(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            word = body.get("word", "").strip()

            if not word:
                self._json_response(400, {"error": "No word provided."})
                return

            # Check if already exists
            db = load_db()
            if word.lower() in {w["word"].lower() for w in db["words"]}:
                self._json_response(409, {"error": f"'{word}' already exists."})
                return

            # Enrich via Claude
            enriched = enrich_word(word)

            # Validate
            for field in ["word", "pos", "pronunciation", "definition", "register",
                          "tags", "examples", "misuses", "related", "triggers"]:
                if field not in enriched:
                    self._json_response(500, {"error": f"Enrichment missing field: {field}"})
                    return

            result, err = add_word_to_db(enriched)
            if err:
                self._json_response(409, {"error": err})
                return

            self._json_response(200, {"word": result})

        except json.JSONDecodeError:
            self._json_response(400, {"error": "Invalid JSON."})
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        # Cleaner log output
        sys.stderr.write(f"  [{self.log_date_time_string()}] {format % args}\n")


def main():
    port = 9876
    server = HTTPServer(("127.0.0.1", port), VocabHandler)
    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  Vocab Dashboard Server                          ║")
    print(f"  ║  http://localhost:{port}                          ║")
    print(f"  ╚══════════════════════════════════════════════════╝")
    print(f"  Serving vocab_dashboard.html + enrichment API")
    print(f"  POST /add-word  {{\"word\": \"...\"}} → enrich + save")
    print(f"  Ctrl+C to stop\n")

    webbrowser.open(f"http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
