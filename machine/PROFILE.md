# Machine Profile

This is the canonical inventory of managed Codex, Claude and optional Pi
configuration, local packages, reviewed upstream packages, and reconciliation boundaries. It declares
Managed State, not authority to change a machine merely by reading it.

## Source and targets

On a user-requested Machine Reconciliation, fetch the freshest current-branch
source while preserving local work, select one concrete Git revision, and read all
assets from it throughout the run. Report the revision. Investigate detached,
unpublished, ambiguous, divergent, or unavailable source; do not silently switch
branches or fall back to stale content. There is no separate manifest, lockfile,
generator, or profile version.

The Codex inventory applies to macOS desktop, headless Linux, native Windows
11 x64 desktop/CLI, and WSL 2 Ubuntu 24.04 LTS x64 with Linux Codex CLI.
Desktop Linux remains out of scope. Windows uses native
Python 3.11+ and native Codex; do not cross into WSL to reconcile a Windows home.
Each environment owns its configuration, skills, credentials, and receipts.
Resolve CODEX_HOME and supported skill destinations
on the actual host. The copied user-skill destination reviewed during planning is
`$HOME/.agents/skills`; verify it on the target. Supported installer storage may use
a different root. Do not normalize roots with symlinks or own their containing
directories. A headless host still receives browser_verifier; ability to execute a
browser task depends on actual host capabilities.

Native Windows targets use local filesystem paths. UNC/network/device paths,
drive-relative roots, symlinks, junctions, and other reparse points require
investigation before writes. Supported custom roots must be discovered in the
same environment. Use separate writable repository checkouts and Git common
directories for native Windows and WSL; cross-environment paths are read-only.

WSL uses its Linux filesystem for writable checkouts, configuration, skills,
staging, and receipts. Mounted Windows storage is not a supported writable target,
including DrvFS mounted outside the usual `/mnt` locations. Use Linux-native
Python, Git, gh, Bash, and Codex inside the distribution. A launcher symlink may
resolve within Linux storage, but must not redirect execution onto Windows storage.
Authentication is established independently inside each environment.

## Shared configuration and whole files

Merge only these thirteen dotted paths from [config.toml](config.toml) into
`$CODEX_HOME/config.toml`; never replace that file wholesale:

- model
- model_reasoning_effort
- default_permissions
- approval_policy
- approvals_reviewer
- agents.enabled
- agents.max_concurrent_threads_per_session
- agents.default_subagent_model
- agents.default_subagent_reasoning_effort
- agents.interrupt_message
- features.multi_agent_v2.min_wait_timeout_ms
- features.multi_agent_v2.default_wait_timeout_ms
- features.sleep_tool.mode

Longer idle waits reduce repeated parent-agent wakeups while subagents work.
Codex ends a wait early when agent messages or user input arrive. Multi-agent V2
enablement and maximum wait time remain unmanaged.

Expose native sleep across the model roster as a fallback when no completion-aware
wait is available. Prefer native agent and process waits that return on completion;
sleep availability alone does not prevent repeated goal continuations.

All other fields remain unmanaged, including root service_tier, credentials,
providers, MCP servers and environment, trust, history, projects, and UI settings.
The profile selects Full Access: tool calls using this default run without Codex's
filesystem or network sandbox restrictions and routine approval prompts.
`approvals_reviewer` remains configured for eligible approval routes; it adds no
review gate to actions already allowed under Full Access.

Full Access changes tool permissions, not task authorization. Preserve explicit
human-approval boundaries for deployments, destructive actions and main promotion.
Trusted repository configuration and managed requirements can tighten the defaults.

