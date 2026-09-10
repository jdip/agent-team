#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
"${AGENT_TEAM_PYTHON:-python3}" - <<'PY'
from pathlib import Path
import ast
import subprocess
import tomllib
for root in ('machine', 'scripts'):
    for path in Path(root).rglob('*.toml'):
        tomllib.loads(path.read_text(encoding='utf-8'))
    for path in Path(root).rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for path in Path(root).rglob('*.sh'):
        subprocess.run(['bash', '-n', path.as_posix()], check=True)
print('Source syntax checks passed. Operational evidence remains required.')
PY

"${AGENT_TEAM_PYTHON:-python3}" scripts/check_secrets.py
