---
name: triage
description: Assess incoming implementation work, maintain ready parents, and activate an approved ready parent when no backlog is active.
---

# Triage

Adapted from [`mattpocock/skills` triage](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/triage), revision `3cca18b368ae95cdbdebbff572ccafa662551015`.
Copyright (c) 2026 Matt Pocock. This adaptation is licensed under the included [MIT License](LICENSE).

Refine implementation intake into approved, discoverable work without changing an
active effort. Issue bodies hold current scope and acceptance criteria; comments
hold discussion, decisions, and evidence. Fold an approved amendment into its
body instead of treating a triage brief or comment as the contract.

## Establish backlog state

Resolve the current repository with `gh repo view` and read its tracker guidance.
Resolve `git rev-parse --path-format=absolute --git-common-dir`, then inspect
`codex-implementation-backlog`.

- A missing pointer means there is no active parent.
- A pointer to a closed parent means there is no active parent; retain the pointer
  until an authorized selection replaces it.
- A pointer that is unreadable, does not contain exactly one valid URL, identifies
  another repository, or cannot be read from the tracker is an error, not an
  empty active state. Stop and report it.
- An open pointed parent must be labelled `implementation:backlog`; it is the one
  active parent. Routine triage preserves its selection and claims; refinement
  follows the approved-scope rules below.

A **Ready Backlog** is an open, non-active parent carrying both
`implementation:backlog` and `implementation:ready`. Read all such parents before
recommending work. Readiness is separate from active selection and execution
authorization.

## Assess intake

Read each named issue's full body, comments, labels, parent, dependencies, and
assignees. For broad intake, paginate every open issue from the current repository,
including blocked and claimed candidates; exclude pull requests where the tracker
does not use them as a request surface. Inspect candidate parent and dependency
relationships directly when summary data is unclear.

Use the repository's domain terms and inspect relevant code before recommending an
outcome. Search existing issues and current behavior for duplicates. Refine,
deduplicate, and order work autonomously within already approved scope, while
preserving claims. Surface external blockers rather than absorbing them into an
unrelated parent.

Use proportional planning:

- Put a small, understood, approved fix with clear acceptance criteria in a
  suitable approved parent when its scope allows it. Do not manufacture a map or
  new specification for that case.
- Send a larger effort to `$to-spec` and `$to-tickets` for one specification
  parent and an approved ticket batch.
- Return substantive unresolved decisions to Wayfinder. Its entire map must be
  resolved before associated implementation proceeds.

Scope expansion and moving an issue between efforts require the user's explicit
decision. Do not reparent another effort's issue or modify an existing claim.
When approved work enters a parent, use the tracker’s native membership and
dependency operations separately, preserve its actual blockers, and read both
relationships back.

## Admit and activate deliberately

Batch ready human decisions in ordinary text and wait for answers. Reuse explicit
prior admission or activation authorization when it covers the same parent and
scope. When no parent is active, admission and activation may be approved together;
specification approval alone supplies neither.

For a prepared non-active parent, first show its objective, child scope, external
blockers, and source links. Ask whether it should join the Ready Backlog. This
admission needs explicit consent independent of any prior specification or ticket
approval. After consent, create `implementation:ready` if necessary, apply it
alongside `implementation:backlog`, and read the parent back. Do not alter the
active pointer.

Offer activation only when there is no active parent. Name the selected Ready
Backlog parent and obtain authorization to activate it. Recheck the saved pointer and parent state immediately before selection; if another
parent has become active, preserve it and stop activation. Then run
`../set-backlog/scripts/set-backlog.sh <parent-url>`, resolved relative to this
skill directory, and report its readback. This shared operation is the only
selection mechanism; do not duplicate its validation or offer to replace an active
parent during routine triage.

Creating or admitting a Ready Backlog parent does not authorize implementation.
Execution begins only through an explicitly authorized `$next-issue` or
`$next-issue-loop` invocation after activation.

## Report

Report the active parent or the exact pointer error, Ready Backlog parents,
triaged candidates and visible blockers, duplicate decisions, and every approved
write with its readback. If approval or required context is missing, leave the
affected issue and backlog state unchanged.
