#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 && !( $# -eq 2 && "$1" == "--refresh" ) ]]; then
  echo "usage: set-map.sh <map-url> | --refresh <expected-issue-node-id>" >&2
  exit 2
fi

git rev-parse --is-inside-work-tree >/dev/null
git_common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
state_path="$git_common_dir/codex-wayfinder-map"
map_input=$1
refresh=false
if [[ "$1" == "--refresh" ]]; then
  if [[ $# -ne 2 || -z "$2" ]]; then
    echo "error: refresh requires the previously verified issue node ID" >&2
    exit 2
  fi
  refresh=true
  map_input=$(cat "$state_path")
  if [[ -z "$map_input" || "$map_input" == *$'\n'* ]]; then
    echo "error: saved map must contain exactly one URL" >&2
    exit 1
  fi
fi

repository_url=$(gh repo view --json url --jq .url)
map_fields=$(gh issue view --json id,title,url,state,labels \
  --jq '.id, .url, .state, (.labels | any(.name == "wayfinder:map")), .title' -- "$map_input")
# Keep the free-form title last so embedded whitespace is preserved.
{
  IFS= read -r map_id
  IFS= read -r map_url
  IFS= read -r map_state
  IFS= read -r map_labelled
  map_title=$(cat)
} <<<"$map_fields"

if [[ "$map_url" != "$repository_url"/issues/* ]]; then
  echo "error: the map must belong to the current repository: $repository_url" >&2
  exit 1
fi

if [[ "$refresh" == "true" && "$map_id" != "$2" ]]; then
  echo "error: saved map no longer resolves to the expected issue identity" >&2
  exit 1
fi

if [[ "$refresh" != "true" && "$map_state" != "OPEN" ]]; then
  echo "error: the Wayfinder map is not open: $map_title" >&2
  exit 1
fi

if [[ "$map_labelled" != "true" ]]; then
  echo "error: the issue is not labelled wayfinder:map: $map_title" >&2
  exit 1
fi

temporary_path=$(mktemp "$git_common_dir/.codex-wayfinder-map.XXXXXX")
trap 'rm -f "$temporary_path"' EXIT

printf '%s\n' "$map_url" >"$temporary_path"
chmod 600 "$temporary_path"
mv -f "$temporary_path" "$state_path"
trap - EXIT

printf '%s\n%s\n' "$map_title" "$map_url"
