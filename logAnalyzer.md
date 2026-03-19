# LogAnalyzer — Complete Project Snapshot

> **Purpose of this document:**
> This file is the single source of truth for the LogAnalyzer project.
> It is updated every time a change is made. Share this file with any AI model
> (ChatGPT, Gemini, Claude, Mistral, etc.) to get it to understand, extend,
> or recreate the project exactly as built.
>
> **Last Updated:** 2026-03-19
> **Build Status:** v1.0.0 COMPLETE — All screens implemented, tests passing

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Name** | LogAnalyzer |
| **Type** | Interactive Unix TUI Application |
| **Purpose** | Search log files for patterns, copy matched files, analyze with AI |
| **Target Platform** | Unix/Linux servers (including SSH sessions) |
| **GitHub Repo** | https://github.com/skm-inn/UnixlogAnalyzer |
| **Version** | 1.0.0 (initial) |

---

## 2. Tech Stack

| Component | Library / Tool | Version | Notes |
|-----------|---------------|---------|-------|
| Language | Python | 3.8+ | Must be available on target Unix server |
| TUI Framework | Textual | >=0.47.0 | Modern terminal UI, works over SSH |
| Terminal Styling | Rich | >=13.0.0 | Colors, tables, progress bars |
| File Search | `os`, `fnmatch`, `re` | stdlib | No external dependency |
| File Copy | `shutil` | stdlib | Read-only safe |
| AI Tier 1 | huggingface_hub | >=0.23.0 | HuggingFace Inference API |
| AI Tier 2 | requests | >=2.31.0 | Ollama local API calls |
| AI Tier 3 | (none) | — | Prompt file export, no AI needed |
| Version Control | git + GitHub | — | Remote: skm-inn/UnixlogAnalyzer |

### Install Command
```bash
pip install textual>=0.47.0 rich>=13.0.0 huggingface_hub>=0.23.0 requests>=2.31.0
```

### Environment Variables
```bash
# Optional — only needed for AI analysis Tier 1
export HUGGINGFACE_API_TOKEN=hf_...   # free at huggingface.co

# Optional — Tier 2 needs Ollama running locally
# ollama serve && ollama pull mistral
```

---

## 3. Directory Structure (Complete)

```
LogAnalyzer/                        ← project root / application folder
├── loganalyzer.py                  ← entry point: `python loganalyzer.py`
├── PLAN.md                         ← detailed implementation plan
├── logAnalyzer.md                  ← THIS FILE — living project snapshot
├── CLAUDE.md                       ← instructions for Claude Code AI assistant
├── requirements.txt                ← pip dependencies
├── app/
│   ├── __init__.py
│   ├── screens/
│   │   ├── welcome.py              ← Screen 1: splash/banner
│   │   ├── paths.py                ← Screen 2: log path input (up to 5)
│   │   ├── criteria.py             ← Screen 3: search term + file pattern
│   │   ├── progress.py             ← Screen 4: search progress bars
│   │   ├── results.py              ← Screen 5: match results table
│   │   ├── copy_confirm.py         ← Screen 6: copy progress
│   │   ├── ai_context.py           ← Screen 7: optional AI context input
│   │   ├── ai_progress.py          ← Screen 8: AI analysis progress
│   │   └── ai_report.py            ← Screen 9: AI analysis report view
│   ├── core/
│   │   ├── searcher.py             ← recursive log file search engine
│   │   ├── file_copier.py          ← copy matched files to lookup/
│   │   └── ai_analyzer.py          ← AI: HuggingFace / Ollama / prompt export
│   └── utils/
│       └── validators.py           ← path validation, pattern checks
├── lookup/                         ← auto-created by app (NEVER pre-exists)
│   └── <TERM>_<YYYYMMDD_HHMMSS>/  ← one folder per search run
│       ├── <mirrored log files>    ← source files copied here (read-only copy)
│       ├── analysis_report_<ts>.md ← AI-generated analysis (if AI ran)
│       └── analysis_prompt_<ts>.md ← ready-to-use prompt (if AI not available)
└── tests/
    ├── test_loganalyzer.sh         ← shell test script (11 test cases)
    ├── sample_logs/                ← synthetic log files for testing
    │   ├── app/
    │   │   └── application.log
    │   ├── svc/
    │   │   └── service.log
    │   └── web/
    │       └── access.log
    └── README_tests.md
```

