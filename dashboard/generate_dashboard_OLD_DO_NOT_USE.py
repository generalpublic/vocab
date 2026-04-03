"""
DO NOT RUN THIS FILE.

This generates the OLD sidebar-layout dashboard and WILL DESTROY the
premium top-bar dashboard (vocab_dashboard.html). This has caused
production bugs multiple times.

To update words in the dashboard, inject them into the const WORDS
array in vocab_dashboard.html directly. See the memory file
feedback_vocab_sync.md for the correct approach.
"""
import sys
print("\n  ERROR: This script is deprecated and will destroy the premium dashboard.")
print("  Do NOT run it. See feedback_vocab_sync.md for how to update words.\n")
sys.exit(1)

# --- ORIGINAL CODE BELOW (disabled) ---
"""
Generate a self-contained HTML vocabulary dashboard from vocab_db.json.
Outputs vocab_dashboard.html — open in any browser, no server needed.
"""

import json
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "vocab_db.json"
USAGE_LOG_PATH = SCRIPT_DIR / "usage_log.json"
FLASHCARD_PATH = SCRIPT_DIR / "flashcard_progress.json"
OUTPUT_PATH = SCRIPT_DIR / "vocab_dashboard.html"
NAS_PATH = Path(r"Z:\Sek\Vocab")


def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate():
    db = load_json(DB_PATH)
    usage = load_json(USAGE_LOG_PATH)
    flashcards = load_json(FLASHCARD_PATH)

    words = db.get("words", [])
    meta = db.get("meta", {})

    # Collect all tags, registers, POS for filters
    all_tags = sorted({t for w in words for t in w.get("tags", [])})
    all_registers = sorted({r for w in words for r in w.get("register", [])})
    all_pos = sorted({p for w in words for p in w.get("pos", [])})
    all_versions = sorted({w.get("version", 1) for w in words})
    versions_meta = meta.get("versions", {})
    active_version = meta.get("active_version", 1)

    words_json = json.dumps(words, ensure_ascii=False)
    usage_json = json.dumps(usage, ensure_ascii=False)
    flashcard_json = json.dumps(flashcards, ensure_ascii=False)
    tags_json = json.dumps(all_tags)
    registers_json = json.dumps(all_registers)
    pos_json = json.dumps(all_pos)
    versions_json = json.dumps(all_versions)
    versions_meta_json = json.dumps(versions_meta, ensure_ascii=False)
    active_version_json = json.dumps(active_version)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vocab Dashboard — {meta.get('word_count', len(words))} Words</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #1a1a2e; line-height: 1.6; }}

