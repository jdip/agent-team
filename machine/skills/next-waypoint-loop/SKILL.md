---
name: next-waypoint-loop
description: Work successive frontier tickets from this repository's saved Wayfinder map until human input or approval is needed, or no further ticket is available.
---

# Next Waypoint Loop

This is the continuous version of `next-waypoint`. Its invocation authorizes
continuing across ticket boundaries in the current conversation. It overrides
Wayfinder's one-ticket-per-session limit and normal stop after a resolved ticket;
all other Wayfinder rules, including the map's planning/execution boundary,
remain in force. It does not authorize answering human decisions or bypassing
approvals. An authorized `whats-next` handoff supplies this invocation for the
established selected map; no additional slash command is needed.

## Load the saved map

Resolve the current repository's absolute Git common directory:

```bash
git rev-parse --path-format=absolute --git-common-dir
```

Read `codex-wayfinder-map` from that directory. A valid pointer is exactly one
non-empty line. If it is absent or invalid, return the pointer problem to
`whats-next` when it is the caller; otherwise ask the user to invoke `$set-map`
with the map URL. This loop never infers or searches for a replacement selection.

Read the `wayfinder` skill completely and the repository's issue-tracker
instructions. Use the saved URL with **Work through the map**, with no named
ticket. If Wayfinder is unavailable, report the missing dependency.

## Continue through the frontier

1. Load the map and select its first open, unblocked, unclaimed child in tracker
   order. Claim it before work. Do not skip a human-in-the-loop ticket to reach
   an autonomous one. Do not take a ticket claimed by another session.
2. Follow Wayfinder's workflow and the selected ticket's required skills.
   Continue independently through authorized work and routine recoverable
   failures. A prototype or grilling ticket requires the human's actual
   participation; never supply their answers yourself.
3. Before pausing for input or approval, assemble the full ready decision round
   for the claimed ticket as described below. Complete the independent work
   needed to present concrete recommendations or reviewable results. Ask the
   ready questions together, then pause. Keep the ticket claimed and unresolved;
   do not claim another ticket while this one waits for the human.
4. When the ticket is resolved, finish **all** Wayfinder bookkeeping: record the
   resolution, satisfy Wayfinder’s implementation handoff, close the ticket,
   append the map's context pointer, and create or
   update newly surfaced tickets and dependency edges. A subagent's report or
   a completed local artifact alone is not a resolved tracker ticket.
5. Refresh the map and frontier from the tracker, accounting for concurrent
   sessions. Under `whats-next`, return for reassessment at this boundary before
   the next selection, continuing here when the same map remains the chosen action.
   Otherwise immediately repeat from step 1 without asking whether to continue
   or ending the turn merely because one ticket finished.

After the human answers a round, apply all supplied answers, complete newly
authorized independent work, and recompute the ready decisions. Resume the same
claimed ticket, then continue the loop. Do not treat a partial answer as approval
of unanswered decisions; carry those forward without blocking unrelated progress
within the ticket. Honor a later request to stop or change scope.

## Batch decisions and work within each turn

Wayfinder's ticket frontier chooses **which ticket to work**. Grilling's decision
frontier chooses **all questions ready to ask within that ticket**. One claimed
ticket does not mean one question per turn. The instruction to pause for human
input means pause after preparing the ready round, not at the first uncertainty.

- Survey the claimed ticket's whole decision tree before asking. Gather available
  facts and advance independent work across it, rather than following one branch
  through a succession of tiny confirmations.
- Follow grilling's existing whole-frontier rule: batch independent, answerable
  decisions in one numbered round, with a concrete recommendation for each. Use
  as many questions as are useful and coherent; do not impose a one-question cap
  or pad a round to meet a quota. Combine tightly related choices into a coherent
  proposal when that makes the human's decision easier.
- A question is ready only when its prerequisites are settled. Do not assume an
  answer to another open question to make a larger batch. Research unsettled
  facts as required by the ticket's skills; only dependent questions wait for
  those results. If only one meaningful question is ready, ask that one.
- Choose routine implementation details within the agreed constraints and state
  consequential assumptions. Do not turn every filename, restatement of an
  accepted rule, or already-authorized next step into another approval request.
- Human decisions and required approvals remain human-owned. Where grilling
  needs confirmation of shared understanding, include the concrete consolidated
  proposal in the ready round; do not add repeated confirmations of points the
  human has already explicitly confirmed.
- After answers settle a ticket, finish its bookkeeping and immediately advance
  to the refreshed tracker frontier in the same turn. Ticket boundaries are not
  turn boundaries; human input dependencies are.

## End conditions

Pause for required human input or approval. Otherwise continue until the map is
complete, the user stops the run, or no actionable frontier remains.

An empty frontier is not necessarily a complete map: distinguish completion
from tickets blocked or claimed elsewhere, and from remaining fog. If a precise
in-scope question can now be ticketed, follow Wayfinder's fog-graduation rules
and refresh the frontier. If progress requires a human decision, ask it. If only
external work remains, report what must change and stop; do not steal claims,
invent work, poll indefinitely, or create a scheduled automation.

If an unrecoverable tool/access failure prevents progress, report the exact
blocker and preserve unresolved work. Never mark a ticket resolved merely to
keep the loop moving.

When called by `whats-next`, return the completed outcome or specific pending
decision/blocker to it; the coordinator may continue independent authorized work
without claiming this loop's unresolved ticket or supplying a human answer.

At a pause or end, briefly name and link the tickets completed during the run
and the pending question or stopping reason. The human should not need to
reconstruct the run from progress messages.
