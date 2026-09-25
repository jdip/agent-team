---
name: pr-to-test
description: Deliver the intended task changes through the repository’s canonical PR-to-test workflow and actual test verification.
---

# PR to Test

Before any GitHub write, follow the target repository's applicable publication
policy for outgoing source, metadata and evidence. Inspect approved commit identity
and verify platform-created merge metadata after delivery; report any mismatch.

Use on the human's delivery request or as the explicitly authorized delivery step
of implementation/adoption work. A commit or finished subagent alone is not a new
delivery request. This workflow does not authorize main promotion.

Read the target repository's AGENTS.md, `docs/workflows/pr-to-test.md`, and its
actual development/verification instructions. Use `scripts/pr-to-test.sh` as the
canonical entry point. Investigate missing or contradictory interfaces before
acting; do not invent a competing release process or copy Agent Team's own runtime
assumptions into another repository.

For implementation changes, confirm covering resolved map/spec evidence under
the global Planning before implementation rule, or the operator's explicit scoped
exception. Pure planning records and research artifacts may be delivered under
that rule's planning-work boundary while a map remains open; this does not admit
implementation changes alongside them. A pre-existing
PR or delivery request does not waive it; return missing coverage to Wayfinder
through the originating owner. Reuse coverage without restarting settled design.

Prepare and commit the intended changes, preserving unrelated work in a suitable
checkout. Review every submitted change. Reuse completed review only when evidence
clearly covers all changes and findings are resolved or explicitly accepted; doubt
means perform the needed review. Do not create a review ledger.

For an implementation parent using a rollup, read
[rollup integration and completion](ROLLUP.md) before child integration or final
delivery. The canonical test script runs on the completed rollup, once for the
combined change. Child PRs target the rollup through the local integration path.

## Execution ownership

Before starting a long-running gate or delivery wait, explicitly choose its
execution and observation owner. On Codex, the primary owns validation and may
assign a workflow monitor to execute or observe a predefined bounded sequence
while the primary has useful parallel work. On Claude Code, use its native
available delegation for validation or observation within the assigned authority.
Short checks may stay with the primary; when delegation is unavailable, state
that limit and own the bounded operation directly.

The assignment names the exact command and checkout/revision or existing run,
required success evidence, failure and overall/stall boundaries, permitted
task-owned cleanup, and reporting conditions: the delegate reports terminal
evidence, actionable failure, required input or target drift, and stays quiet on
unchanged healthy progress. Authorize any successful-path mutations explicitly
within the task's scope. Before temporary compute starts, the primary uses
`cleanup-task-artifacts` to establish resource ownership and teardown.

For work already running, transfer observation with its run/session identity,
current state and log/status location, preserving the operation without restarting
it. One owner observes each run: the primary uses delegated evidence for required
progress updates rather than independently polling the same logs or status.
The primary retains interpretation, discretionary recovery, scope decisions and
final acceptance. A delegate returns failures and partial effects for that
decision; a recovery assignment must precede further corrective execution.

## Validate and deliver

Perform actual local gates: rigorous lint/type/validation/meaningful high-coverage
checks for Application Code; successful real use for Tooling. Do not build a fake
forge, fixture machine, orchestration suite, or tests of tests. Resolve routine
semver labeling using [Version classification](#version-classification) before
calling the script; pass the chosen contribution explicitly when supported.
Bookkeeping remains advisory.

Call the fixed script with the local runbook's actual arguments. Follow the result
through the runbook's completion evidence, including test deployment/processing and
usability checks when applicable. A launched script, open PR, or merge alone may be
partial progress. All canonical task-to-test merges use merge commits.

On failure inspect the earliest error and actual partial effects before recovery.
Continue routine authorized fixes and remaining steps; never blindly rerun a merge
or overwrite protection. Complete independent work. Before pausing or reporting a
failure, use `cleanup-task-artifacts` with local guidance. The delivery authority
covers this phase cleanup; preserve the current task environment and resources
needed by a pending gate. Then batch ready human decisions with concrete
recommendations when a new decision or external prerequisite is needed.

After verified delivery, record the PR and evidence, then use
`cleanup-task-artifacts` with local guidance before closing the originating issue
or final reporting. Follow its resource and retention policy; close the issue only
if its whole acceptance outcome is met. Verified test delivery permits the next
authorized issue/milestone without promotion.

If the cleanup package is unavailable, use local artifact guidance to stop/remove
only exact task-owned resources proven safe for that action. Preserve active,
shared, uncertain or needed state and attached checkouts; use supported lifecycle
tools. Report the unavailable policy and actual cleanup limits.

## Version classification

Classify the delivered behavior and compatibility impact, including behavior
encoded in rules, skills, configuration and automation prompts. Application Code
versus Tooling determines verification requirements, not version contribution.

- **major**: breaks an existing supported contract.
- **minor**: adds a backward-compatible capability.
- **patch**: corrects existing behavior while preserving supported contracts.
- **none**: changes no delivered behavior, such as editorial-only wording or links.

For a mixed task PR, choose the highest applicable contribution. A rollup is one
test-bound contribution classified from the combined behavior and compatibility
impact; its child PRs are integration events and are not added again. Independent
test-bound PRs retain the repository's additive version policy. A rule that
corrects missing teardown is a patch; correcting its spelling without changing
execution is none. Judge instruction edits by the behavior they direct, not their
file extension. Apply a repository's explicit compatibility/version policy where
it refines this classification, and record the contribution's reason in the PR.
