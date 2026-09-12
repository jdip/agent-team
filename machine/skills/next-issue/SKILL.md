---
name: next-issue
description: Claim and implement one eligible issue from this repository's saved implementation backlog, through verified delivery and safe cleanup.
---

# Next Issue

Use this for a request to implement the next backlog issue. Discussing or
creating this skill does not authorize executing the backlog. Work one issue per
invocation; `$next-issue-loop` overrides that boundary. Apply the Design gate
before edits; resume covered implementation without another planning interview.
An authorized coordinator or named workflow handoff carries the request's
execution authority for the target Active Backlog without waiving scope, claims
or planning.

## Load the backlog and select work

Read [selection scope and handoff](../set-map/SELECTIONS.md). Resolve the
explicit backlog scope and task owner through `set-backlog`'s selector. Establish
a new authorized binding with `show`, retain scope, owner, generation and parent
URL, and use `check` with that binding for continuation and before mutations.
Missing, invalid or transferred state returns to the selection owner with existing
authority. This executor never adopts another scope or parent. Preserve the
independently selected map.

Read repository instructions, the saved parent, and relevant design/decision
links. Verify the parent is an issue in this repository labelled
`implementation:backlog`. A closed parent does not authorize starting another
effort: report its state; if unfinished children remain, surface the inconsistency.
The parent body and child bodies hold current approved scope and acceptance;
comments hold decision history and delivery evidence. Ready labels do not select
work or authorize execution. Keep this invocation within the initially selected
parent; if the selection binding changes, stop and report it rather than following
another session into a different effort.

Apply the **Design gate** below before selecting or resuming work.

Fetch ALL children in tracker order and their current dependencies and claims.
For GitHub use `gh` and the repository's issue-tracker conventions: native
`/issues/<parent>/sub_issues --paginate` and
`/issues/<child>/dependencies/blocked_by --paginate`. Use the parent's explicit
ordered `## Backlog` task list only when the repository uses the fallback.
If a dependency summary is stale or unclear, inspect the blocker issues directly.

Select the first open, unblocked, unclaimed child in parent order unless
`whats-next` supplies a completion-first eligible selection under its approved
ranking rules. Recheck that selection against this parent, dependencies, explicit
user order, and claims; a coordinator handoff cannot waive eligibility. An assignee is
a claim, even if it is the same GitHub user: another session may own it. Resume a
claim only when this conversation established it or the user explicitly hands it
over. Re-read the candidate immediately before claiming, assign the driving user
(`gh issue edit <n> --add-assignee @me`), and record this session's claim in an issue
comment with a task/session link or identifier when available. Assignment is not an
atomic lock; inspect claim evidence and yield on a concurrent ownership conflict.
Do not steal a claim, bypass a blocker, or skip a selected human-dependent issue.

If no issue is eligible, distinguish completed backlog from blocked or claimed
work. Name what must change; do not poll indefinitely, invent tasks, or schedule
a continuation. Close the parent only when its full outcome is actually complete.

## Design gate

Identify the associated Wayfinder map from the specification's approved design
links and the originating decision's parent relationship. Read that map's body,
comments, and all children with pagination, including their resolutions and any
remaining fog. Distinguish this effort's map from incidental historical
references. Use the specification's sources, not the independently selected
planning map, which may belong to an unrelated effort. Require a resolved map
and approved specification that cover this child, unless the operator explicitly waived the
missing planning requirement for this scope. Record and honor only that
exception. Small fixes, standalone decisions and direct implementation requests
do not self-exempt. Missing coverage returns to Wayfinder and `to-spec` through
the invoking owner; continue read-only discovery and preserve claims while
planning is unresolved.

Apply Wayfinder's **Map-entry evidence** rule before accepting the associated
map as design coverage, including when its map and specification are already
approved. Missing dialogue evidence returns to that owner before implementation.

The entire associated map must be resolved: the map and every required decision
are closed and no substantive decision remains unsettled. An open or reopened
map pauses the whole associated backlog, including otherwise independent
tickets. A closed map with open required decisions or unresolved fog is an
inconsistency to investigate, not permission to execute. A standalone source
decision that is reopened likewise needs resolution before associated work
proceeds. Unavailable or ambiguous source state is unresolved; never infer
clearance from a failed read.

Recheck the selection owner and generation, parent state, and associated design
state before a claim, when resuming after human input or interruption, before each repository or
tracker mutation, before delivery or issue closure, and between loop issues. Stop
on a changed selection, transferred ownership, stale generation or closed parent;
resume only within explicit user authorization. If implementation exposes a
substantive missing decision, reopen the associated map (or standalone decision),
record the concrete question there and link it from the implementation issue,
and pause the whole backlog until the decision is resolved. Keep the current issue
claimed and open. Use Wayfinder for an actual missing decision; routine implementation
choices stay with the implementing agent and do not reopen a map.

