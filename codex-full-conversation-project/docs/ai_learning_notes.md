# AI Learning Notes

## What Another AI Should Infer

If asked to share Codex work between accounts, first separate:

- Codex task history
- Code project files
- Generated artifacts
- External service permissions

The answer differs for each category.

## Practical Recommendation

For real work, use a GitHub repository as the shared state layer.

Write down context in project files so the next account can continue without needing the original chat.

## Handoff Pattern

Use:

```text
README.md
HANDOFF.md
TASK_NOTES.md
```

Include:

- Goal
- Current state
- Important files
- Known problems
- Next steps
- Security notes

## No-Git Fallback Pattern

If the local environment has no `git`, do not stop.

Use:

1. GitHub ZIP download for reading projects.
2. GitHub Contents API for uploading small projects.
3. GitHub Contents API for deleting files.

## Validation Pattern

After building a handoff project:

1. Re-download the repository.
2. Read the files from scratch.
3. Confirm the next AI can recover the goal and workflow.
4. Run a secret scan.

## Quality Criteria

A good AI-readable project should answer:

- What happened?
- Why was it done that way?
- What commands or APIs were used?
- What failed?
- How was the failure fixed?
- What should the next AI do?
- What secrets must not be exposed?

