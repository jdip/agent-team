# Repository Standard

This directory is the ordinary versioned source for Repository Adoption and
Standards Upgrade. Its Git revision identifies the standard; the application's
semantic version is separate. Apply outcomes to the actual repository rather than
copying an entire scaffolding tree.

## Required outcomes

- A concise project-purpose blurb at the top of every root README, directly below
  the project title. Use `define-project-goal` to agree missing or changed wording
  with the human operator; reuse a clear existing purpose and keep variants
  consistent in meaning. Include approved edits in the adoption or upgrade change.

- Short root AGENTS.md with repository-specific scope, pointers, and the explicit
  checkout and delivery rules below; runbook links alone are insufficient.
- Concrete issue-tracker instructions and commands; GitHub uses the native issue,
  sub-issue, dependency, claim, and remediation deduplication conventions in
  docs/agents/issue-tracker.md. Include search, matching-issue reuse, evidence,
  readback, and blocker links so global filing guidance has a concrete local path.
- Lazy domain-documentation guidance like docs/agents/domain.md. Read existing
  CONTEXT.md or CONTEXT-MAP.md and relevant ADRs. Create or change domain docs when
  real terms or decisions emerge, never as empty scaffolding.
- Actual development and verification instructions, with a local classification
  of Application Code and Tooling by purpose.
- Guidance retirement under the outcome below, including inherited process that
  adds unjustified complexity without directly contradicting another rule.
- A target-specific plan under Target assessment and planning below, resolved
  before implementing preparation, adoption or upgrade changes.
- A root language/environment declaration for each existing component, following
  the policy below; component classification alone does not select its stack.
