# Pi with Agent Team

Read the shared Agent Team instructions at `$CODEX_HOME/AGENTS.md` (default
`~/.codex/AGENTS.md`) and the current repository's instructions before working.
The shared instructions' Codex-only and Claude-only routes apply to those hosts;
Pi uses [Herdr coordination](HERDR.md) for delegation, independent review,
timeouts and worker cleanup. Load that guide before creating or reusing a worker
and at each worker lifecycle boundary.

Use Pi's OpenAI ChatGPT subscription login with the same account used for Codex.
Authentication belongs to Pi: use interactive `/login`, selecting OpenAI. Before
provider verification, use `pi auth check --provider openai --json --no-refresh`
and require `ready` with `authType` `oauth`. Preserve credentials locally. An API
key or a different provider/model does not satisfy subscription setup.
