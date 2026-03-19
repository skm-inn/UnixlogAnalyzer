# LogAnalyzer — Implementation Plan

## Overview
An interactive Terminal User Interface (TUI) application for Unix servers that searches across multiple log file paths for a given string pattern, displays a structured report, and copies matched files for further analysis — without modifying anything on the server outside the application folder.

---

## Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Language | Python 3.8+ | Available on most Unix servers, rich ecosystem |
| TUI Framework | [Textual](https://github.com/Textualize/textual) | Modern, rich TUI with widgets, color, keyboard nav |
| Terminal Output | [Rich](https://github.com/Textualize/rich) | Tables, progress bars, syntax highlighting |
| File Search | Python `os`, `fnmatch`, `re` | Standard library, no server writes |
| Progress Bar | Rich `Progress` via Textual | Live updating, industry-standard look |
| Report | Rich `Table` rendered in Textual `DataTable` | Sortable, scrollable |
| File Copy | Python `shutil` | Standard library |
| **AI Analysis** | **HuggingFace `huggingface_hub` + Ollama fallback** | **Open-source models, no vendor lock-in, free tier available** |
| **Prompt Export** | Plain text / Markdown file | Fallback when no AI access — copy-paste to any AI |
| Packaging | Single folder, `requirements.txt` | Easy deployment |
| Version Control | Git → GitHub (`skm-inn/UnixlogAnalyzer`) | All changes committed here |
| Living Docs | `logAnalyzer.md` | Auto-updated project snapshot for AI-assisted rebuild |

**Dependencies (pip installable, no system-level changes):**
```
textual>=0.47.0
rich>=13.0.0
huggingface_hub>=0.23.0
requests>=2.31.0          # for Ollama local API calls
```

**AI Access — Three-tier Strategy (no vendor lock-in):**
```
Tier 1 — HuggingFace Inference API (free, cloud):
  HUGGINGFACE_API_TOKEN=hf_...   # free at huggingface.co

Tier 2 — Ollama (free, local, no token needed):
  ollama serve                   # must be running on localhost:11434
  ollama pull mistral            # or llama3, qwen2.5, etc.

Tier 3 — Prompt Export (no AI required):
  Generates analysis_prompt_<timestamp>.md
  Copy-paste into ChatGPT / Claude.ai / Gemini / any AI
```

---

## Directory Structure

```
LogAnalyzer/
├── loganalyzer.py          # Main application entry point
├── app/
│   ├── __init__.py
│   ├── screens/
│   │   ├── welcome.py      # Welcome/splash screen
│   │   ├── paths.py        # Log path input screen
│   │   ├── criteria.py     # Search criteria screen
│   │   ├── progress.py     # Search progress screen
│   │   ├── results.py      # Results report screen
│   │   └── analyze.py      # AI Analyze & Recommend screen (NEW)
│   ├── core/
│   │   ├── searcher.py     # Core search engine
│   │   ├── file_copier.py  # Copy matched files logic
│   │   └── ai_analyzer.py  # AI analysis: HuggingFace / Ollama / Prompt export (NEW)
│   └── utils/
│       └── validators.py   # Path/pattern validators
├── lookup/                 # Auto-created; stores copied log files
│   └── <criterion>_<YYYYMMDD_HHMMSS>/   # Per-run subfolder
│       ├── (copied log files preserving relative path)
│       ├── analysis_report_<timestamp>.md    # AI-generated analysis (NEW)
│       └── analysis_prompt_<timestamp>.md   # Prompt export fallback (NEW)
├── logAnalyzer.md          # Living project snapshot — updated on every change (NEW)
├── requirements.txt
└── tests/
    ├── test_loganalyzer.sh # Shell test script
    ├── sample_logs/        # Synthetic log files for testing
    └── README_tests.md
```

> All writes happen only inside the `LogAnalyzer/` directory. No server files are touched.

---

## Application Flow

```
┌─────────────────────────────────┐
│         WELCOME SCREEN          │
│  Logo · Version · Instructions  │
│     [Press ENTER to Start]      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│      LOG PATH INPUT SCREEN      │
│  Path 1: [________________]     │
│  Path 2: [________________]     │
│  Path 3: [________________]     │
│  Path 4: [________________]     │
│  Path 5: [________________]     │
│  (1 required, up to 5 allowed)  │
│     [Validate Paths]  [Next]    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     SEARCH CRITERIA SCREEN      │
│  Search Term: [_____________]   │
│  File Pattern Filter (opt):     │
│  e.g. *.log, app_*.log          │
│  [________________]             │
│        [Back]  [Search]         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       PROGRESS SCREEN           │
│  Scanning paths...              │
│  ████████████░░░░░░  65%        │
│  Files scanned: 142 / 218       │
│  Matches found so far: 37       │
│  Current: /var/log/app/svc.log  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│        RESULTS SCREEN           │
│  ┌──────────────────────────┐   │
│  │ Matches found: 37        │   │
│  ├────────┬────────┬────────┤   │
│  │ FILE   │ LINE # │ TEXT   │   │
│  ├────────┼────────┼────────┤   │
│  │ app.log│  1042  │ ...ERR │   │
│  │ svc.log│   203  │ ...ERR │   │
│  └────────┴────────┴────────┘   │
│  [Export Report]  [Copy Files]  │
│  [Analyze & Recommend] [Quit]   │◄── NEW
│  [New Search]                   │
└────────────────┬────────────────┘
                 │
       ┌─────────┴──────────┐
       ▼                    ▼
┌──────────────┐   ┌────────────────────────────────┐
│ COPY CONFIRM │   │   AI CONTEXT SCREEN (NEW)       │
│ 8 files →    │   │  Provide optional context:      │
│ lookup/...   │   │  What type of log is this?      │
│ ████  100%   │   │  e.g. "Java Spring Boot app",   │
│ [Done][Main] │   │  "Nginx web server",            │
└──────────────┘   │  "Python microservice"          │
                   │  [Context: ________________]    │
                   │  (Leave blank to auto-detect)   │
                   │     [Cancel]  [Analyze]         │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │   AI ANALYSIS PROGRESS (NEW)    │
                   │  Reading copied log files...    │
                   │  ██████░░░░░░  40%              │
                   │  Sending to Claude Opus 4.6...  │
                   │  ████████████  Streaming...     │
                   │  [Cancel]                       │
                   └────────────────┬───────────────┘
                                    │
                                    ▼
                   ┌────────────────────────────────┐
                   │   AI ANALYSIS REPORT (NEW)      │
                   │  ╔══════════════════════════╗  │
                   │  ║  ERRORS IDENTIFIED        ║  │
                   │  ╠══════════════════════════╣  │
                   │  ║  1. DB Connection Failure ║  │
                   │  ║  2. OOM at 14:02:11       ║  │
                   │  ╠══════════════════════════╣  │
                   │  ║  RECOMMENDATIONS          ║  │
                   │  ╠══════════════════════════╣  │
                   │  ║  1. Increase conn pool... ║  │
                   │  ║  2. Tune heap settings... ║  │
                   │  ╚══════════════════════════╝  │
                   │  [Save Report] [New Search]     │
                   │  [Back to Results] [Quit]       │
                   └────────────────────────────────┘
```

---

## Screen Layouts (Detailed)

### 1. Welcome Screen
- Full-width **ASCII banner** with app name "LogAnalyzer"
- Version badge, author info
- Brief one-line description
- Color: Dark background (`#1a1a2e`), cyan accent (`#00d4ff`), white text
- Press `ENTER` or click `[Start]` to proceed

### 2. Log Path Input Screen
- Header bar with step indicator: `Step 1 of 3 — Log Paths`
- 5 labeled `Input` widgets stacked vertically
- Each path has an inline validation icon: ✓ (green) / ✗ (red) on focus-out
- Only Path 1 is mandatory
- Footer: key hints `Tab` to move · `F1` Help · `Ctrl+Q` Quit
- `[Validate & Next]` button — turns green when at least 1 valid path given

### 3. Search Criteria Screen
- Header: `Step 2 of 3 — Search Criteria`
- **Search Term** input (required) — searched as `*<term>*` (case-insensitive, substring match)
- **File Name Pattern** input (optional) — e.g. `*.log`, `app_*.log`, `debug*`
  - Hint text: "Leave blank to search all files"
- Live preview line: `Will search for: *error* in *.log files`
- `[Back]` and `[Search]` buttons

### 4. Progress Screen
- **Cannot be dismissed** while search is running (prevents accidental cancel)
- Two progress bars:
  - File discovery progress (files indexed)
  - Search progress (files processed)
- Live stats panel: Files Scanned | Matches Found | Current File
- Spinner animation on the current file path
- `[Cancel]` button available (stops gracefully)

### 5. Results Screen
- Header: `Step 3 of 3 — Results`
- Summary bar: `X matches across Y files from Z total scanned`
- Scrollable **DataTable** with columns:
  - `#` (row number)
  - `File Path` (truncated with tooltip on hover)
  - `Line #`
  - `Matched Text` (highlighted match term in a different color)
- Toolbar buttons:
  - `[Export Report]` → saves `report_<term>_<timestamp>.txt` in app folder
  - `[Copy Matched Files]` → triggers copy flow; **must run before AI analysis**
  - `[Analyze & Recommend]` → only enabled after files are copied; triggers AI analysis flow
  - `[New Search]` → back to Step 1
  - `[Quit]`

### 6. Copy Progress / Confirmation Screen
- Shows destination path: `lookup/<term>_<YYYYMMDD_HHMMSS>/`
- File copy progress bar
- Final summary: N files copied, destination path
- After copy completes, `[Analyze & Recommend]` button appears prominently
- `[Open Folder in Shell]` (prints `cd` command to terminal after exit)
- `[Back to Results]` or `[New Search]`

### 7. AI Context Screen (NEW)
- Header: `Analyze & Recommend — Step 1: Context`
- Info banner: `Analyzing logs from: lookup/<term>_<timestamp>/`
- **Context input** (optional multiline text area):
  - Label: "What type of system/log is this? (optional)"
  - Placeholder examples: `"Java Spring Boot microservice"`, `"Nginx reverse proxy"`, `"Python Celery worker"`, `"Oracle DB"`, `"Kubernetes pod"`
  - Hint: "Providing context helps Claude give more precise recommendations. Leave blank for auto-detection."
- `[Cancel]` and `[Start Analysis]` buttons

### 8. AI Analysis Progress Screen (NEW)
- Header: `Analyzing Logs with Claude Opus 4.6...`
- Three-phase progress display:
  1. `Reading log files from lookup folder...` (file loading bar)
  2. `Sending to Claude Opus 4.6...` (spinner)
  3. `Receiving analysis...` (streaming token counter: `Tokens received: 1,240`)
- Live streaming output panel — shows first lines of AI response as they arrive
- `[Cancel]` button (gracefully stops streaming)
- Note: `ANTHROPIC_API_KEY` must be set in environment; if missing, shows clear error with instructions

### 9. AI Analysis Report Screen (NEW)
- Header: `Analysis Complete — Claude Opus 4.6 Report`
- Full-screen scrollable panel with AI response rendered using Rich Markdown:
  - **Errors Identified** section — numbered list of detected error types
  - **Root Cause Analysis** section — per-error explanation
  - **Recommendations** section — actionable fix steps
  - **Prevention** section — how to avoid recurrence
- Color-coded sections: Errors in red, Recommendations in green, Prevention in cyan
- Footer buttons:
  - `[Save Report]` → saves `analysis_report_<timestamp>.md` inside the `lookup/<run>/` folder
  - `[Back to Results]` → return to search results
  - `[New Search]` → start fresh
  - `[Quit]`

---

## Color Palette (Industry Standard — Dark Theme)

| Element | Color |
|---------|-------|
| Background | `#0d1117` (GitHub dark) |
| Header/Footer bar | `#161b22` |
| Primary accent | `#58a6ff` (blue) |
| Success / Valid | `#3fb950` (green) |
| Error / Invalid | `#f85149` (red) |
| Warning | `#d29922` (amber) |
| Progress bar fill | `#1f6feb` |
| Table header | `#21262d` |
| Table row alt | `#161b22` |
| Match highlight | `#e3b341` (yellow) |
| Text primary | `#c9d1d9` |
| Text muted | `#8b949e` |

---

## Core Logic — Search Engine (`searcher.py`)

```
search_term = "ERROR"         # user input
file_pattern = "*.log"        # optional filter (fnmatch)
search_glob = f"*{search_term}*"   # substring match style

For each log_path (1–5):
  Walk recursively (os.walk)
  For each file:
    If file_pattern provided → fnmatch(filename, file_pattern)
    Open file in read-only mode
    For each line:
      If search_term in line (case-insensitive):
        Record: (absolute_filepath, line_number, line_text)
  Yield result chunks for live progress update
```

- Files are opened **read-only** (`open(f, 'r', errors='replace')`)
- Binary files are skipped gracefully
- Encoding errors are handled (replace mode)
- Symlinks are followed but circular references are detected

---

## File Copy Logic (`file_copier.py`)

```
destination = LogAnalyzer/lookup/<sanitized_term>_<YYYYMMDD_HHMMSS>/

For each unique matched file:
  Compute relative path from the log_path root
  Create mirrored directory structure under destination
  shutil.copy2(src, dest)   # preserves metadata, does not modify source
```

- Only unique files (deduplicated by absolute path) are copied
- Source files are **never modified**
- If destination already exists (collision), a counter suffix is appended

---

## AI Analysis Logic (`ai_analyzer.py`)

### Overview
Uses **open-source models** via a three-tier strategy — no vendor lock-in, no paid API required. The system auto-detects which tier is available and falls back gracefully.

### Three-Tier AI Strategy

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1: HuggingFace Inference API                      │
│  Model: mistralai/Mistral-7B-Instruct-v0.3              │
│         (or meta-llama/Llama-3.1-8B-Instruct)           │
│  Requires: HUGGINGFACE_API_TOKEN env var                 │
│  Free tier: yes (rate-limited)                          │
│  Streaming: yes                                         │
├─────────────────────────────────────────────────────────┤
│  Tier 2: Ollama (local, no token needed)                │
│  Model: mistral / llama3 / qwen2.5 / phi3 (any pulled) │
│  Requires: ollama running on localhost:11434             │
│  Free: completely free, runs on-server                  │
│  Streaming: yes (SSE)                                   │
├─────────────────────────────────────────────────────────┤
│  Tier 3: Prompt Export (always available)               │
│  No AI required — generates a ready-to-use .md file    │
│  User copies prompt to ChatGPT/Claude.ai/Gemini/any AI │
│  Streaming: N/A                                         │
└─────────────────────────────────────────────────────────┘
```

### Auto-detection Logic
```python
def detect_ai_tier():
    # Try Tier 1: HuggingFace
    if os.environ.get("HUGGINGFACE_API_TOKEN"):
        return "huggingface"
    # Try Tier 2: Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200 and r.json().get("models"):
            return "ollama"
    except Exception:
        pass
    # Tier 3: Prompt export
    return "prompt_export"
```

### Tier 1 — HuggingFace Inference API
```python
from huggingface_hub import InferenceClient

HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",   # default: fast, good reasoning
    "meta-llama/Llama-3.1-8B-Instruct",      # alternative: strong instruction following
    "Qwen/Qwen2.5-7B-Instruct",              # alternative: multilingual, technical
]

client = InferenceClient(
    model=HF_MODELS[0],
    token=os.environ["HUGGINGFACE_API_TOKEN"]
)

# Streaming chat completions
for chunk in client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": assembled_log_content}
    ],
    stream=True,
    max_tokens=4096,
):
    delta = chunk.choices[0].delta.content
    if delta:
        yield delta
