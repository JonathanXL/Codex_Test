# GitHub Operations

## Repositories Involved

Source sample repository:

```text
JonathanXL/Bond_trade
```

Target test and learning repository:

```text
JonathanXL/Codex_Test
```

## Download Without Git

When `git` was unavailable, the repository was downloaded with GitHub codeload:

```text
https://codeload.github.com/{owner}/{repo}/zip/refs/heads/main
```

Example:

```text
https://codeload.github.com/JonathanXL/Bond_trade/zip/refs/heads/main
```

## Upload Without Git

The GitHub Contents API was used.

Create or update:

```text
PUT /repos/{owner}/{repo}/contents/{path}
```

Required body:

```json
{
  "message": "Upload file",
  "content": "<base64 content>",
  "branch": "main"
}
```

For updates, add:

```json
{
  "sha": "<existing file sha>"
}
```

## Delete Without Git

Delete:

```text
DELETE /repos/{owner}/{repo}/contents/{path}
```

Required body:

```json
{
  "message": "Delete file",
  "sha": "<existing file sha>",
  "branch": "main"
}
```

## Permission Failure

Observed failure:

```text
HTTP 403
Resource not accessible by personal access token
```

Cause:

The token did not have write access to repository contents.

Fix:

Give the token target repository access and:

```text
Contents: Read and write
```

## Secret Handling

The real token is not included in this project.

Scripts should read:

```text
GITHUB_TOKEN
```

from the environment.

