from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import requests

# Load lightweight model
model = SentenceTransformer("all-MiniLM-L6-v2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(BASE_DIR, "knowledge_base.txt")

# Load knowledge base
with open(kb_path, "r", encoding="utf-8") as f:
    knowledge = [k.strip() for k in f.read().split("\n\n") if k.strip()]

# Create embeddings
embeddings = model.encode(knowledge)

# similarity threshold
THRESHOLD = 0.55


def search_online(query):
    """
    Simple online search fallback
    Uses DuckDuckGo Instant API (no key needed)
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1
        }

        res = requests.get(url, params=params, timeout=5).json()

        if res.get("AbstractText"):
            return res["AbstractText"]

        elif res.get("RelatedTopics"):
            for topic in res["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]

        return "I couldn't find a reliable answer online."

    except:
        return "Online search failed. Please check your internet connection."


def generate_response(query):

    if not query.strip():
        return "Please type a question."

    query_embedding = model.encode([query])

    similarity = cosine_similarity(query_embedding, embeddings)[0]

    index = np.argmax(similarity)
    score = similarity[index]

    # If similarity is strong → return local knowledge
    if score >= THRESHOLD:
        return knowledge[index]

    # Otherwise search online
    return search_online(query)