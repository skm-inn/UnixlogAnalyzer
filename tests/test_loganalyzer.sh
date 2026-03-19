#!/usr/bin/env bash
# ============================================================
# LogAnalyzer — automated test suite
# Run from the project root: bash tests/test_loganalyzer.sh
# ============================================================
set -euo pipefail

PASS=0
FAIL=0
SAMPLE="tests/sample_logs"

# ── helpers ─────────────────────────────────────────────────
ok()  { echo "  [PASS] $1"; PASS=$((PASS + 1)); }
fail(){ echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }

run_python() {
    python - "$@" 2>/dev/null
}

# ── 1. Imports ───────────────────────────────────────────────
echo
echo "=== 1. Module imports ==="
python -c "
from app.utils.validators import validate_path, validate_file_pattern, sanitize_term
from app.core.searcher import count_files, search_logs, is_binary
from app.core.file_copier import copy_matched_files
from app.core.ai_analyzer import detect_ai_tier, assemble_log_content
print('OK')
" && ok "All modules import cleanly" || fail "Import error"

# ── 2. validate_path ────────────────────────────────────────
echo
echo "=== 2. validate_path ==="
python -c "
from app.utils.validators import validate_path
ok, _ = validate_path('$SAMPLE/app')
assert ok, 'existing dir should pass'
ok2, _ = validate_path('/this/does/not/exist/ever')
assert not ok2, 'nonexistent dir should fail'
ok3, _ = validate_path('')
assert not ok3, 'empty string should fail'
print('OK')
" && ok "validate_path works" || fail "validate_path failed"

# ── 3. validate_file_pattern ────────────────────────────────
echo
echo "=== 3. validate_file_pattern ==="
python -c "
from app.utils.validators import validate_file_pattern
ok, _ = validate_file_pattern('')       # blank = accept all
assert ok
ok2, _ = validate_file_pattern('*.log')
assert ok2
ok3, _ = validate_file_pattern('app_*.log')
assert ok3
ok4, _ = validate_file_pattern('../../etc/passwd')  # path traversal
assert not ok4
print('OK')
" && ok "validate_file_pattern works" || fail "validate_file_pattern failed"

# ── 4. sanitize_term ────────────────────────────────────────
echo
echo "=== 4. sanitize_term ==="
python -c "
from app.utils.validators import sanitize_term
assert sanitize_term('ERROR') == 'ERROR'
assert sanitize_term('hello world') == 'hello_world'
assert sanitize_term('a/b\\\\c') == 'a_b_c'
assert len(sanitize_term('x' * 200)) <= 64
print('OK')
" && ok "sanitize_term works" || fail "sanitize_term failed"

# ── 5. is_binary ────────────────────────────────────────────
echo
echo "=== 5. is_binary ==="
python -c "
from app.core.searcher import is_binary
assert not is_binary('$SAMPLE/app/application.log'), 'text file should not be binary'
import tempfile, os
with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
    f.write(b'hello\x00world')
    name = f.name
assert is_binary(name), 'null-byte file should be binary'
os.unlink(name)
print('OK')
" && ok "is_binary works" || fail "is_binary failed"

# ── 6. count_files ──────────────────────────────────────────
echo
echo "=== 6. count_files ==="
python -c "
from app.core.searcher import count_files
n = count_files(['$SAMPLE/app', '$SAMPLE/web'])
assert n >= 3, f'expected >=3 files, got {n}'
n2 = count_files(['$SAMPLE/app'], '*.log')
assert n2 >= 2, f'expected >=2 .log files, got {n2}'
n3 = count_files(['$SAMPLE/app'], '*.xyz')
assert n3 == 0, 'no .xyz files expected'
print('OK')
" && ok "count_files works" || fail "count_files failed"

# ── 7. search_logs — basic ──────────────────────────────────
echo
echo "=== 7. search_logs basic ==="
python -c "
from app.core.searcher import search_logs
results = list(search_logs(['$SAMPLE/app'], 'error'))
assert len(results) > 0, 'should find ERROR lines'
for fp, ln, txt in results:
    assert 'error' in txt.lower(), f'matched line should contain error: {txt}'
print(f'Found {len(results)} matches')
print('OK')
" && ok "search_logs finds ERROR" || fail "search_logs basic failed"

# ── 8. search_logs — case-insensitive ───────────────────────
echo
echo "=== 8. search_logs case-insensitive ==="
python -c "
from app.core.searcher import search_logs
r1 = list(search_logs(['$SAMPLE/app'], 'error'))
r2 = list(search_logs(['$SAMPLE/app'], 'ERROR'))
r3 = list(search_logs(['$SAMPLE/app'], 'Error'))
assert len(r1) == len(r2) == len(r3), 'case should not matter'
print('OK')
" && ok "search_logs case-insensitive" || fail "search_logs case-insensitive failed"

# ── 9. search_logs — file pattern filter ────────────────────
echo
echo "=== 9. search_logs file pattern ==="
python -c "
from app.core.searcher import search_logs
import os
r_all = list(search_logs(['$SAMPLE/app'], 'error'))
r_err = list(search_logs(['$SAMPLE/app'], 'error', '*.log'))
# all .log results should be subset of all results
filenames_all = {os.path.basename(fp) for fp, _, _ in r_all}
filenames_err = {os.path.basename(fp) for fp, _, _ in r_err}
assert filenames_err.issubset(filenames_all)
print('OK')
" && ok "search_logs file pattern works" || fail "search_logs file pattern failed"

# ── 10. file_copier ─────────────────────────────────────────
echo
echo "=== 10. file_copier ==="
python -c "
import shutil, os
from pathlib import Path
from app.core.searcher import search_logs
from app.core.file_copier import copy_matched_files

matches = list(search_logs(['$SAMPLE'], 'error'))
assert matches, 'need matches for copy test'

dest = copy_matched_files(matches, ['$SAMPLE'], 'error')
assert dest.exists(), f'dest folder missing: {dest}'

copied = list(dest.rglob('*'))
files = [f for f in copied if f.is_file()]
assert len(files) >= 1, f'no files copied, found: {copied}'

# verify no .md files (skipped)
for f in files:
    assert not f.name.startswith('analysis_'), f'generated file should not be copied: {f}'

# cleanup
shutil.rmtree(dest)
print('OK')
" && ok "file_copier works" || fail "file_copier failed"

# ── 11. assemble_log_content ────────────────────────────────
echo
echo "=== 11. assemble_log_content ==="
python -c "
import shutil
from pathlib import Path
from app.core.searcher import search_logs
from app.core.file_copier import copy_matched_files
from app.core.ai_analyzer import assemble_log_content

matches = list(search_logs(['$SAMPLE'], 'error'))
dest = copy_matched_files(matches, ['$SAMPLE'], 'error')

content = assemble_log_content(dest, 'error')
assert 'error' in content.lower(), 'assembled content should mention error'
assert len(content) > 0

shutil.rmtree(dest)
print(f'Content length: {len(content)} chars')
print('OK')
" && ok "assemble_log_content works" || fail "assemble_log_content failed"

# ── Summary ─────────────────────────────────────────────────
echo
echo "============================================"
echo "  Results:  PASS=$PASS  FAIL=$FAIL"
echo "============================================"
if [[ $FAIL -eq 0 ]]; then
    echo "  All tests passed!"
    exit 0
else
    echo "  $FAIL test(s) FAILED"
    exit 1
fi
