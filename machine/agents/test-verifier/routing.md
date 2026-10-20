# Test verifier routing

The Codex primary owns this selection for every `test_verifier` assignment. The
verifier executes its assignment without selecting another verifier.

Assigned independent verification stays with a separate verifier. The primary
still inspects sources, runs short checks and operates canonical scripts; the
`pr-to-test` workflow keeps its execution/observation ownership. A blocked or
incompatible verifier launch leaves the assignment pending; the primary does not
perform it instead.

## Packet

Prepare the complete bounded assignment before selecting a route: exact checkout,
revision and dirty state; change under verification; approved requirements and
acceptance; repository classification and applicable instructions; checks or
operations to run; write and tool authority; expected evidence. Include the exact
`developer_instructions` text from the `test_verifier` role. Use `tst_<purpose>`
and display `🧪 TST` followed by the exact task name.

## Dispatch surface

Inspect the directly exposed dispatch schema and supported current-task metadata.
Establish role selection/loading, model/effort controls and observable inherited
permissions on this surface. Installed configuration, roster inventory, catalog
membership and account entitlement prove none of these. Role sandbox settings are
defaults; the parent's live sandbox and approval choices can override them.

- **A. Named role:** spawn `test_verifier` after the loaded-role check below.
- **B. Ordinary native dispatch:** only when named-role selection or loading is
  unavailable. Identify the exact direct tool and missing control, then assign the
  standalone packet. Route B never bypasses a conflicting loaded role or a
  rejected dispatch.
- **C. Missing delegation, model or effort control, or rejected dispatch:**
  verification stays pending with the packet. Preserve an actual denial's exact
  action, target and reason.

## Select and dispatch

1. Establish mode from supported current-task metadata or a valid explicit
   operator declaration for this task. In a supported thread/read schema,
   `daybreakEnabled` `true` means Daybreak, `false` means standard, and `null` or
   missing means unknown; resolve any current-turn discrepancy first. Model names,
   catalog membership, eligibility and entitlement are not mode evidence. Unknown
   mode gets one standard attempt without asking the operator solely to classify it.
2. Read [models.toml](models.toml). Select `daybreak` for known Daybreak mode,
   otherwise `standard`, at `medium`. Verify the execution host's catalog supports
   that model at `medium` and, for `daybreak`, Daybreak Blue eligibility where model
   metadata exposes it. The catalog covers model and effort only; native spawn sets model
   and effort only, and program selection stays host-owned.
3. For A, verify the loaded role will execute the selected model at `medium`. The
   managed role omits a fixed model. An identical loaded pin satisfies selection.
   A conflicting pin leaves verification pending until a separately authorized
   reconciliation or restart refreshes the role; source edits refresh nothing.
4. Dispatch once. For A, spawn the role with the selected explicit model (or the
   verified identical pin) and `medium`. For B, invoke the direct tool with
   `fork_turns="none"`, the explicit model/`medium` and the standalone packet.
   Preserve the primary's mode, sandbox and approval controls.
5. Recover only when the standard attempt is rejected by a host response
   explicitly identifying active Daybreak mode or a requirement for a
   Daybreak-compatible model. Treat it as mode evidence, repeat steps 2–3 for
   `daybreak`, and dispatch once through the same route and packet.
   Authentication, entitlement, rate-limit, service, safeguard, unavailable-model
   and unrelated failures do not establish mode and leave verification pending, as
   does a failed Daybreak attempt. Keep the primary's mode, program and
   permissions; select no third model, add no retries, and launch no extra CLI or
   cloud coordinator.

## Outcome

Failing checks are verification results: return them as findings to the
implementation owner, never as model unavailability. The verifier stops after the
relevant checks; repair or redelegation needs a new bounded assignment.

Report mode evidence, route, requested model and effort, dispatch result and any
recovery. Separate requested, accepted and observable effective identity,
including access program; unexposed telemetry stays unknown. For A, report
loaded-role evidence; for B, instruction-only authority. Report actual or unknown
inherited permissions and the verification outcome with its limits.

## Daybreak qualification

The `daybreak` entry is a candidate until qualified. Only a successful bounded
verifier assignment dispatched from a confirmed Daybreak primary on the applicable
host, at that model and `medium`, qualifies it. Catalog membership, eligibility,
unknown-mode success and another role's or an older alias's success do not.
Record the evidence in the existing task or issue and report the candidate
unqualified until then.
