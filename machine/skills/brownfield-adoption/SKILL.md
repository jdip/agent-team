---
name: brownfield-adoption
description: Adopt the Repository Standard in an existing repository while preserving product behavior and useful compatible workflows.
---

# Brownfield Adoption

An explicitly approved `whats-next` alignment proposal can supply the target,
source baseline, and authorized scope. Reuse that consent; assessment alone does
not authorize this workflow's edits. Return its verified outcome or unresolved
decision to the coordinator after following this workflow's own gates.

Establish the selected standard's visibility and public-work outcome before any
GitHub writes in this workflow, including tracker updates. Verify current visibility,
preserve licensing and owner decisions, and connect the target's applicable policy
to root guidance, tracker, review and delivery owners. Resolve required decisions
before dependent publication; continue independent local work. Report actual policy
use and unexercised paths with the delivery evidence.

Resolve the human's target repository and source request. Inspect existing product
behavior, workflows, root instructions, domain docs, dirty state, and any Repository
Standard declaration. If a valid declaration already exists, use Standards Upgrade.
Preserve unrelated work and attached checkouts.

Before selecting adoption work, read any supplied preparation handoff issue. When
none is supplied, search the target repository's tracker for preparation handoffs
and adoption prerequisites, including closed issues and their comments. Inspect
likely matches against the repository identity, intended workflow, and prepared
branch or commit, using Git ancestry when continuation has moved to another branch.
Use the matching handoff's findings, preserved decisions, and remaining prerequisites
as context within the current authorization. Resolve competing matches from that
evidence; ask only if a material ambiguity remains. If no handoff exists, continue
normal inspection. Report inaccessible tracker evidence without treating it as an
absent handoff; pause only work whose scope or safety depends on resolving it.

Read `standard/README.md` at one concrete source revision from
https://github.com/jdip/agent-team. Use a user-specified revision when supplied;
otherwise resolve the source default branch. Investigate unavailable or ambiguous
source rather than silently switching branches or using stale content.

Use the selected standard's checkout requirements to prepare the adoption feature
worktree. Establish its checkout and delivery outcomes in the actual repository
and root guidance, including missing prerequisites within adoption scope. Preserve
active work and report unresolved checkout conflicts rather than bypassing the standard.

Assess the required surface against what actually exists. Preserve useful compatible
implementations and customizations. For an intentional replacement, migrate callers
and guidance and remove obsolete implementation/configuration within that scope.
Do not keep abandoned mechanisms behind shims or duplicate paths. Thin canonical
shell entry points around a deliberately retained implementation are valid.

Establish actual root guidance, tracker instructions, lazy domain guidance, local
Application Code/Tooling mapping, development commands, fixed delivery scripts, and
local runbooks. Use rigorous application lint/type/validation and meaningful high
coverage. Tooling requires successful real use, without fake infrastructure or
recursive tooling tests. Document each identified application coverage deficiency
and tooling coverage/tests to remove in scoped tracker issues after duplicate checks.
Do not hide deficiencies, weaken real gates, or require those remediation fixes to
finish adoption.

Use `define-project-goal` to establish the project purpose with the human operator.
Reuse a clear existing blurb; include approved purpose edits at the top of every
root README in this workflow's own change and delivery. The skill owns the
conversation and wording; return here afterward to complete adoption.

Use `dependabot-upkeep` to establish the selected standard's dependency-protection
outcome on the actual target. Pass the alignment setup authority, repository,
dependency surfaces and delivery rules; preserve compatible automation and explicit
exceptions. Verify enabled settings and active coverage, or report the exact
unresolved capability. Return here for alignment delivery.

Use `repository-verification` for its suitability assessment during normal
inspection. Report its include/omit/defer recommendation with the other ready
decisions; run setup only within explicit opt-in, reusing existing consent. Return
here for this workflow's delivery; existing verification opt-in does not require a new guide.

Apply the selected standard's Claude guidance bridge contract to root and applicable
nested repository-owned guidance.

Investigate substantive behavior changes and tradeoffs. Finish independent work
and batch all ready human decisions with concrete recommendations; do not ask the
human to restate already-settled standards or routine implementation details.

Add the one standardized Repository Standard Source/Revision section to root
AGENTS.md with the exact source URL and full selected SHA. Ship the declaration in
the same adoption PR, not a bookkeeping PR. It is an intended target until delivery.

Use shared `pr-to-test` for reviewed, verified delivery, including actual test
deployment when applicable and the shared cleanup procedure without orphaning task
checkouts. Record delivered evidence, remediation issues, and retained resources.
Main promotion remains separately requested; successful test delivery permits the
next task without resolving non-blocking remediation first.
