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

For an implementation rollup, use the child integration path below until every
child is complete. Run this canonical test-delivery path once from the completed
rollup, with final acceptance recorded on the implementation parent. Single-ticket
work defaults to direct delivery. The shared
[rollup contract](../../machine/skills/pr-to-test/ROLLUP.md) owns the lifecycle.

Choose the contribution using the shared
[Version classification](../../machine/skills/pr-to-test/SKILL.md#version-classification)
guidance, then set `contribution` to `major`, `minor`, `patch` or `none`.
From the repository root run:

```bash
scripts/pr-to-test.sh --title 'Concrete change' --body-file /path/to/pr-body.md --semver "${contribution:?Set contribution from the actual change}"
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
workflow does not promote main; verified direct delivery permits continuation,
and verified rollup delivery completes the implementation parent's delivery gate.

## Feature PR into an implementation rollup

This is the native integration path for a parent whose specification records the
rollup. Use Git and `gh`; `scripts/pr-to-test.sh` always targets test and must not be
used for child integration. Before the first push, inspect `.github/workflows/`
and relevant hosted deployment configuration. Agent Team currently has only the
Validate workflow on pushes and PRs, without branch filters, and no deployed app.
Changes to those triggers require fresh inspection.

Start a child's `codex/` branch in its worktree from the fetched rollup. Review,
commit and run `scripts/check.sh` and `git diff --check`. Set `rollup` to the exact
branch recorded on the parent and `feature` to the current child branch. Inspect
existing PRs before creating one:

```bash
git push origin "HEAD:refs/heads/${feature:?Set the child branch}"
gh pr list --base "${rollup:?Set the parent rollup}" --head "$feature" --state open
gh pr create --base "$rollup" --head "$feature" --title 'Concrete child outcome' --body-file /path/to/child-pr.md
```

Reuse one matching PR; multiple matches or an unexpected base require investigation.
Record the intended feature head and current rollup base SHAs. Wait at most fifteen
minutes for the current PR's Validate run to register and pass, using `gh pr view`,
`gh pr checks` and `gh run view` to inspect the linked run. Require the `validate`
job for the current pull_request event and integration revision, not merely an old
passing push run. All other applicable checks must pass too. No registered checks,
a skipped required job, or unavailable evidence means stop. The rollup may lack
branch protection, so `--required` alone and merge readiness alone are insufficient.

```bash
gh pr checks "$child_pr" --watch --fail-fast --interval 10
gh pr view "$child_pr" --json state,baseRefName,baseRefOid,headRefName,headRefOid,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup
```

Before merging, require OPEN, the intended branch names and SHAs, non-draft status,
satisfied hosted review policy and CLEAN merge readiness. Recheck parent ownership
and serialize integrations. On base/head drift, merge current rollup into the child
and repeat affected review/checks. Use the authenticated account's GitHub no-reply
address for `merge_email`, following the public-work policy above:

```bash
gh pr merge "$child_pr" --merge --match-head-commit "$child_head" --author-email "$merge_email"
gh pr view "$child_pr" --json state,mergeCommit,url
git fetch origin
```

Verify MERGED, exactly two merge parents matching the intended rollup base and child
head, and merge reachability in `origin/$rollup`. Inspect author/committer metadata
against the public-work policy. Run `scripts/check.sh` from a task-owned detached
worktree at that exact merge revision; remove only this verification worktree after
success, retaining failed state for investigation. Record review, checks and merge
evidence on the child before explicitly closing it. Do not rely on issue auto-close
keywords for a PR into a non-default branch. Keep the parent open for final delivery.
The PR body links the parent without an auto-close instruction.

For final delivery, fetch the rollup and test, merge any newer test changes into the
rollup, and validate/review the resulting combined diff. Use the canonical path above
with one semver classification for the whole result. Promotion already counts only
first-parent test PR merges, so child integration PRs are excluded without a new
version ledger. On a failure inspect actual refs, PR state and merge effects before
resuming; never blindly replay a merge or bypass branch protection.
