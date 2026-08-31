#!/usr/bin/env bash

set -euo pipefail

issue_number="${1:-}"
force_in_progress="${2:-false}"
repository="${GITHUB_REPOSITORY:-viniciusnevescosta/A-Maze-ing}"
repository_owner="${repository%%/*}"
repository_name="${repository#*/}"
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

project_api() {
  GH_TOKEN="$PROJECT_TOKEN" gh api graphql "$@"
}

get_project_item() {
  local number="$1"

  project_api \
    -F owner="$repository_owner" \
    -F name="$repository_name" \
    -F number="$number" \
    -f query='
      query($owner: String!, $name: String!, $number: Int!) {
        repository(owner: $owner, name: $name) {
          issue(number: $number) {
            projectItems(first: 20) {
              nodes {
                id
                project { id }
                fieldValueByName(name: "Status") {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                  }
                }
              }
            }
          }
        }
      }' |
    jq -c --arg project_id "$project_id" '
      .data.repository.issue.projectItems.nodes[] |
      select(.project.id == $project_id)'
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

project_metadata=$(project_api \
  -F login="$project_owner" \
  -F number="$project_number" \
  -f query='
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          field(name: "Status") {
            ... on ProjectV2SingleSelectField {
              id
              options { id name }
            }
          }
        }
      }
    }')
project_id=$(jq -r '.data.user.projectV2.id // empty' \
  <<<"$project_metadata")
status_field_id=$(jq -r '.data.user.projectV2.field.id // empty' \
  <<<"$project_metadata")

if [ -z "$project_id" ] || [ -z "$status_field_id" ]; then
  echo "Project $project_owner/$project_number or its Status field was not found."
  exit 1
fi

if [ "$open_count" -eq 0 ]; then
  target_status="Done"
elif [ "$force_in_progress" = "true" ]; then
  target_status="In progress"
else
  target_status="Epics"

  while read -r open_number; do
    child_item=$(get_project_item "$open_number")
    child_status=$(jq -r '.fieldValueByName.name // empty' \
      <<<"$child_item")

    if [ "$child_status" = "In progress" ]; then
      target_status="In progress"
      break
    fi
  done < <(jq -r '.[]' <<<"$open_numbers")
fi

parent_item=$(get_project_item "$parent_number")
parent_item_id=$(jq -r '.id // empty' <<<"$parent_item")
current_status=$(jq -r '.fieldValueByName.name // empty' \
  <<<"$parent_item")

if [ -z "$parent_item_id" ]; then
  echo "Epic #$parent_number is not present in project $project_owner/$project_number."
  exit 1
fi

target_option_id=$(jq -r \
  --arg target_status "$target_status" \
  '.data.user.projectV2.field.options[] |
    select(.name == $target_status) | .id' \
  <<<"$project_metadata")

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
  project_api \
    -F project_id="$project_id" \
    -F item_id="$parent_item_id" \
    -F field_id="$status_field_id" \
    -F option_id="$target_option_id" \
    -f query='
      mutation(
        $project_id: ID!,
        $item_id: ID!,
        $field_id: ID!,
        $option_id: String!
      ) {
        updateProjectV2ItemFieldValue(input: {
          projectId: $project_id,
          itemId: $item_id,
          fieldId: $field_id,
          value: {singleSelectOptionId: $option_id}
        }) {
          projectV2Item { id }
        }
      }' \
    >/dev/null
fi

echo "Epic #$parent_number synchronized successfully."
