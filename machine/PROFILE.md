# Machine Profile

This is the canonical inventory of managed Codex and Claude configuration, local
packages, reviewed upstream packages, and reconciliation boundaries. It declares
Managed State, not authority to change a machine merely by reading it.

## Source and targets

On a user-requested Machine Reconciliation, fetch the freshest current-branch
source while preserving local work, select one concrete Git revision, and read all
assets from it throughout the run. Report the revision. Investigate detached,
unpublished, ambiguous, divergent, or unavailable source; do not silently switch
branches or fall back to stale content. There is no separate manifest, lockfile,
generator, or profile version.

The Codex inventory applies to macOS desktop and headless Linux. Windows and
desktop Linux are out of scope. Resolve CODEX_HOME and supported skill destinations
on the actual host. The copied user-skill destination reviewed during planning is
`$HOME/.agents/skills`; verify it on the target. Supported installer storage may use
a different root. Do not normalize roots with symlinks or own their containing
directories. A headless host still receives browser_verifier; ability to execute a
browser task depends on actual host capabilities.

## Shared configuration and whole files

Merge only these nine dotted paths from [config.toml](config.toml) into
`$CODEX_HOME/config.toml`; never replace that file wholesale:

- model
- model_reasoning_effort
- default_permissions
- approval_policy
- agents.enabled
- agents.max_concurrent_threads_per_session
- agents.default_subagent_model
- agents.default_subagent_reasoning_effort
- agents.interrupt_message

All other fields remain unmanaged, including root service_tier, credentials,
providers, MCP servers and environment, trust, history, projects, and UI settings.
The deliberately approved permission defaults do not broaden task authorization;
trusted repository configuration can tighten them.

| Source relative to machine/ | Destination | Scope |
| --- | --- | --- |
| AGENTS.md | $CODEX_HOME/AGENTS.md | Whole file |
| agents/browser_verifier.toml | $CODEX_HOME/agents/browser_verifier.toml | Whole file |
| agents/critical_reviewer.toml | $CODEX_HOME/agents/critical_reviewer.toml | Whole file |
| agents/deep_specialist.toml | $CODEX_HOME/agents/deep_specialist.toml | Whole file |
| agents/explorer.toml | $CODEX_HOME/agents/explorer.toml | Whole file |
| agents/planner.toml | $CODEX_HOME/agents/planner.toml | Whole file |
| agents/security_specialist.toml | $CODEX_HOME/agents/security_specialist.toml | Whole file |
| agents/sysadmin_operator.toml | $CODEX_HOME/agents/sysadmin_operator.toml | Whole file |
| agents/test_verifier.toml | $CODEX_HOME/agents/test_verifier.toml | Whole file |
| agents/worker.toml | $CODEX_HOME/agents/worker.toml | Whole file |
| agents/workflow_monitor.toml | $CODEX_HOME/agents/workflow_monitor.toml | Whole file |

Each role's name, instructions, model, effort, tier, and sandbox move together.
The current Astra/Daybreak assignments and naming are in [AGENTS.md](AGENTS.md)
and those ordinary role files. The code-review package owns the optional Claude CLI
review preference and native critical_reviewer fallback. Claude installation and
account authentication remain outside this profile; their absence does not block
Machine Reconciliation. Verify model/effort support during reconciliation;
never silently substitute. Preserve AGENTS.override.md and surface its interference
as a supervised conflict. No default role shadow or renderer is included.

## Copied local packages

Each listed `machine/skills/<name>/` is one whole directory copied to the supported
user-skill root under the same name, including its companion metadata and helpers.
Only the listed package identities are approved; neighbors are not managed.

