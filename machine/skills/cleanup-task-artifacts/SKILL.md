---
name: cleanup-task-artifacts
description: Clean verified task artifacts after delivery or during an authorized daily sweep, preserving active and uncertain work.
---

# Cleanup Task Artifacts

Use for authorized delivery cleanup or the explicitly installed daily cleanup sweep.
Cleanup does not authorize Machine Reconciliation, updates, unrelated repair,
publication, or broader deletion. Read the relevant repository's AGENTS.md and
local delivery/artifact guidance. Protect the current task's own environment.

## Discover participating repositories

For a daily sweep, obtain exact known project roots from the host's supported project
inventory, or use roots explicitly supplied by the supervising agent. On Codex, use
the supported Codex project inventory. Pass those roots to this package's
`scripts/discover.py` with Python 3.9+ (resolve the script relative to this skill).
It parses only the root AGENTS.md Repository Standard section and verifies the exact
Agent Team source and adopted commit through gh. It checks each distinct revision
once and reports eligible roots or skip reasons. Never replace this discovery procedure
with a grep for arbitrary hashes, a filesystem sweep, internal app-storage scraping,
or a new registry. Unavailable inventory/source evidence means skip, not inferred
participation. Direct delivery cleanup may use the already verified current
task/repository scope before the repository's first adoption.

## Establish what can be removed

Eligibility only establishes participation. For every candidate establish BOTH
association with the completed task and safe removal, using actual task, Git,
container, process, or artifact evidence. Names and age can suggest candidates but
never prove ownership or safety. Inspect exact resource identifiers and local
runbook-defined artifacts; clean all qualifying task resources, not just branches.

Preserve active work, shared resources, uncommitted/unpublished changes, needed
evidence, uncertain artifacts, and the sweep's stable source checkout. Verify a
branch's commits are delivered before deleting it. Inspect dirty state and current
users before considering a worktree. Never blanket-prune branches, worktrees,
containers, or logs. Reinspect the exact resource immediately before mutation.

Never remove a checkout still backing a task. Use supported host lifecycle
operations for app-owned worktrees. On Codex, use Handoff only when supported,
appropriate, and safe for both checkouts; the calling task cannot hand itself off,
and shell cd does not change task attachment. Do not create helper tasks or edit
internal app storage to evade this limitation. On a host without supported lifecycle
evidence or handling, retain the checkout. Report actual cleanup separately from
delivery completion.

## Conservative automatic archival

Automatic archival additionally requires positively verified completion, unpinned
status, no active execution, no pending input/approval or unresolved work, and MORE
THAN SEVEN DAYS since the task's exact observed last-turn timestamp. No timestamp
or unclear completion means skip. Do not use file modification time, task title,
creation date, or an invented timestamp as a substitute. Do not relax the threshold.

Use supported task listing/reading to establish evidence, recheck current state,
then use supported archival. Do not assume that archival physically removed its
checkout; observe and report actual lifecycle results. Preserve any local state
that archival/removal could endanger. Headless hosts without supported task evidence
skip affected archival and checkout removal.

## Finish

Remove only the proven-safe exact resources under existing authorization. Investigate
unexpected failures before further action; do not blindly retry destructive steps
or build a cleanup journal/state machine. Batch genuine human decisions after
finishing independent cleanup. Report meaningful cleanup, failures, and required
action; remain quiet on unchanged/no-op scheduled runs. No notifications about an
unchanged skipped set are needed on every run. Never mark unresolved work complete.
