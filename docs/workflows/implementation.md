# Implementation workflow

Use [whats-next](../../machine/skills/whats-next/SKILL.md) to choose and advance
current-repository work through these owners. It carries established approval
across handoffs and reassesses at completed planning/implementation boundaries.
It may supply a completion-first eligible child; dependencies, explicit user
order, claims, and the Design gate still apply. Missing selection/execution
authority remains a concrete human decision. The coordinator also considers
dependency upkeep, hygiene, opted-in verification audits and Agent Team alignment
under its stable-baseline assessment rules; existing update PRs remain candidates
for ordinary implementation delivery.

Wayfinder records substantive decisions and their resolutions. Resolve the whole
associated map before executing mapped work. Small understood fixes can enter a
suitable approved parent with clear acceptance criteria; they need no manufactured
map. A resolved standalone design decision also needs no map merely for this handoff.

Use `to-spec` to synthesize the approved design into one Implementation
Specification parent and its outcome-based ticket proposal. Review the parent and
breakdown together, reusing applicable approval. `to-tickets` publishes or reuses
that same parent, its native children, real dependencies, and reciprocal design
links. Bodies hold current approved scope; comments hold discussion and evidence.
Before a resolved design closes with implementation remaining, Wayfinder verifies
an open follow-up or the user's explicit deferral/abandonment.

Triage refines approved work and offers prepared parents for Ready Backlog
admission. The [tracker convention](../agents/issue-tracker.md#ready-backlog-and-triage)
keeps future readiness separate from the single active selection. Triage offers
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
full outcome and children are complete. Keep its pointer as the completed
selection, and wait for explicit selection/execution of another effort. Preserve
claims, dependencies, unrelated state, and checkouts still backing Codex tasks.

The [Machine Profile](../../machine/PROFILE.md) owns the exact distribution.
Wayfinder, to-spec, to-tickets, and triage are attributed Agent Team adaptations;
next-issue and its loop remain the sole implementation workflow. Reconciliation
is separately requested, so source delivery does not claim a live installation.

## Prepare target guidance before adoption or upgrade

When conflicting target guidance needs preparation, invoke
[prepare-repository](../../machine/skills/prepare-repository/SKILL.md) from Agent
Team with the target path and intended Greenfield Initialization, Brownfield
Adoption, or Standards Upgrade workflow. The skill resolves one exact Agent Team
baseline, assesses target documents as review material, and makes authorized
preparation edits. Its final pass invokes the full OpenAI `openai-docs` skill for
the migration and instruction audit before combined review and verification.

The result is a committed local preparation branch and an evidence-based readiness
handoff. Continue from that prepared branch's changes when separately authorized
to perform adoption or upgrade; do not lose them by starting from an unchanged
baseline. Preparation itself does not deliver adoption, push, or merge the target.
The Machine Profile distributes the package through ordinary reconciliation;
source delivery alone does not install it. Verify package delivery separately from
real installation and target preparation.
