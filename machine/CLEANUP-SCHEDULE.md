# Cleanup schedule installation and reconciliation

Use one roughly daily target-appropriate schedule under an authorized installation
or reconciliation request. The shared cleanup-task-artifacts skill is the policy;
no scheduler expands cleanup authority. Keep its source checkout stable and
outside task cleanup. Select one verified source revision; do not fetch or update
it during scheduled sweeps. A native job may start in a saved stable project while
reading the shared policy from a separate stable source checkout.

## Shared evidence

Use Python 3.11+ and cleanup_schedule.py. The existing receipt stores only the exact
schedule identity, dedicated cleanup-schedule scope, SHA-256 algorithm, and hash of
normalized owned configuration. Preserve all unrelated receipt entries. First
inspect actual schedule inventory and receipt evidence. No existing schedule files
or cron entry plus no prior receipt permits first creation. Existing unproven,
modified, or unexpectedly missing state requires supervised investigation, meaningful
differences, and a concrete decision; never enroll old bytes merely because they
match desired settings.

The schedule helper preflights all other receipted file scopes before operations.
For a full Machine Reconciliation, also prepare and inspect every declared file,
package, model, and retirement scope before writes, as RECONCILE.md requires. Batch
all ready conflicts. An explicit `--resolve target=observed-hash` can carry an
approved file conflict through a schedule operation while preserving its old receipt;
the subsequent fresh file publication must still resolve that conflict. An approval
of the end state alone does not authorize those switches.

The filesystem reconciler preserves cleanup-schedule receipt entries but does not
observe, require, update, or retire native schedules. It never treats
automation/cron identities as paths. Schedule-only installation does not claim that
the rest of the Machine Profile is reconciled. After a failure inspect actual
API/crontab and receipt state; successful writes can precede receipt publication.
There is no recovery journal or rollback.

## macOS and Windows desktop

Use the supported Codex automation tool for creation, updates, views, and deletion.
Inspect the supported automation configuration inventory and existing receipt first;
reuse the existing identity rather than create duplicates. The local automation TOML
is an observation surface, never a mutation interface. Do not write app storage.

Use a native standalone project cleanup job from a stable saved project, roughly
daily (9 a.m. local is the default preference). Select the approved primary model
and effort supported on that host. Its prompt explicitly loads the stable shared
cleanup skill, obtains known roots through supported project inventory, calls positive
adoption discovery, preserves attached/active/shared/uncertain resources, and permits
automatic archival only with complete evidence and a last turn more than seven days
old. Notify only meaningful cleanup, failures, or required action; no-op runs stay
quiet. Do not schedule Machine Reconciliation or software/source updates.

Before updating an existing native job, use:

```bash
python3 machine/cleanup_schedule.py inspect --codex-home /actual/codex-home \
  --identity automation:actual-id
```

The normalized observed fields are kind, name, prompt, status, rrule, model,
reasoning_effort, execution_environment, target, and cwds. Identity is separate.
RRULE clause ordering is normalized. Native created/updated timestamps and unrelated
notification preferences are excluded. The adapter requires the observed v1 cron
schema; a changed schema stops for inspection rather than inventing a mapping.

Retain the pre-operation receipt hash. Recheck current native configuration immediately
before the supported API write, preserving every unrelated field and schedule. For
a conflict, `inspect --approve observed-hash` is only permitted after the human's
specific decision. After a successful API write, view the same identity and read
back its saved configuration. Verify every submitted owned value and capture that
observed configuration fingerprint. Then record the actual operation:

```bash
python3 machine/cleanup_schedule.py record-desktop --codex-home /actual/codex-home \
  --identity automation:actual-id --receipt-hash pre-operation-hash-or-absent \
  --observed-hash observed-after-write-hash --observed-write
```

This records only an actual authorized API creation/update, not existing unproven
state. The adapter verifies the captured post-write observation and unchanged receipt.
For retirement first preflight the prior receipt and native state, perform the
supported deletion, verify actual absence, then use the same recording command with
`--removed --observed-hash absent`. Missing prior ownership evidence cannot authorize
retirement. Re-run inspect after publication to verify the new receipt matches.

Actual evidence on the development Mac: native creation returned a stable automation
id, supported view succeeded, and the saved v1 configuration matched the requested
project/model/prompt/schedule. A normalized receipt was recorded after that observed
creation and read back successfully. This is configuration evidence, not a claim
that a scheduled wake already ran or that headless cron was exercised.

## Headless Linux and WSL

