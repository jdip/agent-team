---
name: greenfield-init
description: Adopt the Repository Standard in a repository without established product behavior or development workflows.
---

# Greenfield Initialization

An explicitly approved `whats-next` alignment proposal can supply the target,
source baseline, and authorized scope. Reuse that consent; assessment alone does
not authorize this workflow's edits. Return its verified outcome or unresolved
decision to the coordinator after following this workflow's own gates.

Resolve the human's target repository and requested source revision. Inspect the
actual repository and local work first. If product behavior/workflows already exist,
use Brownfield Adoption within the same request rather than treating the repo as
empty. A valid existing Repository Standard declaration instead calls for an upgrade.

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

Read the selected Agent Team source's `standard/README.md` and relevant ordinary
templates. Source is https://github.com/jdip/agent-team. Unless the user specifies a
revision, resolve its default branch and select one concrete commit. An unavailable
or ambiguous source requires investigation; do not silently use stale content or
switch to another branch. Apply the selected standard's checkout and delivery
requirements to the actual repository and root guidance, including initial branch
setup when needed; preserve local work while preparing the adoption worktree.

Establish short root guidance/pointers, actual tracker conventions, lazy domain
guidance, and minimal canonical delivery shell entry points with the two fixed
local runbooks. Document the actual Application Code/Tooling mapping and commands.
Do not select or scaffold an application stack, empty coverage program, CI matrix,
or deployment environment without explicit user authorization. Apply the selected
standard's language/environment declaration to each actual component. Application
linting, type checking, validation, and meaningful high coverage grow with actual
application development; Tooling is verified through real use.

Use `define-project-goal` to establish the project purpose with the human operator.
Reuse a clear existing blurb; include approved purpose edits at the top of every
root README in this workflow's own change and delivery. The skill owns the
conversation and wording; return here afterward to complete adoption.

Use `repository-verification` for its suitability assessment during normal
inspection. Report its include/omit/defer recommendation with the other ready
decisions; run setup only within explicit opt-in, reusing existing consent. Return
here for this workflow's delivery; existing verification opt-in does not require a new guide.

Apply the selected standard's Claude guidance bridge contract to root and applicable
nested repository-owned guidance.

If inspection identifies application coverage gaps or tooling tests/coverage that
should be removed, record every identified gap in scoped, deduplicated tracker
issues. Link those issues without making their remediation an adoption prerequisite
or claiming unmet coverage is satisfied.

Add one Repository Standard section to root AGENTS.md with Source set to the exact
source repository URL and Revision set to the full selected commit SHA, as specified
by the standard. Include it in the same adoption PR. In an undelivered branch the
marker is the intended target, not completion evidence.

Make routine choices within the approved standard; complete independent work and
batch substantive unresolved decisions with recommendations. Deliver through the
shared `pr-to-test` skill and actual local completion criteria. No application means
report that reality, not invent a deployment. Record remediation links, verified
test delivery, and safe cleanup/retained artifacts. Main promotion is separately
requested and never required merely to complete adoption or begin the next task.
