"""
Upload a local directory to GitHub using the REST Contents API.

The token must be provided through the GITHUB_TOKEN environment variable.
Do not hardcode tokens in this file.
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


def request(method: str, url: str, token: str, body: dict | None = None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Codex-Full-Conversation-Project",
    }
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        if exc.code == 404 and method == "GET":
            return None
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"GitHub API failed: HTTP {exc.code} {detail}") from exc


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

    base = f"https://api.github.com/repos/{args.owner}/{args.repo}/contents"
    local_dir = Path(args.local)
    uploaded = []

    for file_path in sorted(local_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel = file_path.relative_to(local_dir).as_posix()
        remote_path = f"{args.remote.rstrip('/')}/{rel}"
        get_url = f"{base}/{quote_path(remote_path)}?ref={urllib.parse.quote(args.branch)}"
        existing = request("GET", get_url, token)
        body = {
            "message": f"Upload {remote_path}",
            "content": base64.b64encode(file_path.read_bytes()).decode("ascii"),
            "branch": args.branch,
        }
        if existing and existing.get("sha"):
            body["sha"] = existing["sha"]
        result = request("PUT", f"{base}/{quote_path(remote_path)}", token, body)
        uploaded.append(result["content"]["html_url"])

    print(json.dumps(uploaded, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

