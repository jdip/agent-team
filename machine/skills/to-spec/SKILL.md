---
name: to-spec
description: Turn a resolved design or larger approved effort into a draft implementation specification and ticket batch for review.
---

# To Spec

Adapted from [`mattpocock/skills` to-spec](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-spec), revision `3cca18b368ae95cdbdebbff572ccafa662551015`.
Copyright (c) 2026 Matt Pocock. This adaptation is licensed under the included [MIT License](LICENSE).

Turn a resolved Wayfinder map or larger approved effort into the draft for one
implementation specification parent and its executable ticket breakdown. The
parent is also the implementation backlog; do not create a parallel planning or
queue issue. `to-tickets` owns publication after the batch is approved.

## Choose the planning path

Read the repository instructions, issue-tracker conventions, domain vocabulary,
relevant code, and supplied design sources. Treat issue bodies as the current
approved scope and acceptance criteria; use comments for discussion, decisions,
and evidence. Fold an approved amendment into the draft body instead of making a
comment the authoritative contract.

Search the open `implementation:backlog` parents for one already linked to the
same effort. Reuse that parent and its approved children when they match the
sources and scope; preserve their claims, dependencies, and current scheduling
state. Do not create a duplicate parent or move work from another effort.

For work from Wayfinder, read the complete map, its comments, every child, and
material linked decisions. Proceed only when the whole map is resolved. A
substantive unresolved decision returns to Wayfinder and pauses the associated
effort; routine implementation choices stay with the implementer.

Use proportional planning. Route a small, understood fix with clear acceptance
criteria to its suitable approved backlog; do not manufacture a map or a new
specification. Use this skill for a larger effort that needs a bounded parent and
decomposition.

Before a resolved design closes, ensure its implementation follow-up is open and
linked both ways, or record the user's explicit decision to defer or abandon that
work. Reuse one follow-up across related decisions rather than creating duplicates.

## Draft the handoff

Synthesize a parent issue draft with:

- an objective and current approved scope;
- acceptance criteria and completion boundary;
- links to the resolved map, material decisions, and other accepted sources;
- the `implementation:backlog` role; a newly created parent is not active or
  implementation authorization, while an existing parent's actual scheduling
  state remains unchanged; and
- applicable standing execution preferences, without copying the design's full
  discussion history.

Then propose independently verifiable ticket outcomes. Prefer vertical slices
where they make a complete behavior demonstrable; create prerequisite
infrastructure work only when it is a real prerequisite. For every proposed
ticket, state its outcome, acceptance criteria, relevant source links, and only
the tickets that genuinely block it.

Classify each outcome by purpose. Application Code needs linting, type checking,
validation, meaningful behavioral tests, and strong coverage. Tooling needs
successful real use and focused source checks; do not manufacture coverage or
fake-environment suites. Prefer a clean replacement that removes superseded
callers and configuration; use expand--contract only when a concrete blast radius
requires both forms to coexist temporarily.

Present the parent draft and the full ticket breakdown together in one ordinary
text batch. Ask for approval of the scope, acceptance criteria, ticket granularity,
and real dependency edges together. Reuse an explicit approval that covers this
same draft; a material change needs review of the changed scope. Do not use timed
or disappearing questions.

After approval, hand the approved draft and sources to `$to-tickets`. It creates
the parent and children, records separate native membership and dependency edges,
and reads them back. That publication does not select the parent as active or
authorize execution; use `$set-backlog` and `$next-issue` or `$next-issue-loop`
only with the required explicit authorization.
