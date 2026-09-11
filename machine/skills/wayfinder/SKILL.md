---
name: wayfinder
description: Plan repository changes before implementation, from compact settled work to large uncertain efforts. Start or resume a shared map when change conversations lack covering design, and resolve its decisions before specification and delivery.
---

Begin from the desired **destination** and the actual repository. This skill
charts or resumes a **shared map** before implementation. For uncertain work,
its **decision tickets** resolve questions rather than slice up the build. For
settled small work, record a compact map with the agreed direction and no
invented decision children. Reuse covering maps instead of restarting planning
for routine implementation choices.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

When resolving or changing a saved selection, read
[selection scope and handoff](../set-map/SELECTIONS.md). Carry the explicit
scope, task owner and generation through handoffs to selection/execution owners.
Keep map and backlog bindings independent. Publication and closed design do not
change another effort's selections or grant takeover authority.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. Record standing preferences in **Notes**. Execute associated implementation through `next-issue` only after the entire map is resolved and the user authorizes execution. Decision-unblocking tasks remain part of planning.

## Refer by name

Every map and ticket is an issue, so it has a **name**: its title. In everything the human reads (narration, the map's Decisions-so-far), refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish; a name wraps its link, but they ride _inside_ the name, never stand in for it.

## The Map

The map is a single issue on this repo's issue tracker, labelled `wayfinder:map`, the canonical artifact. Its tickets are child issues of the map.

The map indexes decision tickets and links their resolutions without copying
them. When the conversation has already settled a compact design with no
decision tickets, record that agreed direction directly in Decisions so far. Do
not invent children just to hold an answer already established in the same
planning exchange.

The target repository owns the map and specification, including cross-repository
preparation. Consult its tracker guidance for map, child, dependency and
frontier operations. If tracker access or a required planning capability is
unavailable, continue conversational planning and resolve the durable
target-owned artifact location before implementation. Report the concrete
limitation; do not invent a local tracker, bootstrap framework or setup command.
Follow publication policy for planning records.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed: they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child issue** of the map; the tracker's issue id is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a `wayfinder:<type>` label, one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)).

A session **claims** a ticket by assigning it to the dev driving the map, **first**, before any work, so concurrent sessions skip it. That assignee _is_ the claim: an open, unassigned ticket is unclaimed.

Blocking uses the tracker's **native** dependency relationship: essential because it renders the frontier _visually_ in the tracker's own UI, so the human sees what's takeable without opening the map. Only a tracker that lacks native blocking falls back to a body convention. A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked, unclaimed children, the edge of the known.

The answer isn't part of the body; it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Use the `research` skill; an assigned researcher investigates directly and returns cited evidence within its write authority. Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to (an outline, a rough take, a stub, or UI/logic code) using the `prototype` skill. Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Read and apply the `grilling` and `domain-modeling` skills.
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made: nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. Keep it limited to unblocking a decision within existing action authority;
  repository implementation changes intended to ship follow the global planning
  gate. The agent drives authorized work alone where it can (AFK); otherwise it
  hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination: everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **Ticket when** the question is already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates (the frontier stops at the destination), so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination (mis-scoped in while charting, or exposed by a resolution), **close it** (a closed ticket is unambiguously off the frontier) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session**, with the exception of research tickets.

### Chart the map

A change conversation or implementation request can begin this planning session,
directly or through `whats-next` or another owning workflow. Start dialogue
without a separate invocation approval; create or reuse tracker artifacts once
the destination is concrete. Reuse established direction and the global Planning
before implementation rule, including its explicit-waiver and planning-work
boundaries.

1. **Name the destination.** Read and apply `grilling` and `domain-modeling` to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Inspect the whole destination for actual open decisions,
   using `grilling` where human judgment is unresolved. Reuse supplied answers.
   If the route is already clear, keep the map compact with the agreed direction;
   it still precedes the spec unless the operator explicitly waived planning.
3. **Create or reuse the map** (label `wayfinder:map`): record Destination, Notes, settled direction and only real remaining fog. Keep it open until its resolution and implementation handoff are recorded.
4. **Create the tickets you can specify now** as child issues of the map, then wire blocking edges in a **second pass** (issues need ids before they can reference each other). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog: the **Not yet specified** section.
5. **Research actual open questions.** When research tickets exist, use the `research` skill to assign independent research with bounded questions and evidence requirements. On Codex, assign canonical `explorer` agents. On Claude Code, use its native available subagents without an Agent Team role or model override. Prepare artifacts in a separate worktree on a `codex/research-<name>` branch from fresh `origin/test`, following the target repository's checkout and delivery rules. Each assigned researcher investigates directly and returns cited findings; the primary owns any repository artifact and tracker resolution. Link the retained findings from the ticket. The primary serializes shared Git mutations and resolves the research tickets from the returned evidence.
6. For a chart-only request, return the map. When the request includes continuation
   or implementation, select the open map through `set-map` before closure, then
   use `next-waypoint-loop` under that authority. Reusing an already resolved map
   needs no new selection; retain its source links and existing pointer.
   An already settled compact map proceeds directly to the Implementation handoff:
   prepare its specification and executable breakdown, record resolution and close
   the map after verifying that no decision remains. No dummy frontier is needed.

### Work through the map

User invokes with a map (URL or number). A ticket is **optional**: without one, you pick the next decision, not the user.

1. Load the **map**: the low-res view, not every ticket body.
2. If no open decisions or fog remain, complete the Implementation handoff and
   map resolution directly, including for a compact map with no children.
   Otherwise choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: assign it to yourself before any work.
3. Resolve it. **Zoom as needed**: fetch the full body of any related or closed ticket on demand; read and apply whichever skills the `## Notes` block names. Use `grilling` and `domain-modeling` when an unresolved human decision requires them; reuse settled answers.
4. Record the resolution: post the answer as a **resolution comment**, satisfy the **Implementation handoff** below, **close** the issue, and **append a context pointer** to the map's Decisions-so-far when it has a map parent.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals that a ticket (this one or another) sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.

## Implementation handoff

Resolve the entire map before its associated implementation proceeds. If implementation exposes a substantive missing decision, reopen the map and pause the whole associated backlog until it is resolved again. Routine implementation choices remain with the implementing agent. Ask ready human questions together in ordinary text and wait for answers.

Before closing a resolved design ticket or completed map that leaves
implementation work, find or create an open implementation follow-up and link it
both ways. Reuse an existing follow-up for the same effort; one shared follow-up
may cover several decisions. Record its intended outcome and references to the
approved decisions. Once every decision is settled, use `to-spec` to draft one
specification/backlog parent and its executable breakdown. For a settled compact
map, record its agreed direction in the map's resolution comment. Record
resolution and close the map once its open follow-up is verified; `to-tickets`
publishes the approved batch after the map closes. While design remains
unsettled, keep the follow-up explicitly awaiting planning rather than inventing
executable scope.

Verify the follow-up is open and discoverable through the repository's implementation intake. Creating it does not activate a backlog, claim implementation, or start development. If the user explicitly chooses to defer tracking or abandon implementation, record that disposition instead; do not infer it merely from "later" or from a closed design. A decision with no remaining implementation needs no follow-up. Include the follow-up link or explicit disposition in the resolution and final handoff.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently.

## Attribution

Adapted by Agent Team from [Matt Pocock’s Wayfinder](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/wayfinder/SKILL.md), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns the implementation handoff and backlog boundary adaptations.
