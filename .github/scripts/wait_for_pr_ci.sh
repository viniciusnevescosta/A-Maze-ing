#!/usr/bin/env bash
set -euo pipefail

# Read checks for GitHub's test merge commit, not an older branch commit.
for attempt in $(seq 1 60); do
  pr=$(gh api "repos/$GITHUB_REPOSITORY/pulls/$PR_NUMBER")
  head_sha=$(jq -r '.head.sha' <<<"$pr")
  merge_sha=$(jq -r '.merge_commit_sha // empty' <<<"$pr")

  if [ "$head_sha" != "$EXPECTED_HEAD_SHA" ]; then
    echo "::error::The PR changed after approval; a new review is needed."
    exit 1
  fi

  if [ -n "$merge_sha" ]; then
    checks=$(gh api --paginate --slurp \
      "repos/$GITHUB_REPOSITORY/commits/$merge_sha/check-runs?per_page=100")
    check=$(jq -c '[.[].check_runs[] | select(
      .name == "Lint and Tests" and .app.slug == "github-actions"
    )] | sort_by(.id) | last // {}' <<<"$checks")

    if [ "$(jq -r '.status // empty' <<<"$check")" = "completed" ]; then
      if [ "$(jq -r '.conclusion // empty' <<<"$check")" = "success" ]; then
        echo "CI passed for the current test merge commit."
        exit 0
      fi
      echo "::error::Lint and Tests did not pass; merge blocked."
      exit 1
    fi
  fi

  sleep 5
done

echo "::error::No successful CI check was available before the timeout."
exit 1
