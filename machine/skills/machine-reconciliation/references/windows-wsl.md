# Windows and WSL

Reference for the machine-reconciliation skill on native Windows and WSL 2.

## Preparation

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

## Publication

On native Windows, publication preserves discretionary access restrictions and
checks owner, group, and mandatory integrity labels before replacement. Existing
files use the native replacement API; prepared directories receive the intended
parent inheritance and existing per-path restrictions. A permission mismatch,
locked file, or denied operation stops the run. Inspect any reported partial
publication or retained replacement before recovery; never relax permissions to
make reconciliation pass. POSIX file modes and publication remain unchanged.

## Delivered support handoff

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
