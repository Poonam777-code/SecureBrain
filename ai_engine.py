from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import numpy as np
import requests
import os
import re
from urllib.parse import quote
from functools import lru_cache

# -----------------------------
# MODEL LOADING (LAZY)
# -----------------------------
model = None

def get_model():
    global model
    if model is None:
        print("Loading SecureBrain AI model... Please wait.", flush=True)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("SecureBrain AI model loaded successfully.", flush=True)
    return model

# -----------------------------
# LOAD KNOWLEDGE BASE
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(BASE_DIR, "knowledge_base.txt")

knowledge = []

if os.path.exists(kb_path):
    with open(kb_path, "r", encoding="utf-8") as f:
        knowledge = [k.strip() for k in f.read().split("\n\n") if k.strip()]

embeddings = None
THRESHOLD = 0.45

HEADERS = {
    "User-Agent": "SecureBrainChatBot/1.0"
}


# -----------------------------
# SPELL CORRECTION
# -----------------------------
def correct_spelling(query):
    try:
        return str(TextBlob(query).correct())
    except:
        return query


# -----------------------------
# GREETING
# -----------------------------
def check_greeting(query):

    greetings = [
        "hi","hello","hey","hii",
        "good morning","good evening","good afternoon"
    ]

    query = query.lower()

    for g in greetings:
        if query.startswith(g):
            return "Hello! How can I help you today?"

    return None


# -----------------------------
# SAFE MATH SOLVER
# -----------------------------
def solve_math(query):

    try:
        if re.fullmatch(r"[0-9+\-*/ ().]+", query):
            result = eval(query, {"__builtins__":None}, {})
            return str(result)
    except:
        pass

    return None


# -----------------------------
# PROGRAMMING DETECTOR
# -----------------------------
def is_programming_question(query):

    keywords = [
        "python","java","c++","javascript","html",
        "css","sql","error","bug","algorithm",
        "function","loop","class","compile",
        "program","code","exception"
    ]

    q = query.lower()

    return any(k in q for k in keywords)


# -----------------------------
# KNOWLEDGE SEARCH (LOCAL AI)
# -----------------------------
def search_knowledge(query):

    global embeddings

    if not knowledge:
        return None

    try:

        if embeddings is None:
            print("Creating knowledge embeddings...")
            embeddings = get_model().encode(
                knowledge,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

        query_embedding = get_model().encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        similarity = cosine_similarity(query_embedding, embeddings)[0]

        best_index = np.argmax(similarity)
        best_score = similarity[best_index]

        if best_score >= THRESHOLD:
            return knowledge[best_index]

    except Exception as e:
        print("Embedding search error:", e)

    return None


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text):

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------
# WIKIPEDIA SEARCH (CACHED)
# -----------------------------
@lru_cache(maxsize=100)
def wikipedia_search(query):

    try:

        search_url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action":"query",
            "list":"search",
            "srsearch":query,
            "format":"json"
        }

        r = requests.get(search_url, params=params, headers=HEADERS, timeout=8)

        data = r.json()

        results = data.get("query", {}).get("search", [])

        if not results:
            return None

        title = results[0]["title"]

        encoded = quote(title)

        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"

        r = requests.get(summary_url, headers=HEADERS, timeout=8)

        if r.status_code != 200:
            return None

        summary = r.json()

        extract = summary.get("extract")

        if extract:
            return extract[:700]

    except Exception as e:
        print("Wikipedia API error:", e)

    return None


# -----------------------------
# DICTIONARY SEARCH
# -----------------------------
def dictionary_search(query):

    try:

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"

        r = requests.get(url, headers=HEADERS, timeout=8)

        data = r.json()

        if isinstance(data, list):

            definition = data[0]["meanings"][0]["definitions"][0]["definition"]

            return definition

    except:
        pass

    return None


# -----------------------------
# STACKOVERFLOW SEARCH
# -----------------------------
def stackexchange_search(query):

    try:

        url = "https://api.stackexchange.com/2.3/search/advanced"

        params = {
            "order":"desc",
            "sort":"relevance",
            "q":query,
            "site":"stackoverflow",
            "filter":"withbody"
        }

        r = requests.get(url, params=params, timeout=8)

        data = r.json()

        items = data.get("items", [])

        if items:

            text = clean_text(items[0].get("body",""))

            if len(text) > 100:
                return text[:700]

    except Exception as e:
        print("StackOverflow API error:", e)

    return None


# -----------------------------
# FALLBACK
# -----------------------------
def fallback_explanation(query):

    return (
        "I couldn't find an exact answer for that question. "
        "Try asking in a different way or provide more details."
    )


# -----------------------------
# MAIN CHATBOT ENGINE
# -----------------------------
def generate_response(query):

    query = query.strip()

    if not query:
        return "Please type a question."

    query = correct_spelling(query)

    # Greeting
    greeting = check_greeting(query)
    if greeting:
        return greeting

    # Math
    math = solve_math(query)
    if math:
        return math

    # Local AI knowledge
    kb = search_knowledge(query)
    if kb:
        return kb

    # Wikipedia general knowledge
    wiki = wikipedia_search(query)
    if wiki:
        return wiki

    # Dictionary for single words
    if len(query.split()) == 1:
        definition = dictionary_search(query)
        if definition:
            return definition

    # Programming help
    if is_programming_question(query):
        stack = stackexchange_search(query)
        if stack:
            return stack

    return fallback_explanation(query)