**Safety Rule:** The application ONLY writes inside the `LogAnalyzer/` project folder.
No server files are ever modified. Source log files are opened read-only.

---

## 4. Application State Machine (Screen Flow)

```
[WELCOME] ──ENTER──► [LOG PATHS] ──Next──► [SEARCH CRITERIA] ──Search──►
    ▲                    ▲                        ▲
    └── New Search ───────┴────────────────────────┘

[SEARCH CRITERIA] ──► [PROGRESS] ──Complete──► [RESULTS]
                              └──Cancel──► [RESULTS (0 matches)]

[RESULTS] ──Export Report──► (saves .txt, stays on screen)
[RESULTS] ──Copy Files──────► [COPY CONFIRM] ──Done──► [RESULTS]
[RESULTS] ──Analyze & Recommend (only after copy)──► [AI CONTEXT]
[RESULTS] ──New Search──────► [LOG PATHS]
[RESULTS] ──Quit──────────────► exit

[AI CONTEXT] ──Cancel──────► [RESULTS]
[AI CONTEXT] ──Start Analysis──► [AI PROGRESS]

[AI PROGRESS] ──Cancel──────► [RESULTS]
[AI PROGRESS] ──Complete────► [AI REPORT]

[AI REPORT] ──Save Report───► (saves .md to lookup/<run>/, stays on screen)
[AI REPORT] ──Back to Results► [RESULTS]
[AI REPORT] ──New Search────► [LOG PATHS]
[AI REPORT] ──Quit──────────► exit
```

---

## 5. Screen-by-Screen Specification

### Screen 1: Welcome
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ██╗      ██████╗  ██████╗      ██╗                   │
│   ██║     ██╔═══██╗██╔════╝     ███║                   │
│   ██║     ██║   ██║██║  ███╗    ╚██║                   │
│   ██║     ██║   ██║██║   ██║     ██║                   │
│   ███████╗╚██████╔╝╚██████╔╝     ██║                   │
│                                                         │
│              LogAnalyzer v1.0.0                         │
│      Unix Log Search & AI Analysis Tool                 │
│                                                         │
│            [ Press ENTER to Start ]                     │
│                                                         │
│   Ctrl+Q: Quit    F1: Help                              │
└─────────────────────────────────────────────────────────┘
```
- Background: `#0d1117`, Accent: `#58a6ff`, Text: `#c9d1d9`

### Screen 2: Log Path Input
```
┌─────────────────────────────────────────────────────────┐
│  Step 1 of 3 — Log File Paths            [F1 Help]      │
├─────────────────────────────────────────────────────────┤
│  Enter up to 5 log directory paths (Path 1 required):   │
│                                                         │
│  Path 1 *  [/var/log/app___________________________] ✓  │
│  Path 2    [/var/log/svc___________________________] ✓  │
│  Path 3    [________________________________________]    │
│  Path 4    [________________________________________]    │
│  Path 5    [________________________________________]    │
│                                                         │
│  ✓ = path exists and is readable                        │
│                                                         │
│              [Back]    [Validate & Next ►]              │
└─────────────────────────────────────────────────────────┘
```
- Tab navigates between fields
- Real-time validation icon (✓ green / ✗ red) on focus-out

### Screen 3: Search Criteria
```
┌─────────────────────────────────────────────────────────┐
│  Step 2 of 3 — Search Criteria           [F1 Help]      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Search Term *  [ERROR_____________________________]    │
│  (searched as *ERROR* — case-insensitive substring)     │
│                                                         │
│  File Name Filter (optional):                           │
│  [*.log__________________________________________]      │
│  Examples: *.log  app_*.log  debug*  (blank = all)      │
│                                                         │
│  Preview: Will search for *ERROR* in *.log files        │
│                                                         │
│              [◄ Back]    [Search ►]                     │
└─────────────────────────────────────────────────────────┘
```