Role sandbox settings are defaults. Codex reapplies the parent's live sandbox and
approval overrides when spawning subagents, even when a role declares another
sandbox default; see [subagent permission inheritance](https://learn.chatgpt.com/docs/agent-configuration/subagents).
The review owner's [routing](skills/code-review/reviewer-routing.md) keeps the
assignment read-only and reports inherited permissions without requiring separate
review approval. A read-only assignment does not prove enforced filesystem isolation.

Installation alone does not establish changed permissions in existing threads.
Verify fresh-task defaults in each actual client and report any required reload or
restart separately, preserving active work.

| Source relative to machine/ | Destination | Scope |
| --- | --- | --- |
| AGENTS.md | $CODEX_HOME/AGENTS.md | Whole file |
| agents/browser_verifier.toml | $CODEX_HOME/agents/browser_verifier.toml | Whole file |
| agents/critical_reviewer.toml | $CODEX_HOME/agents/critical_reviewer.toml | Whole file |
| agents/claude-delegation.md | $CODEX_HOME/agents/claude-delegation.md | Whole file |
| agents/deep_specialist.toml | $CODEX_HOME/agents/deep_specialist.toml | Whole file |
| agents/explorer.toml | $CODEX_HOME/agents/explorer.toml | Whole file |
| agents/planner.toml | $CODEX_HOME/agents/planner.toml | Whole file |
| agents/security_specialist.toml | $CODEX_HOME/agents/security_specialist.toml | Whole file |
| agents/sysadmin_operator.toml | $CODEX_HOME/agents/sysadmin_operator.toml | Whole file |
| agents/test_verifier.toml | $CODEX_HOME/agents/test_verifier.toml | Whole file |
| agents/worker.toml | $CODEX_HOME/agents/worker.toml | Whole file |
| agents/workflow_monitor.toml | $CODEX_HOME/agents/workflow_monitor.toml | Whole file |

Each role's name, instructions, model presence, effort, tier, and sandbox move together.
The current roster assignments and naming are in [AGENTS.md](AGENTS.md)
and those ordinary role files. [Claude delegation](agents/claude-delegation.md) owns
preferred Opus planning/implementation and native Sol fallback. The code-review
package owns default native review and optional additional Claude review. Its
[reviewer routing](skills/code-review/reviewer-routing.md) and
[model declaration](skills/code-review/reviewer-models.toml) own mode-aware native
selection; critical_reviewer intentionally omits a fixed model to permit explicit
dispatch. Claude installation and account authentication remain outside this
profile; their absence does not block
Machine Reconciliation. Verify model/effort support during reconciliation;
never silently substitute. Inventory validation proves declared model/effort
support, not Daybreak Blue program eligibility or selection, account entitlement,
current task mode compatibility or successful independent review.
Verify native dispatch on the execution host through the owning routing, including
its single standard attempt when mode evidence is missing; report unknown mode and
unexercised recovery honestly. Loaded roles can require restart after reconciliation.
Preserve AGENTS.override.md and surface
its interference as a supervised conflict. No default role shadow or renderer is
included.

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
| dependabot-upkeep | Original dependency-alert protection and repository-owned remediation workflow |
| code-simplification | Original behavior-preserving simplification workflow |
| research | Adapted primary-source research and assigned artifact ownership |
| reflect | Original focused lesson capture and actionable issue follow-through |
| audit-agent-instructions | Original evidence-based skill and rule audit |
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
agreement. Actual local runbooks govern workflow completion. Distribute set-map
and set-backlog together: the latter uses the former's shared selector helper.
Preserve untracked effort-scoped selection state and legacy repository-wide
pointers; [selection scope and handoff](skills/set-map/SELECTIONS.md) owns their
explicit migration and task binding. Source installation never migrates selections.
The maintained [implementation workflow](../docs/workflows/implementation.md)
connects these packages and records their authorization boundaries.

## Upstream packages

### Matt Pocock

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

### Herdr

Source: [herdrdev/herdr](https://github.com/herdrdev/herdr).
Update policy: latest default-branch commit on each reconciliation.
This is the operator-approved exception to reviewed upstream pins. Resolve one
immutable commit per run, report it, and reuse it for supported staged acquisition,
exact-file/Git blob verification, preflight, and publication. A later run resolves
the latest commit again; matching installed bytes retain the ordinary no-op behavior.

| Identity | Path at the resolved commit |
| --- | --- |
| herdr | skills/herdr |

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
| dependabot-upkeep | Original dependency-alert protection and repository-owned remediation workflow |
| code-simplification | Original behavior-preserving simplification workflow |
| research | Adapted primary-source research and assigned artifact ownership |
| reflect | Original focused lesson capture and actionable issue follow-through |
| audit-agent-instructions | Original evidence-based skill and rule audit |
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

Use the Codex upstream inventory's reviewed pin for the Matt Pocock packages and
the same run's resolved latest commit for Herdr. Complete packages use supported
staged acquisition and retain companions, licenses, and any upstream-authored
manual-invocation settings.

| Identity | Path at the selected revision |
| --- | --- |
| grilling | skills/productivity/grilling |
| domain-modeling | skills/engineering/domain-modeling |
| codebase-design | skills/engineering/codebase-design |
| diagnosing-bugs | skills/engineering/diagnosing-bugs |
| improve-codebase-architecture | skills/engineering/improve-codebase-architecture |
| writing-for-agents | skills/productivity/writing-for-agents |
| wizard | skills/engineering/wizard |
| wait-what | skills/productivity/wait-what |
| herdr | skills/herdr |

## Shared Codex shell integration

Normal reconciliation manages this shell integration on macOS/Linux whenever
native Bash 3.2+ or Zsh is available, independently of Pi participation. Native
Windows is excluded; unavailable-shell scopes retain their receipts and pass the
same fingerprint gate without repair or retirement.

Helper source: `shell/codex-herdr.sh`.
Helper destination: `$CODEX_HOME/shell/codex-herdr.sh`.
Hook marker: `agent-team codex-herdr`.

| Shell startup | Destination |
| --- | --- |
| bash | .bashrc |
| bash-login | .bash_profile, .bash_login, .profile |
| zsh | $ZDOTDIR/.zshrc |

Bash receives a hook in .bashrc and its first existing login file in the declared
order, creating .bash_profile only when none exists. Zsh's effective native
ZDOTDIR defaults to HOME. Roots and login-file selection must agree with prior
hook receipt anchors; symlinks and ambiguous or moved targets stop before writes.
Each exact marked hook sources the same helper only in its matching interactive
shell, guarding existing Codex aliases/functions. Repeated sourcing is harmless.
Direct competing declarations in the known startup files stop preparation; guards
also preserve definitions supplied by other startup code. Fresh-shell verification
must establish actual discovery rather than infer it from the source hook alone.

The function named `codex` checks only HERDR_ENV presence, including an empty
value, and a whitespace-boundary regex for --no-daemon in invocation text. When
present and unmatched it executes `command codex --no-daemon "$@"`; otherwise it
executes `command codex "$@"`. It preserves original arguments and native status,
with command interpretation and validity left entirely to Codex. Other commands
are unaffected; no command classification or option parsing belongs in this helper.

The receipt owns the helper file and only each startup file's marked hook bytes,
including their boundary newlines. All unrelated startup bytes and existing modes
remain unmanaged. Missing/changed hooks and duplicate/malformed markers require
investigation. Prepare complete candidates and recheck each entire raw startup
file before publication; a concurrent unowned edit stops the run. Retiring a hook
can remove only its receipted bytes, never the containing startup file. Existing
sessions need a new shell or deliberate sourcing; publication does not prove live
Herdr routing context or change a shared Codex daemon's environment.

## Optional Pi configuration

Opt in a machine with `--enable-pi`; later reconciliations reuse its proven
`HERDR.md` receipt anchor and automatically consider age-qualified upgrades. Without
an anchor or explicit opt-in, Pi remains inactive. Use `--skip-pi` to preserve
anchored Pi scopes and receipt entries for this run; they still pass the ordinary
fingerprint gate, and skipping participation never uninstalls Pi. This includes the
whole runtime and launcher outside the configuration root. A foreign installation,
changed owned bytes or modes, root move or conflicting override requires investigation
before any managed writes. An active owned runtime blocks an upgrade; preserve all
running tasks and retry after they exit. Native macOS uses its `lsof` executable
mapping inspection; Linux inspects current-user `/proc` executable identities;
Windows inspects native process executable paths. Unavailable inspection stops an
upgrade rather than assuming the runtime is idle.

Resolve `PI_CODING_AGENT_DIR`, otherwise `$HOME/.pi/agent`; an explicit
`--pi-config-root` may select a custom root when the environment is unset, and must
agree when it is set. With neither override, reuse an existing receipt anchor
before the default root. The effective root must agree with that prior anchor.
An existing or symlinked `AGENTS.override.md` in an enabled Pi root suppresses its
managed instructions: preserve it and stop for investigation before managed writes.
Configuration, auth, sessions, extensions and skill containers
remain unmanaged except for the exact scopes below. Never copy Codex tokens or
substitute an API key: use Pi's interactive `/login` with the same OpenAI ChatGPT
subscription account.

Release source: https://github.com/earendil-works/pi.
Minimum release age: 168 hours.

Capture one UTC run start before source selection. From all paginated canonical
releases, select the highest stable semantic version published at or before that
start minus the minimum age; exclude drafts, prereleases and non-semantic tags.
Malformed publication metadata for a stable release stops preparation.
Freeze its version, publication timestamp, exact asset identity and published
SHA256SUMS checksum for the run, verifying advertised SHA-256 digests when present.
Missing metadata, matching artifacts or checksum stops before managed writes.
Never fall back to latest/npm. Initial installation uses the same policy; retain an
unchanged newer owned runtime without downgrading. Report frozen provenance.

| Python platform | Architecture | Official artifact |
| --- | --- | --- |
| darwin | arm64 | pi-darwin-arm64.tar.gz |
| darwin | x64 | pi-darwin-x64.tar.gz |
| linux | arm64 | pi-linux-arm64.tar.gz |
| linux | x64 | pi-linux-x64.tar.gz |
| win32 | arm64 | pi-windows-arm64.zip |
| win32 | x64 | pi-windows-x64.zip |

The complete native bundle is one owned directory, preserving its layout and file
modes; it includes the native executable, package.json and all shipped resources.
No Node installation is required. Its separately receipted global launcher is an
ordinary executable file, exporting the resolved Pi configuration root and the
native app-server-discovered `CODEX_HOME` before executing that bundle. This binds
Pi’s shared instruction pointer to the same Codex home, including a supported
`--codex-home` override. The launcher directory must be on the native PATH; report
a missing PATH entry rather than editing shell or system configuration.

| Runtime platform | Runtime directory | Command file |
| --- | --- | --- |
| posix | $HOME/.local/share/agent-team/pi | $HOME/.local/bin/pi |
| win32 | $LOCALAPPDATA/AgentTeam/pi | $HOME/.local/bin/pi.cmd |

| Source relative to machine/ | Destination relative to Pi root | Scope |
| --- | --- | --- |
| pi/AGENTS.md | AGENTS.md | Whole file |
| pi/HERDR.md | HERDR.md | Whole file |

Merge the scalar fields declared in [pi/settings.json](pi/settings.json) into
`settings.json`. Own only those scalar fields and membership of each declared skill
path in its native `skills` array; retain unrelated values and foreign resource
paths. Recheck the complete settings file immediately before publication so a
concurrent unmanaged edit stops rather than being overwritten. Pi reuses the
Claude copied/upstream package inventory above through native absolute skill paths
to the Codex-installed complete packages, with no Pi copies or changed upstream
manual-invocation metadata. Native discovery deduplicates identical real paths;
conflicting other packages remain a supervised usability failure.

Herdr extension source: `src/integration/assets/pi/herdr-agent-state.ts`.

Use that exact upstream native Pi integration at the same run's frozen Herdr
commit. Verify its Git blob, retain the upstream license, and publish only
`extensions/herdr-agent-state.ts` and `licenses/herdr-LICENSE`, preserving foreign
extensions. This is the native
installer's payload; filesystem reconciliation owns this named file, rather than
running the installer against a live home. Pi-only coordination, leaf workers and
lifecycle rules are owned by [pi/HERDR.md](pi/HERDR.md); other hosts retain their
existing routing. Runtime/configuration publication does not prove account or model
entitlement, live worker usability, or adoption by an existing Pi session.

## Experiment-to-test migration

Use `--migrate-experiment` only for an operator-approved move from the former
Claude-primary experiment to this profile. The canonical preparation command
preflights every prior receipt scope and every current target before writes.
The following exact prior scopes are released to Unmanaged Local State; their
files and all settings values remain unchanged. Relative destinations use the
established Claude receipt root or the native Claude desktop data root. Unknown
paths, different scopes and changed fingerprints still stop for investigation.

| Prior host | Relative destination | Kind | Owned fields |
| --- | --- | --- | --- |
| Claude | agents/CriticalReviewer.md | file | - |
| Claude | agents/Explore.md | file | - |
| Claude | agents/SecuritySpecialist.md | file | - |
| Claude | agents/WorkflowMonitor.md | file | - |
| Claude | settings.json | json | effortLevel, env.CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS, model |
| Claude desktop | claude_desktop_config.json | json | preferences.ccBranchPrefix |

Before any release or current-target publication, preserve the complete original
receipt beside the active receipt as `receipt-before-test-migration-<sha256>.json`,
where the hash covers its exact original bytes. Preserve this private installation
record; it does not enroll targets or participate in skill discovery. The active
version-1 receipt then records current ownership normally. The explicit migration
removes only the declared prior entries, after verifying their saved fingerprints
and unchanged complete files; it never changes their contents. Other obsolete
receipted packages use the ordinary supervised retirement gate. Subsequent ordinary
reconciliation ignores released Unmanaged Local State and retains the original record.

## Preflight, publication, and retirement

Use the narrow Machine Reconciliation Receipt at
`$CODEX_HOME/.agent-team/reconciliation-receipts-v1.json`. Preflight all current
targets and receipted retirement candidates before any managed write. Existing
unreceipted content, changed or missing targets, symlinks/reparse points, unsupported models, and
unavailable declared sources require investigation before proceeding. Do not enroll
unexplained bytes as evidence simply to bypass a stop.

Whole files use exact-byte fingerprints; directory fingerprints account for
relative paths and bytes, including added, missing, and renamed files. Pi runtime
fingerprints additionally own POSIX file/directory modes; its ordinary launcher
fingerprint owns its POSIX mode. Pi JSON fingerprints project only declared scalars
and named resource membership, retaining unowned values. Shared TOML
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

One target-appropriate cleanup schedule is managed per environment and Codex home:
a supported desktop automation on macOS or Windows, a native Task Scheduler job
for Windows CLI-only use, or a dedicated Linux user-cron entry (including WSL)
invoking Codex from a stable checkout. Windows desktop and CLI sharing a home
share one schedule. Prove retirement before changing schedulers. Preserve
unrelated schedules and never fingerprint whole crontabs or app storage. Use the
existing receipt for exact schedule identity and normalized owned configuration;
verify identity and normalization on the real target. Use
[CLEANUP-SCHEDULE.md](CLEANUP-SCHEDULE.md) and the narrow target adapter for
installation, observation, and receipt updates. The managing agent owns that
separate native operation; filesystem reconciliation preserves its receipt entry
without requiring or observing the schedule. There is no scheduled reconciliation
or update.
Windows CLI jobs run only as the logged-in user, without elevation, stored account
passwords, or machine wake. Missed runs are acceptable; native delayed-run
settings do not promise catch-up execution. WSL cron requires the distribution and daemon to be running; missed
stopped-distribution runs are skipped. No Windows job starts WSL for cleanup.
Cleanup participation requires verified Agent Team adoption in each project's root
AGENTS.md; participation never replaces association and removal-safety evidence.
