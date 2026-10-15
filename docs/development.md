# Development and verification

Agent Team's `.agents/skills/` and `machine/` packages, `standard/` guidance and
templates, and `scripts/` delivery helpers are Tooling: they maintain machines and
repositories. There is no separate application, server, or deployable
product runtime here. Classify future code by purpose rather than its language.

Requirements: Git, authenticated `gh` for this repository, Bash, and Python 3.11+.
Native Windows delivery uses Git Bash rather than Windows' WSL launcher; Linux
and macOS use their `bash` as usual.
Use `AGENT_TEAM_PYTHON=python3.13` when the host's `python3` is older. CI uses 3.12.

Stage intended changes, then run `python3 scripts/check_secrets.py` for the
mandatory pre-push Git-index privacy check (see [SECURITY.md](../SECURITY.md)).
`scripts/check.sh` adds native Python/TOML/shell syntax checks and remains available
for optional local feedback. Use
`git diff --check` for the actual change. Verify each changed helper through its
actual authorized operation.

Hosted Validate is the authoritative source check, run once per pull-request
integration; an unchanged promotion or sync can reuse its prior integration's
successful run when the source tree, runner image and Python version match.
The delivery scripts attribute the current run to each merge by its tested parents and tree, as the
[standard's verification evidence](../standard/README.md#verification-evidence)
outcome requires; a changed or unproven merge needs its own Validate run. Source parsing is not evidence of machine agreement,
a deployment, or successful promotion. Follow machine/RECONCILE.md for the real
all-target gate; missing profile assets and unproven state must stop live writes.
Do not fabricate machine homes, forge services, orchestration tests, or coverage
apparatus for Tooling. Reported real failures drive concrete fixes.

Application Code, if introduced, requires rigorous linting, type checking,
validation, and meaningful tests with high coverage across its behavior and failure
paths. Choose and enforce the actual stack's gates and justified coverage targets
when that code exists. No stack, package manager, CI matrix, or numeric floor is
invented in anticipation of a product.
