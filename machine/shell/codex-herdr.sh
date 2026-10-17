# Source from the matching interactive shell's managed startup hook.
# Keep an existing alias/function, including one already loaded from this file.
if ! alias codex >/dev/null 2>&1 && ! typeset -f codex >/dev/null 2>&1; then
    function codex {
        local _agent_team_no_daemon='(^|[[:space:]])--no-daemon($|[[:space:]])'
        if [ "${HERDR_ENV+x}" = x ] && ! [[ "$*" =~ $_agent_team_no_daemon ]]; then
            command codex --no-daemon "$@"
        else
            command codex "$@"
        fi
    }
fi
