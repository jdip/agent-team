---
name: set-backlog
description: Select an existing implementation specification parent as this repository's Active Backlog. Does not start implementation.
---

# Set Backlog

Use GitHub through `gh` and read the repository's tracker instructions. Resolve
this repository with `gh repo view`. This entry point selects an existing parent;
`triage` owns intake and grouping, while `to-spec` and `to-tickets` own preparing
and publishing an approved specification and breakdown.

## Select the existing parent

A supplied parent may come from an explicitly approved `whats-next` selection
proposal; the human need not repeat its URL.

Read the supplied issue, comments, all native children (`sub_issues --paginate`),
and its linked design. Verify it is an open implementation specification in this
repository with an objective, approved scope and sources, completion boundary,
and standing preferences. For mapped work, verify the entire associated map is
resolved; a closed planning map is not an implementation parent. Show the parent's
name, objective, and child scope. Preserve membership, blockers, and claims.

An explicit request to select that parent is sufficient authorization, including
replacing an existing selection. Add `implementation:backlog` if absent and the
issue is clearly the requested implementation parent; create the label if needed.
Clarify an ambiguous issue's role before converting it. Ready admission alone is
not activation authorization.

Without a supplied parent, inspect the saved pointer and paginate all open
`implementation:backlog` parents. Show the current selection and recommend an
existing prepared parent by name and scope. Wait for the user's selection in
ordinary text, unless this conversation already supplies it. If no suitable parent
exists, use `triage` to prepare approved work; do not create or group issues here.

## Save and verify

Recheck the intended parent's state and role, then run
`scripts/set-backlog.sh <parent-url>` relative to this skill directory. This is the
shared selection mechanism also used by triage after authorized activation.
It validates the open current-repository parent and atomically writes one URL line
to `codex-implementation-backlog` in Git's absolute common directory. Failure
preserves the existing pointer. The pointer is shared across worktrees and remains
independent of `codex-wayfinder-map`.

Read the saved pointer back and report the parent's name, URL, and selected scope.
Selection does not claim work or start development; `next-issue` or
`next-issue-loop` requires execution authorization.
