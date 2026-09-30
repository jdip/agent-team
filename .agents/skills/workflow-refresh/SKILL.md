---
name: workflow-refresh
description: Refresh an orchestrator’s understanding of Agent Team skills and workflow from current repository sources, with commit provenance and session capability checks.
---

# Workflow Refresh

Use for Agent Team workflow orientation or when an orchestrator’s reference may be
stale. This repository-local skill generates a source index and routes the reader
to existing workflow owners. It does not select or execute repository work.

Read [the orchestration guide](../../../docs/workflows/orchestration.md) for the
repository retrieval path and capability distinctions. The target repository’s
current instructions govern any work the orchestrator subsequently dispatches.

## Refresh from source

1. Resolve the canonical `jdip/agent-team` repository and available read capability.
   Use the existing GitHub identity. An access denial is a reported limit, not
   permission to change credentials or bypass that denial. A cloud reader without
   shell access can follow the guide’s immutable repository links or ask an
   operator-authorized task with repository access to generate the reference.
2. On a host with an Agent Team checkout, preserve local work and fetch
   `origin test` without switching branches or merging. Use the existing Python
   3.11+ runtime and run this package’s helper:

   ```bash
   python3.13 .agents/skills/workflow-refresh/scripts/refresh.py --repository .
   ```

   Use the host’s established Python command when it differs. The helper resolves
   the live `test` head, requires that revision’s successful `validate` check,
   reads its committed blobs, retrieves separately pinned upstream metadata, and
   rechecks `test` before returning the on-demand Markdown snapshot on stdout.
   Missing Git objects require inspection and a fresh fetch; the helper performs
   no checkout, installation, publication, or local inventory read.
3. Read the returned snapshot. Report its commit and verification evidence,
   upstream metadata gaps, and any freshness limit. Keep it on demand or in
   task-approved private output; generated catalogs are not committed to Agent
   Team. `--candidate <full-SHA>` is only for explicit local implementation
   validation and labels test delivery/freshness as unverified.
4. Choose relevant entries by their source descriptions/triggers. Read the full
   `SKILL.md`, relevant companions, applicable `AGENTS.md`, and the current
   runbook at the same commit. Preserve declared manual invocation settings and
   the owning skill’s authorization and completion boundaries. The README skill
   guide supplies additional usage context; `whats-next` owns ongoing coordination.
5. Compare source guidance with the executing session’s actual catalog and tools.
   Inspect relevant repository-local skill files even when the session omitted
   them. A source file can be read as guidance; invoking a tool or script requires
   that host’s actual capability and authorization. Keep installed-source
   comparisons, host details, private memories and transcripts in task context.

Refresh is complete when the reader has an exact source revision, source-linked
skill/workflow entries, disclosed unavailable metadata, and a concrete capability
assessment for the proposed next action. A successful index is not evidence of
installation agreement or successful execution in the cloud orchestrator.
