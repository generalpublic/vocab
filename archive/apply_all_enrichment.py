"""
Apply all enrichment batches to vocab_db.json.
Run once: python apply_all_enrichment.py
"""
import json
from datetime import date

null = None  # handle JSON-style nulls in batch files

# Load all batches
all_enriched = []
for i in range(1, 8):
    filename = f"enrich_batch_{i}.py"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        local_ns = {"null": None}
        exec(code, local_ns)
        batch = local_ns["ENRICHED"]
        print(f"  Batch {i}: {len(batch)} words")
        all_enriched.extend(batch)
    except Exception as e:
        print(f"  ERROR in batch {i}: {e}")

# Also include the original 25 from enrich_words.py
try:
    with open("enrich_words.py", "r", encoding="utf-8") as f:
        code = f.read()
    local_ns = {"null": None}
    exec(code, local_ns)
    original = local_ns["ENRICHED"]
    print(f"  Original enrichment: {len(original)} words")
    all_enriched.extend(original)
except Exception as e:
    print(f"  Skipping original enrichment: {e}")

print(f"\nTotal enrichment entries: {len(all_enriched)}")

# Build lookup map (last entry wins for duplicates)
enrichment_map = {}
for e in all_enriched:
    enrichment_map[e["word"].lower()] = e

print(f"Unique words to enrich: {len(enrichment_map)}")

# Load and update database
with open("vocab_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

enriched_count = 0
not_found = []

for entry in db["words"]:
    key = entry["word"].lower()
    if key in enrichment_map:
        e = enrichment_map[key]
        entry["pronunciation"] = e.get("pronunciation", entry.get("pronunciation"))
        entry["register"] = e.get("register", [])
        entry["tags"] = e.get("tags", [])
        entry["examples"] = e.get("examples", [])
        entry["misuses"] = e.get("misuses", [])
        entry["related"] = e.get("related", [])
        entry["triggers"] = e.get("triggers", [])
        entry["enriched"] = True
        enriched_count += 1
        del enrichment_map[key]

# Check for any enrichment entries that didn't match a DB word
if enrichment_map:
    print(f"\nWARNING: {len(enrichment_map)} enrichment entries didn't match any DB word:")
    for k in sorted(enrichment_map.keys()):
        print(f"  - {k}")

db["meta"]["last_updated"] = str(date.today())
db["meta"]["word_count"] = len(db["words"])

with open("vocab_db.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

total = len(db["words"])
still_skeleton = sum(1 for w in db["words"] if not w.get("enriched"))
print(f"\nDone. {enriched_count} words enriched.")
print(f"Total: {total} | Enriched: {total - still_skeleton} | Skeletons remaining: {still_skeleton}")
print(f"File size: {len(json.dumps(db, indent=2, ensure_ascii=False)):,} bytes")
