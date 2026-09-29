#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
"${AGENT_TEAM_PYTHON:-python3}" - <<'PY'
from pathlib import Path
import ast
import subprocess
import sys
import tomllib
for root in ('.agents/skills', 'machine', 'scripts'):
    for path in Path(root).rglob('*.toml'):
        tomllib.loads(path.read_text(encoding='utf-8'))
    for path in Path(root).rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for path in Path(root).rglob('*.sh'):
        subprocess.run(['bash', '-n', path.as_posix()], check=True)
sys.dont_write_bytecode = True
sys.path.insert(0, 'machine')
from reconcile import HOSTS, render
for path in (Path('machine/AGENTS.md'), *Path('machine/agents').rglob('*'), *Path('machine/skills').rglob('*')):
    if path.is_file():
        for host in HOSTS:
            try:
                render(path.read_bytes(), host, path.as_posix())
            except ValueError as error:
                sys.exit(f'Host rendering failed: {error}')
print('Source syntax checks passed. Operational evidence remains required.')
PY

"${AGENT_TEAM_PYTHON:-python3}" scripts/check_secrets.py