- Dependency protection and native update coverage under the
  [dependency upkeep](#dependency-upkeep) outcome below.
- Discoverable current repository visibility, with licensing and publication
  safeguards under [visibility and public work](#visibility-and-public-work).
- Executable scripts/pr-to-test.sh and scripts/promote-to-main.sh, paired with
  docs/workflows/pr-to-test.md and docs/workflows/promote-to-main.md.
- One source/revision declaration in root AGENTS.md, delivered in the adoption or
  upgrade PR, using the exact fields below.

```markdown
## Repository Standard

- Source: https://github.com/jdip/agent-team
- Revision: <full adopted commit SHA>
```

Replace the placeholder with a real commit from this source. The declaration in a
working branch is the intended target, not proof of delivery. Source authorship
alone is not adoption; Agent Team also records its declaration in root AGENTS.md.
Unmarked repos
need Repository Adoption; ordinary upgrades use the recorded source's default
branch unless the user requests a revision. Select one concrete revision and apply
its relevant delta, preserving unrelated work.

## Target assessment and planning

Preparation, Greenfield Initialization, Brownfield Adoption and Standards Upgrade
begin with a proportionate read-only assessment of the actual target. Establish
its identity and starting state, purpose, chosen workflow and exact source baseline;
inspect relevant code, guidance, current mechanisms, constraints, capabilities and
existing preparation/map/spec evidence against that workflow's required outcomes.
An empty-looking repository or a source revision delta does not replace assessment.

Conduct or resume Wayfinder with that evidence to resolve how this target should
reach the workflow's goals. The target owns the map and specification, including
when preparation is driven from Agent Team. Reuse covering plans and settled
decisions; one plan may cover preparation and subsequent adoption/upgrade while
preserving each phase's authorization and completion boundary. If the target
tracker is unavailable, continue conversational planning and resolve the artifact
location before implementation. Follow publication policy for planning writes.

Before implementation, resolve the map and approve the specification and executable
breakdown through the existing planning owners, unless the operator explicitly
waives planning. A workflow invocation carries its normal authorized outcome; it
does not waive planning. Keep small plans brief. Plan actual changes, prerequisites,
deferred work and evidence for the target's completion boundary, rather than create
a universal bootstrap program. Research and planning records may precede approval;
target guidance/configuration changes and adoption setup follow the approved plan.
Use the existing backlog selection and `next-issue` owners for child claims and
resolution in the target tracker. Resolve their pointer and execution context from
the target checkout, even when this session starts elsewhere. A direct workflow
invocation hands its target, approved child and authority to that executor before
edits; within an already claimed child, execute the named skill without recursive
handoff. The skill supplies implementation and its completion boundary, then returns
evidence for child resolution. Preparation completes its documentation child at the
verified local handoff; separately scoped adoption/delivery children remain open.

At execution and handoff, verify that the target state, baseline and scope still
match the plan. Refresh affected evidence; substantive changes return to Wayfinder,
while routine covered choices remain with the implementer. Include map/spec links
and the assessed target/baseline in the existing handoff or delivery evidence.
Missing capabilities or unresolved decisions remain explicit rather than becoming
silent implementation.

## Guidance retirement

Preparation, adoption and upgrades assess repository-owned guidance by purpose and
effect. Inspect the repository broadly, including unlinked documents, embedded
instructions, hidden agent/editor rules, skills and templates; follow references
and copied rules into their current owners. Names and keywords are discovery clues,
not a scope checklist. Report exclusions and inaccessible surfaces; preserve
separately owned content and Unmanaged Local State.

Treat inherited development manifestos, bootstrap programs, process decision
compilations, milestone machinery and enforcement roadmaps as highly suspect.
Judge what they make agents do against the selected standard's minimalist intent:
each retained obligation must serve a concrete current need with proportionate
complexity. Compatibility, prior adoption, historical labels, incoming links and
existing enforcement alone do not justify retention. Challenge unnecessary ceremony,
speculative infrastructure, duplicated principles and accumulated exceptions even
when no pair of sentences directly conflicts. Apply the same test to the Agent Team
baseline itself. If a source requirement fails it, record the concrete mismatch
with the source owner and resolve the intended change through Wayfinder rather than
silently importing the requirement or creating a local policy fork.

Favor complete removal of obsolete process artifacts, including records and
tombstones. Extract only indispensable current facts or still-valid decisions into
their existing owners; remove dubious process from otherwise useful documents.
Git history normally supplies the archive. A disclaimer, renamed file or relocated
rule does not retire an obligation. Preserve current product requirements,
necessary safety controls and justified repository constraints; resolve substantive
unsettled decisions with the operator rather than infer them from old plans.

Remove obsolete requirements from guidance during authorized alignment, retaining
successful real-use verification. Trace affected callers and enforcement; file
deduplicated issues for later removal of permanent Tooling tests, validation suites,
fake environments and their supporting machinery. Those follow-ups do not block
guidance alignment. Describe surviving enforcement as pending retirement, not as
endorsed development policy. Prose edits do not bypass executable controls.
Classify by purpose: application tests remain application tests when invoked by
tooling. Preserve necessary application/security checks and the canonical delivery
route. Preparation retains its documentation-only local-branch handoff boundary.

Reassess the final guidance across the discovered scope for surviving obsolete
obligations and inbound references, including content migrated into another owner.
Report removals, justified retention and unresolved mismatches in the existing
handoff or delivery evidence, without a new inventory framework. Complete independent
authorized guidance cleanup before batching decisions. Distinguish unresolved
guidance or actual delivery blockers from deferred machinery removal; filing a
follow-up does not justify retaining the obsolete rule. Preparation readiness
covers its documentation outcome and identifies remaining adoption/upgrade work.

## Visibility and public work

Greenfield Initialization, Brownfield Adoption and Standards Upgrade establish
the target's current visibility in root guidance or a directly linked policy.
Verify the exact remote and actual GitHub visibility when available. Record current
public/private state separately from any intended future publication. An absent
remote, inaccessible hosting state, or conflicting declaration leaves visibility
unresolved: obtain the owner's intended state and resolve actual state before
dependent publication. Adoption and upgrade authority never changes visibility.

For public targets, inspect existing licensing and provenance, preserve required
third-party notices, and establish an appropriate owner-approved license. Reuse
settled licensing decisions. Missing or conflicting licensing requires an owner
decision before publication; adoption does not grant relicensing authority.

Establish a repository-owned public-work policy for public targets, linked from
root agent guidance. Preserve an adequate existing policy and deliberate local
choices. Private targets still exclude credentials and can apply an explicitly
approved public-work policy during preparation for future publication.

The policy requires review before the first applicable GitHub write, including
issue/PR creation, comments, pushes and uploads. Cover source and relevant history,
credentials, private identifiers and contact details, attribution, commit identity,
branch/tag names, CI output, logs, screenshots, attachments and linked evidence.
Establish approved commit identity and verify platform-created merge metadata.
Preserve explicit public attribution and legitimate upstream authorship. Sanitize
outgoing evidence; retain necessary unsanitized originals only in an established
private destination. If none exists, resolve that destination before retaining or
sharing such material. Automated checks supplement review, not complete privacy
clearance; editing after publication does not retract earlier exposure.

Wire the policy into the target's tracker instructions, review requirements and
both delivery runbooks, so the adoption or upgrade itself follows it before any
applicable publication. Reuse existing mechanisms instead of a separate publishing
system. Complete independent local work while visibility or licensing decisions
are pending; keep dependent writes paused. Verify actual declaration, license and
policy handling through authorized real use, reporting unexercised paths and
unresolved decisions without claiming publication approval.

## Dependency upkeep

Authorized Greenfield Initialization, Brownfield Adoption and Standards Upgrade
include establishing supported dependency protection through `dependabot-upkeep`.
For GitHub targets, enable the dependency graph, Dependabot alerts and Dependabot
security updates where available, and configure version updates for the actual
supported dependency surfaces. This is part of alignment, not a separate optional
assessment. Preserve working configuration, compatible existing update automation
and deliberate owner-approved exceptions; resolve conflicting policy with the
owner instead of silently disabling or replacing it.

Use manifests consumed by the real build or install path. A dependency hidden in
an installation command is a coverage gap to assess, not automatically exempt;
prefer exposing the existing pin through that installer's native manifest without
duplicating its owner. Report unsupported sources such as manually reviewed external
Git revisions through their existing update owner.

Verify actual hosted settings and distinguish delivered configuration from active
service. Record coverage, justified exceptions and exact blocked capabilities in
the existing alignment evidence. Missing permissions or unavailable hosting features
leave protection explicitly incomplete; continue independent alignment work.
Configuration awaiting separately authorized default-branch delivery can finish
verified test delivery with activation reported as pending. Do not claim active
coverage or require promotion merely to complete source delivery.
Additional credentials, paid features, visibility changes and separately required
main promotion retain their own approval boundaries. Do not widen permissions,
change hosting or invent a new updater to claim completion. Alignment does not
authorize merging future dependency PRs.

## Optional repository verification

Greenfield Initialization, Brownfield Adoption and Standards Upgrade assess whether
reusable real-behavior verification would benefit the repository and recommend
include, omit or defer, using `repository-verification`'s suitability assessment.
The assessment is required; inclusion is explicit opt-in, not a baseline requirement.
Preserve sufficient existing controls and guides. Deferral names a revisit condition;
UI, a new runtime, a helper framework and a separate guide are not prerequisites.

For an opted-in repository, root guidance declares adoption and links its maintained
instructions. Keep them current alongside relevant behavior changes, with proven
controls, observable outcomes and evidence/cleanup rules. `repository-verification`
owns setup and audits. `whats-next` considers useful audits alongside hygiene on a
stable baseline, using prior evidence, churn and friction rather than repeating
unchanged audits. No background scheduling is implied.

## Claude guidance bridges

Adoption and upgrades create a relative `CLAUDE.md -> AGENTS.md` symlink beside the
root guidance and each applicable nested `AGENTS.md`, whether or not Claude is
installed on the current machine. An applicable nested file is repository-owned
guidance for a scoped component; do not traverse symlinked directories or create
bridges in vendor, generated, submodule, independent-repository, or other worktree paths.

Confirm the sibling `AGENTS.md` is a regular file. Investigate reversed links or
cycles and preserve the guidance before changing link direction. Inspect each
existing `CLAUDE.md` before changing it. Retain a correct relative link. A file, a
different link, or any other conflicting content requires investigation before
replacement. Verify every created or retained bridge with
`readlink` and Git's staged `120000` symlink mode, confirming that its target is the
sibling `AGENTS.md`. The bridge makes repository guidance discoverable; it does not
install Claude or prove session loading.

## Languages and environments

Record each actual component's approved implementation language, runtime,
build/package toolchain, and execution/deployment environment in root guidance
or a directly linked authoritative section. Cover CLI, app, server, and Tooling
only where they exist; do not invent
stacks for absent components. Derive existing choices from source, callers, and
build configuration, preserving their scope rather than treating any language
found anywhere in the repo as approved for every component.

Require explicit user authorization before adding a language, runtime, build/
package toolchain, or execution/deployment environment, including helper scripts
and adoption tooling. Prefer reuse of one existing language across components
where practical. A feature or adoption
request does not implicitly approve a new environment. Greenfield choices without
an approved stack require a concrete recommendation and explicit authorization;
brownfield adoption and upgrades preserve established choices. This policy does
not authorize migrations or language consolidation of existing code.

## Validation and adoption

Application Code implements product behavior, including a CLI that is itself the
product. Require rigorous linting, type checking, validation, and meaningful tests
with high coverage across all application behavior. Each repository selects and
enforces appropriate stack-specific gates and coverage targets. Do not use a local
target as permission for weak coverage or inflate numbers with meaningless tests.

Tooling supports development, validation, delivery, and machine/repository maintenance.
Validate it by successful real use. No tooling coverage targets, fake environments,
conformance suites, tests of tests, or resumable workflow engines. Running application
checks through a shell wrapper does not turn those checks into prohibited Tooling tests.

Greenfield Initialization establishes only the needed organization, guidance, tracker
conventions, and minimal shell entry points. Application tooling grows with actual
application development. Preserve mechanisms justified by current needs and retire
obsolete guidance and enforcement under the guidance-retirement outcome above.
Track application coverage gaps as scoped, deduplicated issues; those gaps remain
visible without blocking adoption. Actual delivery prerequisites still apply.

## Checkouts and delivery

Keep the primary local checkout on `test`, refreshed from `origin/test` by
fast-forward only when clean. Reserve `test` for that checkout; never check the
branch out in a linked worktree. Make all changes, including adoption, upgrades,
documentation, and small fixes, on `codex/` feature branches in separate worktrees
based on fresh `origin/test`. Preserve unrelated local work and attached checkouts.
Detached revision worktrees are valid for canonical verification.

Root guidance must require the global `pr-to-test` skill with the local
`docs/workflows/pr-to-test.md` and `scripts/pr-to-test.sh` through checks, merge,
and verified test delivery. Direct commits or pushes to `test` and protection
bypasses are not delivery alternatives. Separately requested promotion uses the
global `promote-to-main` skill, `docs/workflows/promote-to-main.md`, and
`scripts/promote-to-main.sh` from the clean primary `test` checkout, completing
verification and main-to-test synchronization.

Adoption and upgrades establish these outcomes in both the actual checkout layout
and root guidance. If required branches are absent, establish them from the target
repository's intended baseline; resolve ambiguous history before changing refs.
An empty repository needs an initial baseline before feature worktrees and PRs can
be used. This setup does not authorize product changes directly on `test`.
Missing canonical scripts are part of adoption/upgrade scope: implement the real
local entry points and runbooks before claiming completion. During ordinary work,
root guidance must instead direct agents to check for duplicates, file an
implementation issue for a missing script, and report the delivery blocker rather
than invent an alternate flow. Preserve active/attached worktrees; unresolved
checkout conflicts or missing delivery prerequisites mean adoption is incomplete.

## Delivery and versions

Shared human-invoked skills read the fixed local runbooks and call the repository's
fixed scripts. Ordinary toolchain and operational differences belong locally; do
not fork shared skills, duplicate machine model/role configuration, or add a plugin
framework. Thin wrappers are sufficient; implement the actual happy path and return
unexpected conditions to the supervising agent with partial effects visible.

Use merge commits for task-to-test, test-to-main, and main-to-test synchronization.
Review every submitted change; reuse prior evidence only when it covers all changes
and findings are resolved or explicitly accepted. No review ledger is required.
Completion means the local runbook's verified result, including real deployment or
processing when applicable. Verified test delivery permits the next issue; promotion
is separately requested. Do not make promotion a per-task gate.

Use semver:major, semver:minor, semver:patch, and semver:none labels. Count each
applicable merged task PR once in deterministic merge order, with normal resets:
1.4.2 + patch + minor + patch = 1.5.1. Synchronization contributes none; promotion
wrappers do not recount component changes. All-none promotion keeps the existing
version without a new tag. Use existing tags and Git/GitHub evidence, never a ledger.

Bookkeeping is advisory: resolve routine missing/conflicting labels from the actual
change, otherwise report uncertainty without guessing a version or moving tags.
Version metadata cannot waive real application/delivery gates or invent an artificial
blocker. A real artifact pipeline's version prerequisite and initial version are
local runbook decisions.

Clean only artifacts proven associated with the task and safe to remove. Preserve
shared, active, uncertain, uncommitted, or unpublished state and needed evidence.
Never delete a Codex-attached checkout; use supported lifecycle handling or retain
it. Daily cleanup adds no authority beyond the same safety checks. Automatic archival
also requires proven completion, unpinned/inactive state, and more than seven days
since an observed last turn. Missing evidence means skip.
