#!/usr/bin/env bash
set -euo pipefail

export GH_TOKEN="$REPO_TOKEN"
default_branch=$(gh api "repos/$GITHUB_REPOSITORY" --jq .default_branch)
pulls=$(gh api --paginate --slurp \
  "repos/$GITHUB_REPOSITORY/pulls?state=closed&sort=updated&direction=desc&per_page=100")

while read -r pr; do
  branch=$(jq -r '.head.ref' <<<"$pr")
  number="${branch%%-*}"
  [[ "$number" =~ ^[0-9]+$ ]] || continue
  body=$(jq -r '.body // ""' <<<"$pr")
  # Only finish the branch issue when the PR explicitly claims to close it.
  grep -Eiq "(closes|fixes|resolves)[[:space:]:]+#$number([^0-9]|$)" \
    <<<"$body" || continue
  issue=$(gh api "repos/$GITHUB_REPOSITORY/issues/$number")
  jq -e 'has("pull_request") or any(.labels[]?; .name == "epic")' \
    <<<"$issue" >/dev/null && continue

  # Preserve tasks deliberately reopened after their implementation merged.
  merged_at=$(jq -r .merged_at <<<"$pr")
  events=$(gh api --paginate --slurp \
    "repos/$GITHUB_REPOSITORY/issues/$number/events?per_page=100")
  if jq -e --arg merged "$merged_at" \
    'any(.[][]; .event == "reopened" and .created_at > $merged)' \
    <<<"$events" >/dev/null; then
    continue
  fi

  item=$(GH_TOKEN="$PROJECT_TOKEN" gh api graphql \
    -F number="$number" -f query='
    query($number: Int!) {
      repository(owner:"viniciusnevescosta", name:"A-Maze-ing") {
        issue(number:$number) {
          projectItems(first:100) { nodes {
            id project { id }
            fieldValueByName(name:"Status") {
              ... on ProjectV2ItemFieldSingleSelectValue { name }
            }
          } }
        }
      }
    }' --jq '.data.repository.issue.projectItems.nodes[] |
      select(.project.id == "PVT_kwHOA_3kws4Bhy9u")')
  status=$(jq -r '.fieldValueByName.name // empty' <<<"$item")
  if [ "$(jq -r .state <<<"$issue")" = closed ] && [ "$status" = Done ]; then
    continue
  fi

  gh issue close "$number" --repo "$GITHUB_REPOSITORY" --reason completed
  item_id=$(jq -r '.id // empty' <<<"$item")
  if [ -n "$item_id" ]; then
    GH_TOKEN="$PROJECT_TOKEN" gh api graphql \
      -F item_id="$item_id" -f query='
      mutation($item_id: ID!) {
        updateProjectV2ItemFieldValue(input: {
          projectId: "PVT_kwHOA_3kws4Bhy9u",
          itemId: $item_id,
          fieldId: "PVTSSF_lAHOA_3kws4Bhy9uzhgtaI8",
          value: {singleSelectOptionId: "98236657"}
        }) { projectV2Item { id } }
      }' >/dev/null
  fi
  bash .github/scripts/sync_epic_status.sh "$number"
done < <(jq -c --arg base "$default_branch" \
  '.[][] | select(.merged_at != null and .base.ref == $base)' <<<"$pulls")
