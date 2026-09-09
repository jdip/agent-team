# Maintenance and alignment

Use this branch when dependency upkeep, hygiene, adopted repository verification
or Agent Team alignment is a plausible next action.
Consider missing assessment history, relevant changes since earlier evidence, and
visible friction. Inspect enough to make a useful proposal with rough effort;
compare it with other candidates instead of performing a full audit to rank them.
Age, missing history, and a newer standard revision are signals, not proof of a
defect. Reuse existing findings and keep/defer decisions unless evidence changes.

## Establish a stable baseline

Get active code tasks, implementation PRs, and unfinished local code changes through
verified delivery to `test` before hygiene, verification audits or intrusive
alignment assessment/changes.
Preserve others' active work; do not take over just to clear this gate. Old parked
branches do not automatically block an assessment. A quick declaration/status read
can still identify alignment as a future candidate while code is moving.

A greenfield or unadopted repository may lack `test` and delivery tooling. Establish
its actual stable starting state and use the adoption owner's baseline/bootstrap
rules; do not require adoption's own outputs before it can start. Unfinished or
uncertain local work still needs preservation and resolution. This exception does
not make an in-flux codebase ready for hygiene.

## Dependency upkeep

Include missing/stale Dependabot setup, actionable dependency alerts, and pending
update PRs in the ordinary candidate comparison. Inspect enough existing evidence
to distinguish a setup gap, a failing update and an almost-delivered PR. Preserve claims, native
dependencies, completion-first ranking and the user's keep/defer decisions.

Apply the stable-baseline gate above before changing dependency automation or
starting broad upkeep. An existing update PR is implementation work: assess its
ownership and actual conflicts alongside other PRs rather than waiting for itself
to finish before it becomes eligible. An urgent alert can justify proposing a
priority change; it does not authorize taking over another task's work.

Use `dependabot-upkeep` for the selected setup or update scope. Pass the repository,
configuration/PR/alert evidence, delivery target and existing authorization. A
discovery request can produce a recommendation; setup and update execution need
approval covering the concrete work. That owner handles current GitHub behavior,
breaking-update decisions, failed checks and review/delivery handoffs. Keep
dependency justification with `dependency-review`, reached when relevant.

After a verified upkeep step, return to ordinary selection with the observed
remaining work. Reuse unchanged assessments and defer decisions; revisit them when
dependency surfaces, automation, alerts, update PRs or relevant failures change.

## Hygiene

Use `codebase-hygiene` for the selected authorized assessment. It owns dependency
justification through `dependency-review`, including used packages, and structural
investigation. Valid keep/no-change outcomes are useful.

For proposed edits, present a concrete cleanup batch: changes, expected benefit,
rough effort, and material risks. Reuse consent already covering that batch;
otherwise obtain it before edits. The owner chains `code-simplification`, required
review, and verified test delivery. Return to the coordinator after the batch.

## Adopted repository verification

Check the root opt-in declaration and maintained guide before considering an audit.
For adopters, use prior issue/PR/task evidence, relevant behavior/control churn and
observed friction to propose a bounded audit alongside hygiene and alignment.
Missing history is a candidate signal; age alone does not require a run. Reuse a
recent unchanged assessment, and avoid a full audit just to rank candidates.
Repositories without opt-in have no audit obligation; suitability belongs to the
adoption/upgrade assessment below.

For the selected authorized audit, use `repository-verification` with the scope,
stable baseline and existing evidence. It owns actual execution, drift correction,
regression filing and delivery. Reuse existing edit authority; an assessment alone
does not approve unrelated changes. Return here after the result and record it in
the existing task/issue/PR, without a new ledger. Reconsider at later meaningful
completion boundaries when evidence changes; do not create a background schedule.

## Agent Team alignment

Inspect the repository's actual guidance/workflow state and Repository Standard
Source/Revision declaration. Distinguish absent from malformed, conflicting, or
inaccessible evidence; investigate uncertainty rather than guessing adoption status.
Route by actual state:

- No declaration and no established product behavior/workflows: `greenfield-init`.
- No declaration with established product behavior/workflows: `brownfield-adoption`.
- Valid declaration: `standards-upgrade` for relevant alignment changes.

Read the selected owner and resolve one exact source baseline under its rules.
Honor an explicit revision; ordinary upgrades use the recorded source's default
branch, not the current Agent Team working branch. Compare relevant changes and
actual repository outcomes; a declaration in an undelivered branch is only an
intended target. A current, aligned repository needs no change.

Before invoking a workflow that edits, establish authorization for the concrete
proposed alignment work: target, selected baseline, changes, benefit, rough effort,
and material risks. An assessment request alone is insufficient. Carry existing
approval through the appropriate owner, including `define-project-goal` for concise
root README purpose. Preserve local constraints and separately required environment
choices. The adoption/upgrade owner performs review and verified delivery, after
which the coordinator refreshes.

If conflicting guidance requires `prepare-repository`, resolve its explicit target
and preparation scope first. That owner edits guidance and ends at a local branch
handoff; it is not a read-only scan or adoption itself. Complete independent work
before presenting needed preparation and subsequent adoption/upgrade approvals,
which may be granted together for a concrete proposal. Reuse an existing matching
preparation handoff. If the current host/session cannot satisfy that owner's
boundary, preserve the affected work and report the actionable handoff rather than
silently taking another role or creating a task. Return here after authorized
preparation and continue only the approved downstream work.
