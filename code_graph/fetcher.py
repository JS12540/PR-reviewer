import os
import requests
from base64 import b64decode

def get_all_files_in_repo(repo, ref="main"):
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    api_url = f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return [f['path'] for f in response.json().get("tree", []) if f["path"].endswith(".py")]

def fetch_file_content(repo, path, ref="main"):
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        return b64decode(content).decode()
    return ""
