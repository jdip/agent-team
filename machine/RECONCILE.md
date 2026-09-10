# Machine Reconciliation

Use this procedure only for an explicit reconciliation request. Python 3.11+ and
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

It resolves the checkout's tracked branch and freshest published remote revision,
uses a temporary detached worktree, discovers the actual Codex home and user-skill
destinations through the native app-server and existing receipt, and checks the
target operating system and every declared model/effort. When `claude` is available,
it runs only a bounded `claude --version` probe and resolves the separate Claude
configuration root from `CLAUDE_CONFIG_DIR` or its default. It stages the upstream
packages with the installed skill-installer at the declared pin, verifies their Git
blobs, builds the complete formatting-preserving shared-config candidate, and
invokes the existing all-target read-only gate. It makes no managed writes. The
command removes complete temporary preparation after a successful preflight and
retains failed acquisition staging for inspection. Supply an explicit
`--skills-root` (and, when distinct, `--upstream-root`) only when native discovery
and receipt evidence cannot establish a single destination.

Candidate preparation acquires [tomlkit](https://pypi.org/project/tomlkit/) at the
exact pin in [requirements.txt](requirements.txt), consumed by the existing Python
`pip` or `uv` installer into that run's staging directory with no transitive
installation. Dependabot can propose changes to this same manifest; the installed
version is checked against it. Preparation never installs a global dependency.

The command stops if the current branch has unpublished commits, has diverged from
its tracked remote, or a required target capability/source is unavailable. Publish
or resolve the source authority first; do not bypass that evidence with a local
checkout.

After specific preflight conflicts have been resolved, run the same command with
`--apply` and each exact approved `--resolve target=observed-sha256` argument. It
prepares the candidate config, verifies declared model/effort availability, reruns
the filesystem gate, publishes, and verifies fresh Codex skill discovery. It manages
only the Machine Profile's files, configuration, and skill directories. A successful
Claude filesystem publication is not Claude session usability; record that evidence
through the separate host verification workflow. The managing agent maintains cleanup
schedules separately through the native tools and `cleanup_schedule.py`.

## Preparation details

Resolve the repository's current branch and its remote. Fetch that branch,
preserving dirty work. Select and report one concrete freshest revision. If branch
identity, detached state, divergence, or unpublished work leaves intent unclear,
resolve that concrete source question. Use an isolated clean checkout of the chosen
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
`--repo mattpocock/skills`, PROFILE.md's exact `--ref`, all declared `--path`
values, and `--dest` pointing to that empty staging directory. Do not implement an
alternate downloader. A failed acquisition leaves live skills unchanged; inspect
partial staging before retrying. The helper checks every staged relative file and
Git blob against the pinned upstream tree, including companion files.

The preparation command passes its resolved paths to the read-only gate; agents do
not assemble an alternate preparation command.

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
editing only the nine owned paths to match machine/config.toml. Preserve comments,
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
staging, prepares complete copied packages, and rechecks observations before and
immediately at each mutation.

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
make reconciliation pass. POSIX file modes and publication remain unchanged.

After each actual successful publication, the helper fingerprints the installed
result and atomically writes the existing narrow receipt. A failed write before
receipt publication fails closed on the next run. Printed writes are actual partial
progress, not a promise that the run completed. Inspect actual state after failures;
do not erase receipt evidence, enroll existing bytes, blindly retry, roll back
unrelated work, or build a recovery journal.

The receipt contains version 1 and entries with only target, scope, algorithm, and
fingerprint. Whole files hash exact bytes. Whole directories hash canonical sorted
relative file names and their byte hashes. TOML hashes sorted dotted fields with
type and value or an absent marker; unrelated values never enter the fingerprint.
The narrow schedule seam consists of `cleanup_schedule_fingerprint`,
`cleanup_schedule_preflight`, and `cleanup_schedule_entry`. The schedule adapter
supplies its exact `automation:<id>` or `cron:<id>` identity and only normalized owned
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
