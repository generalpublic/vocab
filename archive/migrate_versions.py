"""One-time migration: add version field to all existing words, update meta."""
import json
from pathlib import Path

DB = Path(__file__).parent / "vocab_db.json"

with open(DB, "r", encoding="utf-8") as f:
    db = json.load(f)

# Stamp every existing word as version 1
for w in db["words"]:
    w["version"] = 1

# Update meta
db["meta"] = {
    "schema_version": 2,
    "last_updated": "2026-03-30",
    "word_count": len(db["words"]),
    "active_version": 1,
    "versions": {
        "1": {"count": len(db["words"]), "locked": True, "label": "Foundation"},
        "2": {"count": 0, "locked": False, "label": "Literary & Academic"}
    }
}

with open(DB, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Migration complete: {len(db['words'])} words stamped as V1")
print(f"Meta: {json.dumps(db['meta'], indent=2)}")
