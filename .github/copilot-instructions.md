# Git commit message instructions

When generating a Git commit message in GitHub Desktop:

- Always write both the Summary and Description in English.
- Follow the Conventional Commits 1.0.0 specification.
- Format the Summary as `<type>[optional scope][!]: <description>`.
- Use one of these types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, or `revert`.
- Use a scope only when it adds clear context; do not invent one.
- Write the Summary in the imperative mood, use a lowercase description, omit the final period, and keep it at 72 characters or fewer.
- Always generate a non-empty Description that explains what changed and why. Do not merely repeat the Summary.
- Use concise bullet points in the Description when the commit contains multiple relevant changes.
- For a breaking change, add `!` before the colon and include a `BREAKING CHANGE: <explanation>` footer.
- If an issue number is clearly available from the branch name or context, add `Refs #<number>` as a footer. Never invent an issue number.
- Do not mention GitHub Copilot or the fact that the message was AI-generated.
- Output only the commit Summary and Description, without commentary.
