import os
from github_api import post_comment, get_commit_id
from ai_agent import create_agents
import requests
import re

def fetch_file_content(repo, filename, ref):
    """Fetch the entire content of the file from the repo."""
    url = f"https://api.github.com/repos/{repo}/contents/{filename}?ref={ref}"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch file content: {filename}")
        return None

    file_data = response.json()
    if "content" in file_data:
        import base64
        return base64.b64decode(file_data["content"]).decode("utf-8")
    return None


def read_diff():
    """Read the diff from the PR and include full file context."""
    pr_number = os.getenv("PR_NUMBER")
    repo = os.getenv("GITHUB_REPO")
    base_ref = os.getenv("BASE_REF")  # Base branch reference
    print(f"Base branch: {base_ref}")
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
    file_changes = {}

    for file in files:
        filename = file['filename']
        patch = file.get('patch', '')
        if not patch:
            continue
        
        # Fetch the full file content
        full_content = fetch_file_content(repo, filename, base_ref)
        if full_content is None:
            print(f"Skipping {filename} due to missing content")
            continue

        if filename not in file_changes:
            file_changes[filename] = {
                "full_context": full_content,
                "changes": [],
                "positions": []
            }
        
        patch_lines = patch.split('\n')
        position = 0
        for line in patch_lines:
            if line.startswith('@@'):
                # Extract line numbers from the diff header using regex
                match = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    new_line = int(match.group(1))
                    position = 0  # Reset position at each new diff
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                file_changes[filename]["changes"].append(f"Added: {line[1:]}")
                file_changes[filename]["positions"].append(position)
            elif line.startswith('-') and not line.startswith('---'):
                # Removed line
                file_changes[filename]["changes"].append(f"Removed: {line[1:]}")
            elif not line.startswith(('\\', '+++', '---')):
                # Context line (no changes)
                file_changes[filename]["changes"].append(f"Context: {line}")
            position += 1
    
    return file_changes

def find_valid_position(changes, positions):
    """Find a valid position in the diff for posting a comment.
    
    GitHub requires comments to be posted on unchanged context lines or added lines,
    not on removed lines or diff headers.
    
    Returns:
        int: A valid position in the diff, or None if no valid position found
    """
    for i, change in enumerate(changes):
        # Look for added lines or context lines (not removed lines)
        if change.startswith("Added:") or change.startswith("Context:"):
            # If this is a valid line with a corresponding position
            if i < len(positions):
                return positions[i]
    
    # Fallback - if there are any positions at all, use the first one
    if positions:
        return positions[0]
    
    return None

def review_code():
    reviewer = create_agents()

    # Get the code changes from PR
    changes = read_diff()

    for filename, details in changes.items():
        full_context = details["full_context"]
        changes_summary = "\n".join(details["changes"])

        # Include the full file context in the review request
        review_prompt = (
            f"### Full File Context:\n"
            f"{full_context}\n\n"
            f"### Code Changes:\n"
            f"{changes_summary}\n\n"
            f"Provide a review considering the entire file context."
        )

        # Review with AI
        chat_result = reviewer.initiate_chat(
            recipient=reviewer,
            message=review_prompt,
            max_turns=1
        )

        review_comment = chat_result.chat_history[-1].get("content", "")
        print(f"Review Comment for {filename}: {review_comment}")

        # Get a valid position for the comment - find the first added or unchanged line
        commit_id = get_commit_id()
        
        # Find a valid position for the comment
        valid_position = find_valid_position(details["changes"], details["positions"])
        
        if valid_position is not None:
            post_comment(review_comment, filename, valid_position, commit_id)
        else:
            print(f"Could not find a valid position for comment in {filename}")


if __name__ == "__main__":
    review_code()