| Package | Source responsibility |
| --- | --- |
| wayfinder | Adapted decision mapping and implementation handoff |
| code-review | Adapted Standards/Spec review with bounded reviewer ownership |
| whats-next | Original current-repository progress coordination |
| define-project-goal | Original human–AI project purpose and root README workflow |
| codebase-hygiene | Original maintenance survey and authorized cleanup coordination |
| dependency-review | Original dependency justification and replacement assessment |
| code-simplification | Original behavior-preserving simplification workflow |
| research | Adapted primary-source research and assigned artifact ownership |
| reflect | Original focused lesson capture and actionable issue follow-through |
| repository-verification | Original suitability assessment, opt-in setup and audit workflow |
| prototype | Adapted planning prototypes and authorized implementation handoff |
| tdd | Adapted behavioral testing at established public boundaries |
| resolving-merge-conflicts | Adapted conflict resolution preserving unrelated work |
| to-spec | Adapted Implementation Specification authoring |
| to-tickets | Adapted executable ticket authoring and publication |
| triage | Adapted intake, Ready Backlog admission, and authorized activation |
| set-map | Original saved Wayfinder map helper |
| next-waypoint | Original single-ticket Wayfinder entry point |
| next-waypoint-loop | Continuous Wayfinder workflow with implementation handoff |
| set-backlog | Explicit existing-parent Active Backlog selection |
| next-issue | Claim-to-delivery workflow with whole-map Design gate |
| next-issue-loop | Continuous execution within one explicitly active parent |
| pr-to-test | Canonical shared delivery package |
| promote-to-main | Canonical shared delivery package |
| prepare-repository | External guidance preparation and committed local branch handoff |
| greenfield-init | Canonical shared adoption package |
| brownfield-adoption | Canonical shared adoption package |
| standards-upgrade | Canonical shared upgrade package |
| cleanup-task-artifacts | Canonical shared cleanup package |

All declared local packages are present. Reconciliation still preflights
every source and live target; a complete source inventory is not proof of machine
agreement. Actual local runbooks govern workflow completion. Preserve the distinct
codex-wayfinder-map and codex-implementation-backlog Git-common-directory pointers.
The maintained [implementation workflow](../docs/workflows/implementation.md)
connects these packages and records their authorization boundaries.

## Upstream packages

