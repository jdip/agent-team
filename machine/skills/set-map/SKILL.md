---
name: set-map
description: Save a Wayfinder map URL for this repository so later sessions can continue it with $next-waypoint.
---

# Set Map

Use the map URL supplied by the user or established in an explicitly approved
`whats-next` select-and-start proposal. Then run this skill's script exactly once:

```bash
scripts/set-map.sh <map-url>
```

Resolve the script relative to this skill directory. If the URL is missing, ask
the user for it. The script accepts only an open `wayfinder:map` issue in the
current repository and leaves any existing pointer unchanged on failure.

The script stores the pointer in Git's common metadata directory, making it
untracked and shared by the repository's worktrees. Completion is a successful
exit followed by reporting both output lines: the saved map's name and URL.

For an authorized repository rename, refresh the existing selection with
`scripts/set-map.sh --refresh <expected-issue-node-id>`. Capture the issue's
immutable GraphQL node ID before the rename from trusted tracker evidence, then
refresh after updating the Git remote and before reusing the old repository name.
This resolves the saved URL, requires the same issue identity in the current
repository, and permits retaining a completed map. It does not select another map
or reopen the design. Read back the canonical URL; failure preserves the pointer.
