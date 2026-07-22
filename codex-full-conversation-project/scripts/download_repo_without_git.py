"""
Download a GitHub repository as a ZIP archive when git is unavailable.

Example:
  python download_repo_without_git.py --owner JonathanXL --repo Codex_Test --branch main --output ./downloaded
"""

import argparse
import shutil
import ssl
import urllib.request
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    zip_path = output / f"{args.repo}-{args.branch}.zip"
    url = f"https://codeload.github.com/{args.owner}/{args.repo}/zip/refs/heads/{args.branch}"

    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context, timeout=60) as response:
        with open(zip_path, "wb") as handle:
            shutil.copyfileobj(response, handle)

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(output)

    print(zip_path)


if __name__ == "__main__":
    main()

