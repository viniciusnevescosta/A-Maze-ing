#!/usr/bin/env bash

set -euo pipefail

issue_number="${1:-}"
force_in_progress="${2:-false}"
repository="${GITHUB_REPOSITORY:-viniciusnevescosta/A-Maze-ing}"
project_owner="${PROJECT_OWNER:-viniciusnevescosta}"
project_number="${PROJECT_NUMBER:-9}"
dry_run="${DRY_RUN:-false}"
api_version="2026-03-10"

: "${REPO_TOKEN:?REPO_TOKEN is required}"
: "${PROJECT_TOKEN:?PROJECT_TOKEN is required}"

if [[ ! "$issue_number" =~ ^[0-9]+$ ]]; then
  echo "Issue number must contain digits only."
  exit 2
fi

if [[ "$force_in_progress" != "true" && "$force_in_progress" != "false" ]]; then
  echo "force_in_progress must be true or false."
  exit 2
fi

repo_api() {
  GH_TOKEN="$REPO_TOKEN" gh api \
    -H "X-GitHub-Api-Version: $api_version" \
    "$@"
}

project_gh() {
  GH_TOKEN="$PROJECT_TOKEN" gh project "$@"
}

parent_json=$(repo_api \
  "repos/$repository/issues/$issue_number/parent" \
  2>/dev/null || true)

if [ -z "$parent_json" ] || \
  ! jq -e '.number | type == "number"' <<<"$parent_json" >/dev/null; then
  echo "Issue #$issue_number has no parent issue; nothing to synchronize."
  exit 0
fi

parent_number=$(jq -r '.number' <<<"$parent_json")
parent_state=$(jq -r '.state' <<<"$parent_json")
is_epic=$(jq -r 'any(.labels[]?; .name == "epic")' <<<"$parent_json")

if [ "$is_epic" != "true" ]; then
  echo "Parent issue #$parent_number is not labeled epic; skipping."
  exit 0
fi

subissues_json=$(repo_api \
  "repos/$repository/issues/$parent_number/sub_issues?per_page=100")
total_count=$(jq 'length' <<<"$subissues_json")

if [ "$total_count" -eq 0 ]; then
  echo "Epic #$parent_number has no sub-issues; skipping."
  exit 0
fi

open_numbers=$(jq '[.[] | select(.state == "open") | .number]' \
  <<<"$subissues_json")
open_count=$(jq 'length' <<<"$open_numbers")

project_items=""

if [ "$open_count" -eq 0 ]; then
  target_status="Done"
elif [ "$force_in_progress" = "true" ]; then
  target_status="In progress"
else
  project_items=$(project_gh item-list "$project_number" \
    --owner "$project_owner" \
    --format json \
    --limit 500)
  in_progress_count=$(jq \
    --arg repository "$repository" \
    --argjson open_numbers "$open_numbers" \
    '[.items[] | select(
      .status == "In progress" and
      .content.type == "Issue" and
      .content.repository == $repository and
      (.content.number as $number | $open_numbers | index($number)) != null
    )] | length' \
    <<<"$project_items")

  if [ "$in_progress_count" -gt 0 ]; then
    target_status="In progress"
  else
    target_status="Epics"
  fi
fi

if [ -z "$project_items" ]; then
  project_items=$(project_gh item-list "$project_number" \
    --owner "$project_owner" \
    --format json \
    --limit 500)
fi

parent_item_id=$(jq -r \
  --arg repository "$repository" \
  --argjson parent_number "$parent_number" \
  '.items[] | select(
    .content.type == "Issue" and
    .content.repository == $repository and
    .content.number == $parent_number
  ) | .id' \
  <<<"$project_items")
current_status=$(jq -r \
  --arg repository "$repository" \
  --argjson parent_number "$parent_number" \
  '.items[] | select(
    .content.type == "Issue" and
    .content.repository == $repository and
    .content.number == $parent_number
  ) | .status' \
  <<<"$project_items")

if [ -z "$parent_item_id" ] || [ "$parent_item_id" = "null" ]; then
  echo "Epic #$parent_number is not present in project $project_owner/$project_number."
  exit 1
fi

project_id=$(project_gh view "$project_number" \
  --owner "$project_owner" \
  --format json \
  --jq '.id')
project_fields=$(project_gh field-list "$project_number" \
  --owner "$project_owner" \
  --format json)
status_field_id=$(jq -r \
  '.fields[] | select(.name == "Status") | .id' \
  <<<"$project_fields")
target_option_id=$(jq -r \
  --arg target_status "$target_status" \
  '.fields[] | select(.name == "Status") | .options[] |
    select(.name == $target_status) | .id' \
  <<<"$project_fields")

if [ -z "$target_option_id" ] || [ "$target_option_id" = "null" ]; then
  echo "Status option '$target_status' was not found in the project."
  exit 1
fi

echo "Epic #$parent_number: $open_count/$total_count sub-issues open."
echo "Epic #$parent_number: status '$current_status' -> '$target_status'."

if [ "$dry_run" = "true" ]; then
  echo "Dry run enabled; no changes were made."
  exit 0
fi

if [ "$target_status" = "Done" ] && [ "$parent_state" = "open" ]; then
  repo_api \
    "repos/$repository/issues/$parent_number" \
    --method PATCH \
    -f state=closed \
    -f state_reason=completed \
    >/dev/null
elif [ "$target_status" != "Done" ] && [ "$parent_state" = "closed" ]; then
  repo_api \
    "repos/$repository/issues/$parent_number" \
    --method PATCH \
    -f state=open \
    >/dev/null
fi

if [ "$current_status" != "$target_status" ]; then
  project_gh item-edit \
    --id "$parent_item_id" \
    --project-id "$project_id" \
    --field-id "$status_field_id" \
    --single-select-option-id "$target_option_id" \
    >/dev/null
fi

echo "Epic #$parent_number synchronized successfully."
