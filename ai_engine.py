from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import requests
import re

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(BASE_DIR, "knowledge_base.txt")

# Load knowledge base
with open(kb_path, "r", encoding="utf-8") as f:
    knowledge = [k.strip() for k in f.read().split("\n\n") if k.strip()]

embeddings = model.encode(knowledge)

THRESHOLD = 0.65


# ---------- Greeting handler ----------
def check_greeting(query):
    greetings = ["hello", "hi", "hii", "hey"]
    if query.lower() in greetings:
        return "Hello! How can I help you today?"
    return None


# ---------- Simple math ----------
def solve_math(query):
    try:
        if re.match(r"^[0-9+\-*/ ().]+$", query):
            return str(eval(query))
    except:
        pass
    return None


# ---------- Online search ----------
def search_online(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1
        }

        response = requests.get(url, params=params, timeout=10).json()

        if response.get("AbstractText"):
            return response["AbstractText"]

        if response.get("RelatedTopics"):
            for topic in response["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]

        return "I couldn't find a good answer online, but you can try rephrasing your question."

    except:
        return "Online search failed. Check internet connection."


# ---------- Main chatbot ----------
def generate_response(query):

    query = query.strip()

    if not query:
        return "Please type a question."

    # Greeting
    greet = check_greeting(query)
    if greet:
        return greet

    # Math
    math_result = solve_math(query)
    if math_result:
        return math_result

    # Knowledge base search
    query_embedding = model.encode([query])

    similarity = cosine_similarity(query_embedding, embeddings)[0]

    index = np.argmax(similarity)
    score = similarity[index]

    if score >= THRESHOLD:
        return knowledge[index]

    # Online search fallback
    return search_online(query)