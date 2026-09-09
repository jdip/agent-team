#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: set-backlog.sh <parent-url>" >&2
  exit 2
fi

git rev-parse --is-inside-work-tree >/dev/null
repository_url=$(gh repo view --json url --jq .url)
parent_fields=$(gh issue view --json number,title,url,state,labels \
  --jq '.url, .state, (.labels | any(.name == "implementation:backlog")), .title' -- "$1")
# Keep the free-form title last so embedded whitespace is preserved.
{
  IFS= read -r parent_url
  IFS= read -r parent_state
  IFS= read -r parent_labelled
  parent_title=$(cat)
} <<<"$parent_fields"

if [[ "$parent_url" != "$repository_url"/issues/* ]]; then
  echo "error: backlog must be an issue in the current repository: $repository_url" >&2
  exit 1
fi
if [[ "$parent_state" != "OPEN" ]]; then
  echo "error: backlog is not open: $parent_title" >&2
  exit 1
fi
if [[ "$parent_labelled" != "true" ]]; then
  echo "error: issue is not labelled implementation:backlog: $parent_title" >&2
  exit 1
fi

git_common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
temporary_path=$(mktemp "$git_common_dir/.codex-implementation-backlog.XXXXXX")
trap 'rm -f "$temporary_path"' EXIT
printf '%s\n' "$parent_url" >"$temporary_path"
chmod 600 "$temporary_path"
mv -f "$temporary_path" "$git_common_dir/codex-implementation-backlog"
trap - EXIT
printf '%s\n%s\n' "$parent_title" "$parent_url"
