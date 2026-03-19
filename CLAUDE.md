# LogAnalyzer — Project Instructions for Claude Code

## GitHub Repository
**All changes to this project must be committed to:**
```
https://github.com/skm-inn/UnixlogAnalyzer
```

Remote is already configured as `origin`. After completing any implementation task:
1. Stage relevant files
2. Commit with a descriptive message
3. Push to `origin main` (or `origin master`) unless the user says otherwise

## Project Overview
An interactive TUI log analyzer for Unix servers. See [PLAN.md](PLAN.md) for the full implementation plan and [logAnalyzer.md](logAnalyzer.md) for the living project snapshot.

## Tech Stack
- Python 3.8+
- Textual (TUI framework)
- Rich (terminal formatting)
- huggingface_hub (AI Tier 1 — HuggingFace Inference API)
- requests (AI Tier 2 — Ollama local model API)
- Prompt Export file (AI Tier 3 — no AI required)

## Key Rules
- Never modify files outside this project directory
- Source log files on the server are read-only — never write to them
- All output goes to `lookup/` subfolder or project root
- AI analysis: Tier 1 = HuggingFace (HUGGINGFACE_API_TOKEN), Tier 2 = Ollama local, Tier 3 = prompt export file
- No Anthropic/Claude API calls in the application code — use open-source models only

## Living Document — logAnalyzer.md
**IMPORTANT: After every change to this project, update `logAnalyzer.md`:**
1. Update `## 12. Build State Changelog` with date, new version, and change description
2. Update any section that reflects the change (screens, algorithms, file structure, etc.)
3. Update the `Last Updated` date at the top of the file
4. Commit `logAnalyzer.md` together with the code changes

Purpose: `logAnalyzer.md` is a complete, self-contained project snapshot that can be
shared with any AI model (ChatGPT, Gemini, Mistral, etc.) to understand or recreate
the project exactly as built.

## Commit Convention
Use conventional commit style:
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code refactor
- `test:` test additions
- `docs:` documentation update (always commit logAnalyzer.md with docs commits)
