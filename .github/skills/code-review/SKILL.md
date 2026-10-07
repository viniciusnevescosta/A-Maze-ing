---
name: code-review
description: Review A-Maze-ing pull requests against linked issue criteria, Python quality gates, maze invariants, and GitHub Actions safety.
---

# A-Maze-ing code review

Review the pull request diff and its linked issue. Focus on defects introduced
by the change, not unfinished work belonging to future backlog issues.

Do not apply the 42 C Norm to Python code. This project follows its Python
subject, flake8, mypy, PEP 257, and the repository conventions.

## Review priorities

Report issues that can cause:

- incorrect behavior or a subject violation;
- crashes, unclear errors, or leaked resources;
- inconsistent maze data or invalid output;
- security or permission problems in GitHub Actions;
- regressions not covered by proportionate tests.

Do not repeat flake8 or mypy diagnostics unless they reveal a behavioral risk.
Do not require tests for empty scaffolding or configuration-only changes.

## Python requirements

When relevant to the changed code, verify:

- compatibility with Python 3.10 or later;
- type hints and successful mypy checking;
- useful PEP 257 docstrings for functions and classes;
- graceful handling of invalid input and filesystem errors;
- context managers for files and other resources;
- clear, single-purpose functions and readable names;
- `make check` remains usable.

## Maze requirements

When maze functionality is changed, verify:

- entry and exit are distinct and within bounds;
- neighboring cells agree about shared walls;
- external borders remain closed;
- every non-pattern cell is reachable;
- seeded generation is reproducible;
- no open 3x3 area is created;
- `PERFECT=True` produces exactly one path;
- non-perfect mode has at least two independent routes;
- wall bits use North=1, East=2, South=4, West=8;
- output rows, blank line, coordinates, path and final newlines follow the
  required format;
- coordinate and direction conventions remain consistent.

## GitHub Actions

When workflows or automation are changed, verify:

- permissions use the least privilege necessary;
- secrets are never printed or exposed to forked code;
- `pull_request_target` never executes untrusted PR code;
- automations are idempotent and do not duplicate or delete unrelated data;
- failures do not bypass the required human CODEOWNER approval.

## Feedback style

Write all review summaries and comments in Brazilian Portuguese (pt-BR).
Keep code, identifiers, file paths, commands, and exact error messages in
their original language.

Leave one actionable issue per comment. Explain the failing scenario, its
impact, and the smallest reasonable correction. Prefer changed lines and avoid
speculative, cosmetic, or duplicate comments.

The Copilot review is advisory. Never treat it as a replacement for peer review
or the required CODEOWNER approval.
