import os
import openai
from openai import OpenAI
from pymongo import MongoClient
from git import Repo
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import tiktoken
import shutil
import stat

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)
def get_code_chunks(text, file_path):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return [{"content": chunk, "file_path": file_path} for chunk in splitter.split_text(text)]

def embed_text(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def process_repo(repo_path):
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.rb', '.go')):
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        text = f.read()
                        chunks = get_code_chunks(text, full_path)
                        for chunk in chunks:
                            embedding = embed_text(chunk["content"])
                            collection.insert_one({
                                "embedding": embedding,
                                "content": chunk["content"],
                                "file_path": chunk["file_path"]
                            })
                    except Exception as e:
                        print(f"Skipping {full_path}: {e}")

if __name__ == "__main__":
    repo_url = "https://github.com/JS12540/PR-reviewer.git"
    repo_path = "./cloned_repo"

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)

    Repo.clone_from(repo_url, repo_path)
    process_repo(repo_path)
