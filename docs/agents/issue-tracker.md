# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

Before creating, editing or commenting on issues/PRs, applying labels, or
uploading evidence, follow the [public-work policy](../../SECURITY.md#public-repository-work).
Review the outgoing text, metadata, attachments and linked destinations; publish
sanitized evidence and keep private originals outside this repository.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Remediation findings and deduplication

Use this procedure for actionable friction, discovered weaknesses, and deferred
blockers under the global scope guidance. The primary agent completes filing for
findings returned by delegated agents.

1. Resolve the owning repository from its remote and affected component; use
   `--repo <owner>/<repo>` explicitly when filing outside the current clone.
2. Search open and closed issues using component names, symptoms, and distinctive
   error text, for example
   `gh issue list --repo <owner>/<repo> --state all --search '<terms>' --limit 100`.
   Vary the terms and expand or paginate results when truncated; an empty narrow
   search alone is insufficient. Read likely matches with
   `gh issue view <number> --repo <owner>/<repo> --comments` and inspect relevant
   code or recorded fixes. Match the underlying problem and affected behavior,
   rather than title similarity alone.
3. Reuse a matching open issue, adding a comment only for material new evidence.
   For a closed match, inspect its resolution and current behavior: a resolved
   problem needs no new issue; a demonstrated recurrence can be recorded in a new
   issue linked to the prior fix, explaining why it is new work. Preserve existing
   ownership, claims, and approved scope.
4. If no issue covers the remaining problem, create a scoped issue with the
   observed behavior, concrete reproduction or source evidence, impact, relevant
   workaround, and a verifiable remediation outcome. State whether it blocks the
   current task and link the originating issue or PR when one exists. Use a body
   file for multiline text: `gh issue create --repo <owner>/<repo> --title '<title>'
   --body-file <path>`. Filing does not admit work to an implementation backlog.
5. Read back the created issue or updated comment and report its URL. When the
   current task has an issue, link the finding there and record an actual blocker
   using the native dependency convention below; use an explicit linked blocker
   note when native dependencies cannot represent it. Keep the blocked task open.
   If tracker access fails, retain the evidence and proposed issue text in the task
   response and identify the failed operation; the global blocker rule still applies.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: record the answer, complete Wayfinder’s implementation handoff,
  close the decision, then append a context pointer to its map when present.
  Before closing a design with remaining implementation, verify an open follow-up
  linked both ways, or record the user’s explicit deferral/abandonment. Reuse the
  same effort’s follow-up; unsettled designs remain explicitly awaiting planning.

## Implementation backlogs

Used by `to-spec`, `to-tickets`, `triage`, `set-backlog`, `next-issue`, and
`next-issue-loop`.

The Implementation Specification body owns current approved scope and acceptance;
comments hold decisions, discussion, and evidence. Present the proposed parent and
child breakdown together for one batch approval, reusing explicit prior approval.
Publish the approved relationships through `to-tickets` and verify them before
reporting completion. Publication alone does not select or execute a backlog.

- **Parent**: an open issue labelled `implementation:backlog`, containing the
  implementation objective, approved design links, execution boundaries, and
  completion criteria. Native sub-issues hold the ordered work set. Do not use
  the closed planning map as the implementation parent.
- **Pointer**: `codex-implementation-backlog` in the absolute Git common directory
  contains exactly one parent URL. It is untracked, shared across worktrees, and
  independent of `codex-wayfinder-map`.
- **Membership**: use the same native sub-issue operations described above. Inspect
  `GET repos/<owner>/<repo>/issues/<child>/parent` before attaching existing work.
  Do not silently reparent issues from another effort. Preserve dependencies.
- **Design gate**: before taking or continuing implementation, follow next-issue’s
  Design gate against the specification’s associated map, not the saved planning
  pointer. An open/reopened map pauses the whole backlog until resolved. Routine
  implementation choices do not reopen maps. A substantive missing decision is
  recorded in the reopened map and linked from the claimed, open implementation
  issue. A closed map with unsettled required decisions is not clearance.
- **Selection and claim**: first open, unblocked, unclaimed child in parent order,
  or a completion-first eligible child supplied by `whats-next`. Its ranking
  preserves dependencies and explicit user ordering; eligibility and claims are
  still checked by `next-issue`.
  Recheck before assigning `@me`, then leave a session-identifying claim comment.
  An existing assignee can belong to another session of the same user; do not
  steal it. Resume only this conversation's claim or an explicit handoff.
- **Resolution**: record the delivered PR and actual verification evidence, then
  close the issue when its outcome is met. Verified delivery to `test`, including
  applicable test deployment, permits the next task. Promotion is separately
  requested, not a per-issue gate. Close the parent only when its outcome and all
  children are complete.

## Ready Backlog and Triage

`implementation:backlog` identifies an Implementation Specification parent.
`implementation:ready` records the user's approval to admit that prepared parent
for future execution. Create the ready label when needed. The Ready Backlog is
open ready-labelled parents except the currently active parent. Labels do not
activate work; the saved pointer identifies the one Active Backlog.

Paginate open parent intake, for example:
`gh api repos/<owner>/<repo>/issues --method GET -f state=open -f labels=implementation:backlog --paginate`.
Exclude pull requests. Read children, claims, and native dependencies separately;
blocked children still belong to the approved scope. For other incoming work,
paginate the relevant open issues without filtering out blocked or claimed work.

Triage refines, deduplicates, and orders within approved scope, preserving claims
and dependencies. Group approved small fixes in a suitable approved parent without
manufacturing a map or a new specification. Expanding scope, moving work between
efforts, and admitting prepared parents to the Ready Backlog require a human
decision. Current scope and acceptance live in issue bodies; comments hold evidence.

Triage reads and validates the saved pointer before offering activation. An absent
pointer or a verified closed selected parent means no active parent. An invalid,
unreadable, wrong-repository, or inaccessible pointer is an unresolved error,
not an empty queue. Preserve the pointer while investigating. Offer activation
only when no parent is active, and carry out explicit approval through the shared
`set-backlog/scripts/set-backlog.sh` mechanism. Routine triage preserves an open
active parent; explicit `set-backlog` may switch it at the user's request.
Completion never selects another parent automatically. Readiness and activation
provide no independent permission to execute work.
