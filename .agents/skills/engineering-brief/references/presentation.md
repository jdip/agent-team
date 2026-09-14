# Local HTML reader

The completed Markdown reports remain canonical history. The reusable templates
in `templates/` generate a derived, private blog archive with article pages, source
links, a history index, previous/next navigation, and collapsed discussion prompts.
No server, public hosting, or browser JavaScript is needed.

After saving a checked brief or audit, run the package's `scripts/render.sh` from
inside Agent Team, selecting Python 3.11+ through `AGENT_TEAM_PYTHON` when needed.
The entrypoint owns its isolated Python environment in the local archive and
installs only the package's declared `requirements.txt`. Do not install dependencies
globally or add this skill to Machine Reconciliation.

```sh
AGENT_TEAM_PYTHON=python3.13 <skill-directory>/scripts/render.sh
```

Use the returned index and article paths. Open the HTML through the host's file or
browser capability; verify readable typography, narrow-window layout, working
source/history links, and collapsed prompts after a template or rendering change.
For a new edition, inspect its main article and topic panels before reporting it as
ready. Disclose missing browser coverage rather than claiming visual verification.

The renderer reads validated completed history and does not alter its metadata,
coverage boundaries, or canonical Markdown. Rebuild pages after correcting an
edition or explicitly removing an archived report. A failed render leaves the
completed Markdown intact; fix the rendering problem and rebuild, never save a
second completed brief merely to retry presentation. Preserve private archive and
environment state during task cleanup.

## Conversation handoff

Return a short editorial summary, a link to the current HTML article, a link to
the archive, and native topic controls using [topic actions](topic-actions.md).
Do not paste the full article and fallback prompts into chat. Source links remain
in the article. The HTML discussion panel contains selectable, copyable text;
selecting it does not create a task. Actual native task requests live in the chat
summary, where Codex can interpret them. Do not invent desktop deep-link URLs or
introduce a bridge/service to simulate direct HTML task creation.
