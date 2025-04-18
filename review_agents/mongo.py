import os
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["codegraph_db"]

def store_codegraph(repo, codegraph):
    db.graphs.replace_one({"repo": repo}, {"repo": repo, "graph": codegraph}, upsert=True)

def get_codegraph(repo):
    doc = db.graphs.find_one({"repo": repo})
    return doc["graph"] if doc else None
