# Security Notes

## Token Handling

Never commit real Personal Access Tokens.

If a token is pasted into chat, logs, a terminal transcript, or a repository, treat it as compromised.

Recommended response:

1. Finish only the required immediate operation if the user understands the risk.
2. Tell the user to revoke the exposed token.
3. Recommend generating a new token with the smallest needed permissions.

## Minimum GitHub Token Permissions

For uploading files to an existing repository through the Contents API:

- Repository access: target repository only
- Contents: Read and write
- Metadata: Read-only

For public repository metadata reads, no token may be needed. For private repositories or writes, a token is required.

## Avoid Secret Persistence

Do not store tokens in:

- Project files
- README files
- Example scripts
- Commit messages
- Shell history where avoidable
- Shared logs

Use environment variables in examples:

```powershell
$env:GITHUB_TOKEN = "..."
```

Then read the token from the environment inside scripts.
