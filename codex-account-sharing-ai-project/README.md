# Codex Account Project Sharing Playbook

This project turns a real Codex support conversation into a reusable learning package for other AI agents.

It teaches how to help a user move a Codex task/project between accounts by using a GitHub repository as the shared source of truth, even when the local environment does not have the `git` command installed.

## What This Covers

- How Codex tasks differ from code projects
- How two Codex accounts can share project state through GitHub
- How to clone or download a repository when `git` is unavailable
- How to upload files to GitHub with the REST Contents API
- How to handle Personal Access Token permission failures
- How to package a conversation into an AI-readable handoff project
- How to avoid leaking secrets into shared artifacts

## Key Lesson

Codex task history is usually account-bound. The most reliable way to share work across Codex accounts is to store the code, notes, handoff files, and project state in a Git repository that both accounts can access.

## Recommended Structure

```text
codex-account-sharing-ai-project/
  README.md
  conversation_summary.md
  workflow_guide.md
  security_notes.md
  examples/
    github_contents_api_upload.py
  templates/
    HANDOFF.md
```

## Safe Use

Never commit real access tokens, passwords, cookies, or private credentials. If a token appears in chat or logs, revoke it and generate a new one.
