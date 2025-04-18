import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]


def store_codegraph(repo, file_path, codegraph):
    """Store the code graph in MongoDB."""
    collection.update_one(
        {"repo": repo, "file_path": file_path},
        {"$set": {"code_graph": codegraph}},
        upsert=True
    )

    
def get_codegraph(repo, file_path):
    """Retrieve the code graph for a specific file in a repo."""
    doc = collection.find_one({"repo": repo, "file_path": file_path})
    return doc["code_graph"] if doc else None
