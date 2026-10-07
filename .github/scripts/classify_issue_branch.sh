#!/usr/bin/env bash

set -euo pipefail

branch_name="${1:-}"
repository="${GITHUB_REPOSITORY:-viniciusnevescosta/A-Maze-ing}"
api_version="2026-03-10"

: "${GH_TOKEN:?GH_TOKEN is required}"

if [ -z "$branch_name" ]; then
  echo "Branch name is required." >&2
  exit 2
fi

api() {
  gh api \
    -H "X-GitHub-Api-Version: $api_version" \
    "$@"
}

emit_result() {
  local classification="$1"
  local issue_number="${2:-}"
  local parent_number="${3:-}"

  jq -cn \
    --arg classification "$classification" \
    --arg issue_number "$issue_number" \
    --arg parent_number "$parent_number" \
    '{
      classification: $classification,
      issue_number: $issue_number,
      parent_number: $parent_number
    }'
}

issue_number="${branch_name%%-*}"

if [[ ! "$issue_number" =~ ^[0-9]+$ ]]; then
  emit_result "unrelated"
  exit 0
fi

issue_json=$(api \
  "repos/$repository/issues/$issue_number" \
  2>/dev/null || true)

if [ -z "$issue_json" ] || \
  ! jq -e '.number | type == "number"' <<<"$issue_json" >/dev/null || \
  jq -e 'has("pull_request")' <<<"$issue_json" >/dev/null; then
  emit_result "missing_issue" "$issue_number"
  exit 0
fi

if jq -e 'any(.labels[]?; .name == "epic")' \
  <<<"$issue_json" >/dev/null; then
  emit_result "epic" "$issue_number"
  exit 0
fi

parent_json=$(api \
  "repos/$repository/issues/$issue_number/parent" \
  2>/dev/null || true)

if [ -z "$parent_json" ] || \
  ! jq -e '.number | type == "number"' <<<"$parent_json" >/dev/null; then
  emit_result "standalone_issue" "$issue_number"
  exit 0
fi

parent_number=$(jq -r '.number' <<<"$parent_json")

if jq -e 'any(.labels[]?; .name == "epic")' \
  <<<"$parent_json" >/dev/null; then
  emit_result "sub_issue" "$issue_number" "$parent_number"
else
  emit_result "invalid_parent" "$issue_number" "$parent_number"
fi
