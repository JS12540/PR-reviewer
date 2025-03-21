import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
PR_NUMBER = os.getenv("PR_NUMBER")

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/comments"


def post_comment(body, path, position,commit_id):
    """Post a review comment on a specific line of the PR.
    
    Args:
        body: The content of the comment
        path: The file path to comment on
        line: The line number to comment on
        position: The position in the diff to place the comment
    """
    pr_number = os.getenv("PR_NUMBER")
    repo = os.getenv("GITHUB_REPO")
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Endpoint for creating a PR review comment
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "position": position,  # This is required instead of "line"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in (200, 201):
        print(f"Comment added to {path} at position {position}")
    else:
        print(f"Failed to add comment: {response.text} with status code {response.status_code}")


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


def get_diff_position(path, line):
    """Get the diff position for a given path and line."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(GITHUB_API_URL, headers=headers)
    files = response.json()

    for file in files:
        if file['filename'] == path:
            patch = file['patch'].split('\n')
            added_line_count = 0
            for i, patch_line in enumerate(patch):
                # Identify the hunk header to track line numbers
                if patch_line.startswith('@@'):
                    hunk_info = patch_line.split(' ')[2]  # Example: "+1,10"
                    start_line = int(hunk_info.split(',')[0][1:])  # Skip the '+'

                # Count only added lines
                if patch_line.startswith('+'):
                    added_line_count += 1

                # Match the added line with given 'line'
                if added_line_count == line:
                    return i  # Position in the patch

    return None
