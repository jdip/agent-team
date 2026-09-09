#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec "${AGENT_TEAM_PYTHON:-python3}" scripts/delivery.py pr-to-test "$@"
