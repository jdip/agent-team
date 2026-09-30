# Retrieve current Agent Team workflow guidance

An orchestrator can start from this public repository without inheriting a local
Codex installation. Use [workflow-refresh](../../.agents/skills/workflow-refresh/SKILL.md)
when orienting to Agent Team or refreshing a stale workflow reference. Use
[whats-next](../../machine/skills/whats-next/SKILL.md) to advance an authorized
outcome in its owning repository.

## Resolve one current source

The agreed workflow baseline is the latest verified `test` revision. Resolve
`jdip/agent-team`’s `test` head to a full commit SHA and inspect its current
`validate` check. A failed, pending or unavailable check leaves verification
unresolved; a cached checkout or a recent timestamp is insufficient. The refresh
helper performs that lookup, checks the gate and detects branch movement during
its read. Its snapshot records the commit, observation time, check link and
separately reviewed upstream pin.

On a host with the existing Git/gh/Python tools and repository access, preserve
local changes, fetch `origin test`, and run the helper shown in the skill. Read
the output before using it. Repeat before a new orchestration decision or after
a relevant workflow change; compare commits rather than treating a fixed age as
proof of freshness. Generated snapshots remain on demand.

For a cloud session with repository reading but no shell, begin at
[this guide on test](https://github.com/jdip/agent-team/blob/test/docs/workflows/orchestration.md).
Resolve the current branch revision through the repository capability actually
available in that session, then retrieve files with that exact SHA in place of
`test`. For example:

```text
https://github.com/jdip/agent-team/blob/<full-SHA>/README.md
https://raw.githubusercontent.com/jdip/agent-team/<full-SHA>/machine/skills/whats-next/SKILL.md
```

Follow relative links within that revision; retain explicit upstream pins. Read
the root `AGENTS.md`, `SECURITY.md`, README and relevant path instructions first.
The [Machine Profile](../../machine/PROFILE.md) owns managed package identities
and upstream sources. Enumerate `.agents/skills/**/SKILL.md` separately for
repository-local skills. Read each relevant skill’s exact name, description,
invocation metadata and companions rather than relying on a remembered catalog.

If the cloud reader cannot establish revision or verification evidence, report
that specific limit. An operator-authorized task on a connected host with verified
repository access can return the public reference and evidence. Preserve the
operator’s selected identity and route; an access denial does not authorize a
different identity, credential installation or permission change.

## Follow the existing owners

The [implementation workflow](implementation.md) owns the phase connections.
The [README skill guide](../../README.md#skill-guide) owns concise use examples.
Load the relevant owner’s full instructions at the resolved revision:

| Current need | Owner and source |
| --- | --- |
| Orient and choose authorized work | [whats-next](../../machine/skills/whats-next/SKILL.md) |
| Establish or resume design | [Wayfinder](../../machine/skills/wayfinder/SKILL.md), then its grilling/selection/frontier instructions |
| Turn resolved design into executable work | [to-spec](../../machine/skills/to-spec/SKILL.md) and [to-tickets](../../machine/skills/to-tickets/SKILL.md) |
| Select and execute approved work | [set-backlog](../../machine/skills/set-backlog/SKILL.md), [next-issue](../../machine/skills/next-issue/SKILL.md), and [selection scope/handoff](../../machine/skills/set-map/SELECTIONS.md) |
| Review and verify the change | [code-review](../../machine/skills/code-review/SKILL.md) and the target’s development guidance; Agent Team uses [scripts/check.sh](../../scripts/check.sh) |
| Deliver to test | [pr-to-test](../../machine/skills/pr-to-test/SKILL.md), the target runbook and canonical script; Agent Team uses [this runbook](pr-to-test.md) and [scripts/pr-to-test.sh](../../scripts/pr-to-test.sh) |
| Assess maintenance or alignment | [whats-next’s maintenance branch](../../machine/skills/whats-next/maintenance.md), then the selected specialist |
| Release task resources at a phase boundary | [cleanup-task-artifacts](../../machine/skills/cleanup-task-artifacts/SKILL.md) |

These pointers retain each owner’s approval and completion rules. Main promotion,
Machine Reconciliation and scheduling need their separately required requests.
Another repository’s instructions and real runtime gates govern work there;
Agent Team’s source index does not replace them.

## Establish actual capability

Keep these evidence types distinct:

| Evidence | What it establishes |
| --- | --- |
| Agent Team package at a commit | Maintained instructions and helpers available to retrieve |
| Machine Profile identity and upstream pin | Intended managed inventory and provenance |
| Installed files compared with source | Agreement on the inspected host only |
| Current session skill catalog | Skills exposed for discovery in that session |
| Callable tools and observed access | Operations the executing session can actually perform within its authorization |

A local source, installation or catalog entry does not transfer tools, credentials
or filesystem access into a dot’s cloud session. Repository-local instructions
may be readable even when absent from a runtime catalog. Preserve manual-only
upstream invocation and skill-to-skill chaining declared by their owners.

Official [skill documentation](https://learn.chatgpt.com/docs/build-skills)
describes repository skill discovery, and [dot documentation](https://learn.chatgpt.com/docs/dots)
describes connected-computer tasks and configured cloud environments. Those
product capabilities still require current session evidence. Keep private host
inventories, local memories and task transcripts outside public reference output.