### Screen 4: Search Progress
```
┌─────────────────────────────────────────────────────────┐
│  Searching...                            [Cancel]       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Discovering files...                                   │
│  ████████████████████████░░░░░░░░  218 files found      │
│                                                         │
│  Scanning files...                                      │
│  ████████████░░░░░░░░░░░░░░░░░░░░  142 / 218  (65%)    │
│                                                         │
│  Matches found so far: 37                               │
│  ⟳ /var/log/app/application.log                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
- Cannot be dismissed while running (blocks accidental close)

### Screen 5: Results
```
┌─────────────────────────────────────────────────────────┐
│  Step 3 of 3 — Results                   [F1 Help]      │
│  37 matches  ·  8 files  ·  218 scanned                 │
├────┬─────────────────────────┬───────┬──────────────────┤
│  # │ File Path               │ Line  │ Matched Text     │
├────┼─────────────────────────┼───────┼──────────────────┤
│  1 │ app/application.log     │  1042 │ ...⚡ERROR DB... │
│  2 │ app/application.log     │  1089 │ ...⚡ERROR Tim... │
│  3 │ svc/service.log         │   203 │ ...⚡ERROR Cra... │
│ .. │ ...                     │   ... │ ...              │
├────┴─────────────────────────┴───────┴──────────────────┤
│ [Export Report] [Copy Files] [Analyze & Recommend*] [Quit]│
│ [New Search]                  * enabled after copy       │
└─────────────────────────────────────────────────────────┘
```
- Match term highlighted in amber `#e3b341`
- `[Analyze & Recommend]` is greyed out until `[Copy Files]` completes

### Screen 6: Copy Confirmation
```
┌─────────────────────────────────────────────────────────┐
│  Copying matched files...                               │
├─────────────────────────────────────────────────────────┤
│  Destination: lookup/ERROR_20260319_143022/             │
│                                                         │
│  ██████████████████████████████████  8 / 8  (100%)     │
│                                                         │
│  Done! 8 files copied.                                  │
│  Path: ./lookup/ERROR_20260319_143022/                  │
│                                                         │
│  [Back to Results]    [Analyze & Recommend ►]           │
└─────────────────────────────────────────────────────────┘
```

### Screen 7: AI Context Input
```
┌─────────────────────────────────────────────────────────┐
│  Analyze & Recommend — AI Context        [F1 Help]      │
├─────────────────────────────────────────────────────────┤
│  Analyzing: lookup/ERROR_20260319_143022/               │
│  AI Engine: HuggingFace (Mistral-7B) ✓                 │
│  ─ or ─  Ollama (mistral) ✓  ─ or ─  Prompt Export     │
│                                                         │
│  What type of system/log is this? (optional)            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Java Spring Boot microservice on Kubernetes     │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│  Examples: "Nginx web server", "Python Flask API",      │
│  "Oracle DB", "Node.js Express", "Tomcat webapp"        │
│  Leave blank → AI will auto-detect from log content     │
│                                                         │
│         [◄ Cancel]    [Start Analysis ►]               │
└─────────────────────────────────────────────────────────┘
```

### Screen 8: AI Analysis Progress
```
┌─────────────────────────────────────────────────────────┐
│  Analyzing with Mistral-7B (HuggingFace)...  [Cancel]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Reading log files from lookup folder...             │
│     ████████████████████████████████  8 files loaded   │
│                                                         │
│  2. Sending to AI model...                              │
│     ████████████████████████████████  Done             │
│                                                         │
│  3. Receiving analysis...                               │
│     ⟳ Streaming response...  1,842 tokens received     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ## Errors Identified                            │   │
│  │ 1. Database Connection Pool Exhausted...        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Screen 9: AI Analysis Report
```
┌─────────────────────────────────────────────────────────┐
│  Analysis Complete — Mistral-7B Report    [F1 Help]     │
├─────────────────────────────────────────────────────────┤
│ ╔═════════════════════════════════════════════════════╗ │
│ ║ ## Errors Identified                                ║ │
│ ║ 1. Database Connection Pool Exhausted               ║ │
│ ║    app/application.log lines 1042, 1089             ║ │
│ ║ 2. Service crash (OOM)                              ║ │
│ ║    svc/service.log line 203                         ║ │
│ ╠═════════════════════════════════════════════════════╣ │
│ ║ ## Root Cause Analysis                              ║ │
│ ║ 1. HikariCP pool exhausted under high load...       ║ │
│ ╠═════════════════════════════════════════════════════╣ │
│ ║ ## Recommendations                                  ║ │
│ ║ 1. Increase pool size in application.properties...  ║ │
│ ╠═════════════════════════════════════════════════════╣ │
│ ║ ## Prevention                                       ║ │
│ ║ Add Prometheus metrics for pool utilization...      ║ │
│ ╚═════════════════════════════════════════════════════╝ │
│  [Save Report] [Back to Results] [New Search] [Quit]    │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Core Algorithms

