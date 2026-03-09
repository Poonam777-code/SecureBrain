from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

# Load model (small and lightweight)
model = SentenceTransformer("all-MiniLM-L6-v2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(BASE_DIR, "knowledge_base.txt")

# Load knowledge
with open(kb_path, "r", encoding="utf-8") as f:
    knowledge = f.read().split("\n\n")

# Create embeddings
embeddings = model.encode(knowledge)

def generate_response(query):

    if not query.strip():
        return "Please type a question."

    query_embedding = model.encode([query])

    similarity = cosine_similarity(query_embedding, embeddings)

    index = np.argmax(similarity)

    return knowledge[index]