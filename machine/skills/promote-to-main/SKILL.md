---
name: promote-to-main
description: Promote verified test work through the repository’s canonical main promotion and synchronization workflow when explicitly requested.
---

# Promote to Main

Before any GitHub write, follow the target repository's applicable publication
policy for outgoing source, metadata and evidence. Inspect approved commit identity
and verify platform-created merge metadata after delivery; report any mismatch.

Require the human's separate promotion request. Implementation, adoption, upgrade,
or successful test delivery alone does not authorize promotion. Preserve the
request's repository, environment, and intended test revision.

Read AGENTS.md, `docs/workflows/promote-to-main.md`, and relevant test-delivery and
review evidence. Use `scripts/promote-to-main.sh` with that runbook's arguments.
Investigate absent or contradictory local guidance; do not invent a release process.
Prepare the intended clean checkout while preserving unrelated work. Review any
submitted changes not covered by sufficient completed review evidence.

Follow actual gates and effects through verification, including deployment,
signing, processing, and user-visible behavior only where the local runbook
requires them. Use merge commits for test-to-main and required main-to-test sync.
Check the intended revisions and investigate drift before including changed scope.

Versioning uses each applicable task PR once in merge order: major/minor/patch/none,
with normal resets. Sync contributes none; promotion wrappers do not recount task
changes. All-none retains the version without a new tag. Resolve routine metadata
from evidence; otherwise report uncertainty without fabricating a version, moving
a tag, or turning bookkeeping into an artificial gate. A real artifact pipeline's
version prerequisite remains a genuine prerequisite defined locally.

Inspect actual partial effects after failures before recovering. Do not blindly
replay publication or treat script launch as completion. Continue independent
work and batch ready intent-dependent decisions with concrete recommendations.
Honor external approval/processing gates and report them pending until satisfied.

After the locally defined promotion and synchronization results are verified,
finish tracker bookkeeping and use `cleanup-task-artifacts` plus local guidance
when available. Its absence does not waive evidence-based cleanup: remove only
associated resources proven safe, retain attached/shared/uncertain checkouts and
unpublished work, and use supported Codex lifecycle handling. Report verified
results, exact tags actually published, partial failures, and retained resources.
