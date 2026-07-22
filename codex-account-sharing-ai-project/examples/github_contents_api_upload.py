"""
Upload a local folder to a GitHub repository using the REST Contents API.

This is useful when the local environment does not have the `git` command.

Required environment variable:
  GITHUB_TOKEN

Example:
  python github_contents_api_upload.py --owner USER --repo REPO --branch main --local ./project --remote project
"""

import argparse
import base64
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def quote_path(path: str) -> str:
    return "/".join(urllib.parse.quote(part) for part in path.split("/"))


class GitHubContentsClient:
    def __init__(self, owner: str, repo: str, token: str):
        self.base = f"https://api.github.com/repos/{owner}/{repo}/contents"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Codex-Learning-Example",
        }
        self.context = ssl.create_default_context()

    def request(self, method: str, url: str, body: dict | None = None):
        data = None
        headers = dict(self.headers)
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=self.context, timeout=60) as response:
                text = response.read().decode("utf-8")
                return json.loads(text) if text else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            if exc.code == 404 and method == "GET":
                return None
            raise RuntimeError(f"GitHub API {method} failed: HTTP {exc.code} {detail}") from exc

    def get_file(self, remote_path: str, branch: str):
        url = f"{self.base}/{quote_path(remote_path)}?ref={urllib.parse.quote(branch)}"
        return self.request("GET", url)

    def put_file(self, remote_path: str, branch: str, content: bytes, message: str):
        existing = self.get_file(remote_path, branch)
        body = {
            "message": message,
            "content": base64.b64encode(content).decode("ascii"),
            "branch": branch,
        }
        if existing and existing.get("sha"):
            body["sha"] = existing["sha"]

        url = f"{self.base}/{quote_path(remote_path)}"
        return self.request("PUT", url, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--local", required=True)
    parser.add_argument("--remote", required=True)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN first.")

    local_dir = Path(args.local)
    if not local_dir.exists():
        raise SystemExit(f"Local directory not found: {local_dir}")

    client = GitHubContentsClient(args.owner, args.repo, token)
    uploaded = []

    for file_path in sorted(local_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(local_dir).as_posix()
        remote_path = f"{args.remote.rstrip('/')}/{rel}"
        result = client.put_file(
            remote_path=remote_path,
            branch=args.branch,
            content=file_path.read_bytes(),
            message=f"Upload {remote_path}",
        )
        uploaded.append(result["content"]["html_url"])

    print(json.dumps(uploaded, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
