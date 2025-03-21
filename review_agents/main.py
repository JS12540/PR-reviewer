import os
from github_api import post_comment
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

        position = 0  # GitHub diff positions are relative to the diff
        old_line, new_line = None, None

        for line in patch:
            if line.startswith('@@'):
                # Extract line numbers from the diff header
                _, old_info, new_info, _ = line.split(' ')
                old_line = int(old_info.split(',')[0][1:])
                new_line = int(new_info.split(',')[0][1:])
                position = 0  # Reset diff position at each hunk

            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                code_changes.append({
                    "file": filename,
                    "line": new_line,
                    "content": line[1:],  # Skip the leading +
                    "position": position
                })
                new_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line (just increment position, no comment needed)
                old_line += 1
                position += 1
            else:
                # Context line (no changes, just increment both line and position)
                old_line += 1
                new_line += 1
                position += 1

    return code_changes


def review_code():
    reviewer = create_agents()

    # Get the code changes from PR
    changes = read_diff()

    for change in changes:
        file_path = change["file"]
        position = change["position"]
        code = change["content"]

        # Review the line with AI
        reviewer.initiate_chat(
            recipient=reviewer,
            message=f"Review this line:\n{code}",
            max_turns=2
        )

        review_comment = reviewer.chat_messages[-1]
        print(f"Review Comment: {review_comment}")

        # Add comment using diff position
        post_comment(review_comment, file_path, position)


if __name__ == "__main__":
    review_code()
