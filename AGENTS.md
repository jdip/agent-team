# Agent Team

Agent Team maintains portable Codex machine configuration and Repository Standard
sources. Read [standard/README.md](standard/README.md) for the standard and
[machine/PROFILE.md](machine/PROFILE.md) for the exact Machine Profile ownership.
Machine reconciliation follows [machine/RECONCILE.md](machine/RECONCILE.md).

The canonical GitHub repository is public and is intended to remain public.
Changing visibility or licensing requires explicit owner approval.

Before repository or GitHub writes, follow the
[public-work policy](SECURITY.md#public-repository-work), including outgoing
metadata, logs and attachments.

Work is tracked in GitHub Issues; follow [tracker guidance](docs/agents/issue-tracker.md).
Read [domain guidance](docs/agents/domain.md) before exploring domain terminology.
Follow [development guidance](docs/development.md) for verification.

Classify this repository's machine/repository maintenance helpers as Tooling.
Validate through actual use and the small source syntax check; do not create
coverage suites, fake machines, or release state machinery. Preserve credentials,
unrelated machine state, local work, and checkouts still backing Codex tasks.

## Languages and environments

Tooling logic uses Python with the existing Python runtime. Bash is accepted for
canonical shell entry points and existing shell helpers; prefer Python for new
logic. Keep this toolchain cohesive. Adding another language, runtime, build/
package toolchain, or execution/deployment environment requires explicit user
authorization, including JavaScript/Node helpers. Application, CLI product, and server stacks are not established here;
selecting one requires explicit authorization. See docs/development.md for runtime
requirements. This policy does not authorize rewriting existing tools.

## Checkouts and delivery

Keep the primary local checkout on `test`, refreshed from `origin/test` by
fast-forward only when clean. Reserve the `test` branch for that checkout; never
check it out in a linked worktree. Make all changes on `codex/` feature branches
in separate worktrees based on fresh `origin/test`. Preserve existing local work
before switching or updating a checkout. Detached revision worktrees remain valid
for the canonical scripts' verification.

Deliver feature changes with the global `pr-to-test` skill and the local
[PR-to-test runbook](docs/workflows/pr-to-test.md), invoking
`scripts/pr-to-test.sh` through checks, merge, and verified test delivery.
Use this path even for documentation or small fixes; do not commit or push changes
directly to `test` or bypass branch protections.

Promote only on a separate explicit user request, using the global
`promote-to-main` skill and local [promotion runbook](docs/workflows/promote-to-main.md).
Invoke `scripts/promote-to-main.sh` from the clean primary `test` checkout and
complete its verification and main-to-test synchronization. If either canonical
script is missing, check for duplicates and file an implementation issue in this
repository; report the delivery blocker instead of inventing an alternate flow.

## Repository Standard

- Source: https://github.com/jdip/agent-team
- Revision: a8b363e79cf1001b42c3e79317348e27b26b3eb3
