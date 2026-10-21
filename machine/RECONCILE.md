# Machine Reconciliation

Use this procedure only for an explicit reconciliation request or the
[current-Mac self-healing cleanup run](CLEANUP-SCHEDULE.md#current-mac-self-healing-run)
that its prompt authorizes. Python 3.11+ and
Git/gh are needed for the narrow helper; supported skill-installer performs upstream
acquisition. Read PROFILE.md and the exact target's current instructions first.
These are Tooling helpers, verified by actual operations. No machine simulator or
coverage suite is part of this workflow.

## Canonical preparation and preflight

From the current Agent Team checkout, invoke the single preparation command:

```bash
python3 machine/prepare_reconciliation.py --repository /actual/agent-team
```

On native Windows, run the same Python helper from PowerShell with an installed
native Python 3.11+ interpreter and the native checkout path:

```powershell
& $PythonExecutable machine/prepare_reconciliation.py --repository $RepositoryPath
```

Resolve those variables to actual local paths first. Do not use a Windows Store
execution alias or WSL Python for this operation. The Codex app-server must report
the same operating system as the interpreter. Native Windows paths remain separate
from WSL roots; symlinks, junctions, and other reparse points stop preparation.

In WSL 2 Ubuntu 24.04, use a separate checkout under the Linux home with its own
Git common directory. Install and sign in to the Linux Codex CLI inside that
distribution, then invoke the same Python preparation command there. Do not copy
Windows authentication or receipts, use a mounted Windows checkout, or invoke a
Windows executable through WSL interop. The path gate inspects the actual mount
table so moving a Windows mount does not make it eligible for managed writes.
Verify native Windows state remains unchanged after WSL reconciliation.

It resolves the checkout's tracked branch and selects the freshest published remote
revision, with the no-apply unpublished-preview exception below. It uses a temporary
detached worktree, discovers the actual Codex home and user-skill
destinations through the native app-server and existing receipt, and checks the
target operating system and every declared model/effort. When `claude` is available,
it runs only a bounded `claude --version` probe and resolves the separate Claude
configuration root from `CLAUDE_CONFIG_DIR` or its default. It stages the upstream
packages with the installed skill-installer at their declared revisions: the
reviewed Matt Pocock pin and one latest default-branch Herdr commit resolved and
reported for this run. It verifies their exact file sets and Git blobs, builds the
complete formatting-preserving shared-config candidate, and
invokes the existing all-target read-only gate. It makes no managed writes. The
command removes complete temporary preparation after a successful preflight and
retains failed acquisition staging for inspection. Supply an explicit
`--skills-root` (and, when distinct, `--upstream-root`) only when native discovery
and receipt evidence cannot establish a single destination.

Candidate preparation acquires [tomlkit](https://pypi.org/project/tomlkit/) at the
exact pin in [requirements.txt](requirements.txt), consumed by the existing Python
`pip` or `uv` installer into that run's staging directory with no transitive
installation. Dependabot alerts cover this same manifest; the installed version is
checked against it. Preparation never installs a global dependency.

The command stops if the current branch has diverged from its tracked remote or a
required target capability/source is unavailable. When the branch is only ahead of
its freshly fetched remote, a run without `--apply` may preview the exact local HEAD
commit, provided the checkout has no staged, unstaged or untracked changes; the
source report labels it `"publication": "unpublished"`. That preview supplies no
application authority: `--apply` refuses unpublished commits before preparing a
source. Publish or resolve the source authority before applying; do not bypass that
evidence with a local checkout.

After specific preflight conflicts have been resolved, run the same command with
`--apply` and each exact approved `--resolve target=observed-sha256` argument. It
prepares the candidate config, verifies declared model/effort availability, reruns
the filesystem gate, publishes changed targets, and verifies fresh Codex skill
discovery. It manages only the Machine Profile's files, configuration, and skill directories. A successful
Claude filesystem publication is not Claude session usability; record that evidence
through the separate host verification workflow. The managing agent maintains cleanup
schedules separately through the native tools and `cleanup_schedule.py`.

## Frozen published revision

`--published-revision <full-sha>` selects that exact commit instead of the freshest
one, so separate read-only and `--apply` invocations use one revision even after
main advances:

```bash
python3 machine/prepare_reconciliation.py --repository /actual/clone \
  --published-revision full-commit-sha --preserve-model-settings
```

The repository must be a clean ordinary checkout of `main` tracking `origin` at
`https://github.com/jdip/agent-team.git`, with HEAD exactly at that commit. Each
invocation still reads remote main, fetches its objects without moving local refs or
the checkout, and requires the commit to be reachable from it, with or without
`--apply`. A newer head is reported as `published_head`, never selected; a rewritten
or unreachable main stops before a source is prepared. The temporary detached
worktree is created beside the repository. Without the option, source selection is
unchanged.

## Preserving root model settings

To keep this machine's existing root model selection for one run, add the flag to
both the read-only and `--apply` invocations:

```bash
python3 machine/prepare_reconciliation.py --repository /actual/agent-team --preserve-model-settings
```

Preparation freezes root `model` and `model_reasoning_effort` once from the native
app-server-discovered `config.toml`. Both must be present nonblank strings that the
installed Codex advertises as a supported model/effort pair; a missing, blank or
unsupported pair stops before managed writes. The candidate config keeps that pair
and applies the other owned fields from source; the source stays unchanged. Every
declared role, subagent and reviewer pair is still verified, and post-apply
verification checks the installed pair. A pair changed after freezing fails the
preflight, candidate and raw-config rechecks; prepare again.

The config receipt fingerprints all thirteen fields together. Each config entry
reconciliation writes also carries `evidence`: a digest of that entry's eleven
other owned fields. With the flag, a live config differing from its receipt passes
the gate only when that evidence proves those fields unchanged, so the frozen pair
alone moved. Mixed drift, missing evidence and newly owned fields remain ordinary
conflicts requiring an exact `--resolve`; without the flag every mismatch does. The
flag never substitutes the newer source profile for this history.

A legacy entry without evidence acquires it only from verified state. When the
live config matches that receipt, preflight reports `Would record unchanged-field
evidence` and apply rewrites only the receipt entry, not the config. A conflicting
legacy entry stays unresolved until an exact `--resolve`; that publication receipts
the evidence. Malformed evidence, or evidence contradicting a matching fingerprint,
stops reconciliation. Apply receipts the actual installed config, and an
unchanged later run with the flag is a no-op. A later run without the flag treats
the profile values as desired again and reports `Would publish` for the config
when those values differ from the installed pair.

## Shared Codex shell integration

Normal reconciliation manages the declared shared `codex` function for available
Bash 3.2+ and Zsh on macOS/Linux, independently of Pi participation. Read Profile's
[shell inventory](PROFILE.md#shared-codex-shell-integration) for exact helper and
startup targets. Native startup probes establish alias/function provenance and
consistent effective ZDOTDIR across ordinary, interactive and login modes without
printing private function bodies. Preserve normal startup-created state. Foreign
Codex definitions, changed hook bytes, malformed/duplicate markers, ambiguous roots
or changed Bash login precedence stop before managed writes.

The function checks only whether HERDR_ENV is set, including an empty value, and
whether a regex finds --no-daemon in invocation text. Set and unmatched prepends
one flag; otherwise the original invocation passes through. It forwards exact
arguments and native exit status with `command codex`, leaving all command and
option interpretation to Codex. Verify installed support through bounded native
help; see the official [CLI options](https://learn.chatgpt.com/docs/developer-commands).

Each matching interactive shell sources the same helper through its exact guarded
startup block, preserving foreign aliases/functions and every unowned byte and
existing file mode. Repeated sourcing is harmless. Complete raw-file rechecks stop
concurrent unowned edits before replacement; retirement can remove only receipted
hook bytes, never the startup file. Unavailable-shell and native Windows scopes
remain preserved. A second unchanged reconciliation retains content and receipts.

Use a new shell or deliberately source the changed startup file to load the
function. Existing Codex backends retain their environment: an active TUI with
missing routing context may need a new direct resume after preserving its work.
Verify actual execution-side HERDR_ENV and native caller resolution before Herdr
mutations, honoring caller aliases after pane moves. Wrapper flag insertion does
not prove genuine Herdr context. Preserve state rather than inject context or
restart a shared daemon. Pi's separate `-c agents.enabled=false` leaf restriction
still applies; report actual worker usability separately from configuration.

## Optional Pi participation

Opt in this machine explicitly on its first requested Pi reconciliation:

```bash
python3 machine/prepare_reconciliation.py --repository /actual/agent-team --enable-pi
```

After the complete read-only gate passes, repeat with `--enable-pi --apply` and
only specifically approved conflict resolutions. This flag propagates through
canonical source preparation. Later ordinary reconciliations reuse the proven
Pi receipt anchor and automatically consider age-qualified upgrades. Machines
without an anchor or opt-in remain inactive. Use `--skip-pi` to preserve all anchored
Pi targets and receipts for one run, including the runtime and command; it never
uninstalls Pi. The enable and skip flags are mutually exclusive. Changed or missing
inactive targets still stop the shared gate rather than being repaired or retired.
Explicit Pi participation is independent of optional Claude discovery.

`PI_CODING_AGENT_DIR` selects Pi's native root; its default is `~/.pi/agent`.
Use `--pi-config-root` for a custom root when that environment variable is unset;
when set, both must agree. With neither override, reuse an existing receipt
anchor before the default. The effective root must also match its prior anchor.
An existing or symlinked `AGENTS.override.md` in an enabled Pi root suppresses the
managed instruction pointer; the gate preserves it and stops before managed writes.
Root moves, ambiguous paths, existing foreign commands, changed
owned content/modes and symlinks require investigation before writes. Configuration
root containers, auth.json, sessions, foreign extensions/skills and unowned
settings remain unmanaged.

Preparation freezes UTC start before source selection, then reads Profile's
canonical release source, age threshold and platform mapping. It paginates releases,
selects the highest stable semantic version published at least 168 hours before
that frozen start, and reports version, publication timestamp, cutoff, exact asset
ID/URL and checksum. It verifies SHA256SUMS and any advertised SHA-256 digests,
rejects unsafe archive paths/types and extracts the entire native bundle with its
original layout/modes. Exact native/package version agreement is mandatory. No
eligible release, archive or checksum stops the entire run before managed writes;
there is no latest/npm fallback or additional Node installation. Unchanged newer
owned bundles remain installed; automatic upgrades move forward only.

The ordinary receipt engine owns the complete native bundle and a separate global
launcher at Profile's declared native destinations. The launcher selects the
resolved Pi root and the same native app-server-discovered `CODEX_HOME` before
executing that bundle. This preserves shared instruction discovery when using
`--codex-home`, even if that root differs from the inherited environment/default.
Confirm its directory is already on native PATH; the helper reports a missing PATH entry without changing shell/system
configuration. Running managed Pi tasks prevent an upgrade; finish them normally
and reconcile later. Existing sessions may require restart to adopt configuration
or skills, so preserve active work and report that limit.

Pi reuses the relevant complete local/upstream skill packages through native
absolute resource paths, preserving original frontmatter and manual-only settings.
Its scoped settings candidate merges only declared scalars and those exact skill
entries, retaining foreign entries. The complete settings file is rechecked at
publication, including unowned values. Native realpath deduplication avoids duplicate
loads; a different package with the same name is a usability conflict to resolve.
The exact upstream Herdr Pi extension and license are acquired from the same run's
immutable Herdr commit, verified against Git blob hashes, and receipted as named
files. Other extensions remain untouched. See the installed HERDR.md for Pi-only
leaf-worker and lifecycle rules; Codex/Claude global behavior stays with its owner.

Active Pi participation also stages the standalone Fast extension source and
license declared in [Profile's Fast inventory](PROFILE.md#fast-extension). The
reviewed immutable pin is independent of Pi's age-qualified runtime and Herdr's
latest-commit policy. Acquisition verifies each Git blob; the all-target gate
reverifies the staged files against that pin before any publication. The existing
file receipt/conflict/no-op/retirement rules apply to `extensions/fast.ts` and
`licenses/pi-fast-LICENSE`. No Node/npm installation, live `pi install`, settings
array edit or user `fast.json` write is needed. Without Pi participation, or with
`--skip-pi`, preserve anchored files and receipts rather than fetching, repairing
or retiring them. Existing foreign target files stop as ordinary conflicts;
inspect native startup for a different extension registering a duplicate `/fast`
command before claiming usability, and preserve that foreign extension.

After an authorized apply, use `/reload` in Pi and confirm `/fast` appears among
the extension commands. `/fast` toggles Fast for the current runtime/session;
run it again to turn Fast off. The upstream default is off; existing global or
trusted-project Fast preferences are preserved and may select a different default.
Reconciliation does not toggle Fast, change authentication/models/reasoning, or
establish that the backend accepted a faster tier. The reviewed extension requests
`service_tier: "fast"` for eligible `openai` models (including `gpt-6.1-sol`) and
`"priority"` on eligible `openai-codex` OAuth models. Its direct OpenAI ChatGPT
OAuth tier acceptance remains unverified upstream. Tier availability, rate and
quota consumption depend on the account/backend; Pi's displayed cost is not
subscription-quota evidence. Any live Fast-enabled inference is a separately
authorized check, not an installation requirement.

For source-only verification without live publication or inference, load the
actual staged `fast.ts` explicitly with the native Pi runtime in offline,
nonpersistent RPC mode and request `get_commands`. Confirm the extension command
is discovered without load errors or duplicate-command warnings; do not invoke
it. This exercises discovery, not backend tier acceptance. Keep all existing
credentials, preferences, sessions and unrelated extensions unchanged.

After installation, prove the global `pi --version`, then inspect native readiness
without refreshing or exposing credentials:

```bash
pi auth check --provider openai --json --no-refresh
```

Require the selected provider to report both ready and OAuth authentication before
inference. If login is needed, open native interactive Pi and use `/login` to select
OpenAI and the same ChatGPT subscription account used by Codex. The human completes
browser consent. Keep auth files, tokens and account details private; never copy
Codex credentials or substitute API billing. A pending login is an incomplete setup
gate, separate from successful filesystem reconciliation.

Once ready, send one minimal prompt with explicit `--provider openai`,
`--model gpt-6.1-sol`, `--thinking high`, `--print` and `--no-session`. Inspect native
verbose startup/resource diagnostics and an explicit skill invocation to prove
actual selected-release discovery and manual-only behavior. Finally exercise an
isolated Herdr leaf-worker, reuse, result acceptance and verified teardown through
the installed guide, preserving user panes, transcripts and worktrees. Report
unavailable hosts, entitlement, worker or interactive capabilities as unverified;
version and syntax checks alone do not establish these outcomes.


## Approved experiment-to-test migration

For an explicitly approved move from the former Claude-primary experiment, run
this same preparation command with `--migrate-experiment`. Read the exact release
inventory and evidence rules in [PROFILE.md](PROFILE.md#experiment-to-test-migration).
Preparation reports every proposed ownership release, retirement and publication;
it makes no managed writes. Validate that plan against the actual prior receipt
and the operator's preservation requirements before applying.

After a passing preflight and any necessary specific conflict decisions, repeat
with `--migrate-experiment --apply`. The helper preserves the complete original
receipt in its hash-named installation record before changing active ownership.
It leaves the declared former agent files, shared settings and desktop preferences
byte-for-byte unchanged and releases them to Unmanaged Local State. It then
publishes current profile targets and updates their existing narrow receipt through
the normal verified path. Unknown scopes or unexplained changed state remain blockers.

Verify the original record matches the pre-migration receipt, the released files
remain unchanged, and every current target agrees with its current receipt and
selected source. Check fresh discovery and model support. Preserve the original
record and report ownership release separately from actual file retirement and
publication; existing schedules and unrelated state retain their owners.

## Preparation details

Resolve the repository's current branch and its remote. Fetch that branch,
preserving dirty work. Select and report one concrete freshest published revision,
an explicit frozen `--published-revision`, or, for a clean no-apply preview only,
the unpublished local HEAD ahead of it. If
branch identity, detached state, divergence, or unpublished work for an apply leaves
intent unclear, resolve that concrete source question. Use an isolated clean
checkout of the chosen
revision for the run; never silently change the source branch or use stale content.
Read every declared source there. An incomplete profile stops before live writes.

Machine Bootstrap ends with official Codex acquisition, authentication, obtaining
this repository, and asking an agent to reconcile it: macOS uses the official
desktop download; headless Linux uses the supported standalone CLI path; native
Windows uses the official Windows desktop or native CLI installation. Update
Codex only when the profile requires a newer version. There is no custom bootstrap
framework or background update.

On the actual target resolve CODEX_HOME, the supported copied-skill destination,
and upstream installer destination. Pass `--upstream-root` when the supported installer destination differs from
`--skills-root`. Never silently relocate existing packages. When Claude is present,
resolve its root separately. An explicit `--claude-config-root`, `CLAUDE_CONFIG_DIR`,
settings environment override, and prior `rules/agent-team.md` receipt anchor must
agree. Inspect only known local user settings and platform managed-settings
files/fragments; unavailable server or MDM policy remains a reported limit. Do not
print settings or environment values. A Claude executable that is not discovered
leaves anchored Claude receipt scopes preserved; a found executable whose version
probe fails is an availability error.

Claude discovery checks PATH, then the native `~/.local/bin/claude` launcher.
Use `--claude /actual/claude` for a verified installation elsewhere; the explicit
path takes precedence and must pass the bounded version probe. No login hooks or
shell-setting changes are needed. A `not-discovered` result is unresolved discovery,
not proof Claude is absent: inspect the actual host before accepting preserved
Claude scopes as the intended outcome. Invalid or broken discovered launchers stop
reconciliation instead of falling back to an apparent absence.

Verify every declared model and effort is supported. Preserve credentials, sessions,
unrelated configuration, directories, plugins, and global overrides. An interfering
AGENTS.override.md requires a concrete supervised decision, never automatic removal.

## Prepare and preflight

Create temporary staging outside every skill-discovery root and on the destination
filesystem, using a location whose association with this run is known. Read the
installed system skill-installer and use its `install-skill-from-github.py` with
each repository and package path declared in PROFILE.md, the selected immutable
`--ref`, and `--dest` pointing to that run's staging directory. The Matt Pocock
reviewed pin stays fixed. Herdr alone resolves the latest default-branch commit
once per preparation run; both hosts use that commit. Do not implement an alternate
downloader. A failed acquisition leaves live skills unchanged; inspect partial
staging before retrying. The helper checks every staged relative file and Git blob
against its selected upstream tree, including companion files.

The preparation command passes its resolved paths and immutable `--herdr-ref` to
both the read-only gate and apply. Each gate verifies staging against that same
commit and the reviewed pin; the filesystem helper requires the resolved Herdr
commit rather than resolving latest itself. Agents use canonical preparation.
Invoking preparation again, including a later `--apply` run, resolves latest again
and repeats the full gate. Herdr's exception changes no receipt, conflict,
retirement, target-root, or absent-Claude preservation rules.

The helper reads PROFILE.md's tables directly; there is no parallel manifest. It
checks every declared target plus every previously receipted retirement candidate.
It reports absent source packages and conflicting target/scope/saved/observed
fingerprints without printing configuration values. No receipt for an existing
target, changed/missing receipted state, symlinks, or unknown scope stops all writes.
An absent target without prior receipt is eligible for creation.

Claude owns only the Profile's explicit `rules/agent-team.md` anchor and selected
skill directories. Its root is never inferred from overlapping Codex skill names.
The anchor must agree with the effective root and is written before Claude skills.
Staging stays outside both hosts' discovery roots and on every destination
filesystem. When Claude is absent, its anchored receipted paths still pass the same
fingerprint gate but remain untouched; they are not retirement candidates and cannot
consume a `--resolve` override. While Claude remains absent, restore changed or
missing scopes to their receipted bytes before continuing. For normal supervised
repair, re-establish Claude availability and resolve each conflict. A changed
effective root is a relocation to investigate before writes. Restore the effective
root to the receipted location to resume ordinary reconciliation; deliberate moves
require investigation, never an automatic relocation or receipt edit.

Investigate all conflicts before asking. Show meaningful differences, what replacement
would lose, and concrete recommendations. Batch the ready human decisions. For each
explicitly approved conflict, pass `--resolve /exact/target=observed-sha256`, or
`=absent` for an approved unexpectedly missing target. This binds permission to the
observed scope and current proposal; it is not a receipt-enrollment switch. Do not
supply it merely because the human wants the profile. Reinspect after approval;
newly changed observations need fresh investigation. Retained differences keep
reconciliation incomplete; ask whether they should become the standard, without
silently publishing them or establishing permanent exceptions.

Prepare a complete temporary candidate config from the actual shared config,
editing only the thirteen owned paths to match machine/config.toml, less any pair
kept by `--preserve-model-settings`. Preserve comments,
formatting, and unrelated fields. Retired previously owned fields are removed only
after their prior receipt passes. The helper parses the candidate and proves its
owned values match the source and its unowned values match the actual config. It
rechecks the full original config immediately before replacement to avoid losing
concurrent unmanaged edits. Never copy the fragment over the shared config.

## Apply and verify

Repeat the canonical preparation command with `--apply` and the exact approved
`--resolve` arguments only after the supervising agent has resolved each reported
conflict. The helper prepares the complete candidate config and performs the native
model check itself, then reruns the all-target filesystem gate, verifies upstream
staging, prepares complete copies of changed packages, and rechecks observations
before and immediately at each mutation.

A declared target whose receipt scope, gate-verified live fingerprint and desired
fingerprint already agree is unchanged: the helper skips its preparation and
publication, leaving its content, file metadata and receipt entry untouched. A run
with no changed target and no config evidence to record leaves the receipt file
itself untouched. Every target still
passes the gate and its pre-write receipt, live-state and shared-config rechecks;
upstream and candidate-config validation still run. Changed or missing targets,
changed scopes, approved conflicts, retirement and release follow the paths below.
Preflight reports `Would publish` for each target the apply would publish or
re-receipt, including a scope or receipt change with identical content.

Whole files are replaced atomically. Directories are prepared off discovery on the
same filesystem, the exact verified old directory is removed, and the prepared
replacement is renamed into place. A brief absence is permitted; no live partial
copy or fallback across filesystems is permitted. Directory retirement removes only
the receipted scope. Unexpected ownership-kind changes or relocation of a retired
shared config require investigation rather than deleting a shared file.

On native Windows, publication preserves discretionary access restrictions and
checks owner, group, and mandatory integrity labels before replacement. Existing
files use the native replacement API; prepared directories receive the intended
parent inheritance and existing per-path restrictions. A permission mismatch,
locked file, or denied operation stops the run. Inspect any reported partial
publication or retained replacement before recovery; never relax permissions to
make reconciliation pass. Existing POSIX publication remains unchanged; Pi alone
adds mode-aware runtime and executable-launcher receipt scopes.

After each actual successful publication, the helper fingerprints the installed
result and atomically writes the existing narrow receipt. A failed write before
receipt publication fails closed on the next run. Printed writes are actual partial
progress, not a promise that the run completed. Inspect actual state after failures;
do not erase receipt evidence, enroll existing bytes, blindly retry, roll back
unrelated work, or build a recovery journal.

The receipt contains version 1 and entries with only target, scope, algorithm, and
fingerprint. The shared config entry may add `evidence`, holding its scope's sorted
fields other than the root pair and their projection fingerprint; entries without
it stay valid. Whole files hash exact bytes. Whole directories hash canonical sorted
relative file names and their byte hashes. Pi runtime directory fingerprints also
include POSIX file/directory modes; its launcher includes its POSIX mode. Scoped Pi
JSON hashes only declared scalar values and exact skill-path membership counts,
including absence. TOML hashes sorted dotted fields with
type and value or an absent marker; unrelated values never enter the fingerprint.
The narrow schedule seam consists of `cleanup_schedule_fingerprint`,
`cleanup_schedule_preflight`, and `cleanup_schedule_entry`. The schedule adapter
supplies its exact `automation:<id>`, `cron:<id>`, or `task-scheduler:<name>`
identity and only normalized owned
configuration. It reobserves immediately before mutation and creates an entry only
after observing its own successful write. Retirement removes its entry only after
observed authorized removal. The filesystem runner preserves schedule receipt
entries but does not observe, require, modify, or retire native schedules. The
managing agent resolves changed/missing schedules with the target adapter under
[CLEANUP-SCHEDULE.md](CLEANUP-SCHEDULE.md). No general external-object engine is
provided.

Finish by checking actual usability, including fresh-session/restart requirements.
Report written changes separately from verified capabilities, unresolved differences,
partial failures, and required human action. Clean only the staging and candidates
proven associated with this run and safe to remove. A local syntax check alone never
establishes successful use on each supported platform.

## Windows and WSL support handoff

The delivered implementation revision is
`b1fa4662a4794ab85f0c539924cd653cb275b52e` (PR #37). Its sequence includes
PRs #32/#34, #35, and #36. Reconciliation, WSL boundary, and scheduler evidence
is recorded with [#27](https://github.com/jdip/agent-team/issues/27),
[#28](https://github.com/jdip/agent-team/issues/28), and
[#29](https://github.com/jdip/agent-team/issues/29); [#31](https://github.com/jdip/agent-team/issues/31#issuecomment-5611628172)
records the owner confirmation.

Native Windows and WSL each reconciled all 51 declared targets using independent
homes, receipts, native tools, and checkouts; the WSL run left native Windows
state unchanged. Desktop scheduling preserved uncertain work. The Windows CLI
scheduler was created, updated, read back, run manually with exit 0, and retired.
WSL cron invoked the installed native Linux runner; its cron exit was not captured,
while the equivalent standalone run exited 0. Both preferred schedules are 09:00
local time and use the fixed stable source revision `1c304e6`. Only the desktop
automation remains installed for the Windows home; Task Scheduler is the
CLI-only alternative, not a second Windows schedule.

The operator reported no regressions on macOS or Linux after PR #37; this is a
compatibility confirmation, not a record of detailed per-command checks. Optional
Claude session usability was not verified. WSL runs remain skipped while its
distribution or daemon is stopped. Missed scheduled runs are
acceptable on Windows too; the owner removed delayed-run verification from
acceptance in #38. No catch-up behavior is promised.

For a future re-proof, focus on reconciliation update/no-op and conflict
preservation; skill/config discovery with valid receipt preservation; canonical
source and delivery; and preservation of existing desktop and cron schedules.
These are suggested checks, not retrospective command claims or a requirement to
rerun them now.