```

### Tier 2 — Ollama (local)
```python
import requests, json

def query_ollama(prompt, model="mistral"):
    # Auto-pick first available model if default not found
    tags = requests.get("http://localhost:11434/api/tags").json()
    available = [m["name"].split(":")[0] for m in tags.get("models", [])]
    chosen = model if model in available else (available[0] if available else "mistral")

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": chosen,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": assembled_log_content}
            ],
            "stream": True,
        },
        stream=True,
        timeout=120,
    )
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            delta = chunk.get("message", {}).get("content", "")
            if delta:
                yield delta
```

### Tier 3 — Prompt Export (no AI required)
```python
def export_prompt(lookup_folder, search_term, user_context, assembled_log_content):
    """Generates a ready-to-use prompt file the user can paste into any AI."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_path = lookup_folder / f"analysis_prompt_{timestamp}.md"

    prompt = f"""# Log Analysis Request
**Search Term:** `{search_term}`
**Context:** {user_context or "Not provided — please detect from logs"}
**Instructions:** You are an expert systems reliability engineer.
Analyze the log excerpts below and provide:
1. **ERRORS IDENTIFIED** — list each unique error with file name and line number
2. **ROOT CAUSE ANALYSIS** — explain the likely cause for each error
3. **RECOMMENDATIONS** — specific, actionable fix steps
4. **PREVENTION** — how to prevent recurrence

