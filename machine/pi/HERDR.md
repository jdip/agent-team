# Pi-owned Herdr coordination

This guide applies when Pi coordinates workers through Herdr, including Codex and
Claude workers Pi launches. The Pi parent owns the task and lifecycle. Ordinary
Codex/Claude tasks retain their host's delegation and cleanup rules.

## Establish ownership and capacity

Load the installed `herdr` skill and follow its environment and targeting checks.
Verify Pi has `HERDR_ENV=1` and proven pane identity in its execution-side
environment before mutations; apply the shared Host capabilities checks to Codex
workers too. If routing context is unavailable, preserve affected state, report
the capability limit and continue independent work. Use the current
session's proven workspace/tab/pane identities. Another session's agents are not
available merely because they appear in an inventory.

Allow at most four agents total for this Pi task: Pi plus three workers, counting
running, starting and retained workers. Before creating one, inspect the owned
workers and reuse a suitable idle worker when its repository, permissions and
assignment fit. Count a timed-out or unconfirmed worker until its state is known.
Pi alone decomposes work, assigns workers and reconciles their results. Workers
return follow-up needs to Pi.

Keep exact returned session, workspace, pane and agent identities with their
assignment and ownership evidence in the existing parent task context. Do not add
a registry. Native `idle` or `done` signals readiness, not accepted correctness or
process exit. Recheck identity and state before prompts, replacement or teardown.

## Assign leaf workers

Send a complete bounded packet: repository and revision/dirty scope; role;
operator answers and applicable instructions/skills; owned paths or read-only
limits; requested model/effort and actual permission controls; acceptance criteria;
expected evidence; parent identity and teardown owner. Include this leaf rule in
every initial assignment and reuse prompt:

> Execute this assignment directly as a leaf worker owned by the Pi parent. Do
> not create, spawn or delegate to any agent using native tools, Herdr, shell
> commands or another service. Return decomposition, extra-review and follow-up
> needs to Pi. Keep within the assigned repository, permissions and scope.

At every worker start, inspect the installed CLI's supported controls and pass
native delegation restrictions for that invocation through Herdr's `--`:

- Codex: `-c agents.enabled=false` on every worker CLI invocation. Use the
  managed `codex` function when launching from Bash/Zsh; keep explicit
  `--no-daemon` when invoking the executable directly through Herdr's `--`.
  The daemon flag and native delegation restriction serve separate purposes;
  apply the shared Host capabilities context checks on starts, resumes and reuse.
- Claude Code: `--disallowedTools Agent Task` when supported; `Agent` is the
  current tool name and `Task` covers older versions. Verify the installed
  version's accepted spelling before launching.

Keep native delegation restrictions in every fresh worker invocation and leaf
instructions in every reuse assignment; do not change either host's global
configuration. If the required restriction is unavailable, preserve the assignment
and report that worker route unavailable. Workers with shell access still have a
cooperative instruction boundary against launching another CLI or Herdr agent;
these controls disable native delegation, not arbitrary process creation.

## Independent work and review

Use bounded workers for independent investigation, planning and implementation
when they can run alongside useful Pi work. Give a planner the actual operator
answers; Pi owns live dialogue, approval, tracker writes and integration. A worker
implements only its assigned paths. Serialize Git mutations in shared checkouts.
Use existing host model/effort choices where applicable and verify requested
support before dispatch; preserve unavailable assignments instead of silently
substituting. Do not install another CLI or arrange account/API billing for a
worker without separate authority.

For `code-review`, Pi dispatches one independent leaf reviewer through Herdr after
preparing the skill's immutable comparison and full Standards/Spec packet. Supply
the skill and smell baseline, repository instructions, approved requirements,
verification and its limits. Use the selected CLI's verified repository-read-only
controls, no external connectors and the leaf restrictions above. Report actual
permissions; a read-only assignment alone does not establish enforced isolation.
The reviewer returns findings directly to Pi and never selects another reviewer.
Unavailable independent dispatch leaves review pending. Pi resolves findings and
obtains review of affected conclusions after fixes before delivery.

## Receive results and finish

Use Herdr's bounded completion-aware wait/prompt operations. On timeout, inspect
the exact owned worker and read its available output before deciding to continue,
interrupt or exit it through its CLI controls. Herdr supports
`herdr agent send-keys <owned-name> ctrl+c`; inspect the result because an
interrupt need not exit the process. A timeout is not evidence of failed delivery
or process exit; resolve the original worker before launching its replacement.

At completed validation, substantial phase end, failure/waiting, delivery and
final handoff, inspect every worker owned by this Pi task. Capture needed output
and accept or reject its result. Reuse an idle worker needed by the next immediate
assignment within the same task; otherwise exit the exact owned agent through
its supported CLI controls, then close its owned pane with `herdr pane close`. Verify the worker
process is absent, the pane is closed and no child agent remains before releasing
its capacity. A successful command alone is insufficient teardown evidence.

Preserve Pi's parent pane, user panes, shared servers/sessions, transcripts,
credentials, and worktrees still backing tasks. Apply `cleanup-task-artifacts` to
other task resources under their existing ownership and retention rules. Missing
identity or safety evidence preserves the resource. If a worker must stay live,
record its exact identity, reason, capacity cost and stop/restart procedure in the
parent task context and report it at handoff. Do not close the overall task while
required worker teardown or verification remains unresolved.
