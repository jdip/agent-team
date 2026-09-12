# Agent Team

Portable Codex configuration and repository working conventions for macOS desktop,
headless Linux, native Windows, and WSL 2 Ubuntu.

The [Machine Profile](machine/PROFILE.md) defines the configuration, agent roles,
and skills installed on a machine. The [Repository Standard](standard/README.md)
defines how an adopting repository organizes guidance, tracks work, verifies
changes, and delivers them. Updating this source does not automatically install
machine changes or upgrade other repositories.

## Start on a machine

1. Obtain official Codex and sign in on that machine: use the desktop app on
   macOS, the desktop app or standalone CLI on native Windows, or the standalone
   CLI on headless Linux or WSL. Start with the
   [official quickstart](https://developers.openai.com/codex/quickstart/).
2. Clone this repository with your own GitHub access, or open an existing checkout.
   See [development requirements](docs/development.md) for the local tools.
3. Ask Codex from this checkout: **“Reconcile this machine with the current Agent
   Team Machine Profile, following machine/RECONCILE.md.”**

[Machine Reconciliation](machine/RECONCILE.md) is explicitly user-requested. The
agent selects a concrete source revision, checks the actual host and managed
state, investigates conflicts, and verifies what it publishes. Credentials,
account history, and unrelated local configuration stay on the machine; see
[security boundaries](SECURITY.md). Keep operator-specific repository and host
inventories local and untracked, using the supported host project inventory where
available. The profile and reconciliation runbook own the exact installation
inventory and commands.

## Existing installations

The v0.4.0 baseline starts independent Git history. For an installation using an
older baseline, create a fresh checkout instead of merging the two histories.
Preserve old checkouts, unfinished changes, and every checkout still backing a
task. Register the fresh checkout through the host's supported project controls
before selecting it for new work.

An older Repository Standard revision cannot be resolved in this history. An
explicitly authorized migration must compare trusted, privately retained old-source
evidence with the chosen new revision and apply the relevant guidance changes;
changing the recorded SHA alone does not establish adoption. Ordinary Standards
Upgrade requires resolvable source revisions. Cleanup discovery safely skips
repositories whose recorded revision cannot be verified until their migration is
complete.

After the repository migration, request Machine Reconciliation from the fresh
checkout and verify fresh skill discovery. If a cleanup schedule reads an old source,
use the schedule owner in [machine/CLEANUP-SCHEDULE.md](machine/CLEANUP-SCHEDULE.md)
to select the verified new source, reuse its existing identity and cadence, and
record the observed update through its receipt.
Source publication, machine installation, and other repositories' upgrades remain
separate operations.

## Use it in a repository

Authorized repository adoption and upgrades establish supported dependency graph
and Dependabot alerts while disabling GitHub-generated security and version update
pull requests. `whats-next` discovers alerts and each repository remediates them
through its own planning and delivery conventions. Existing policy exceptions and
unavailable capabilities are reported explicitly; see the [dependency upkeep
standard](standard/README.md#dependency-upkeep).

Choose the workflow for the target and give Codex its path:

- [Greenfield Initialization](machine/skills/greenfield-init/SKILL.md) establishes
  the minimal conventions for a new repository.
- [Brownfield Adoption](machine/skills/brownfield-adoption/SKILL.md) brings an
  existing repository onto the standard while preserving its useful mechanisms.
- [Standards Upgrade](machine/skills/standards-upgrade/SKILL.md) updates an already
  adopted repository by the relevant source delta.

Each workflow assesses the target first, then resolves a target-owned Wayfinder
plan and specification against its goals before implementation. Reuse covering
plans and preparation evidence. For obsolete or conflicting guidance, invoke
[prepare-repository](machine/skills/prepare-repository/SKILL.md) from Agent Team.
It leaves a verified local preparation branch and a tracker handoff with concrete
Codex app continuation steps. Preparation and subsequent adoption are separately
authorized; preserve the prepared changes when continuing.

## Everyday workflow: start with whats-next

After machine setup and repository adoption, work from the repository you want to
advance. Ask: **“Use whats-next in this repository.”** Add an outcome or constraint
when you have one, such as “Prioritize finishing the current backlog.”

[whats-next](machine/skills/whats-next/SKILL.md) coordinates the existing skills.
You do not need to remember their invocation order:

1. **Get oriented.** The agent checks project purpose, selected planning map and
   implementation backlog, issues, PRs, local changes, other tasks' ownership, and
   current dependency alerts. It favors prerequisites and work close to completion,
   preserving active work.
2. **Choose the next useful step.** Already-approved work can continue after its
   gates are checked. When paths compete or approval is missing, the agent offers
   concrete options, rough effort, and a recommendation. Reply with your choice
   and the scope you authorize.
3. **Question the direction, then record it.** New-work discussions invoke
   Wayfinder and grilling before a map is created. Confirm shared understanding;
   approved continuations reuse settled answers. Every implementation needs a resolved
   map and approved specification unless you explicitly waive planning. Small work
   keeps those records brief and reuses existing coverage; settled maps need no
   invented decisions. Review the spec and executable ticket breakdown together.
   An implementation request carries through publication, selection and delivery;
   the agent asks only for missing decisions or approvals of concrete scope.
4. **Let the approved work run.** The implementation owner claims eligible work,
   makes the change, verifies it, obtains review, and completes the repository's
   PR-to-test workflow. Existing approval carries across skill handoffs; you do
   not need to repeat a command for every ticket or ordinary step.
5. **Answer decisions and reassess.** The agent returns with substantive questions
   or blockers, and reassesses after meaningful completion boundaries. You can
   steer or stop it at any time. Work owned by another task needs a verified
   handoff; finishing one backlog does not select another automatically.
6. **Consider maintenance when tracked work runs out.** The agent considers dependency
   upkeep, recent hygiene, opted-in verification and Repository Standard alignment evidence,
   proposes bounded assessments or changes, and compares observed outcomes with project purpose.
   An empty queue is not proof that every desired outcome has been achieved.

Saved maps and backlogs belong to explicit effort scopes. Separate tasks can work
independently even in one checkout. Resuming or moving an effort preserves its
binding; independent forks start separately. Ask to hand off a named map, backlog
or both to another task: the workflow obtains human approval, stops source work,
preserves included claims and verifies recipient ownership. Existing repository-wide
selections require explicit import. See [selection scope and handoff](machine/skills/set-map/SELECTIONS.md).

For example, after an assessment proposes two small fixes, **“Proceed with both
fixes through reviewed delivery to test”** authorizes carrying that concrete
batch through planning and delivery; it does not waive a map or spec. A request
to assess alone produces recommendations. If you return in a later session,
invoke whats-next again to rediscover current selections, ownership, and
remaining work. It does not create a background schedule.

[GitHub Issues](https://github.com/jdip/agent-team/issues) holds this repository's
work queue. The [implementation workflow](docs/workflows/implementation.md) explains
planning, Ready Backlog admission, active selection, and execution in detail.
**Main promotion, Machine Reconciliation, and background scheduling require
separate requests.** Updating Agent Team source does not install it on machines
or upgrade other repositories.

For changes to Agent Team, follow [AGENTS.md](AGENTS.md) and
[development guidance](docs/development.md). Work on feature branches in separate
worktrees, then use the canonical [PR-to-test workflow](docs/workflows/pr-to-test.md).
Verified test delivery completes ordinary implementation;
[promotion to main](docs/workflows/promote-to-main.md) is separately requested.

## Skill guide

Ask the agent to use a skill by name and supply the target and intended outcome,
for example **“Use dependency-review for this repository's TOML editor.”** Use
whats-next for coordination; invoke a specialist directly when you already know
the work you want. Direct calls follow the same [global planning
rule](machine/AGENTS.md#planning-before-implementation) for implementation,
including documentation and maintenance. Each linked skill owns its detailed
behavior and approval rules.

This guide covers every skill in the [Machine Profile](machine/PROFILE.md), which
remains the authoritative installation inventory. Links below point to Agent
Team's maintained packages or the profile's pinned upstream source. Host-bundled
and separately installed plugin skills are outside this inventory.

The optional Claude installation shares most skills. `prepare-repository`,
`greenfield-init`, `brownfield-adoption`, `standards-upgrade`, and
`setup-matt-pocock-skills` are distributed to Codex only. Actual tool availability
still governs what a skill can do. Preserve upstream manual-only invocation rules;
a coordinating workflow does not bypass them.

### Repository setup and alignment

| Skill | What it does | When and how to use it |
| --- | --- | --- |
| [prepare-repository](machine/skills/prepare-repository/SKILL.md) | Assesses, plans and retires obsolete target guidance before adoption or upgrade. | Invoke from Agent Team with the target path and intended workflow; continue from its local branch handoff. |
| [greenfield-init](machine/skills/greenfield-init/SKILL.md) | Establishes the standard in a new repository. | Supply the new repository, its agreed purpose, and any explicitly authorized language or environment choices. |
| [brownfield-adoption](machine/skills/brownfield-adoption/SKILL.md) | Adopts the standard around existing useful mechanisms. | Supply an established repository that has not adopted it. |
| [standards-upgrade](machine/skills/standards-upgrade/SKILL.md) | Applies relevant changes from the recorded standard source. | Supply an already-adopted repository when you want its guidance and workflows upgraded. |

### Planning and choosing work

| Skill | What it does | When and how to use it |
| --- | --- | --- |
| [whats-next](machine/skills/whats-next/SKILL.md) | Chooses and advances the next useful repository work. | Start here for ongoing progress; supply priorities and answer concrete decisions. |
| [define-project-goal](machine/skills/define-project-goal/SKILL.md) | Agrees project purpose and records it in root READMEs. | Use when direction is missing, unclear, or changing; discuss the intended outcome. |
| [wayfinder](machine/skills/wayfinder/SKILL.md) | Builds or resumes a proportionate map before implementation. | Discuss a desired change; reuse covering design or resolve a compact map and any real decisions. |
| [set-map](machine/skills/set-map/SKILL.md) | Saves the repository's selected planning map. | Supply the open map URL when explicitly choosing the effort to continue. |
| [next-waypoint](machine/skills/next-waypoint/SKILL.md) | Advances one eligible planning ticket. | Use with a selected map when you want one decision/research step handled. |
| [next-waypoint-loop](machine/skills/next-waypoint-loop/SKILL.md) | Continues planning across eligible tickets. | Use with a selected map to progress until human input or a blocker is needed. |
| [grilling](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grilling/SKILL.md) | Stress-tests a plan or idea through pointed questions. | Wayfinder invokes it for new-work discussions; you can also request it for a concrete decision and its assumptions. |
| [research](machine/skills/research/SKILL.md) | Investigates a question using primary sources. | Supply a question and constraints; explicitly request a saved artifact if needed. |
| [prototype](machine/skills/prototype/SKILL.md) | Builds a throwaway experiment to resolve a design question. | Supply the uncertainty to test and what observation would answer it. |
| [wait-what](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/wait-what/SKILL.md) | Clarifies a confusing explanation. | Invoke when you need the preceding explanation made easier to understand. |
| [to-spec](machine/skills/to-spec/SKILL.md) | Drafts an implementation specification and ticket breakdown. | Use after design is resolved; review the proposed parent and children together. |
| [to-tickets](machine/skills/to-tickets/SKILL.md) | Publishes an approved specification, tickets, and dependencies. | Supply the approved batch; publication alone does not start implementation. |

### Implementation and delivery

| Skill | What it does | When and how to use it |
| --- | --- | --- |
| [triage](machine/skills/triage/SKILL.md) | Refines incoming work and maintains ready backlogs. | Use to assess and group issues; approve admission or activation separately from execution. |
| [set-backlog](machine/skills/set-backlog/SKILL.md) | Selects an existing implementation parent. | Supply the prepared parent URL; selection alone does not authorize execution. |
| [next-issue](machine/skills/next-issue/SKILL.md) | Implements one eligible child through verified test delivery. | Use with an approved active backlog when you want one implementation issue completed. |
| [next-issue-loop](machine/skills/next-issue-loop/SKILL.md) | Continues eligible implementation within the selected backlog. | Authorize continuous execution; it stops for required decisions or blockers. |
| [tdd](machine/skills/tdd/SKILL.md) | Fixes bugs and builds behavior through failing tests, minimal implementation and scoped refactoring. | Use for application bug fixes, new or changed behavior, and explicit test-first work; follow real-use verification for Tooling. |
| [diagnosing-bugs](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/diagnosing-bugs/SKILL.md) | Investigates difficult bugs and performance regressions. | Supply observed behavior, reproduction steps, and the expected result. |
| [resolving-merge-conflicts](machine/skills/resolving-merge-conflicts/SKILL.md) | Resolves an in-progress merge or rebase and verifies the result. | Use when Git reports conflicts; identify the intended combined behavior. |
| [code-review](machine/skills/code-review/SKILL.md) | Reviews Standards and Spec correctness separately. | Supply a PR, branch, or fixed comparison point and its requirements. |
| [pr-to-test](machine/skills/pr-to-test/SKILL.md) | Delivers reviewed work through the repository's canonical test workflow. | Use for authorized delivery; it follows required checks through verified merge. |
| [promote-to-main](machine/skills/promote-to-main/SKILL.md) | Promotes verified test work through the main workflow. | Explicitly request promotion after reviewing the delivered result. |
| [cleanup-task-artifacts](machine/skills/cleanup-task-artifacts/SKILL.md) | Removes only task artifacts proven associated and safe. | Use after delivery or for an authorized cleanup sweep; active or uncertain resources are retained. |

### Maintenance and supporting skills

| Skill | What it does | When and how to use it |
| --- | --- | --- |
| [codebase-hygiene](machine/skills/codebase-hygiene/SKILL.md) | Surveys maintenance opportunities and coordinates approved cleanup. | Request an assessment, then approve a concrete cleanup batch if worthwhile. |
| [reflect](machine/skills/reflect/SKILL.md) | Captures reusable lessons as actionable issues. | Runs when a brief reflection check finds an improvement, or when you ask to reflect; uses current-task evidence. |
| [audit-agent-instructions](machine/skills/audit-agent-instructions/SKILL.md) | Audits instruction quality and interactions with accountable coverage. | Request a full or targeted skill/rule audit; receive evidence-backed findings and proposed changes. Repairs follow the target's authorized workflow. |
| [repository-verification](machine/skills/repository-verification/SKILL.md) | Assesses suitability and creates or audits optional repository verification instructions. | Adoption/upgrade recommends include, omit or defer. Explicitly opt in for setup; `whats-next` considers useful audits for adopters using existing UI or non-UI controls. |
| [dependency-review](machine/skills/dependency-review/SKILL.md) | Assesses whether a dependency earns its maintenance cost. | Name a dependency or scoped inventory; keeping it is a valid result. |
| [dependabot-upkeep](machine/skills/dependabot-upkeep/SKILL.md) | Configures dependency-alert protection and routes alerts through the repository's delivery workflow. | Supply a setup or alert scope; `whats-next` discovers current alerts alongside other work. |
| [code-simplification](machine/skills/code-simplification/SKILL.md) | Simplifies a bounded area while preserving its contract. | Supply an approved cleanup target and the behavior that must remain intact. |
| [codebase-design](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/codebase-design/SKILL.md) | Supplies vocabulary and principles for deep modules. | Use when discussing interfaces, responsibility placement, or testability. |
| [domain-modeling](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/domain-modeling/SKILL.md) | Sharpens domain terminology and records modeling decisions. | Use while resolving domain concepts, CONTEXT.md content, or an ADR. |
| [improve-codebase-architecture](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/improve-codebase-architecture/SKILL.md) | Shows module-deepening opportunities in a visual report, then questions the selected design. | Explicitly invoke for a scoped architecture investigation and choose a candidate to explore. |
| [writing-for-agents](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/writing-for-agents/SKILL.md) | Guides clear agent-facing documents and context pointers. | Use when writing skills, instructions, or documents that agents consume. |
| [wizard](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/wizard/SKILL.md) | Creates an interactive Bash guide for human-only steps. | Use for setup or cutover actions requiring human interaction; supply the goal and confirm proposed stages. |
| [setup-matt-pocock-skills](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/setup-matt-pocock-skills/SKILL.md) | Configures repository tracker, triage labels, and domain-document conventions for upstream engineering skills. | Explicitly invoke for that upstream repository setup; Agent Team repositories normally use the adoption workflows above. |

## License

Original Agent Team material is available under the [MIT License](LICENSE).
Adapted skills retain their upstream copyright and MIT notices in each package's
`LICENSE`; their attribution sections identify the reviewed upstream sources.
Externally acquired skills retain their own licenses.

Before contributing code, issues, pull requests or evidence, follow the
[public-work policy](SECURITY.md#public-repository-work).