### 6.1 Search Engine (`searcher.py`)

```python
def search(log_paths, search_term, file_pattern=None):
    """
    Yields: (absolute_filepath, line_number, line_text)
    - Opens files read-only: open(f, 'r', errors='replace')
    - Skips binary files (checks first 8KB for null bytes)
    - Detects circular symlinks
    - Case-insensitive: search_term.lower() in line.lower()
    - File filter: fnmatch.fnmatch(filename, file_pattern) if pattern given
    """
    for log_path in log_paths:
        for root, dirs, files in os.walk(log_path, followlinks=True):
            for filename in files:
                if file_pattern and not fnmatch.fnmatch(filename, file_pattern):
                    continue
                filepath = os.path.join(root, filename)
                if is_binary(filepath):
                    continue
                with open(filepath, 'r', errors='replace') as f:
                    for lineno, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            yield (filepath, lineno, line.rstrip())
```

### 6.2 File Copy (`file_copier.py`)

```python
def copy_matched_files(matches, log_paths, search_term):
    """
    destination = LogAnalyzer/lookup/<sanitized_term>_<YYYYMMDD_HHMMSS>/
    - Deduplicates files by absolute path
    - Mirrors directory structure relative to the matching log_path root
    - Uses shutil.copy2() — preserves timestamps, never modifies source
    - Returns: destination Path object
    """
    term_safe = re.sub(r'[^\w\-]', '_', search_term)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path("lookup") / f"{term_safe}_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)

    seen = set()
    for filepath, _, _ in matches:
        if filepath in seen:
            continue
        seen.add(filepath)
        # Find which log_path this file is under
        for log_path in log_paths:
            try:
                rel = Path(filepath).relative_to(log_path)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(filepath, target)
                break
            except ValueError:
                continue
    return dest
```

### 6.3 AI Log Assembly

```python
def assemble_log_content(lookup_folder, search_term, max_chars=24000):
    """
    Reads copied files from lookup_folder.
    For each file: header + first 20 lines + matched lines + last 10 lines.
    Truncates to max_chars, always keeping matched lines.
    """
    parts = []
    for filepath in sorted(lookup_folder.rglob("*")):
        if not filepath.is_file() or filepath.suffix == ".md":
            continue
        lines = filepath.read_text(errors="replace").splitlines()
        matched = [l for l in lines if search_term.lower() in l.lower()]
        excerpt = (
            lines[:20] +
            ["--- matched lines ---"] +
            matched +
            ["--- end of file ---"] +
            lines[-10:]
        )
        parts.append(f"=== FILE: {filepath.name} ===\n" + "\n".join(excerpt))

    content = "\n\n".join(parts)
    if len(content) > max_chars:
        # Keep only matched lines + context
        content = content[:max_chars] + "\n\n[TRUNCATED — matched lines preserved above]"
    return content
```

---

## 7. AI Analysis — Three-Tier Strategy

### Tier Detection Order
1. `HUGGINGFACE_API_TOKEN` env var set → use HuggingFace API
2. Ollama responding at `http://localhost:11434` → use Ollama
3. Neither available → export prompt file (Tier 3)

### HuggingFace Models (Tier 1)
| Model | HuggingFace ID | Notes |
|-------|---------------|-------|
| Mistral 7B | `mistralai/Mistral-7B-Instruct-v0.3` | Default, fast, good quality |
| Llama 3.1 8B | `meta-llama/Llama-3.1-8B-Instruct` | Strong instruction following |
| Qwen 2.5 7B | `Qwen/Qwen2.5-7B-Instruct` | Multilingual, technical logs |