Source: [mattpocock/skills](https://github.com/mattpocock/skills).
Shared reviewed pin: `3cca18b368ae95cdbdebbff572ccafa662551015`.
Use the supported skill-installer with this exact repository, ref, and path for
complete packages. Review and deliberately change the pin for updates; fetching
Agent Team does not authorize floating upstream content.

| Identity | Path at the pin |
| --- | --- |
| grilling | skills/productivity/grilling |
| domain-modeling | skills/engineering/domain-modeling |
| setup-matt-pocock-skills | skills/engineering/setup-matt-pocock-skills |
| codebase-design | skills/engineering/codebase-design |
| diagnosing-bugs | skills/engineering/diagnosing-bugs |
| improve-codebase-architecture | skills/engineering/improve-codebase-architecture |
| writing-for-agents | skills/productivity/writing-for-agents |
| wizard | skills/engineering/wizard |
| wait-what | skills/productivity/wait-what |

The copied adaptations retain their upstream revision and MIT notices in each
package. The listed local packages are maintained by Agent Team. Install every
copied identity only from its Agent Team package, not again from upstream. Keep the
remaining upstream payloads outside this repository.
Plugins: zero. Existing plugins and caches remain Unmanaged Local State.

## Optional Claude Code configuration

When `claude` is available on an actual supported target, probe only its bounded
`--version` command. Do not authenticate, query models, modify settings, or install
or update Claude. Resolve its configuration root from `CLAUDE_CONFIG_DIR` when set,
otherwise `$HOME/.claude`. An explicit root, environment root, user or managed
settings environment override, and prior receipt anchor must agree; ambiguity stops
before managed writes. Inspect only the known local user settings and platform
managed-settings files/fragments for that override; do not infer server or MDM
policy. Do not print settings or environment values.

Agent Team owns only `rules/agent-team.md`, copied from [AGENTS.md](AGENTS.md), and
the listed complete skill directories beneath `skills/`. CLAUDE.md, settings,
credentials, plugins, unrelated rules/skills, and containing directories remain
Unmanaged Local State. The anchor rule is published before skills so the receipt
proves the root. Claude's absence preserves anchored prior targets and their receipt
entries; it does not retire or repair them. While Claude remains absent, restore
changed or missing scopes to their receipted bytes before continuing. For normal
supervised repair, re-establish Claude availability and resolve each conflict. A
deliberate root move requires investigation before writes; reconciliation never
relocates Claude state or edits its receipt to make a move appear managed. Filesystem reconciliation
is separate from native Claude session usability.

### Claude copied packages

| Package | Source responsibility |
| --- | --- |
| wayfinder | Adapted decision mapping and implementation handoff |
| code-review | Adapted Standards/Spec review with bounded reviewer ownership |
| whats-next | Original current-repository progress coordination |
| define-project-goal | Original human–AI project purpose and root README workflow |
| codebase-hygiene | Original maintenance survey and authorized cleanup coordination |
| dependency-review | Original dependency justification and replacement assessment |
| code-simplification | Original behavior-preserving simplification workflow |
| research | Adapted primary-source research and assigned artifact ownership |
| reflect | Original focused lesson capture and actionable issue follow-through |
| repository-verification | Original suitability assessment, opt-in setup and audit workflow |
| prototype | Adapted planning prototypes and authorized implementation handoff |
| tdd | Adapted behavioral testing at established public boundaries |
| resolving-merge-conflicts | Adapted conflict resolution preserving unrelated work |
| to-spec | Adapted Implementation Specification authoring |
| to-tickets | Adapted executable ticket authoring and publication |
| triage | Adapted intake, Ready Backlog admission, and authorized activation |
| set-map | Original saved Wayfinder map helper |
| next-waypoint | Original single-ticket Wayfinder entry point |
| next-waypoint-loop | Continuous Wayfinder workflow with implementation handoff |
| set-backlog | Explicit existing-parent Active Backlog selection |
| next-issue | Claim-to-delivery workflow with whole-map Design gate |
| next-issue-loop | Continuous execution within one explicitly active parent |
| pr-to-test | Canonical shared delivery package |
| promote-to-main | Canonical shared delivery package |
| cleanup-task-artifacts | Canonical shared cleanup package |

### Claude upstream packages

Use the same reviewed pin and supported staged acquisition as the Codex upstream
inventory. Complete packages retain companions, licenses, and any upstream-authored
manual-invocation settings.

| Identity | Path at the pin |
| --- | --- |
| grilling | skills/productivity/grilling |
| domain-modeling | skills/engineering/domain-modeling |
| codebase-design | skills/engineering/codebase-design |
| diagnosing-bugs | skills/engineering/diagnosing-bugs |
| improve-codebase-architecture | skills/engineering/improve-codebase-architecture |
| writing-for-agents | skills/productivity/writing-for-agents |
| wizard | skills/engineering/wizard |
| wait-what | skills/productivity/wait-what |

## Preflight, publication, and retirement

Use the narrow Machine Reconciliation Receipt at
`$CODEX_HOME/.agent-team/reconciliation-receipts-v1.json`. Preflight all current
targets and receipted retirement candidates before any managed write. Existing
unreceipted content, changed or missing targets, symlinks, unsupported models, and
unavailable declared sources require investigation before proceeding. Do not enroll
unexplained bytes as evidence simply to bypass a stop.

Whole files use exact-byte fingerprints; directory fingerprints account for
relative paths and bytes, including added, missing, and renamed files. Shared TOML
uses a canonical typed projection of only the owned fields, including absence.
The narrow helper implementation owns the exact encoding.

Upstream installed-directory fingerprints provide change detection without making
those bytes repository-authored.
A pin or installer identity alone does not prove unchanged installation. Acquire
through the supported installer in staging outside discovery, verify the exact
package, then publish to the resolved target after preflight. Replacement may
briefly leave that exact target absent. Investigate partial effects before recovery;
never blindly delete installer storage based on an identity.

A removed declaration is only a retirement candidate. Remove that exact scope only
when the prior receipt proves reconciliation wrote it and its current fingerprint
matches. Preserve all unrelated neighbors and fields. Use atomic individual writes
and receipt replacement, without claiming a cross-file transaction. Record only
actual successful writes and report partial failure honestly; no history, backup
framework, or rollback journal belongs in the receipt.

## Cleanup schedule

One target-appropriate cleanup schedule is managed: a native desktop automation or
a dedicated Linux user-cron entry invoking Codex from a stable checkout. Preserve
unrelated schedules and never fingerprint whole crontabs or app storage. Use the
existing receipt for exact schedule identity and normalized owned configuration;
verify identity and normalization on the real target. Use
[CLEANUP-SCHEDULE.md](CLEANUP-SCHEDULE.md) and the narrow target adapter for
installation, observation, and receipt updates. The managing agent owns that
separate native operation; filesystem reconciliation preserves its receipt entry
without requiring or observing the schedule. There is no scheduled reconciliation
or update.
Cleanup participation requires verified Agent Team adoption in each project's root
AGENTS.md; participation never replaces association and removal-safety evidence.
