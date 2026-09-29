---
name: machine-reconciliation
description: Reconcile this machine's Codex and Claude Code configuration with the Agent Team Machine Profile.
# agent-team:host=claude
disable-model-invocation: true
# agent-team:end
---

# Machine Reconciliation

Run this only on the user's explicit request. Work from the Agent Team checkout the
user names, or the current repository when it is `jdip/agent-team`; on a new machine
the user points to this file inside their checkout. Read that checkout's
`machine/PROFILE.md` and the target's current instructions first. Python 3.11+, Git
and gh are required. The helpers are Tooling, verified by actual operations; no
machine simulator or coverage suite belongs to this workflow.

## 1. Prepare and preflight

From the checkout, run the single preparation command:

```bash
python3 machine/prepare_reconciliation.py --repository /actual/agent-team
```

On native Windows or WSL, follow [Windows and WSL](references/windows-wsl.md) first.
The command selects the freshest published revision of the checkout's tracked branch
in a temporary detached worktree, discovers the Codex home, skill roots and any
Claude Code configuration root and Claude desktop data directory, verifies declared
models, stages pinned upstream packages, renders every host's sources, and runs the
all-target read-only gate. It lists each planned publication and retirement with
owned field names and makes no managed writes. It stops on unpublished or diverged
commits or unavailable capabilities; resolve the source authority rather than
bypassing that evidence. [Helper behavior](references/helper.md) owns the exact
discovery, preflight and ownership rules.

Done when the command reports "prepared and preflighted" or names every blocking
conflict.

## 2. Resolve conflicts

Investigate every reported conflict before asking. Show meaningful differences, what
replacement would lose, and a concrete recommendation, then batch the ready human
decisions. For each explicitly approved conflict, pass
`--resolve /exact/target=observed-sha256` (or `=absent` for an approved missing
target). It binds permission to the observed scope; it is never a receipt-enrollment
switch or a way to publish the profile over unexplained state. First management of
an existing shared settings file is an ordinary supervised conflict. Reinspect after
approval; retained differences keep reconciliation incomplete, and whether they
should become the standard is a separate question.

Done when every conflict has an approved resolution or is reported as retained.

## 3. Desktop app settings

<!-- agent-team:host=claude -->
When this session exposes the Code tab's settings tool, set `branch_prefix` to
`agent` through it now, with the user's approval, and rerun preparation so the helper
sees the matching value. Otherwise the helper writes the Claude desktop app's
Code-tab branch prefix during apply; when it reports changed preferences, ask the user
to restart the Claude desktop app, because the running app keeps its cached
preferences until restart and a later run reports drift if the app saved over them.

The Codex app's branch prefix belongs to the Codex app. Read `git-branch-prefix` in the
Codex home's `.codex-global-state.json` without editing it. Report it as pending
unless it reads `agent/`, and ask the user to set Settings, Git, Branch prefix once or
to run this skill from a Codex app task.
<!-- agent-team:end -->
<!-- agent-team:host=codex -->
In the Codex desktop app, set this app's Git branch prefix to `agent/` through the
app's own settings, never by editing its state files, and read it back. From the CLI,
report that setting as pending when the desktop app is installed on this machine
(its `.codex-global-state.json` exists in the Codex home) and as not applicable
otherwise.

The helper owns the Claude desktop app's Code-tab branch prefix; when apply reports
changed preferences, ask the user to restart the Claude desktop app.
<!-- agent-team:end -->

Done when each installed desktop app's branch prefix is set in-app, left to the
helper, or reported as pending.

## 4. Apply

Rerun the same command with `--apply` and the exact approved `--resolve` arguments.
The helper rechecks every observation, publishes atomically, writes the narrow
receipt, and verifies fresh Codex skill discovery. Printed writes are actual partial
progress: after a failure inspect actual state before recovery, and never erase
receipt evidence, enroll existing bytes, blindly retry, or roll back unrelated work.

Done when the helper reports "reconciled and verified" or you have inspected and
reported a partial failure.

## 5. Verify and report

Check actual usability in fresh sessions: rendered rules, roster and model
assignments, skill discovery, and any restart the host needs before loaded agents or
rules refresh. Report written changes separately from verified capabilities,
unresolved differences, partial failures and required human action. Remove only the
staging and candidates proven associated with this run. A syntax check alone never
establishes successful use on a platform. Cleanup schedules are maintained
separately through the checkout's `machine/CLEANUP-SCHEDULE.md`.
