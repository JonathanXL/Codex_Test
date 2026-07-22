# Workflow Guide

## 1. Clarify What Is Being Shared

Ask whether the user means:

- A Codex task/chat thread
- A local code project
- Generated files or deliverables
- Plugin or connector permissions

Codex task history is usually account-bound. Code and artifacts should be shared through a repository or shared drive.

## 2. Prefer GitHub for Code Project Sharing

Recommended pattern:

1. Put code in a GitHub repository.
2. Add both accounts as collaborators if needed.
3. Store context in project files such as `README.md`, `HANDOFF.md`, or `TASK_NOTES.md`.
4. Let the second Codex account open or clone the same repository.

## 3. Check Local Tooling

Run:

```powershell
git --version
```

If `git` exists, use normal git workflows.

If `git` is missing, use GitHub ZIP download or the GitHub REST API.

## 4. Download Without Git

For public repositories, use GitHub codeload ZIP URLs:

```text
https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}
```

If PowerShell or `curl.exe` fails due to local TLS issues, Python `urllib` may work as an alternative.

## 5. Upload Without Git

Use the GitHub REST Contents API.

High-level steps:

1. Read repository metadata and default branch.
2. For each local file, compute its remote path.
3. Check whether that remote path already exists.
4. Base64 encode local file bytes.
5. Use `PUT /contents/{path}` to create or update.
6. Include `sha` when updating existing files.

## 6. Delete Without Git

High-level steps:

1. Get the remote file metadata.
2. Read the file `sha`.
3. Use `DELETE /contents/{path}` with `message`, `sha`, and `branch`.

For non-ASCII filenames, list the remote folder first and delete paths from the API response.

## 7. Package a Conversation for AI Learning

Create a project that includes:

- A concise README
- A conversation summary
- A repeatable workflow guide
- Security notes
- Example scripts with placeholders
- Handoff templates

Do not include actual tokens or private details.
