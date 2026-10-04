# Reviewer routing

The primary agent owns this selection. An assigned reviewer executes its assignment
without selecting another reviewer. Use one reviewer for both Standards and Spec
unless independent assignments are useful; apply the same routing to each assignment.

## Claude Code native review

When Claude Code is the host, the primary assigns one native available subagent the
complete bounded review packet: exact repository and immutable comparison, complete
requested diff (including WIP when applicable), requirements, applicable
instructions, the code-review skill's axes and smell baseline, and verification
evidence. The reviewer performs its assigned axes directly and does not reroute or
delegate the review. The assignment is read-only. Use the host's ordinary model
selection; do not install an Agent Team reviewer role or override a model. If native
delegation is unavailable, report the missing independent-review capability and
preserve the bounded review task. This Claude Code route ends here.

## Codex: Default native review

The default is the configured read-only `critical_reviewer`. Prepare the complete
immutable comparison and requirements before selecting a route. Use `rev_<purpose>`
and display `🔍 REV` followed by the exact task name. Select
the declared standard model in standard or unknown mode and the declared Daybreak
model in Daybreak mode, at `xhigh`. Neither the generic default nor optional Opus review
replaces the required mode-compatible native reviewer. Unavailable native dispatch
is a concrete blocked review; preserve mode and report the reason.

### Current-task capability gate

Inspect the directly exposed dispatch schema and supported current-task metadata.
Establish role selection/loading, model/effort controls and observable inherited
permissions on this surface. A task-name prefix, installed configuration, roster
inventory, account entitlement or another runtime's API proves none of these.
Distinguish a missing role selector from ineffective permissions after supported
role dispatch; source changes cannot restore a missing host capability.

- **A. Supported named role:** use the default route and its loaded-role checks
  below. Preserve configured read-only authority. A known loaded-role/sandbox
  contradiction blocks this route; return it to the existing enforcement owner
  without changing permissions.
- **B. Missing role selection/loading evidence:** name the exact tool and missing
  control, preserve the review packet, and check existing operator authority for C.
  Without a covering exception, return a blocked review. Tool availability, naming,
  harmless intent and Full Access do not establish exception authority.
- **C. Explicit bounded ordinary-native exception:** require operator authority
  covering this repository, finite task/review scope, assigned axes, direct ordinary
  native tool and disclosed inherited permissions, accepting the absence of an
  enforced role sandbox. Pin the comparison at dispatch and retain the compatible
  model/xhigh and repository-read-only assignment. Reuse matching authority from
  existing task/tracker context; covered corrective iterations may repin without
  duplicate prompts. A new repository/provider or materially changed scope or
  permissions needs covering authority. This is a finite exception, not a standing
  waiver; no approval ledger or credential is needed.
- **D. Unsupported controls or rejected dispatch:** missing required delegation,
  model or effort returns a block with the packet. Preserve an actual denial's
  exact action, target and reason; task transcripts and tool wrappers do not
  guarantee approval. Use only the explicit mode recovery below. Do not force a
  prompt, fabricate approval identifiers, relabel the action, change security
  controls, select a generic substitute or launch an extra CLI/cloud coordinator
  to retry indirectly. Optional review cannot replace required native review.

### Select and dispatch

Apply mode/model selection to both A and an authorized C:

1. Use supported current-task mode evidence when available, including an explicit
   operator declaration that remains valid for this task. Fresh task metadata such
   as `daybreakEnabled: bool | null` from a
   supported thread/read schema records saved task mode, not a per-turn guarantee;
   resolve any current-turn discrepancy before selecting. `true` means Daybreak,
   `false` means standard, and `null` or missing means unknown. Model name and
   account entitlement alone do not establish mode. When the host omits mode
   evidence, retain `unknown` and continue with one standard-model attempt without
   asking the operator solely to classify mode.
2. Read [reviewer-models.toml](reviewer-models.toml), the authoritative native
   reviewer choices. Select `daybreak` for known Daybreak mode, otherwise `standard`.
   Verify the execution host supports the selected model at `xhigh`; catalog
   membership alone does not prove current-mode compatibility. Let the host enforce
   compatibility during dispatch while preserving the orchestrator mode, sandbox
   and approval controls. A known unavailable or incompatible choice blocks review.
3. For A, verify the loaded `critical_reviewer` role will execute the selected model
   at the required effort. Its managed source omits a fixed model; a loaded fixed
   model can still win over a spawn override. An identical loaded pin satisfies
   model selection, so use that verified assignment if an override is unnecessary
   or unsupported. A conflicting pin or host restriction blocks dispatch until
   reconciliation/restart resolves it; source changes alone do not refresh a
   loaded role. Preserve the role's configured read-only authority.
4. For A, spawn that role with the selected explicit model (or verified identical
   pin) and `xhigh` effort. For C, invoke the direct ordinary native tool once with
   `fork_turns="none"`, explicit selected model/xhigh and a standalone complete
   packet: repository, pinned comparison and complete requested diff, requirements,
   applicable instructions, Standards/Spec axes and smell baseline, verification
   evidence and its limits. Generic
   subagent defaults are not reviewer selection. Where full-history forks forbid
   model overrides, use `fork_turns="none"` and supply the bounded review packet
   explicitly, or a supported bounded-history fork with the complete packet.
   Preserve the assigned Standards/Spec axes and read-only limits on either route:
   repository inspection only, no mutations, external connectors, or recursive delegation.