## Implement and verify

Read the entire selected issue and relevant comments, repository instructions,
domain docs, and linked acceptance criteria. Inspect actual code before choosing
the approach. Use the issue's required skills and delegate bounded independent
work when authorized. Make routine implementation choices within the approved
design; do not turn every detail into a user decision.

Use a suitable branch/worktree while preserving unrelated work. Implement the
whole authorized outcome, including necessary concrete fixes. Apply the
repository's documented Application Code/Tooling classification by purpose:

- Application Code gets rigorous linting, type checking, validation, and meaningful
  tests with strong emphasis on high coverage. Invoke `tdd` for bug fixes and
  new or changed application behavior; that skill owns the test-first loop. Follow actual local gates.
- Tooling is validated by successful real use. Do not build coverage suites,
  fake environments, resumable state machines, or tests of tests for tooling.
  Existing real checks can be run without inventing an orchestration test product.

Review the submitted changes. Reuse existing completed review only when evidence
clearly covers ALL of them and findings are resolved or explicitly accepted.
If coverage of the review is uncertain or subsequent changes invalidate it,
perform the necessary review. Add no review ledger or attestation framework.

## Deliver

The request to implement the issue includes its ordinary commits, push, PR to
`test`, applicable gates, merge, and local test-environment verification under the
approved backlog/runbook scope. When an approved child invokes a workflow with a
more limited completion boundary, honor that owner: repository preparation ends
at its verified local documentation handoff; separately scoped adoption/delivery
work remains open. For test delivery, read `docs/workflows/pr-to-test.md`; use the shared
`pr-to-test` skill when available and `scripts/pr-to-test.sh` as the canonical
entry point. Use merge commits, preserving history. Local runbooks define actual
application/deployment effects and completion evidence. An open PR, a successful
script launch, or a merge without required test deployment is not completion.

For this repository's label/tag policy, semver is per PR and `none` is valid.
Bookkeeping must not become an artificial release gate; real application and
delivery requirements remain in force.

**Verified delivery to test is sufficient to continue.** Do not promote to main,
require a promotion per issue/milestone, or block subsequent work on promotion
unless the user explicitly requests it as part of the current scope.

### Initial bootstrap

If canonical delivery skills/scripts do not exist yet, inspect the approved
backlog and current owning guidance for the missing delivery prerequisite.
Assess inherited bootstrap procedures under the repository's adopted Repository
Standard Guidance retirement outcome, where declared; an old plan or prior
approval alone does not make one current authority. Use a concrete documented
native Git/`gh` path only when currently authorized; do not require later
tooling to exist before its prerequisite issues can ship. If no such procedure
exists, prepare one minimal proposal for the actual missing steps and batch the
needed human decisions. Do not silently invent gates, bypass existing checks,
scaffold a full release system, or declare an undelivered issue complete.

## Recover, clean up, and resolve

Investigate failures using actual state and partial effects. Recover routine
problems within scope rather than blindly rerunning commands. Preserve user
decisions and external approval gates. Missing access or a substantive
unresolved design choice keeps the issue claimed and unresolved. Apply the
Design gate for a substantive missing decision; covered implementation reuses
its existing map.

Before pausing, complete independent work within the issue and ask ALL ready
questions together in ordinary text, with concrete recommendations, and wait
for the actual answers. Do not use timed or disappearing question widgets.
Do not guess dependent answers, add confirmation for settled points, or treat a partial reply as approval
of unanswered decisions. Resume this issue after the reply.

After delivery, clean all provably associated AND safe-to-remove task resources,
including branches, worktrees, containers, and logs, under local guidance. Preserve
unpublished work and shared/uncertain artifacts. Never delete a checkout still
backing a Codex task. Use supported app lifecycle handling; if safe removal cannot
be established, retain and report it. Do not use broad pruning or edit app storage.
Deferred safe cleanup is reported honestly and is not a main-promotion gate.

Post a resolution linking the delivered PR, verification/review evidence, and any
remaining non-blocking remediation or retained artifacts. Close the issue only
when its acceptance outcome is met. Do not close dependency-blocking requirements
as complete merely to advance the queue. Record new material work as scoped
issues and preserve/wire dependencies; parent inclusion follows the user's scope,
not arbitrary expansion. Avoid duplicate issues.

Refresh the parent/children and record a concise linked outcome without duplicating
tracker status in a table. If every child is closed, verify the parent outcome
before closing it. Report delivered work and any blocker or retained cleanup.
Stop after this one issue unless running under `$next-issue-loop`.
