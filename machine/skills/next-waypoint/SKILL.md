---
name: next-waypoint
description: Claim and work the next frontier ticket from this repository's saved Wayfinder map.
---

# Next Waypoint

Resolve the current repository's absolute Git common directory:

```bash
git rev-parse --path-format=absolute --git-common-dir
```

Read `codex-wayfinder-map` from that directory. A valid pointer is exactly one
non-empty line. If it is absent or invalid, return the concrete pointer problem
to the invoking owner for resolution through `set-map`, carrying existing selection
authority. In standalone use, resolve the missing selection with the user; no extra
slash command is required. This entrypoint never infers a replacement map.

For a valid pointer, read the `wayfinder` skill completely and follow its
**Work through the map** workflow with the saved URL and no named ticket.
Wayfinder owns ticket selection, claiming, human interaction, completion, and
resolution recording; reaching Wayfinder's stopping condition completes this
skill.
