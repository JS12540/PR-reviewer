import os
import requests

GITHUB_TOKEN = os.getenv("REPO_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
PR_NUMBER = os.getenv("PR_NUMBER")

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/comments"


def post_comment(body, path, line):
    """Post a comment on a specific line of the PR."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "body": body,
        "commit_id": get_commit_id(),
        "path": path,
        "line": line,
    }

    response = requests.post(GITHUB_API_URL, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Comment added to {path} on line {line}")
    else:
        print(f"Failed to add comment: {response.text}")


def get_commit_id():
    """Get the latest commit ID from the PR."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/commits"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        latest_commit = commits[-1]["sha"]
        return latest_commit
    else:
        print(f"Failed to fetch commit ID: {response.text}")
        return None
