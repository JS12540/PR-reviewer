def read_diff():
    """Read the diff from the PR, embed the changes, and store in MongoDB."""
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
                "positions": [],
                "embeddings": None
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

        # Now we have all changes for the file, generate embeddings
        changes_text = "\n".join(file_changes[filename]["changes"])
        file_changes[filename]["embeddings"] = get_embeddings(changes_text)

        # Save file changes, full context, and embeddings to MongoDB
        file_data = {
            "filename": filename,
            "full_context": file_changes[filename]["full_context"],
            "changes": file_changes[filename]["changes"],
            "embeddings": file_changes[filename]["embeddings"]
        }
        collection.update_one(
            {"filename": filename},
            {"$set": file_data},
            upsert=True
        )

    return file_changes

    def review_code():
    reviewer = create_agents()
    changes = read_diff()

    for filename, details in changes.items():
        full_context = details["full_context"]
        changes_summary = "\n".join(details["changes"])
        changes_text = f"{filename}\n{changes_summary}"

        # 1. Get embedding of changes
        change_embedding = get_embedding(changes_text)

        # 2. Retrieve similar contexts from MongoDB
        similar_contexts = search_similar_contexts(change_embedding)
        similar_texts = "\n\n".join(similar_contexts)

        # 3. Construct the review prompt
        review_prompt = (
            f"### Full File Context:\n{full_context}\n\n"
            f"### Code Changes:\n{changes_summary}\n\n"
            f"### Similar Code Contexts:\n{similar_texts}\n\n"
            f"Review the changes considering the file and similar past code contexts."
        )

        # 4. Get AI Review
        chat_result = reviewer.initiate_chat(
            recipient=reviewer,
            message=review_prompt,
            max_turns=1
        )

        review_comment = chat_result.chat_history[-1].get("content", "")
        print(f"Review Comment for {filename}: {review_comment}")

        commit_id = get_commit_id()
        post_comment(review_comment, filename, 0, commit_id)
S