# PR to test

Before GitHub writes, follow the [public-work policy](../../SECURITY.md#public-repository-work)
for outgoing source, metadata and evidence, including approved commit identity.
The script verifies the merge author; inspect that result and the remaining
platform-created metadata against the policy after delivery.

The authenticated GitHub account must enable email privacy for its GitHub-provided
no-reply address to be used for web merges. Repository-local Git author settings
do not configure that account setting. If GitHub rejects the explicit merge email,
preserve the open PR and resolve the account's email privacy setting before
resuming; never fall back to a personal address.

An implementation request includes preparation, intended commits, push, PR, checks,
merge, and verified test delivery. Preserve unrelated work and use a clean committed
task checkout. Read AGENTS.md and docs/development.md. Required tools are Git,
authenticated gh, Bash, and Python 3.11+ (`AGENT_TEAM_PYTHON` can select it).

Review all submitted changes. Reuse completed review only with evidence covering
every change and resolved/accepted findings; doubt requires the relevant review.
Run scripts/check.sh, git diff --check, and the actual changed helper operation.
No review record framework or Tooling coverage suite is needed.

From the repository root run:

```bash
scripts/pr-to-test.sh --title 'Concrete change' --body-file /path/to/pr-body.md --semver none
```

The script pushes the current named task branch, creates or reuses its open PR to
test, applies the chosen advisory semver label, waits up to fifteen minutes for
checks and GitHub merge readiness within one shared fifteen-minute limit, and
merges the exact intended head with a merge commit. Passing older checks alone
do not establish readiness while new PR checks register. Draft/review requirements,
conflicts, branch drift, and failed checks return for investigation; no merge retry
or protection bypass is performed. GitHub's protected
branch gate remains authoritative; the required validate check invokes the actual
source checks. Missing/failed gates or head drift stop the script.

After merge it fetches origin and checks the merged revision in a fresh temporary
Git worktree using that revision's scripts/check.sh. This repository has no deployed
application: completion is merged-source verification plus the issue's applicable
real-use evidence. The script removes only its own successful verification checkout.
A failed verification retains its checkout and reports the path.

The supervising agent then records the PR, review and real-use evidence, closes the
issue only when its acceptance outcome is met, and cleans all associated resources
proven safe. Task-created branches/worktrees, staging, and logs can qualify; shared
or uncertain resources cannot. Never remove a checkout backing a Codex task. Use
supported lifecycle handling or retain it. An attached worktree is not a delivery
failure. Do not use broad pruning or edit app storage.

On failure inspect the earliest causal error and actual push/PR/check/merge effects.
Use gh pr view/checks and git state before deciding recovery; do not blindly replay.
If already merged, verify that exact merge directly and finish bookkeeping instead
of opening another PR. Resolve routine problems within the authorized issue. External
approval or a new intent-dependent decision stays pending. Report partial results.

Semver labels are advisory, with none valid. No tag is made on task delivery. This
workflow does not promote main; verified delivery to test permits the next issue.
