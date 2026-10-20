#!/usr/bin/env bash
# Full source checks, or targeted ones with check_source.py's --base/--feature; the privacy check always runs.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
"${AGENT_TEAM_PYTHON:-python3}" scripts/check_source.py "$@"
"${AGENT_TEAM_PYTHON:-python3}" scripts/check_secrets.py