---

## Log Content

{assembled_log_content}

---
*Copy this entire file content and paste into ChatGPT / Claude.ai / Gemini / any AI assistant.*
"""
    prompt_path.write_text(prompt, encoding="utf-8")
    return prompt_path
```

### Shared System Prompt (all tiers)
```
You are an expert systems reliability engineer and log analyst.
{context_line}
Analyze the provided log files for errors, exceptions, crashes, and anomalies.
Structure your response EXACTLY as:

## Errors Identified
(numbered list of unique error types, with file+line reference)

## Root Cause Analysis
(per-error explanation of likely cause)

## Recommendations
(specific, actionable fix steps with config examples where applicable)

## Prevention
(monitoring, alerting, and architectural improvements)

Be specific: reference exact file names, line numbers, and error messages.
```

### Log Content Assembly & Size Management
```
For each file in lookup/<run>/:
  1. Add file header: "=== FILE: filename.log ==="
  2. Add first 20 lines  (startup context)
  3. Add ALL matched lines (lines containing search_term)
  4. Add last 10 lines (shutdown/summary context)
  5. Deduplicate adjacent identical lines

If assembled content > 6000 tokens (~24KB):
  Show warning: "Large logs — keeping matched lines + context only"
  Keep only: file headers + matched lines + 3 lines before/after each match
```

---

## Report Export Format

**Search Report** — plain text saved to `LogAnalyzer/report_<term>_<timestamp>.txt`:

```
=====================================
LogAnalyzer Report
Generated : 2026-03-19 14:30:22
Search Term: ERROR
File Pattern: *.log
Total Matches: 37
Unique Files : 8
=====================================

FILE: /var/log/app/application.log
  Line  1042 | [2026-03-19 14:01:00] ERROR Failed to connect to DB
  Line  1089 | [2026-03-19 14:02:11] ERROR Timeout reached

FILE: /var/log/svc/service.log
  Line   203 | ERROR: Service crashed unexpectedly
...
=====================================
Copied Files To: lookup/ERROR_20260319_143022/
=====================================
```

**AI Analysis Report** — Markdown saved to `lookup/<term>_<timestamp>/analysis_report_<timestamp>.md`:

```markdown
# LogAnalyzer — AI Analysis Report
**Generated:** 2026-03-19 14:35:10
**Model:** Claude Opus 4.6
**Context Provided:** Java Spring Boot microservice
**Lookup Folder:** lookup/ERROR_20260319_143022/

---

## Errors Identified

1. **Database Connection Failure** — `application.log` lines 1042, 1089
2. **OutOfMemoryError** — `service.log` line 203

---

## Root Cause Analysis

### 1. Database Connection Failure
The connection pool is exhausted under load. Lines show repeated
`HikariPool-1 - Connection is not available, request timed out`...

---

## Recommendations

### Fix 1: Increase HikariCP connection pool size
In `application.properties`:
```
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.connection-timeout=30000
```

### Fix 2: Add heap memory
Start JVM with `-Xmx2g -Xms512m` ...

---

## Prevention
- Add connection pool metrics to Prometheus/Grafana
- Set up alerts when pool utilization > 80%
```

---

## Test Script (`tests/test_loganalyzer.sh`)

The shell test script will:

1. **Setup** — create synthetic log files under `tests/sample_logs/` with known content
2. **Test Case 1** — search for a term that exists in multiple files, verify matches
3. **Test Case 2** — search with a file name pattern filter, verify only matching files are searched
4. **Test Case 3** — search for a term that does not exist, verify empty results
5. **Test Case 4** — verify no server files were modified (checksum before/after)
6. **Test Case 5** — verify `lookup/` folder is created with correct structure
7. **Test Case 6** — verify `report_*.txt` is created with correct content
8. **Test Case 7** — AI Tier 1: if `HUGGINGFACE_API_TOKEN` is set, run analysis and verify `analysis_report_*.md` created
9. **Test Case 8** — AI Tier 2: if Ollama is running, run analysis via local model and verify report
10. **Test Case 9** — AI Tier 3: when no AI is available, verify `analysis_prompt_*.md` is generated correctly
11. **Test Case 10** — verify `logAnalyzer.md` exists and contains correct project state section
10. **Cleanup** — remove generated test artifacts
11. **Summary** — PASS/FAIL summary with color output

Tests run in **non-interactive (headless) mode** by calling the core search engine and AI analyzer directly (not the TUI).

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| TUI vs Web UI | TUI (Textual) | No browser/server needed; works over SSH |
| Search algorithm | Line-by-line read | Memory efficient for large files |
| File copy | `shutil.copy2` | Preserves timestamps; read-only safe |
| Max paths | 5 | Keeps UX simple; covers typical use cases |
| Case sensitivity | Case-insensitive by default | Most log searches are case-insensitive |
| Binary file handling | Skip with warning | Prevents garbled output |
| Encoding errors | Replace mode | Prevents crash on non-UTF8 logs |
| AI model tier 1 | HuggingFace Inference API (Mistral-7B) | Free, open-source, no vendor lock-in |
| AI model tier 2 | Ollama local (Mistral/Llama3/Qwen2.5) | Fully local, no internet needed |
| AI fallback | Prompt Export (`.md` file) | Always works — paste into any AI |
| AI streaming | Yes (HF + Ollama both stream) | Live output in TUI |
| AI input source | Copied files in `lookup/` only | Never reads original server files for AI |
| AI optional | Yes — tiers auto-detected | Core search works with zero AI config |
| Living docs | `logAnalyzer.md` auto-updated | Project snapshot for AI-assisted rebuild |
| Version control | GitHub `skm-inn/UnixlogAnalyzer` | All project changes committed here |

---

## Deliverables

1. `loganalyzer.py` — entry point
2. `app/screens/` — 9 screen modules (including AI context, progress, report)
3. `app/core/searcher.py` — search engine
4. `app/core/file_copier.py` — file copy logic
5. `app/core/ai_analyzer.py` — HuggingFace / Ollama / Prompt export **(UPDATED)**
6. `app/utils/validators.py` — input validators
7. `requirements.txt`
8. `logAnalyzer.md` — living project snapshot (auto-updated) **(NEW)**
9. `tests/test_loganalyzer.sh` — test script (11 test cases)
10. `tests/sample_logs/` — synthetic test log files

---

## GitHub Repository

**Remote:** `https://github.com/skm-inn/UnixlogAnalyzer`

All changes to this project must be committed and pushed to this repository.

---

## What Will NOT Be Done (Safety Guardrails)
- No writes outside the `LogAnalyzer/` directory
- No `sudo`, `chmod`, `chown`, or privilege escalation
- No modification of source log files
- AI analysis only reads from the `lookup/` folder (already-copied files), never original server paths
- No system package installation (only pip packages)
- Network calls only for Claude API (opt-in, requires `ANTHROPIC_API_KEY`)
