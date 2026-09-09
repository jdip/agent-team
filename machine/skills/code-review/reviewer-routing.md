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

## Codex: Prefer Claude CLI

Use Claude Code with the exact model `claude-fable-5-1` and `--effort high` when
available on the execution host. Keep the native `critical_reviewer` role configured
as the fallback; Claude is an external CLI invocation, not a Codex model selector.

Resolve `claude` on the host, inspect `claude --version` and the installed CLI's
options, and check `claude auth status` without exposing account details or secrets.
Verify the effective authentication method and provider are the Claude subscription,
including any environment overrides: an `ANTHROPIC_API_KEY`, auth token, custom
base URL, or Bedrock/Vertex/Foundry selection can override an existing login. Inspect
only variable presence and non-secret authentication metadata; never print values.
If subscription use cannot be established, fall back instead of using those
overrides or changing the user's environment. Account setup, purchases, API billing,
and installing or upgrading the CLI require the user's authorization; a review
must not wait for them. If the CLI, required options, or authenticated subscription
is absent, go directly to the fallback below.

Prepare the same bounded assignment either reviewer would receive: exact repository
and immutable comparison, complete requested diff (including WIP when applicable),
requirements, applicable instructions, the code-review skill's axes and smell
baseline, and verification evidence. Claude does not automatically receive Codex
context. Supply this material explicitly and identify which source files/callers it
should inspect. Keep credentials and unrelated private material out of the packet.

Run from the review checkout, with both the assignment file and captured JSON output
outside the checkout; pass the assignment on stdin. A supported invocation is:

```bash
claude -p --model claude-fable-5-1 --effort high \
  --safe-mode --restricted --strict-mcp-config \
  --tools 'Read,Glob,Grep' --allowedTools 'Read,Glob,Grep' \
  --disallowedTools 'mcp__*' --permission-mode dontAsk \
  --no-session-persistence --output-format json < /absolute/path/review-input.md
```

Use the installed CLI's supported controls to keep hooks and customization disabled
and limit tools to repository reads. `--safe-mode` preserves subscription login;
`--bare` skips OAuth/keychain authentication and is unsuitable for this route.
`--restricted` confines file tools to the working directories. Supply repository
instructions explicitly because safe mode skips their automatic discovery. If
managed policy prevents these restrictions, use the native reviewer. Do not enable
Bash, edits, subagents, external connectors, or permission bypasses for this review.
The primary supplies Git/tracker evidence and runs any required checks separately.

Allow at most 15 minutes for an invocation; supervise and terminate an unfinished
process before falling back. Inspect exit status, JSON error/result fields, reported
model usage, permission denials, and actual coverage of the assigned axes. A zero
exit status alone is not review completion. Accept only a complete review from
Fable 5.1 at the requested effort. Do not configure another Claude fallback model;
if automatic substitution occurs, treat that result as unavailable for this route.

## Fall back to REV

On missing installation/login/model access, unsupported controls, rate or usage
limits, service/network errors, timeout, malformed output, or an incomplete review,
report the concrete reason and assign the same comparison and requirements to
`critical_reviewer` at its configured model and effort, using `rev_<purpose>` and display
`🔍 REV` followed by the exact task name. One failed Claude attempt is enough;
continue through the fallback without asking for permission or retrying Claude.
If the native reviewer is also unavailable, report the blocked review; do not claim
approval or silently substitute a third reviewer.

Findings are successful review output, not provider unavailability: return them to
the implementation owner for resolution. Preserve actionable evidence from partial
Claude output when completing the fallback review. Report the reviewer actually used,
any fallback reason, and Standards/Spec outcomes. The primary validates findings and
coverage and remains accountable for delivery.

## CLI references

Verify options against the installed version and official documentation when they
change: [CLI reference](https://code.claude.com/docs/en/cli-reference) and
[model configuration](https://support.claude.com/en/articles/11940350-claude-code-model-configuration).