/* Layout */
.app {{ display: flex; min-height: 100vh; }}
.sidebar {{ width: 260px; background: #fff; border-right: 1px solid #e0e0e0; padding: 20px; position: fixed; top: 0; left: 0; bottom: 0; overflow-y: auto; z-index: 10; }}
.main {{ margin-left: 260px; flex: 1; padding: 24px; }}

/* Sidebar */
.logo {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; color: #1a1a2e; }}
.subtitle {{ font-size: 13px; color: #888; margin-bottom: 20px; }}
.search-box {{ width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; margin-bottom: 16px; outline: none; transition: border-color 0.2s; }}
.search-box:focus {{ border-color: #4a6cf7; }}
.filter-section {{ margin-bottom: 16px; }}
.filter-title {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: #888; margin-bottom: 8px; letter-spacing: 0.5px; }}
.filter-chips {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.chip {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; color: #555; transition: all 0.15s; }}
.chip:hover {{ border-color: #4a6cf7; color: #4a6cf7; }}
.chip.active {{ background: #4a6cf7; color: #fff; border-color: #4a6cf7; }}
.filter-clear {{ font-size: 12px; color: #4a6cf7; cursor: pointer; margin-top: 8px; display: none; }}
.filter-clear.visible {{ display: block; }}
.sort-toggle {{ display: flex; align-items: center; gap: 8px; margin-left: auto; }}
.sort-btn {{ padding: 5px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; color: #555; transition: all 0.15s; }}
.sort-btn:hover {{ border-color: #4a6cf7; color: #4a6cf7; }}
.sort-btn.active {{ background: #4a6cf7; color: #fff; border-color: #4a6cf7; }}
.synonym-section {{ margin-bottom: 16px; }}
.synonym-group {{ margin-bottom: 8px; }}
.synonym-group-label {{ font-size: 12px; font-weight: 600; color: #444; cursor: pointer; padding: 4px 0; }}
.synonym-group-label:hover {{ color: #4a6cf7; }}
.synonym-group-words {{ display: flex; flex-wrap: wrap; gap: 3px; margin-top: 3px; }}
.synonym-word {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #f0f7ff; color: #4a6cf7; cursor: pointer; border: 1px solid #d0e0f7; transition: all 0.15s; }}
.synonym-word:hover {{ background: #4a6cf7; color: #fff; }}
.synonym-filter-active {{ background: #4a6cf7; color: #fff; border-color: #4a6cf7; }}
.synonym-list {{ max-height: 300px; overflow-y: auto; }}
.stats-bar {{ font-size: 12px; color: #888; padding: 12px 0; border-top: 1px solid #eee; margin-top: 12px; }}
.color-legend {{ margin-bottom: 16px; }}
.legend-items {{ display: flex; flex-wrap: wrap; gap: 6px 12px; }}
.legend-item {{ display: inline-flex; align-items: center; gap: 5px; font-size: 12px; color: #555; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}

/* Tabs */
.tabs {{ display: flex; gap: 0; margin-bottom: 24px; border-bottom: 2px solid #e0e0e0; }}
.tab {{ padding: 10px 24px; cursor: pointer; font-size: 14px; font-weight: 500; color: #888; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.15s; }}
.tab:hover {{ color: #4a6cf7; }}
.tab.active {{ color: #4a6cf7; border-bottom-color: #4a6cf7; }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* Cards grid */
.card-count {{ font-size: 14px; color: #888; margin-bottom: 16px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
.card {{ background: #fff; border: 1px solid #e8e8e8; border-radius: 10px; padding: 18px; cursor: pointer; transition: box-shadow 0.15s, border-color 0.15s; }}
.card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-color: #d0d0d0; }}
.card.expanded {{ grid-column: 1 / -1; cursor: default; }}
.card-header {{ display: flex; justify-content: space-between; align-items: flex-start; }}
.word-title {{ font-size: 20px; font-weight: 700; color: #1a1a2e; }}
.pronunciation {{ font-size: 13px; color: #888; font-style: italic; margin-left: 8px; }}
.pos-badges {{ display: flex; gap: 4px; margin-top: 2px; }}
.pos-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #f0f0f0; color: #666; }}
.definition {{ font-size: 14px; color: #444; margin-top: 8px; }}
.register-tags {{ display: flex; gap: 4px; margin-top: 8px; flex-wrap: wrap; }}
.register-tag {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #e8f0fe; color: #4a6cf7; }}
.tag-pill {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #f3f0ff; color: #7c5cbf; }}
.synonym-row {{ display: flex; align-items: center; gap: 6px; margin-top: 8px; flex-wrap: wrap; }}
.synonym-label {{ font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; }}
.synonym-pill {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }}
.version-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-left: 8px; flex-shrink: 0; }}
.version-dot.v1 {{ background: #4a6cf7; }}
.version-dot.v2 {{ background: #9b59b6; }}
.version-dot.v3 {{ background: #e67e22; }}
.version-chip {{ position: relative; }}
.version-chip .chip-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 4px; vertical-align: middle; }}
.version-chip .chip-dot.v1 {{ background: #4a6cf7; }}
.version-chip .chip-dot.v2 {{ background: #9b59b6; }}
.version-chip .chip-dot.v3 {{ background: #e67e22; }}
.reg-formal {{ background: #eef1ff !important; color: #3a5bc7 !important; border-color: #c8d0f7 !important; }}
.reg-formal:hover {{ background: #3a5bc7 !important; color: #fff !important; }}
.reg-literary {{ background: #f5eeff !important; color: #7c3aed !important; border-color: #ddc8f7 !important; }}
.reg-literary:hover {{ background: #7c3aed !important; color: #fff !important; }}
.reg-academic {{ background: #e8faf5 !important; color: #0d9488 !important; border-color: #b2f0e4 !important; }}
.reg-academic:hover {{ background: #0d9488 !important; color: #fff !important; }}
.reg-general {{ background: #f3f4f6 !important; color: #6b7280 !important; border-color: #d1d5db !important; }}
.reg-general:hover {{ background: #6b7280 !important; color: #fff !important; }}
.reg-technical {{ background: #fff7ed !important; color: #c2410c !important; border-color: #fed7aa !important; }}
.reg-technical:hover {{ background: #c2410c !important; color: #fff !important; }}
.reg-informal {{ background: #ecfdf5 !important; color: #059669 !important; border-color: #a7f3d0 !important; }}
.reg-informal:hover {{ background: #059669 !important; color: #fff !important; }}
.reg-archaic {{ background: #fef2f2 !important; color: #991b1b !important; border-color: #fecaca !important; }}
.reg-archaic:hover {{ background: #991b1b !important; color: #fff !important; }}

/* Expanded card sections */
.card-detail {{ margin-top: 16px; display: none; }}
.card.expanded .card-detail {{ display: block; }}
.detail-section {{ margin-top: 14px; }}
.detail-title {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: #888; letter-spacing: 0.5px; margin-bottom: 6px; }}
.example-item {{ background: #fafafa; border-left: 3px solid #4a6cf7; padding: 10px 14px; margin-bottom: 8px; border-radius: 0 6px 6px 0; }}
.example-context {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: #4a6cf7; margin-bottom: 2px; }}
.example-sentence {{ font-size: 14px; color: #333; font-style: italic; }}
.example-why {{ font-size: 12px; color: #888; margin-top: 4px; }}
.misuse-item {{ background: #fff5f5; border-left: 3px solid #e74c3c; padding: 10px 14px; margin-bottom: 8px; border-radius: 0 6px 6px 0; }}
.misuse-wrong {{ font-size: 14px; color: #c0392b; font-style: italic; text-decoration: line-through; }}
.misuse-problem {{ font-size: 12px; color: #666; margin-top: 4px; }}
.misuse-instead {{ font-size: 12px; color: #27ae60; margin-top: 2px; }}
.related-item {{ display: inline-block; margin-right: 6px; margin-bottom: 6px; }}
.related-link {{ padding: 4px 12px; border-radius: 16px; background: #f0f7ff; color: #4a6cf7; font-size: 13px; cursor: pointer; text-decoration: none; border: 1px solid #d0e0f7; transition: all 0.15s; }}
.related-link:hover {{ background: #4a6cf7; color: #fff; }}
.related-distinction {{ font-size: 12px; color: #888; display: none; margin-top: 2px; }}
.related-item:hover .related-distinction {{ display: block; }}
.trigger-item {{ font-size: 13px; color: #555; padding: 4px 0; }}
.trigger-item::before {{ content: "→ "; color: #4a6cf7; font-weight: 600; }}
.usage-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #e8f5e9; color: #2e7d32; margin-left: 8px; }}
.version-badge {{ font-size: 10px; padding: 2px 7px; border-radius: 10px; margin-left: 6px; font-weight: 600; }}
.version-badge.v1 {{ background: #f3f4f6; color: #6b7280; }}
.version-badge.v2 {{ background: #eff6ff; color: #4a6cf7; }}
.version-badge.v3 {{ background: #ecfdf5; color: #10b981; }}
.version-chip {{ font-weight: 500; }}

/* Add Word button + modal */
.add-word-btn {{ width: 100%; padding: 10px; margin-bottom: 12px; border: 2px dashed #4a6cf7; border-radius: 8px; background: #f8faff; color: #4a6cf7; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s; }}
.add-word-btn:hover {{ background: #4a6cf7; color: #fff; }}
.modal-overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 100; align-items: center; justify-content: center; }}
.modal-overlay.visible {{ display: flex; }}
.modal {{ background: #fff; border-radius: 12px; padding: 28px; width: 480px; max-width: 90vw; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }}
.modal h2 {{ font-size: 20px; margin-bottom: 16px; color: #1a1a2e; }}
.modal-input {{ width: 100%; padding: 12px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; margin-bottom: 16px; }}
.modal-input:focus {{ border-color: #4a6cf7; }}
.modal-actions {{ display: flex; gap: 8px; justify-content: flex-end; }}
.modal-btn {{ padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.15s; }}
.modal-btn.primary {{ background: #4a6cf7; color: #fff; }}
.modal-btn.primary:hover {{ background: #3b5ce4; }}
.modal-btn.primary:disabled {{ background: #a0b4f7; cursor: wait; }}
.modal-btn.secondary {{ background: #f0f0f0; color: #555; }}
.modal-btn.secondary:hover {{ background: #e0e0e0; }}
.modal-status {{ font-size: 13px; margin-top: 12px; padding: 10px; border-radius: 6px; display: none; }}
.modal-status.loading {{ display: block; background: #f0f7ff; color: #4a6cf7; }}
.modal-status.success {{ display: block; background: #e8f5e9; color: #2e7d32; }}
.modal-status.error {{ display: block; background: #fff5f5; color: #c0392b; }}

/* Graph */
#graph-container {{ width: 100%; height: calc(100vh - 140px); position: relative; background: #fff; border-radius: 10px; border: 1px solid #e8e8e8; overflow: auto; }}
#graph-canvas {{ display: block; }}
#graph-tooltip {{ position: fixed; display: none; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); font-size: 13px; max-width: 300px; pointer-events: none; z-index: 20; }}

/* Triggers tab */
.triggers-toolbar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-bottom: 20px; padding: 16px; background: #fff; border-radius: 10px; border: 1px solid #e8e8e8; }}
.trigger-search {{ flex: 1; min-width: 200px; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; }}
.trigger-search:focus {{ border-color: #4a6cf7; }}
.context-filters {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.ctx-btn {{ padding: 6px 14px; border-radius: 16px; font-size: 12px; cursor: pointer; border: 1px solid #ddd; background: #fff; color: #555; transition: all 0.15s; }}
.ctx-btn:hover {{ border-color: #4a6cf7; color: #4a6cf7; }}
.ctx-btn.active {{ background: #4a6cf7; color: #fff; border-color: #4a6cf7; }}
.quiz-btn {{ padding: 6px 16px; border-radius: 16px; font-size: 12px; font-weight: 600; cursor: pointer; border: 2px solid #e8e8e8; background: #fff; color: #555; transition: all 0.15s; }}
.quiz-btn.active {{ background: #1a1a2e; color: #fff; border-color: #1a1a2e; }}
.scenario-category {{ margin-bottom: 8px; }}
.scenario-category summary {{ font-size: 16px; font-weight: 600; color: #1a1a2e; cursor: pointer; padding: 10px 0; list-style: none; display: flex; align-items: center; gap: 8px; }}
.scenario-category summary::-webkit-details-marker {{ display: none; }}
.scenario-category summary::before {{ content: "\\25B6"; font-size: 10px; color: #888; transition: transform 0.2s; }}
.scenario-category[open] summary::before {{ transform: rotate(90deg); }}
.scenario-category .cat-count {{ font-size: 13px; color: #888; font-weight: 400; }}
.scenario-cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; padding: 8px 0 16px; }}
.scenario-card {{ background: #fff; border: 1px solid #e8e8e8; border-radius: 10px; padding: 16px; transition: box-shadow 0.15s, border-color 0.15s; }}
.scenario-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-color: #d0d0d0; }}
.scenario-trigger {{ font-size: 15px; font-weight: 500; color: #1a1a2e; line-height: 1.5; margin-bottom: 10px; }}
.scenario-trigger::before {{ content: "When "; font-weight: 400; color: #888; font-size: 13px; text-transform: uppercase; letter-spacing: 0.3px; }}
.scenario-example {{ font-size: 13px; color: #666; font-style: italic; line-height: 1.5; margin-bottom: 12px; padding: 8px 12px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #4a6cf7; }}
.scenario-def {{ font-size: 12px; color: #888; margin-bottom: 10px; }}
.scenario-footer {{ display: flex; align-items: center; gap: 8px; }}
.scenario-word {{ display: inline-block; padding: 5px 14px; border-radius: 16px; background: #f0f7ff; color: #4a6cf7; font-size: 14px; font-weight: 600; cursor: pointer; border: 1px solid #d0e0f7; text-decoration: none; transition: all 0.15s; }}
.scenario-word:hover {{ background: #4a6cf7; color: #fff; }}
.scenario-reveal-btn {{ display: none; padding: 5px 14px; border-radius: 16px; font-size: 13px; cursor: pointer; border: 1px solid #ddd; background: #fff; color: #555; transition: all 0.15s; }}
.scenario-reveal-btn:hover {{ border-color: #4a6cf7; color: #4a6cf7; }}
.quiz-active .scenario-example, .quiz-active .scenario-word, .quiz-active .scenario-def {{ display: none; }}
.quiz-active .scenario-reveal-btn {{ display: inline-block; }}
.quiz-active .scenario-card.revealed .scenario-example, .quiz-active .scenario-card.revealed .scenario-word, .quiz-active .scenario-card.revealed .scenario-def {{ display: block; }}
.quiz-active .scenario-card.revealed .scenario-word {{ display: inline-block; }}
.quiz-active .scenario-card.revealed .scenario-reveal-btn {{ display: none; }}
.triggers-empty {{ text-align: center; padding: 40px; color: #888; font-size: 15px; }}

/* Mobile */
@media (max-width: 768px) {{
    .sidebar {{ position: relative; width: 100%; border-right: none; border-bottom: 1px solid #e0e0e0; }}
    .main {{ margin-left: 0; }}
    .app {{ flex-direction: column; }}
    .cards {{ grid-template-columns: 1fr; }}
    .card.expanded {{ grid-column: 1; }}
}}

/* Print */
@media print {{
    .sidebar {{ display: none; }}
    .main {{ margin-left: 0; }}
    .card {{ break-inside: avoid; border: 1px solid #ccc; }}
    .tabs {{ display: none; }}
}}
</style>
</head>
<body>
<div class="app">
    <aside class="sidebar">
        <div class="logo">Vocab</div>
        <div class="subtitle">{meta.get('word_count', len(words))} words</div>
        <button class="add-word-btn" onclick="openAddModal()">+ Add Word</button>
        <input type="text" class="search-box" id="search" placeholder="Search words, definitions, tags..." autofocus>

        <div class="filter-section">
            <div class="filter-title">Version</div>
            <div class="filter-chips" id="version-filters"></div>
        </div>
        <div class="filter-section">
            <div class="filter-title">Register</div>
            <div class="filter-chips" id="register-filters"></div>
        </div>
        <div class="filter-section">
            <div class="filter-title">Part of Speech</div>
            <div class="filter-chips" id="pos-filters"></div>
        </div>
        <div class="filter-section">
            <div class="filter-title">Tags</div>
            <div class="filter-chips" id="tag-filters" style="max-height: 200px; overflow-y: auto;"></div>
        </div>

        <div class="filter-section synonym-section">
            <div class="filter-title">Synonym Groups</div>
            <div class="synonym-list" id="synonym-groups"></div>
        </div>
        <div class="filter-clear" id="clear-filters" onclick="clearFilters()">Clear all filters</div>
        <div class="stats-bar" id="stats-bar"></div>
    </aside>
    <main class="main">
        <div class="tabs">
            <div class="tab active" data-tab="cards" onclick="switchTab('cards')">Cards</div>
            <div class="tab" data-tab="triggers" onclick="switchTab('triggers')">Triggers</div>
            <div class="tab" data-tab="graph" onclick="switchTab('graph')">Graph</div>
            <div class="sort-toggle">
                <span style="font-size:12px;color:#888;">Sort:</span>
                <span class="sort-btn active" id="sort-shuffle" onclick="setSortMode('shuffle')">Shuffle</span>
                <span class="sort-btn" id="sort-alpha" onclick="setSortMode('alpha')">A-Z</span>
            </div>
        </div>
        <div class="tab-content active" id="tab-cards">
            <div class="card-count" id="card-count"></div>
            <div class="cards" id="cards-grid"></div>
        </div>
        <div class="tab-content" id="tab-triggers">
            <div class="triggers-toolbar">
                <input class="trigger-search" id="trigger-search" placeholder="Search scenarios, words, examples..." />
                <div class="context-filters">
                    <button class="ctx-btn" data-ctx="essay">Essay</button>
                    <button class="ctx-btn" data-ctx="professional">Professional</button>
                    <button class="ctx-btn" data-ctx="creative writing">Creative</button>
                </div>
                <button class="quiz-btn" id="quiz-toggle" onclick="toggleQuizMode()">Quiz Mode</button>
            </div>
            <div id="triggers-index"></div>
        </div>
        <div class="tab-content" id="tab-graph">
            <div id="graph-container">
                <canvas id="graph-canvas"></canvas>
                <div id="graph-tooltip"></div>
            </div>
        </div>
    </main>
</div>

<script>
const WORDS = {words_json};
const USAGE = {usage_json};
const FLASHCARDS = {flashcard_json};
const ALL_TAGS = {tags_json};
const ALL_REGISTERS = {registers_json};
const ALL_POS = {pos_json};
const ALL_VERSIONS = {versions_json};
const VERSIONS_META = {versions_meta_json};
const ACTIVE_VERSION = {active_version_json};

// Build lookup
const wordMap = {{}};
WORDS.forEach((w, i) => {{ wordMap[w.word.toLowerCase()] = i; }});

// Shuffle helper (Fisher-Yates)
function shuffle(arr) {{
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }}
    return a;
}}

// State
let activeFilters = {{ tags: new Set(), registers: new Set(), pos: new Set(), versions: new Set() }};
let searchQuery = '';
let expandedCard = null;
let sortMode = 'shuffle';
let shuffledOrder = shuffle(WORDS);
let synonymGroupFilter = null;  // set of word names, or null

// Build synonym clusters via union-find on `related` edges
function buildSynonymClusters() {{
    const parent = {{}};
    function find(x) {{ if (parent[x] !== x) parent[x] = find(parent[x]); return parent[x]; }}
    function union(a, b) {{ parent[find(a)] = find(b); }}
    WORDS.forEach(w => {{ parent[w.word.toLowerCase()] = w.word.toLowerCase(); }});
    WORDS.forEach(w => {{
        (w.related || []).forEach(r => {{
            const rk = r.word.toLowerCase();
            if (!(rk in parent)) parent[rk] = rk;
            union(w.word.toLowerCase(), rk);
        }});
    }});
    // Group by root
    const groups = {{}};
    Object.keys(parent).forEach(k => {{
        const root = find(k);
        if (!groups[root]) groups[root] = [];
        groups[root].push(k);
    }});
    // Only keep groups with 2+ members, sort by size desc
    return Object.values(groups)
        .filter(g => g.length >= 2)
        .sort((a, b) => b.length - a.length)
        .map(g => g.sort());
}}

// Init
function init() {{
    buildVersionChips();
    buildFilterChips('register-filters', ALL_REGISTERS, 'registers');
    buildFilterChips('pos-filters', ALL_POS, 'pos');
    buildFilterChips('tag-filters', ALL_TAGS, 'tags');
    buildSynonymGroupsUI();
    renderCards();
    updateStats();
    buildTriggerIndex();
}}

function buildVersionChips() {{
    const container = document.getElementById('version-filters');
    container.innerHTML = ALL_VERSIONS.map(v => {{
        const vm = VERSIONS_META[String(v)] || {{}};
        const count = WORDS.filter(w => (w.version || 1) === v).length;
        const label = vm.label || ('V' + v);
        return `<span class="chip version-chip" data-key="versions" data-value="${{v}}" onclick="toggleFilter(this, 'versions', '${{v}}')"><span class="chip-dot v${{v}}"></span>${{label}} (${{count}})</span>`;
    }}).join('') + `<span class="chip version-chip" data-key="versions" data-value="all" onclick="selectAllVersions(this)"><span class="chip-dot" style="background:#888"></span>All (${{WORDS.length}})</span>`;
}}

function selectAllVersions(el) {{
    // Clear version filter to show all
    activeFilters.versions.clear();
    document.querySelectorAll('#version-filters .chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    renderCards();
    buildTriggerIndex();
}}

function getRegClass(w) {{
    const reg = (w.register || ['general'])[0].toLowerCase();
    return 'reg-' + reg;
}}

function buildSynonymGroupsUI() {{
    const clusters = buildSynonymClusters();
    const container = document.getElementById('synonym-groups');
    container.innerHTML = clusters.map((group, gi) => {{
        // Use the first word that's in our DB as the label
        const labelWord = group.find(g => wordMap[g] !== undefined) || group[0];
        const displayWords = group.slice(0, 8);
        const more = group.length > 8 ? ` +${{group.length - 8}}` : '';
        return `<div class="synonym-group" data-group="${{gi}}">
            <div class="synonym-group-words">
                ${{displayWords.map(w => {{
                    const display = WORDS[wordMap[w]] ? WORDS[wordMap[w]].word : w;
                    return `<span class="synonym-word" onclick="toggleSynonymGroup(${{gi}})">${{display}}</span>`;
                }}).join('')}}
                ${{more ? `<span style="font-size:11px;color:#888">${{more}}</span>` : ''}}
            </div>
        </div>`;
    }}).join('');
    // Store clusters globally
    window._synonymClusters = clusters;
}}

function toggleSynonymGroup(gi) {{
    const cluster = window._synonymClusters[gi];
    if (synonymGroupFilter && synonymGroupFilter._gi === gi) {{
        synonymGroupFilter = null;
        document.querySelectorAll('.synonym-group').forEach(g => g.querySelectorAll('.synonym-word').forEach(w => w.classList.remove('synonym-filter-active')));
    }} else {{
        const nameSet = new Set(cluster);
        nameSet._gi = gi;
        synonymGroupFilter = nameSet;
        document.querySelectorAll('.synonym-group').forEach((g, i) => {{
            g.querySelectorAll('.synonym-word').forEach(w => w.classList.toggle('synonym-filter-active', i === gi));
        }});
    }}
    expandedCard = null;
    renderCards();
}}

function setSortMode(mode) {{
    sortMode = mode;
    if (mode === 'shuffle') shuffledOrder = shuffle(WORDS);
    document.getElementById('sort-shuffle').classList.toggle('active', mode === 'shuffle');
    document.getElementById('sort-alpha').classList.toggle('active', mode === 'alpha');
    expandedCard = null;
    renderCards();
}}

const REG_COLORS = {{ formal:'#3a5bc7', literary:'#7c3aed', academic:'#0d9488', general:'#6b7280', technical:'#c2410c', informal:'#059669', archaic:'#991b1b', poetic:'#7c3aed', legal:'#991b1b', philosophical:'#0d9488', scientific:'#c2410c', medical:'#c2410c' }};

function buildFilterChips(containerId, items, filterKey) {{
    const container = document.getElementById(containerId);
    container.innerHTML = items.map(item => {{
        const dot = filterKey === 'registers' && REG_COLORS[item.toLowerCase()]
            ? `<span class="legend-dot" style="background:${{REG_COLORS[item.toLowerCase()]}};width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px;vertical-align:middle"></span>`
            : '';
        return `<span class="chip" data-key="${{filterKey}}" data-value="${{item}}" onclick="toggleFilter(this, '${{filterKey}}', '${{item}}')">${{dot}}${{item}}</span>`;
    }}).join('');
}}

function toggleFilter(el, key, value) {{
    if (activeFilters[key].has(value)) {{
        activeFilters[key].delete(value);
        el.classList.remove('active');
    }} else {{
        activeFilters[key].add(value);
        el.classList.add('active');
    }}
    // Deselect "All" chip when specific versions are picked
    if (key === 'versions') {{
        const allChip = document.querySelector('#version-filters .chip[data-value="all"]');
        if (allChip) allChip.classList.remove('active');
    }}
    document.getElementById('clear-filters').classList.toggle('visible',
        activeFilters.tags.size + activeFilters.registers.size + activeFilters.pos.size + activeFilters.versions.size > 0);
    renderCards();
    buildTriggerIndex();
}}

function clearFilters() {{
    activeFilters = {{ tags: new Set(), registers: new Set(), pos: new Set(), versions: new Set() }};
    synonymGroupFilter = null;
    document.querySelectorAll('.chip.active').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.synonym-word').forEach(w => w.classList.remove('synonym-filter-active'));
    document.getElementById('clear-filters').classList.remove('visible');
    renderCards();
    buildTriggerIndex();
}}

function matchesSearch(w) {{
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const fields = [
        w.word, w.definition || '',
        (w.tags || []).join(' '),
        (w.triggers || []).join(' '),
        (w.examples || []).map(e => e.sentence).join(' '),
        (w.related || []).map(r => r.word).join(' ')
    ];
    return fields.some(f => f.toLowerCase().includes(q));
}}

function matchesFilters(w) {{
    if (activeFilters.versions.size > 0 && !activeFilters.versions.has(String(w.version || 1))) return false;
    if (activeFilters.tags.size > 0 && !(w.tags || []).some(t => activeFilters.tags.has(t))) return false;
    if (activeFilters.registers.size > 0 && !(w.register || []).some(r => activeFilters.registers.has(r))) return false;
    if (activeFilters.pos.size > 0 && !(w.pos || []).some(p => activeFilters.pos.has(p))) return false;
    return true;
}}

function getUsageCount(word) {{
    const entries = USAGE[word] || [];
    return entries.length;
}}

function renderCards() {{
    const grid = document.getElementById('cards-grid');
    const source = sortMode === 'alpha' ? WORDS : shuffledOrder;
    let filtered = source.filter(w => matchesSearch(w) && matchesFilters(w));
    if (synonymGroupFilter) {{
        filtered = filtered.filter(w => synonymGroupFilter.has(w.word.toLowerCase()));
    }}
    document.getElementById('card-count').textContent = `Showing ${{filtered.length}} of ${{WORDS.length}} words`;

    grid.innerHTML = filtered.map((w, i) => {{
        const idx = WORDS.indexOf(w);
        const usageCount = getUsageCount(w.word);
        const isExpanded = expandedCard === idx;
        return `
        <div class="card ${{isExpanded ? 'expanded' : ''}}" id="card-${{idx}}" onclick="toggleCard(${{idx}})">
            <div class="card-header">
                <div>
                    <span class="word-title">${{esc(w.word)}}</span>
                    <span class="pronunciation">${{esc(w.pronunciation || '')}}</span>
                    <span class="version-dot v${{w.version || 1}}" title="Version ${{w.version || 1}}"></span>
                    <span class="version-badge v${{w.version || 1}}">V${{w.version || 1}}</span>
                    ${{usageCount > 0 ? `<span class="usage-badge">used ${{usageCount}}x</span>` : ''}}
                </div>
                <div class="pos-badges">
                    ${{(w.pos || []).map(p => `<span class="pos-badge">${{p}}</span>`).join('')}}
                </div>
            </div>
            <div class="definition">${{esc(w.definition || '')}}</div>
            <div class="register-tags">
                ${{(w.register || []).map(r => `<span class="register-tag">${{r}}</span>`).join('')}}
                ${{(w.tags || []).map(t => `<span class="tag-pill">${{t}}</span>`).join('')}}
            </div>
            ${{(w.synonyms && w.synonyms.length) ? `<div class="synonym-row"><span class="synonym-label">Synonyms</span> ${{w.synonyms.map(s => `<span class="synonym-pill">${{esc(s)}}</span>`).join('')}}</div>` : ''}}
            <div class="card-detail">
                ${{renderDetail(w)}}
            </div>
        </div>`;
    }}).join('');
}}

function renderDetail(w) {{
    let html = '';
    if (w.triggers && w.triggers.length) {{
        html += `<div class="detail-section"><div class="detail-title">When to use</div>
            ${{w.triggers.map(t => `<div class="trigger-item">${{esc(t)}}</div>`).join('')}}</div>`;
    }}
    if (w.examples && w.examples.length) {{
        html += `<div class="detail-section"><div class="detail-title">Examples</div>
            ${{w.examples.map(e => `
                <div class="example-item">
                    <div class="example-context">${{esc(e.context || '')}}</div>
                    <div class="example-sentence">"${{esc(e.sentence)}}"</div>
                    <div class="example-why">${{esc(e.why || '')}}</div>
                </div>`).join('')}}</div>`;
    }}
    if (w.misuses && w.misuses.length) {{
        html += `<div class="detail-section"><div class="detail-title">Common Misuses</div>
            ${{w.misuses.map(m => `
                <div class="misuse-item">
                    <div class="misuse-wrong">"${{esc(m.wrong)}}"</div>
                    <div class="misuse-problem">${{esc(m.problem)}}</div>
                    <div class="misuse-instead">Use instead: ${{esc(m.use_instead || '')}}</div>
                </div>`).join('')}}</div>`;
    }}
    if (w.related && w.related.length) {{
        html += `<div class="detail-section"><div class="detail-title">Related Words</div>
            ${{w.related.map(r => `
                <div class="related-item">
                    <a class="related-link" onclick="event.stopPropagation(); navigateTo('${{esc(r.word)}}')">${{esc(r.word)}}</a>
                    <div class="related-distinction">${{esc(r.distinction || '')}}</div>
                </div>`).join('')}}</div>`;
    }}
    return html;
}}

function esc(s) {{
    if (!s) return '';
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function toggleCard(idx) {{
    expandedCard = expandedCard === idx ? null : idx;
    renderCards();
    if (expandedCard !== null) {{
        const el = document.getElementById('card-' + idx);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
}}

function navigateTo(word) {{
    const idx = wordMap[word.toLowerCase()];
    if (idx === undefined) return;
    // Clear search/filters to ensure target is visible
    searchQuery = '';
    document.getElementById('search').value = '';
    clearFilters();
    switchTab('cards');
    expandedCard = idx;
    renderCards();
    setTimeout(() => {{
        const el = document.getElementById('card-' + idx);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 50);
}}

// Search
document.getElementById('search').addEventListener('input', function() {{
    searchQuery = this.value;
    expandedCard = null;
    renderCards();
}});

function updateStats() {{
    const usedWords = Object.keys(USAGE).length;
    const totalUses = Object.values(USAGE).reduce((s, arr) => s + arr.length, 0);
    document.getElementById('stats-bar').innerHTML =
        `${{WORDS.length}} words<br>` +
        `${{usedWords}} used in writing<br>` +
        `${{totalUses}} total real-world uses`;
}}

// Tabs
function switchTab(tab) {{
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.toggle('active', t.id === 'tab-' + tab));
    if (tab === 'graph' && !graphInitialized) {{
        // Delay so browser reflows the now-visible container before we read its size
        requestAnimationFrame(() => requestAnimationFrame(() => initGraph()));
    }}
}}

// === TRIGGER INDEX ===
let triggerData = [];
let triggerCtxFilter = '';
let triggerSearchQuery = '';
let quizMode = false;

function buildTriggerIndex() {{
    const tagFreq = {{}};
    WORDS.forEach(w => (w.tags || []).forEach(t => {{ tagFreq[t] = (tagFreq[t] || 0) + 1; }}));

    triggerData = [];
    WORDS.forEach(w => {{
        if (!w.triggers || !w.triggers.length || !w.enriched) return;
        if (activeFilters.versions.size > 0 && !activeFilters.versions.has(String(w.version || 1))) return;
        const bestTag = (w.tags || []).slice().sort((a, b) => (tagFreq[b] || 0) - (tagFreq[a] || 0))[0] || 'other';
        const regClass = 'reg-' + ((w.register || ['general'])[0]).toLowerCase();
        w.triggers.forEach((t, ti) => {{
            const ex = w.examples && w.examples[Math.min(ti, w.examples.length - 1)];
            triggerData.push({{
                trigger: t,
                word: w.word,
                definition: w.definition || '',
                example: ex ? ex.sentence : '',
                exContext: ex ? (ex.context || '').toLowerCase() : '',
                category: bestTag,
                regClass: regClass,
                searchText: (t + ' ' + w.word + ' ' + (w.definition || '') + ' ' + (ex ? ex.sentence : '')).toLowerCase()
            }});
        }});
    }});
    renderTriggers();
    initTriggerListeners();
}}

function renderTriggers() {{
    const q = triggerSearchQuery.toLowerCase();
    const filtered = triggerData.filter(d => {{
        if (q && !d.searchText.includes(q)) return false;
        if (triggerCtxFilter && d.exContext !== triggerCtxFilter) return false;
        return true;
    }});

    const catMap = {{}};
    filtered.forEach(d => {{
        if (!catMap[d.category]) catMap[d.category] = [];
        catMap[d.category].push(d);
    }});

    const MIN_SIZE = 15;
    const otherItems = [];
    const cats = {{}};
    Object.entries(catMap).forEach(([cat, items]) => {{
        if (items.length < MIN_SIZE) otherItems.push(...items);
        else cats[cat] = items;
    }});
    if (otherItems.length) cats['other'] = (cats['other'] || []).concat(otherItems);

    const sortedCats = Object.entries(cats)
        .sort((a, b) => {{ if (a[0] === 'other') return 1; if (b[0] === 'other') return -1; return b[1].length - a[1].length; }});

    if (!sortedCats.length) {{
        document.getElementById('triggers-index').innerHTML = '<div class="triggers-empty">No matching scenarios found.</div>';
        return;
    }}

    const container = document.getElementById('triggers-index');
    container.classList.toggle('quiz-active', quizMode);
    container.innerHTML = sortedCats.map(([cat, items], ci) => `
        <details class="scenario-category" ${{ci < 5 && cat !== 'other' ? 'open' : ''}}>
            <summary>${{esc(cat.charAt(0).toUpperCase() + cat.slice(1))}} <span class="cat-count">(${{items.length}})</span></summary>
            <div class="scenario-cards">
                ${{items.map(d => `
                    <div class="scenario-card">
                        <div class="scenario-trigger">${{esc(d.trigger)}}</div>
                        ${{d.example ? `<div class="scenario-example">"${{esc(d.example)}}"</div>` : ''}}
                        <div class="scenario-def">${{esc(d.definition)}}</div>
                        <div class="scenario-footer">
                            <a class="scenario-word ${{d.regClass}}" onclick="navigateTo('${{esc(d.word)}}')">${{esc(d.word)}}</a>
                            <button class="scenario-reveal-btn" onclick="this.closest('.scenario-card').classList.add('revealed')">Reveal</button>
                        </div>
                    </div>
                `).join('')}}
            </div>
        </details>
    `).join('');
}}

function toggleQuizMode() {{
    quizMode = !quizMode;
    document.getElementById('quiz-toggle').classList.toggle('active', quizMode);
    document.getElementById('triggers-index').classList.toggle('quiz-active', quizMode);
    document.querySelectorAll('.scenario-card.revealed').forEach(el => el.classList.remove('revealed'));
}}

let triggerListenersInit = false;
function initTriggerListeners() {{
    if (triggerListenersInit) return;
    triggerListenersInit = true;
    let debounce;
    document.getElementById('trigger-search').addEventListener('input', function() {{
        clearTimeout(debounce);
        debounce = setTimeout(() => {{ triggerSearchQuery = this.value; renderTriggers(); }}, 200);
    }});
    document.querySelectorAll('.ctx-btn').forEach(btn => {{
        btn.addEventListener('click', function() {{
            const ctx = this.dataset.ctx;
            if (triggerCtxFilter === ctx) {{
                triggerCtxFilter = '';
                this.classList.remove('active');
            }} else {{
                document.querySelectorAll('.ctx-btn').forEach(b => b.classList.remove('active'));
                triggerCtxFilter = ctx;
                this.classList.add('active');
            }}
            renderTriggers();
        }});
    }});
}}

// === GRAPH ===
let graphInitialized = false;

function initGraph() {{
    graphInitialized = true;
    const canvas = document.getElementById('graph-canvas');
    const container = document.getElementById('graph-container');
    const tooltip = document.getElementById('graph-tooltip');
    const ctx = canvas.getContext('2d');
    let mouseX = -9999, mouseY = -9999;
    let dragging = null;
    let hovered = null;

    const viewW = container.clientWidth || 1200;
    const viewH = container.clientHeight || 700;

    // Build nodes/edges
    const nodeSet = new Set();
    const edgeList = [];
    WORDS.forEach(w => {{
        if (w.related && w.related.length) {{
            nodeSet.add(w.word);
            w.related.forEach(r => {{
                nodeSet.add(r.word);
                edgeList.push([w.word, r.word]);
            }});
        }}
    }});
    const nodeArr = Array.from(nodeSet);
    const nodeIdx = {{}};
    nodeArr.forEach((n, i) => {{ nodeIdx[n] = i; }});

    // Union-find for clusters
    const uf = {{}};
    function find(x) {{ if (uf[x] !== x) uf[x] = find(uf[x]); return uf[x]; }}
    function union(a, b) {{ uf[find(a)] = find(b); }}
    nodeArr.forEach(n => {{ uf[n] = n; }});
    edgeList.forEach(([a, b]) => union(a, b));

    const clusterMap = {{}};
    nodeArr.forEach(n => {{
        const root = find(n);
        if (!clusterMap[root]) clusterMap[root] = [];
        clusterMap[root].push(n);
    }});
    const clusterList = Object.values(clusterMap).sort((a, b) => b.length - a.length);

    const regColors = {{ formal: '#4a6cf7', informal: '#e67e22', literary: '#8e44ad', technical: '#16a085', general: '#7f8c8d', academic: '#2c3e50', neutral: '#95a5a6', colloquial: '#e74c3c' }};

    // Bubble radius: enough for labels to be readable
    function bubbleRadius(n) {{ return Math.max(35, Math.sqrt(n) * 32); }}

    // Pack bubbles into rows with no overlap, sizing the canvas to fit
    const GAP = 12;
    const bubbles = clusterList.map((cluster, ci) => ({{
        members: cluster, radius: bubbleRadius(cluster.length), color: ci % 8,
        x: 0, y: 0, homeX: 0, homeY: 0
    }}));

    // Row-pack: place bubbles left to right, wrap when row is full
    let rowX = GAP, rowY = GAP, rowH = 0;
    const canvasW = Math.max(viewW, 1000);
    bubbles.forEach(b => {{
        const d = b.radius * 2;
        if (rowX + d + GAP > canvasW && rowX > GAP) {{
            rowX = GAP;
            rowY += rowH + GAP;
            rowH = 0;
        }}
        b.homeX = rowX + b.radius;
        b.homeY = rowY + b.radius;
        b.x = b.homeX;
        b.y = b.homeY;
        rowX += d + GAP;
        rowH = Math.max(rowH, d);
    }});
    const canvasH = Math.max(rowY + rowH + GAP, viewH);
    canvas.width = canvasW;
    canvas.height = canvasH;

    // Build graph nodes positioned relative to their bubble
    const graphNodes = [];
    const graphNodeIdx = {{}};
    const nodeBubble = {{}};

    bubbles.forEach((bubble, bi) => {{
        const cluster = bubble.members;
        const n = cluster.length;
        cluster.forEach((name, ni) => {{
            const w = WORDS.find(x => x.word.toLowerCase() === name.toLowerCase());
            const reg = (w && w.register && w.register[0]) || 'general';
            let ox = 0, oy = 0;
            if (n > 1) {{
                const angle = (ni / n) * Math.PI * 2 - Math.PI / 2;
                const innerR = bubble.radius * 0.6;
                ox = Math.cos(angle) * innerR;
                oy = Math.sin(angle) * innerR;
            }}
            const idx = graphNodes.length;
            graphNodeIdx[name] = idx;
            nodeBubble[idx] = bi;
            graphNodes.push({{
                name, ox, oy, homeOx: ox, homeOy: oy,
                color: regColors[reg] || '#7f8c8d',
                inDb: !!w
            }});
        }});
    }});

    const graphEdges = edgeList.map(([a, b]) => [graphNodeIdx[a], graphNodeIdx[b]]).filter(([a,b]) => a !== undefined && b !== undefined);

    function nodePos(i) {{
        const b = bubbles[nodeBubble[i]];
        return {{ x: b.x + graphNodes[i].ox, y: b.y + graphNodes[i].oy }};
    }}

    let hoveredBubble = -1;

    function getBubbleAt(mx, my) {{
        for (let i = bubbles.length - 1; i >= 0; i--) {{
            const b = bubbles[i];
            const dx = b.x - mx, dy = b.y - my;
            if (dx * dx + dy * dy < b.radius * b.radius) return i;
        }}
        return -1;
    }}

    // Intro: ease from center to home
    let introFrame = 0;
    const INTRO_FRAMES = 90;
    const centerX = canvasW / 2, centerY = viewH / 2;
    bubbles.forEach(b => {{
        b.x = centerX + (Math.random() - 0.5) * 150;
        b.y = centerY + (Math.random() - 0.5) * 150;
    }});

    function draw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw bubble backgrounds
        const bubbleColors = ['rgba(74,108,247,0.06)', 'rgba(230,126,34,0.06)', 'rgba(142,68,173,0.06)', 'rgba(22,160,133,0.06)', 'rgba(127,140,141,0.06)', 'rgba(44,62,80,0.06)', 'rgba(149,165,166,0.06)', 'rgba(231,76,60,0.06)'];
        const borderColors = ['rgba(74,108,247,0.15)', 'rgba(230,126,34,0.15)', 'rgba(142,68,173,0.15)', 'rgba(22,160,133,0.15)', 'rgba(127,140,141,0.15)', 'rgba(44,62,80,0.15)', 'rgba(149,165,166,0.15)', 'rgba(231,76,60,0.15)'];
        bubbles.forEach((b, bi) => {{
            ctx.beginPath();
            ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
            if (bi === hoveredBubble) {{
                ctx.fillStyle = 'rgba(255,255,255,0.95)';
                ctx.shadowColor = 'rgba(74,108,247,0.3)';
                ctx.shadowBlur = 20;
            }} else {{
                ctx.fillStyle = bubbleColors[b.color % 8];
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
            }}
            ctx.fill();
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            ctx.strokeStyle = bi === hoveredBubble ? 'rgba(74,108,247,0.5)' : borderColors[b.color % 8];
            ctx.lineWidth = bi === hoveredBubble ? 2 : 1;
            ctx.stroke();
        }});

        // Edges (within clusters)
        ctx.strokeStyle = 'rgba(74, 108, 247, 0.12)';
        ctx.lineWidth = 0.8;
        graphEdges.forEach(([a, b]) => {{
            const pa = nodePos(a), pb = nodePos(b);
            ctx.beginPath();
            ctx.moveTo(pa.x, pa.y);
            ctx.lineTo(pb.x, pb.y);
            ctx.stroke();
        }});

        // Nodes + labels
        graphNodes.forEach((n, i) => {{
            const pos = nodePos(i);
            const isHovered = i === hovered;
            const r = isHovered ? 5 : (n.inDb ? 3.5 : 2.5);

            ctx.beginPath();
            ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
            ctx.fillStyle = isHovered ? '#ff6b6b' : n.color;
            ctx.fill();

            // Label
            ctx.font = isHovered ? 'bold 11px -apple-system, sans-serif' : '10px -apple-system, sans-serif';
            ctx.fillStyle = isHovered ? '#1a1a2e' : '#555';
            ctx.textBaseline = 'middle';
            ctx.fillText(n.name, pos.x + r + 3, pos.y);
        }});
    }}

    // Intro: ease from center to home, then stop
    let settled = false;
    function animateIntro() {{
        if (introFrame < INTRO_FRAMES) {{
            introFrame++;
            const t = introFrame / INTRO_FRAMES;
            const ease = 1 - Math.pow(1 - t, 3);
            bubbles.forEach(b => {{
                b.x = centerX + (b.homeX - centerX) * ease;
                b.y = centerY + (b.homeY - centerY) * ease;
            }});
            draw();
            requestAnimationFrame(animateIntro);
        }} else {{
            // Snap to final positions, done
            bubbles.forEach(b => {{ b.x = b.homeX; b.y = b.homeY; b.vx = 0; b.vy = 0; }});
            settled = true;
            draw();
        }}
    }}
    animateIntro();

    // After settled, only redraw on mouse interaction
    function interactionDraw() {{
        if (!settled) return;

        hoveredBubble = getBubbleAt(mouseX, mouseY);

        bubbles.forEach((b, i) => {{
            if (i === hoveredBubble) {{
                // Hovered bubble stays at home
                b.x += (b.homeX - b.x) * 0.12;
                b.y += (b.homeY - b.y) * 0.12;
            }} else if (hoveredBubble >= 0) {{
                // Push overlapping bubbles away from hovered bubble
                const hb = bubbles[hoveredBubble];
                const dx = b.x - hb.x;
                const dy = b.y - hb.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const clearance = hb.radius + b.radius + 15;
                if (dist < clearance && dist > 0) {{
                    // Push outward so they clear the hovered bubble
                    const pushX = (dx / dist) * clearance;
                    const pushY = (dy / dist) * clearance;
                    const targetX = hb.x + pushX;
                    const targetY = hb.y + pushY;
                    b.x += (targetX - b.x) * 0.1;
                    b.y += (targetY - b.y) * 0.1;
                }} else {{
                    // Spring back to home
                    b.x += (b.homeX - b.x) * 0.06;
                    b.y += (b.homeY - b.y) * 0.06;
                }}
            }} else {{
                // No hover — spring back to home
                b.x += (b.homeX - b.x) * 0.08;
                b.y += (b.homeY - b.y) * 0.08;
            }}
        }});

        // Node-level: when hovering a word, push siblings away within the same bubble
        if (hovered !== null) {{
            const hovBi = nodeBubble[hovered];
            const hovNode = graphNodes[hovered];
            // Hovered node stays at home
            hovNode.ox += (hovNode.homeOx - hovNode.ox) * 0.15;
            hovNode.oy += (hovNode.homeOy - hovNode.oy) * 0.15;

            graphNodes.forEach((n, i) => {{
                if (i === hovered || nodeBubble[i] !== hovBi) return;
                const dx = n.ox - hovNode.ox;
                const dy = n.oy - hovNode.oy;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const minDist = 55; // minimum px between hovered and siblings
                if (dist < minDist) {{
                    const pushDist = minDist;
                    const targetOx = hovNode.ox + (dx / dist) * pushDist;
                    const targetOy = hovNode.oy + (dy / dist) * pushDist;
                    n.ox += (targetOx - n.ox) * 0.12;
                    n.oy += (targetOy - n.oy) * 0.12;
                }}
            }});
        }} else {{
            // No hovered node — spring all nodes back to home offsets
            graphNodes.forEach(n => {{
                n.ox += (n.homeOx - n.ox) * 0.1;
                n.oy += (n.homeOy - n.oy) * 0.1;
            }});
        }}

        draw();
        requestAnimationFrame(interactionDraw);
    }}

    // Interaction
    function getNodeAt(mx, my) {{
        for (let i = graphNodes.length - 1; i >= 0; i--) {{
            const p = nodePos(i);
            const dx = p.x - mx, dy = p.y - my;
            if (dx * dx + dy * dy < 144) return i;
        }}
        return null;
    }}

    function getMousePos(e) {{
        const rect = canvas.getBoundingClientRect();
        return [e.clientX - rect.left, e.clientY - rect.top];
    }}

    let interacting = false;
    canvas.addEventListener('mousemove', function(e) {{
        [mouseX, mouseY] = getMousePos(e);
        const idx = getNodeAt(mouseX, mouseY);
        hovered = idx;
        canvas.style.cursor = idx !== null ? 'pointer' : 'default';
        if (idx !== null) {{
            const n = graphNodes[idx];
            const w = WORDS.find(x => x.word.toLowerCase() === n.name.toLowerCase());
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX + 14) + 'px';
            tooltip.style.top = (e.clientY - 10) + 'px';
            tooltip.innerHTML = `<strong>${{n.name}}</strong>` + (w ? `<br><span style="color:#888">${{w.definition || ''}}</span>` : ' <em>(not in vocab)</em>');
        }} else {{
            tooltip.style.display = 'none';
        }}
        if (dragging) {{
            const bi = dragging.bubbleIdx;
            bubbles[bi].x = mouseX;
            bubbles[bi].y = mouseY;
            bubbles[bi].homeX = mouseX;
            bubbles[bi].homeY = mouseY;
        }}
        // Start interaction loop if not running
        if (settled && !interacting) {{
            interacting = true;
            interactionDraw();
        }}
    }});

    canvas.addEventListener('mouseleave', function() {{
        mouseX = -9999; mouseY = -9999;
        hovered = null;
        interacting = false;
        tooltip.style.display = 'none';
        // Snap back to home and redraw once
        if (settled) {{
            bubbles.forEach(b => {{ b.x = b.homeX; b.y = b.homeY; }});
            draw();
        }}
    }});

    canvas.addEventListener('mousedown', function(e) {{
        const [mx, my] = getMousePos(e);
        const idx = getNodeAt(mx, my);
        if (idx !== null) {{
            dragging = {{ bubbleIdx: nodeBubble[idx] }};
        }} else {{
            // Check if clicking on a bubble directly
            for (let i = bubbles.length - 1; i >= 0; i--) {{
                const b = bubbles[i];
                const dx = b.x - mx, dy = b.y - my;
                if (dx * dx + dy * dy < b.radius * b.radius) {{
                    dragging = {{ bubbleIdx: i }};
                    break;
                }}
            }}
        }}
    }});
    canvas.addEventListener('mouseup', function() {{ dragging = null; }});
    canvas.addEventListener('dblclick', function(e) {{
        const [mx, my] = getMousePos(e);
        const idx = getNodeAt(mx, my);
        if (idx !== null) navigateTo(graphNodes[idx].name);
    }});
}}

// ── Add Word Modal ─────────────────────────────────────────────────
function openAddModal() {{
    document.getElementById('add-modal').classList.add('visible');
    const inp = document.getElementById('add-word-input');
    inp.value = '';
    inp.focus();
    setModalStatus('');
}}

function closeAddModal() {{
    document.getElementById('add-modal').classList.remove('visible');
}}

function setModalStatus(text, type) {{
    const el = document.getElementById('add-modal-status');
    el.className = 'modal-status' + (type ? ' ' + type : '');
    el.textContent = text;
    el.style.display = text ? 'block' : 'none';
}}

async function submitAddWord() {{
    const inp = document.getElementById('add-word-input');
    const word = inp.value.trim();
    if (!word) return;

    const btn = document.getElementById('add-word-submit');
    btn.disabled = true;
    setModalStatus('Enriching "' + word + '" via Claude... (takes ~5s)', 'loading');

    try {{
        const resp = await fetch('/add-word', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ word: word }})
        }});
        const data = await resp.json();

        if (!resp.ok) {{
            setModalStatus(data.error || 'Failed to add word.', 'error');
            btn.disabled = false;
            return;
        }}

        // Success — add to local data and re-render
        const w = data.word;
        WORDS.push(w);
        wordMap[w.word.toLowerCase()] = WORDS.length - 1;
        shuffledOrder = shuffle(WORDS);

        setModalStatus('Added "' + w.word + '" to V' + w.version + '!', 'success');
        btn.disabled = false;
        renderCards();
        updateStats();

        // Close after a moment
        setTimeout(() => closeAddModal(), 1500);

    }} catch (e) {{
        setModalStatus('Server not reachable. Run: python vocab_server.py', 'error');
        btn.disabled = false;
    }}
}}

// Enter key in modal input
document.addEventListener('keydown', function(e) {{
    if (document.getElementById('add-modal').classList.contains('visible')) {{
        if (e.key === 'Escape') closeAddModal();
        if (e.key === 'Enter' && document.activeElement.id === 'add-word-input') submitAddWord();
    }}
}});

init();
</script>

<!-- Add Word Modal -->
<div class="modal-overlay" id="add-modal" onclick="if(event.target===this) closeAddModal()">
    <div class="modal">
        <h2>Add a New Word</h2>
        <input type="text" class="modal-input" id="add-word-input" placeholder="Type a word..." autocomplete="off">
        <div class="modal-actions">
            <button class="modal-btn secondary" onclick="closeAddModal()">Cancel</button>
            <button class="modal-btn primary" id="add-word-submit" onclick="submitAddWord()">Add &amp; Enrich</button>
        </div>
        <div class="modal-status" id="add-modal-status"></div>
    </div>
</div>
</body>
</html>"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: {OUTPUT_PATH}")
    print(f"  {len(words)} words, {sum(1 for w in words if w.get('enriched'))} enriched")

    # Copy to NAS if available
    if NAS_PATH.exists():
        dest = NAS_PATH / "vocab_dashboard.html"
        shutil.copy2(OUTPUT_PATH, dest)
        print(f"Copied to NAS: {dest}")
    else:
        print(f"NAS path not available: {NAS_PATH}")

    # Push to GitHub Pages
    try:
        shutil.copy2(OUTPUT_PATH, SCRIPT_DIR / "index.html")
        subprocess.run(["git", "add", "index.html"], cwd=SCRIPT_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Update dashboard"], cwd=SCRIPT_DIR, check=True,
                       capture_output=True)
        subprocess.run(["git", "push"], cwd=SCRIPT_DIR, check=True, capture_output=True)
        print("Pushed to GitHub Pages")
    except subprocess.CalledProcessError as e:
        print(f"GitHub push failed: {e}")


if __name__ == "__main__":
    generate()