### Ollama Models (Tier 2)
Auto-picks first available from: `mistral`, `llama3`, `qwen2.5`, `phi3`, `gemma2`

### Prompt Export (Tier 3)
Generates `analysis_prompt_<timestamp>.md` in the lookup run folder.
File structure:
```markdown
# Log Analysis Request
**Search Term:** `ERROR`
**Context:** Java Spring Boot
**Instructions:** [full system prompt]
---
## Log Content
[assembled log content]
---
*Paste this into ChatGPT / Claude.ai / Gemini / any AI assistant.*
```

### AI System Prompt Template
```
You are an expert systems reliability engineer and log analyst.
{Context: <user_context> | Auto-detect system type from log content.}
Analyze the provided log files for errors, exceptions, crashes, and anomalies.
Provide a structured response with these exact sections:
## Errors Identified (numbered, with file+line references)
## Root Cause Analysis (per-error explanation)
## Recommendations (actionable fix steps with config examples)
## Prevention (monitoring, alerting, architectural improvements)
Be specific: cite exact file names, line numbers, and error messages.
```

---

## 8. Output File Formats

### Search Report (`report_<term>_<YYYYMMDD_HHMMSS>.txt`)
Saved in project root (`LogAnalyzer/`).
```
=====================================
LogAnalyzer Report
Generated : 2026-03-19 14:30:22
Search Term: ERROR
File Pattern: *.log
Total Matches: 37
Unique Files : 8
Paths Searched: /var/log/app, /var/log/svc
=====================================
FILE: /var/log/app/application.log
  Line  1042 | [2026-03-19] ERROR Failed to connect to DB
  Line  1089 | [2026-03-19] ERROR Timeout reached
FILE: /var/log/svc/service.log
  Line   203 | ERROR: Service crashed unexpectedly
=====================================
Copied Files To: lookup/ERROR_20260319_143022/
=====================================
```

### AI Analysis Report (`analysis_report_<YYYYMMDD_HHMMSS>.md`)
Saved inside `lookup/<run>/`. Markdown format for easy sharing.

### AI Prompt Export (`analysis_prompt_<YYYYMMDD_HHMMSS>.md`)
Saved inside `lookup/<run>/`. Contains full prompt + log content ready to paste into any AI.

---

## 9. Color Palette

| Element | Hex Color | Usage |
|---------|-----------|-------|
| Background | `#0d1117` | Main screen background |
| Header/Footer | `#161b22` | Bar backgrounds |
| Primary accent | `#58a6ff` | Buttons, highlights |
| Success | `#3fb950` | Valid paths, done states |
| Error/Invalid | `#f85149` | Errors, invalid input |
| Warning | `#d29922` | Amber warnings |
| Progress fill | `#1f6feb` | Progress bar |
| Table header | `#21262d` | Table header bg |
| Table row alt | `#161b22` | Alternating rows |
| Match highlight | `#e3b341` | Matched text in results |
| Text primary | `#c9d1d9` | Main text |
| Text muted | `#8b949e` | Secondary text, hints |

---

## 10. Key Constraints & Safety Rules

1. **Read-only on server** — No writes outside the `LogAnalyzer/` project directory
2. **No privilege escalation** — No `sudo`, `chmod`, `chown`, or setuid
3. **No modification of source logs** — `shutil.copy2()` only, never `open(f, 'w')`
4. **No system packages** — Only pip-installable dependencies
5. **AI reads only copied files** — `ai_analyzer.py` reads from `lookup/` only
6. **Circular symlink detection** — prevents infinite walk loops
7. **Binary file skip** — graceful skip, not crash
8. **Encoding tolerance** — `open(f, errors='replace')` everywhere

---

## 11. Test Cases (`tests/test_loganalyzer.sh`)

| # | Test | Expected |
|---|------|----------|
| 1 | Search term found in multiple files | Correct file/line matches returned |
| 2 | File pattern filter applied | Only matching filenames searched |
| 3 | Search term not found | Empty result set, no crash |
| 4 | Server files unchanged | MD5 checksums match before/after |
| 5 | `lookup/` folder created | Correct folder name with timestamp |
| 6 | `report_*.txt` created | Contains correct match count and file list |
| 7 | AI Tier 1 (HF token set) | `analysis_report_*.md` created, non-empty |
| 8 | AI Tier 2 (Ollama running) | `analysis_report_*.md` created, non-empty |
| 9 | AI Tier 3 (no AI) | `analysis_prompt_*.md` created, contains prompt |
| 10 | Large log truncation | Warning shown, matched lines preserved |
| 11 | `logAnalyzer.md` up to date | File exists, contains current build state |

