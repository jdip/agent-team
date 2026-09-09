---
name: pr-to-test
description: Deliver the intended task changes through the repository’s canonical PR-to-test workflow and actual test verification.
---

# PR to Test

Use on the human's delivery request or as the explicitly authorized delivery step
of implementation/adoption work. A commit or finished subagent alone is not a new
delivery request. This workflow does not authorize main promotion.

Read the target repository's AGENTS.md, `docs/workflows/pr-to-test.md`, and its
actual development/verification instructions. Use `scripts/pr-to-test.sh` as the
canonical entry point. Investigate missing or contradictory interfaces before
acting; do not invent a competing release process or copy Agent Team's own runtime
assumptions into another repository.

Prepare and commit the intended changes, preserving unrelated work in a suitable
checkout. Review every submitted change. Reuse completed review only when evidence
clearly covers all changes and findings are resolved or explicitly accepted; doubt
means perform the needed review. Do not create a review ledger.

Perform actual local gates: rigorous lint/type/validation/meaningful high-coverage
checks for Application Code; successful real use for Tooling. Do not build a fake
forge, fixture machine, orchestration suite, or tests of tests. Resolve routine
semver labeling from the actual change; none is valid and bookkeeping is advisory.

Call the fixed script with the local runbook's actual arguments. Follow the result
through the runbook's completion evidence, including test deployment/processing and
usability checks when applicable. A launched script, open PR, or merge alone may be
partial progress. All canonical task-to-test merges use merge commits.

On failure inspect the earliest error and actual partial effects before recovery.
Continue routine authorized fixes and remaining steps; never blindly rerun a merge
or overwrite protection. Complete independent work and batch ready human decisions
with concrete recommendations when a new decision or external prerequisite is needed.

After verified delivery, record the PR and evidence and close the originating issue
only if its whole acceptance outcome is met. Use `cleanup-task-artifacts` when
available, together with local artifact guidance. If that package is unavailable,
apply the same rule directly: remove only associated resources proven safe; retain
attached Codex worktrees, shared/uncertain artifacts, and unpublished work. Use
supported lifecycle handling, never raw app-storage edits or blanket pruning.
Report delivery, actual cleanup, retained resources, and unresolved work. Verified
test delivery permits the next authorized issue/milestone without promotion.
