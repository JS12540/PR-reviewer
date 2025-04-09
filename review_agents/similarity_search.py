from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np


def search_similar_contexts(embedding, top_k=3):
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client["pr_reviewer"]
    collection = db["repo_embeddings"]

    all_docs = list(collection.find())
    scored = []

    for doc in all_docs:
        stored_embedding = np.array(doc["embedding"])
        score = cosine_similarity([embedding], [stored_embedding])[0][0]
        scored.append((score, doc["content"]))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in scored[:top_k]]