---

## 12. Build State Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-03-19 | 0.1.0 | Initial plan created — all screens designed |
| 2026-03-19 | 0.2.0 | Added AI Analyze & Recommend feature (Anthropic) |
| 2026-03-19 | 0.3.0 | Replaced Anthropic with HuggingFace + Ollama + Prompt Export |
| 2026-03-19 | 0.4.0 | Added `logAnalyzer.md` living document requirement |
| 2026-03-19 | 1.0.0 | Full implementation complete: all 9 screens, main app, test suite, sample logs |

---

## 13. How to Recreate This Project (AI Prompt)

Copy and send this prompt to any AI model to have it build this project from scratch:

---

```
Build a Python Unix TUI log analyzer application called "LogAnalyzer".

TECH STACK:
- Python 3.8+
- textual>=0.47.0 (TUI framework)
- rich>=13.0.0 (styling)
- huggingface_hub>=0.23.0 (AI Tier 1)
- requests>=2.31.0 (Ollama AI Tier 2)

FEATURES:
1. GUI (TUI) accepts up to 5 log directory paths
2. Search term input — searches as *term* (case-insensitive substring) across all files
3. Optional file name pattern filter (e.g. *.log)
4. Recursive search through all log paths
5. Results table: file path, line number, matched text (term highlighted)
6. Copy matched files to ./lookup/<TERM>_<YYYYMMDD_HHMMSS>/ mirroring directory structure
7. Export plain text search report to project root
8. AI "Analyze & Recommend" feature (only after files are copied):
   - Optional context input (what type of system)
   - Three-tier AI: HuggingFace API → Ollama local → Prompt file export
   - Streams response live in the TUI
   - Saves analysis_report_<ts>.md in the lookup run folder
   - If no AI: saves analysis_prompt_<ts>.md with copy-paste-ready prompt

SCREENS (9 total):
1. Welcome/splash
2. Log path input (1-5 paths, validated)
3. Search criteria (term + file filter)
4. Search progress (two progress bars)
5. Results table (scrollable)
6. Copy confirmation (progress bar)
7. AI context input (optional text)
8. AI analysis progress (streaming)
9. AI analysis report (scrollable markdown)

SAFETY:
- Never write outside the LogAnalyzer project folder
- Open log files read-only only
- Skip binary files gracefully
- Handle encoding errors with replace mode
- Detect circular symlinks

COLOR SCHEME (dark GitHub theme):
- Background: #0d1117
- Accent: #58a6ff
- Success: #3fb950
- Error: #f85149
- Match highlight: #e3b341

The project structure, algorithm details, and full screen layouts are in
the attached logAnalyzer.md file. Implement exactly as specified there.
```

---

## 14. AI Analysis Prompt Template (for manual use)

When AI is not available, the application exports this template filled with
the actual log content. You can also use it manually:

```markdown
# Log Analysis Request

**Search Term:** `<SEARCH_TERM>`
**Context:** <USER_CONTEXT or "Not provided — please auto-detect from log content">

## Instructions

You are an expert systems reliability engineer and log analyst.
Analyze the log excerpts below and provide a structured response:

### Required Output Format:

## Errors Identified
(numbered list — include exact file name and line number for each)

## Root Cause Analysis
(for each error: explain what caused it and why it happened)

## Recommendations
(specific, actionable steps to fix each issue — include config snippets if applicable)

## Prevention
(monitoring, alerting, and architectural changes to prevent recurrence)

---

## Log Content

<ASSEMBLED_LOG_CONTENT>

---
*Generated by LogAnalyzer — paste this file into ChatGPT / Claude.ai / Gemini / any AI*
```

---

*This document is automatically updated by Claude Code whenever changes are made to the LogAnalyzer project. See CLAUDE.md for update instructions.*