5. If the standard attempt is rejected with a host response explicitly identifying
   active Daybreak mode or a requirement for a Daybreak-compatible model, use that
   response as current-mode evidence. Repeat the model/effort and loaded-role checks
   for the declared `daybreak` choice (loaded-role checks only for A) and dispatch
   it once through the same authorized route with the same assignment,
   without another operator question. Authentication, entitlement, rate-limit,
   service, generic safeguard or unrelated launch failures do not establish mode
   and remain concrete blockers. A failed Daybreak attempt also blocks review;
   preserve the failure without repeating a rejected assignment, changing mode or
   selecting a third model.

Findings are successful review output, not provider unavailability: return them to
the implementation owner for resolution. Preserve actionable evidence from any
optional Claude review alongside the native result. Successful dispatch alone does
not establish mode: report `unknown` when evidence remains unavailable. Report the
mode evidence, requested model and effort, dispatch result, any recovery or
availability limit, and Standards/Spec outcomes. Separate requested, accepted and
observable effective identity; unknown telemetry stays unknown. For A, report
loaded-role and effective permission evidence. For C, report ordinary native review,
instruction-only read-only authority and actual or unknown inherited permissions;
never claim a loaded role or enforced read-only sandbox without evidence. Identify
unavailable/unexercised surfaces rather than simulating dispatch or using destructive
permission probes. The primary validates
findings and coverage and remains accountable for delivery.

## Codex: Optional additional Claude review

Use this branch when the operator or primary assigns an additional independent
review. The default review uses the native route above. Use exact
`claude-opus-5-5` with `--effort xhigh` when available on the execution host;
Claude is an external CLI invocation, not a Codex model selector.

Resolve `claude` on the host, inspect `claude --version` and the installed CLI's
options, and check `claude auth status` without exposing account details or secrets.
Verify the effective authentication method and provider are the Claude subscription,
including any environment overrides: an `ANTHROPIC_API_KEY`, auth token, custom
base URL, or Bedrock/Vertex/Foundry selection can override an existing login. Inspect
only variable presence and non-secret authentication metadata; never print values.
If subscription use cannot be established, report the optional route unavailable
instead of using those overrides or changing the user's environment. Account setup, purchases, API billing,
and installing or upgrading the CLI require the user's authorization; a review
must not wait for them. If the CLI, required options, or authenticated subscription
is absent, report this optional route unavailable. The default native review
remains required.

Prepare the same bounded assignment either reviewer would receive: exact repository
and immutable comparison, complete requested diff (including WIP when applicable),
requirements, applicable instructions, the code-review skill's axes and smell
baseline, and verification evidence. Claude does not automatically receive Codex
context. Supply this material explicitly and identify which source files/callers it
should inspect. Keep credentials and unrelated private material out of the packet.

Run from the review checkout, with both the assignment file and captured JSON output
outside the checkout; pass the assignment on stdin. A supported invocation is:

```bash
claude -p --model claude-opus-5-5 --effort xhigh \
  --safe-mode --restricted --strict-mcp-config \
  --settings '{"disableAllHooks":true}' \
  --tools 'Read,Glob,Grep' --allowedTools 'Read,Glob,Grep' \
  --disallowedTools 'mcp__*' --permission-mode dontAsk \
  --no-session-persistence --output-format json < /absolute/path/review-input.md
```

Use the installed CLI's supported controls to keep hooks and customization disabled
and limit tools to repository reads. `--safe-mode` preserves subscription login;
`--bare` skips OAuth/keychain authentication and is unsuitable for this route.
`--restricted` confines file tools to the working directories. Supply repository
instructions explicitly because safe mode skips their automatic discovery. Safe
mode alone does not disable policy hooks. Verify managed policy permits
the restrictions and requested effective effort; unknown or incompatible policy
makes the optional route unavailable. Do not enable Bash, edits, subagents, external connectors, or permission bypasses for this review.
The primary supplies Git/tracker evidence and runs any required checks separately.

Allow at most 15 minutes for an invocation; supervise and terminate an unfinished
process before reporting this optional route unavailable. Inspect exit status,
JSON error/result fields, reported model usage, effective-effort evidence,
permission denials, and actual coverage of the assigned axes. A zero
exit status alone is not review completion. Accept only a complete review from
Opus 5.5 at the requested effort; unknown effective effort leaves completion
unverified. Do not configure another Claude fallback model;
if automatic substitution occurs, treat that result as unavailable for this route.

On optional-route installation/login/model-access gaps, unsupported controls,
usage/service limits, timeout, malformed output, substitutions or incomplete coverage,
report the concrete limit and preserve actionable partial findings. One failed
Claude invocation is enough; do not retry or silently choose another Claude model.
The completed native review remains authoritative. Optional reviewer unavailability
is not an unresolved finding; accepted findings still return to the implementation
owner, and a specifically required additional review stays pending.

## CLI references

Verify options against the installed version and official documentation when they
change: [CLI reference](https://code.claude.com/docs/en/cli-reference) and
[model configuration](https://support.claude.com/en/articles/11940350-claude-code-model-configuration).
