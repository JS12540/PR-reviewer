import os
from github_api import post_comment, get_diff_position
from ai_agent import create_agents
import requests

def read_diff():
    """Read the diff from the PR."""
    pr_number = os.getenv("PR_NUMBER")
    repo = os.getenv("GITHUB_REPO")
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch PR files")
        exit(1)

    files = response.json()

    code_changes = []
    for file in files:
        filename = file['filename']
        patch = file.get('patch', '').split('\n')

        for i, line in enumerate(patch):
            if line.startswith('+') and not line.startswith('+++'):
                code_changes.append({
                    "file": filename,
                    "line": i + 1,
                    "content": line[1:]
                })

    return code_changes


def review_code():
    reviewer = create_agents()

    # Get the code changes from PR
    changes = read_diff()

    for change in changes:
        file_path = change["file"]
        line_number = change["line"]
        code = change["content"]

        # Get diff position (replace with your logic if needed)
        position = get_diff_position(file_path, line_number)
        if position is None:
            print(f"Could not find position for {file_path} at line {line_number}")
            continue

        # Review the line with AI
        reviewer.initiate_chat(
            recipient=reviewer,
            message=f"Review this line:\n{code}",
            max_turns=2
        )
        print(f"Review Comment: {reviewer.chat_messages[-1]}")
        review_comment = reviewer.chat_messages[-1]

        # Add comment to PR using position instead of line_number
        post_comment(review_comment, file_path, position)


if __name__ == "__main__":
    review_code()
