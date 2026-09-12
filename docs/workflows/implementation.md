# Implementation workflow

Use [whats-next](../../machine/skills/whats-next/SKILL.md) to choose and advance
current-repository work through these owners. It carries established approval
across handoffs and reassesses at completed planning/implementation boundaries.
It may supply a completion-first eligible child; dependencies, explicit user
order, claims, and the Design gate still apply. Missing selection/execution
authority remains a concrete human decision. The coordinator reads current
dependency alerts during ordinary discovery, independently of stable-baseline
maintenance assessment, and routes actionable findings through the repository's
planning, pull-request conventions, review and delivery. It also considers hygiene,
opted-in verification audits and Agent Team alignment under its stable-baseline
assessment rules.

The [global planning rule](../../machine/AGENTS.md#planning-before-implementation)
applies inside and outside this coordinator, including direct specialist requests.
Wayfinder owns the grilling entry before new maps and subsequent decision
resolution; the existing executor
uses one specification parent and at least one executable child. Reuse covering
plans and authority across these owners, preserving phase-specific completion
boundaries. Planning records can precede completed implementation planning.

Use `to-spec` to synthesize the approved design into one Implementation
Specification parent and its outcome-based ticket proposal. Review the parent and
breakdown together, reusing applicable approval. `to-tickets` publishes or reuses
that same parent, its native children, real dependencies, and reciprocal design
links. Bodies hold current approved scope; comments hold discussion and evidence.
Before a resolved design closes with implementation remaining, Wayfinder verifies
an open follow-up or the user's explicit deferral/abandonment.

Triage refines approved work and offers prepared parents for Ready Backlog
admission. The [tracker convention](../agents/issue-tracker.md#ready-backlog-and-triage)
keeps future readiness separate from each effort's active selection. Independent
tasks use explicit scopes under [selection scope and handoff](../../machine/skills/set-map/SELECTIONS.md);
resumes, forks, moves and human-approved transfers follow that owner. Triage offers
activation only when no parent is active. Explicit `set-backlog` selects an
existing parent through its shared script. Neither publication nor admission nor
selection independently authorizes execution.

An authorized `next-issue` executes one child through the canonical
[PR-to-test workflow](pr-to-test.md). `next-issue-loop` continues across child
boundaries within the initially selected parent. Next-issue owns the Design gate:
recheck associated design state before taking or continuing work and before
delivery/closure. A reopened map pauses the entire backlog, including independent
tickets; keep the current issue claimed and open. Routine implementation choices
remain with the agent. Ask all ready human questions together in ordinary text,
wait for actual answers, and reuse approvals already supplied.

Relevant reviews, actual repository checks, and verified merged-source delivery
permit the next child; main promotion is separate. Close the parent only when its
full outcome and children are complete. Keep its scoped binding as the completed
selection, and wait for explicit selection/execution of another effort. Preserve
claims, dependencies, unrelated state, and checkouts still backing Codex tasks.

The [Machine Profile](../../machine/PROFILE.md) owns the exact distribution.
Wayfinder, to-spec, to-tickets, and triage are attributed Agent Team adaptations;
next-issue and its loop remain the sole implementation workflow. Reconciliation
is separately requested, so source delivery does not claim a live installation.

## Prepare target guidance before adoption or upgrade

When obsolete or conflicting target guidance needs preparation, invoke
[prepare-repository](../../machine/skills/prepare-repository/SKILL.md) from Agent
Team with the target path and intended Greenfield Initialization, Brownfield
Adoption, or Standards Upgrade workflow. The skill resolves one exact Agent Team
baseline and assesses target documents as review material. All four alignment
workflows follow the selected standard's Target assessment and planning outcome:
read-only assessment, target-owned Wayfinder map and approved spec, then execution
against the target's state and workflow goals. Reuse covering plans and handoffs;
preparation edits retain their documentation-only boundary. The preparation skill's final pass invokes
the full OpenAI `openai-docs` skill for the migration and instruction audit before combined review and verification.

The result is a committed local preparation branch and an evidence-based readiness
handoff. Continue from that prepared branch's changes when separately authorized
to perform adoption or upgrade; do not lose them by starting from an unchanged
baseline. Preparation itself does not deliver adoption, push, or merge the target.
The Machine Profile distributes the package through ordinary reconciliation;
source delivery alone does not install it. Verify package delivery separately from
real installation and target preparation.
