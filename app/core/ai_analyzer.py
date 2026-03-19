"""
AI analysis engine — three-tier open-source strategy:
  Tier 1: HuggingFace Inference API  (requires HUGGINGFACE_API_TOKEN)
  Tier 2: Ollama local               (requires ollama running on localhost:11434)
  Tier 3: Prompt export              (always available — no AI needed)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional

import requests

# ---------------------------------------------------------------------------
# Model preferences
# ---------------------------------------------------------------------------
HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "Qwen/Qwen2.5-7B-Instruct",
]
OLLAMA_PREFERRED = ["mistral", "llama3", "qwen2.5", "phi3", "gemma2", "llama2"]

# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------
_SYSTEM_TMPL = """\
You are an expert systems reliability engineer and log analyst.
{context_line}
Analyze the provided log files for errors, exceptions, crashes, and anomalies.
Provide a structured response with EXACTLY these sections:

## Errors Identified
(numbered list — include exact file name and line number for each error type)

## Root Cause Analysis
(per-error explanation of what likely caused it and why)

## Recommendations
(specific, actionable fix steps — include config/code snippets where helpful)

## Prevention
(monitoring, alerting, and architectural improvements to prevent recurrence)

Be specific: cite exact file names, line numbers, and error messages from the logs.\
"""


def _system_prompt(user_context: str) -> str:
    if user_context and user_context.strip():
        ctx = f"System context provided by user: {user_context.strip()}"
    else:
        ctx = "Auto-detect the system type and technology stack from the log content."
    return _SYSTEM_TMPL.format(context_line=ctx)


def _user_message(log_content: str, search_term: str) -> str:
    return (
        f"Please analyze these log files. The search term that identified these "
        f"files was '{search_term}'.\n\n{log_content}"
    )


# ---------------------------------------------------------------------------
# Tier detection
# ---------------------------------------------------------------------------
def detect_ai_tier() -> str:
    """Return 'huggingface', 'ollama', or 'prompt_export'."""
    if os.environ.get("HUGGINGFACE_API_TOKEN"):
        return "huggingface"
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200 and r.json().get("models"):
            return "ollama"
    except Exception:
        pass
    return "prompt_export"


def get_tier_label(tier: str) -> str:
    if tier == "huggingface":
        return f"HuggingFace API  ({HF_MODELS[0].split('/')[1]})"
    if tier == "ollama":
        models = _ollama_models()
        chosen = _pick_ollama(models)
        return f"Ollama Local  ({chosen})"
    return "Prompt Export  (no AI required)"


def _ollama_models() -> List[str]:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return [m["name"].split(":")[0] for m in r.json().get("models", [])]
    except Exception:
        return []


def _pick_ollama(available: List[str]) -> str:
    for p in OLLAMA_PREFERRED:
        if p in available:
            return p
    return available[0] if available else "mistral"


# ---------------------------------------------------------------------------
# Log content assembly
# ---------------------------------------------------------------------------
def assemble_log_content(
    lookup_folder: Path,
    search_term: str,
    max_chars: int = 24_000,
) -> str:
    """
    Build a compact log excerpt for AI analysis.
    For each file: header + first 20 lines + matched lines + last 10 lines.
    Truncates to max_chars, always preserving matched lines.
    """
    parts = []
    term_lower = search_term.lower()

    for fpath in sorted(lookup_folder.rglob("*")):
        if not fpath.is_file():
            continue
        # Skip generated report/prompt files
        if fpath.suffix == ".md" or fpath.name.startswith("analysis_"):
            continue
        try:
            lines = fpath.read_text(errors="replace").splitlines()
        except Exception:
            continue

        matched = [
            f"  [Line {i + 1}] {l}"
            for i, l in enumerate(lines)
            if term_lower in l.lower()
        ]
        excerpt = (
            [f"  {l}" for l in lines[:20]]
            + (["  --- matched lines ---"] + matched if matched else [])
            + ["  --- last 10 lines ---"]
            + [f"  {l}" for l in lines[-10:]]
        )
        parts.append(f"=== FILE: {fpath.name} ===\n" + "\n".join(excerpt))

    content = "\n\n".join(parts)

    if len(content) > max_chars:
        # Rebuild with matched-lines-plus-context only
        slim_parts = []
        for fpath in sorted(lookup_folder.rglob("*")):
            if not fpath.is_file() or fpath.suffix == ".md":
                continue
            try:
                lines = fpath.read_text(errors="replace").splitlines()
            except Exception:
                continue
            ctx_lines = []
            for i, l in enumerate(lines):
                if term_lower in l.lower():
                    for j in range(max(0, i - 3), min(len(lines), i + 4)):
                        ctx_lines.append(f"  [Line {j + 1}] {lines[j]}")
            if ctx_lines:
                slim_parts.append(f"=== FILE: {fpath.name} ===\n" + "\n".join(ctx_lines))
        content = "\n\n".join(slim_parts)
        content += "\n\n[NOTE: Large logs — showing matched lines + context only]"

    return content


# ---------------------------------------------------------------------------
# Tier 1 — HuggingFace
# ---------------------------------------------------------------------------
def stream_huggingface(
    log_content: str,
    user_context: str,
    search_term: str,
) -> Generator[str, None, None]:
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        yield "[ERROR] huggingface_hub not installed. Run: pip install huggingface_hub"
        return

    token = os.environ.get("HUGGINGFACE_API_TOKEN", "")
    if not token:
        yield "[ERROR] HUGGINGFACE_API_TOKEN environment variable not set."
        return

    sys_p = _system_prompt(user_context)
    usr_m = _user_message(log_content, search_term)

    for model in HF_MODELS:
        try:
            client = InferenceClient(model=model, token=token)
            for chunk in client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": usr_m},
                ],
                stream=True,
                max_tokens=4096,
            ):
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
            return  # success — stop iterating models
        except Exception as exc:
            msg = str(exc)
            if "429" in msg or "rate" in msg.lower():
                yield f"\n[Rate limited on {model.split('/')[-1]}, trying next…]\n"
            else:
                yield f"\n[{model.split('/')[-1]} error: {exc}]\n"
            continue

    yield "\n\n[All HuggingFace models unavailable — try Ollama or Prompt Export]"


# ---------------------------------------------------------------------------
# Tier 2 — Ollama
# ---------------------------------------------------------------------------
def stream_ollama(
    log_content: str,
    user_context: str,
    search_term: str,
) -> Generator[str, None, None]:
    model = _pick_ollama(_ollama_models())
    sys_p = _system_prompt(user_context)
    usr_m = _user_message(log_content, search_term)

    try:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": usr_m},
                ],
                "stream": True,
            },
            stream=True,
            timeout=180,
        )
        for raw in resp.iter_lines():
            if not raw:
                continue
            try:
                chunk = json.loads(raw)
                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    yield delta
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue
    except Exception as exc:
        yield f"\n[Ollama error: {exc}]"


# ---------------------------------------------------------------------------
# Tier 3 — Prompt export
# ---------------------------------------------------------------------------
def export_prompt(
    lookup_folder: Path,
    search_term: str,
    user_context: str,
    log_content: str,
) -> Path:
    """Generate a ready-to-use .md prompt file for any AI assistant."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = lookup_folder / f"analysis_prompt_{ts}.md"

    ctx_str = user_context.strip() if user_context else (
        "Not provided — please auto-detect from log content"
    )

    text = f"""# Log Analysis Request

**Generated by LogAnalyzer**
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Search Term:** `{search_term}`
**Context:** {ctx_str}

## Instructions

You are an expert systems reliability engineer and log analyst.
Analyze the log excerpts below and respond with these exact sections:

### Errors Identified
(numbered list — file name and line number for each)

### Root Cause Analysis
(per-error cause explanation)

### Recommendations
(actionable fix steps with config/code snippets)

### Prevention
(monitoring, alerting, architectural improvements)

---

## Log Content

{log_content}

---
*Generated by LogAnalyzer — paste this entire file into ChatGPT / Claude.ai / Gemini / any AI assistant.*
"""
    out.write_text(text, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Save AI report
# ---------------------------------------------------------------------------
def save_analysis_report(
    lookup_folder: Path,
    analysis_text: str,
    search_term: str,
    tier: str,
    user_context: str,
) -> Path:
    """Save the completed AI analysis as a Markdown report."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = lookup_folder / f"analysis_report_{ts}.md"

    header = f"""# LogAnalyzer — AI Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**AI Engine:** {get_tier_label(tier)}
**Search Term:** `{search_term}`
**Context:** {user_context.strip() if user_context else "Auto-detected"}
**Lookup Folder:** `{lookup_folder}`

---

"""
    out.write_text(header + analysis_text, encoding="utf-8")
    return out
