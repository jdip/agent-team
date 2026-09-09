# Development and verification

Agent Team's `machine/` configuration, skills, reconciliation helpers, `standard/`
guidance/templates, and `scripts/` delivery helpers are Tooling: they maintain
machines and repositories. There is no separate application, server, or deployable
product runtime here. Classify future code by purpose rather than its language.

Requirements: Git, authenticated `gh` for this repository, Bash, and Python 3.11+.
Use `AGENT_TEAM_PYTHON=python3.13` when the host's `python3` is older. CI uses 3.12.

Stage intended changes, then run `scripts/check.sh` for native Python/TOML/shell
syntax checks and narrow Git-index credential and personal-path checks (see [SECURITY.md](../SECURITY.md)).
Use
`git diff --check` for the actual change. Verify each changed helper through its
actual authorized operation. Source parsing is not evidence of machine agreement,
a deployment, or successful promotion. Follow machine/RECONCILE.md for the real
all-target gate; missing profile assets and unproven state must stop live writes.
Do not fabricate machine homes, forge services, orchestration tests, or coverage
apparatus for Tooling. Reported real failures drive concrete fixes.

Application Code, if introduced, requires rigorous linting, type checking,
validation, and meaningful tests with high coverage across its behavior and failure
paths. Choose and enforce the actual stack's gates and justified coverage targets
when that code exists. No stack, package manager, CI matrix, or numeric floor is
invented in anticipation of a product.
