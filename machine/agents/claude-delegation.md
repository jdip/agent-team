# Claude planning and implementation from Codex

The Codex primary uses this route for `planner` and `worker` assignments. Prefer
`claude-opus-5-5` at `high`; the corresponding native role uses
`gpt-6.1-sol` at `high` when this route is unavailable. Retain `pln_<purpose>` /
`🗺️ PLN` and `wrk_<purpose>` / `🛠️ WRK` identities. Claude is an external CLI,
not a Codex model selector. Assigned delegates execute directly.

## Establish availability

For each assignment, resolve `claude` on the executing host and inspect its version,
supported options and sanitized `claude auth status`. Establish an existing Claude
subscription and first-party provider. Check only the presence of API-key, auth-token,
base-URL and Bedrock/Vertex/Foundry overrides; preserve their values and the user's environment.
An override or unverified subscription makes this route unavailable. Account setup,
purchases, API billing, CLI installation and upgrades require separate authority.

Verify supported safe/restricted mode, tool controls, disabled hooks and the requested
model under actual managed policy. Establish effort support from the installed CLI's
supported `--effort` option/value and absence of known incompatible managed overrides
or clamps; no echoed effort or support field is required. Safe mode alone does not
disable policy hooks or prove the effective effort. If required security controls
or access cannot be established, report the limit and use the native role. Missing
effective-effort metadata alone does not invalidate established security controls.
Use subscription-preserving safe mode; bare mode skips its authentication.

## Assign and execute

Supply a complete packet: exact checkout/revision and dirty state; operator answers
and approved scope; applicable repository/path instructions and skill sources;
owned files/behavior; acceptance criteria, verification and completion evidence.
Keep credentials and unrelated private context out. The primary owns live dialogue,
human decisions, tracker writes, integration and final acceptance.

Run from the task worktree. Keep input and captured JSON outside the checkout;
pass the packet on stdin because safe mode omits automatic instruction discovery.
Use a fresh invocation without session persistence or recursive delegation. Establish
an execution/observation owner, a 15-minute overall limit and exact-process teardown
before launching. The supervisor terminates an unfinished process before fallback.

Planner runs with repository reads only:

```bash
claude -p --model claude-opus-5-5 --effort high \
  --safe-mode --restricted --strict-mcp-config \
  --settings '{"disableAllHooks":true}' \
  --tools 'Read,Glob,Grep' --allowedTools 'Read,Glob,Grep' \
  --disallowedTools 'mcp__*' --permission-mode dontAsk \
  --no-session-persistence --output-format json < /absolute/path/assignment.md
```

Planner returns proposed text and unresolved decisions; it does not approve,
publish or implement its plan.

Worker receives only `Read,Glob,Grep,Edit,Write` via `--tools`, retaining the other
controls above. Replace the read-only allowlist with `Read,Glob,Grep` and exact
`Edit(/repository-relative-owned-file)` rules for every assigned file, including
new files. Edit path rules govern both Edit and Write; do not grant blanket Edit
or Write permission. Use the installed CLI's documented path escaping. With
`dontAsk`, unapproved writes fail instead of acquiring more authority. File tools
stay within the worktree; command execution, connectors and subagents are excluded.
The primary runs checks and Git/publication operations separately.

## Accept or fall back

Inspect exit status, JSON errors including `is_error`, model usage, effort evidence,
denials, coverage and actual changed files. A zero exit is insufficient. Accept
complete output from the requested model within ownership when the effort request
is accepted: the supported explicit `--effort` option was passed with no reported
rejection or known incompatible override or clamp. No returned effort or acceptance
field is required; request acceptance does not prove effective effort. Record
requested/accepted effort separately from observed effective effort. Absent
effective-effort metadata is unobserved, not unavailability or incomplete work;
model self-attestation is not observation.

Authentication/provider failures, unsupported or rejected controls, known effort
incompatibility or policy clamps, observed effective-effort mismatch (including lower
effort than requested), automatic model substitution, denials, limits, errors,
timeout, malformed output or incomplete work make the route unavailable
for this assignment; report the concrete reason instead of retrying Claude.

Before a native worker resumes, inspect partial edits and unrelated state. Preserve
valid work and give the fallback an updated packet covering only remaining work;
do not repeat a partially completed write or revert another agent. Verify the
loaded native role supports Sol/high and its assigned authority; unavailable native
dispatch is a reported limit, not permission to select a third model. Report the
actual route, model, requested/accepted effort, observed or unobserved effective
effort, accepted result and verification limits. Recheck current prerequisites for
later assignments; missing telemetry or an earlier failure does not permanently
disable the preferred route.

Claude Code-hosted sessions retain their native delegation rules. Independent review
uses the code-review package's separate routing and read-only assignment.

CLI controls: [reference](https://code.claude.com/docs/en/cli-reference),
[permissions](https://code.claude.com/docs/en/permissions), and
[model/effort configuration](https://code.claude.com/docs/en/model-config).