Use the actual target user's crontab and Codex executable, with working authentication
and a stable source checkout. Inspect `crontab -l`; lack of permission or an unexpected
failure is not an empty crontab. The helper recognizes only its exact dedicated
`# agent-team-cleanup` entry and stops on duplicate managed entries. All other lines
remain byte-for-byte unchanged. It owns no environment-wide crontab configuration.

```bash
python3 machine/cleanup_schedule.py install-cron --codex-home /actual/codex-home \
  --stable-checkout /actual/stable-source --codex /actual/bin/codex --hour 9 --minute 45
```

Add repeatable `--project-root /actual/project` arguments when supplying explicit
roots. For supervised execution verification, `--output-last-message` can retain
Codex's final response in the private `cleanup-last-message.txt` file under the target
Codex home's `.agent-team` directory. This is ordinary optional output, not receipt
or lifecycle evidence. Do not publish its contents without privacy review.

Hour and minute use the target's local cron timezone; defaults are 09:00. The
supported Codex launcher may be a symlink within the Linux filesystem. The helper
validates its resolved executable as well as the supplied launcher.

For WSL, use Linux-native tools, a Linux-filesystem source checkout, and the
distribution's independent Codex home and authentication. Mounted Windows paths
are not writable scheduler targets. Cron runs only while the distribution and
daemon are running; it skips runs missed while stopped. Do not install a Windows
startup job or a catch-up wrapper. Verify the daemon and target timezone on the
actual distribution; a service alone does not keep WSL running.

It preflights receipt and exact current entry, builds the dedicated line invoking
`codex exec -C` with the shared cleanup instructions and command-local resolved
CODEX_HOME/PATH (never global crontab environment edits), rechecks the complete current
crontab to avoid dropping concurrent unrelated edits, writes through `crontab -`,
reads back the exact result, and only then updates the narrow receipt. Pass
`--approve observed-hash` (or absent) only for a specifically approved conflict.
Use retire-cron for an authorized receipt-proven removal. No cron job is installed
on desktop macOS by this helper.

The headless prompt uses only supported project inventory or supplied roots. If
neither is available, or exact task timestamps/completion/attachment cannot be
established, skip affected discovery, archival, and removal. Do not scrape internal
Codex stores. Verify actual Codex startup, authentication, the real cron entry, and
safe sweep behavior on the supported Linux target. A local syntax check is not
headless execution evidence.

## Windows CLI-only

Use the native Windows Task Scheduler adapter when desktop automation is not the
selected scheduler for this Codex home. Inspect the home's receipt and desktop
automation inventory first. A receipted schedule in another scheduler must be
retired through its owner and verified absent before installing this one. Separate
Windows and WSL homes may each have their own schedule.

The adapter derives an exact root task name from the resolved Codex home. It owns
only that task, with its normalized principal, trigger, settings, and action.
An existing unreceipted or changed task requires the same observed-conflict
investigation as other schedule state. Preserve unrelated tasks and task folders.

The task uses the current user's interactive token and least privilege, with no
stored password or machine wake. It runs daily in the target's local timezone,
allows native delayed execution when eligible, and suppresses overlapping runs.
The user must be logged in. A delayed trigger is not a guarantee that every missed
run will be replayed. Verify actual trigger behavior on the target separately from
a successful on-demand run.

Its action invokes the existing Python helper and native Codex executable from a
stable native checkout, setting CODEX_HOME only for that process. Use explicit
project roots for headless cleanup when supported project inventory is unavailable.
Missing task lifecycle evidence still preserves affected checkouts and tasks.

Using the actual native Python executable in `$python`, run from the selected
source checkout (replace the illustrative paths with verified local paths):

```powershell
& $python machine/cleanup_schedule.py inspect --codex-home 'C:/actual/codex-home'
& $python machine/cleanup_schedule.py install-windows --codex-home 'C:/actual/codex-home' `
  --stable-checkout 'C:/actual/stable-source' --codex 'C:/actual/bin/codex.exe' `
  --project-root 'C:/actual/project' --hour 9 --minute 0
& $python machine/cleanup_schedule.py retire-windows --codex-home 'C:/actual/codex-home'
```

On native Windows, these commands infer the exact Task Scheduler identity from the
home when `--identity` is omitted. Desktop operations still pass their explicit
`automation:<id>`. Linux's default remains the dedicated cron identity. The optional
private `--output-last-message` described above also applies to Windows CLI jobs.

Installation rechecks the exact task and receipt immediately before the native
write, reads back the task definition, and records only the observed successful
result. Updates follow the same checks. Retirement requires receipt ownership,
matching observed configuration, and a non-running task; it verifies deletion
before removing the receipt. Investigate partial effects rather than retrying or
switching schedulers after an ambiguous result.
