"""
HuggingFace API connectivity diagnostic.
Run: python tests/test_hf_connectivity.py

Tests:
  1. Basic internet/DNS reachability to api-inference.huggingface.co
  2. Token validity
  3. Each model — first-token response time
"""

import json
import os
import socket
import sys
import time

import requests

TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "")
MODELS = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]
SAMPLE_MESSAGES = [
    {"role": "user", "content": "Reply with exactly: HELLO"},
]

# ── 1. DNS / TCP reachability ────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — DNS + TCP to api-inference.huggingface.co:443")
print("=" * 60)
try:
    ip = socket.getaddrinfo("api-inference.huggingface.co", 443)[0][4][0]
    print(f"  DNS OK  →  {ip}")
    s = socket.create_connection((ip, 443), timeout=5)
    s.close()
    print("  TCP OK  →  port 443 reachable")
except Exception as e:
    print(f"  FAIL  →  {e}")
    print("\n  This server cannot reach HuggingFace — likely a firewall/proxy block.")
    print("  Ask your sysadmin to allow outbound HTTPS to api-inference.huggingface.co")
    sys.exit(1)

# ── 2. Token check ───────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 2 — Token validity")
print("=" * 60)
if not TOKEN:
    print("  FAIL  →  HUGGINGFACE_API_TOKEN is not set")
    sys.exit(1)
print(f"  Token  →  {TOKEN[:8]}...")
r = requests.get(
    "https://huggingface.co/api/whoami",
    headers={"Authorization": f"Bearer {TOKEN}"},
    timeout=10,
)
if r.status_code == 200:
    name = r.json().get("name", "unknown")
    print(f"  Token OK  →  logged in as: {name}")
else:
    print(f"  FAIL  →  HTTP {r.status_code}: {r.text[:200]}")
    sys.exit(1)

# ── 3. Model response test ───────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 3 — Model first-token response time (timeout=30s each)")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

for model in MODELS:
    short = model.split("/")[-1]
    url = f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions"
    payload = {"messages": SAMPLE_MESSAGES, "stream": True, "max_tokens": 10}
    print(f"\n  [{short}]")
    t0 = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload,
                             stream=True, timeout=(10, 30))
        print(f"    HTTP status : {resp.status_code}")
        if resp.status_code == 200:
            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                if line.startswith("data: ") and line[6:].strip() != "[DONE]":
                    try:
                        obj = json.loads(line[6:])
                        delta = obj["choices"][0]["delta"].get("content", "")
                        if delta:
                            elapsed = time.time() - t0
                            print(f"    First token : {elapsed:.1f}s  →  '{delta}'")
                            print(f"    STATUS      : WORKING ✓")
                            break
                    except Exception:
                        pass
        elif resp.status_code == 503:
            print(f"    STATUS      : Model loading (503) — try again in 30s")
        elif resp.status_code == 429:
            print(f"    STATUS      : Rate limited (429)")
        elif resp.status_code == 403:
            print(f"    STATUS      : Access denied (403) — model may need license accept")
            print(f"    Body        : {resp.text[:200]}")
        else:
            print(f"    Body        : {resp.text[:200]}")
    except requests.exceptions.ConnectTimeout:
        print(f"    STATUS      : CONNECT TIMEOUT (10s) — firewall blocking HTTPS?")
    except requests.exceptions.ReadTimeout:
        elapsed = time.time() - t0
        print(f"    STATUS      : READ TIMEOUT after {elapsed:.0f}s — model too slow / blocked")
    except Exception as e:
        print(f"    STATUS      : ERROR — {e}")

print()
print("=" * 60)
print("Done.")
