
import requests, re, os
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
from textblob import TextBlob
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -----------------------------
# LOAD MODEL
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# LOAD KNOWLEDGE BASE
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_FILE = os.path.join(BASE_DIR, "knowledge_base.txt")

def load_kb():
    if os.path.exists(KB_FILE):
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return [k.strip() for k in f.read().split("\n\n") if k.strip()]
    return []

knowledge = load_kb()
embeddings = model.encode(knowledge) if knowledge else None

# -----------------------------
# SAVE NEW KNOWLEDGE
# -----------------------------
def save_kb(q, a):
    try:
        with open(KB_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n{a}")
    except:
        pass

# -----------------------------
# CLEAN
# -----------------------------
def clean(text):
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -----------------------------
# SPELL FIX
# -----------------------------
def fix(q):
    try:
        if len(q.split()) <= 3:
            return str(TextBlob(q).correct())
    except:
        pass
    return q

# -----------------------------
# NORMALIZE
# -----------------------------
def normalize(q):
    q = q.lower()
    q = re.sub(r"[^\w\s]", "", q)
    return q.strip()

# -----------------------------
# KB SEARCH (AI 🔥)
# -----------------------------
def search_kb(q):
    global embeddings, knowledge

    knowledge = load_kb()
    if not knowledge:
        return None

    embeddings = model.encode(knowledge)

    q_emb = model.encode([q])
    sim = cosine_similarity(q_emb, embeddings)[0]

    idx = np.argmax(sim)

    if sim[idx] > 0.5:
        return knowledge[idx]

    return None

# -----------------------------
# DUCKDUCKGO API
# -----------------------------
def ddg(q):
    try:
        url = f"https://api.duckduckgo.com/?q={q}&format=json"
        data = requests.get(url, timeout=5).json()
        if data.get("AbstractText"):
            return data["AbstractText"]
    except:
        pass
    return None

# -----------------------------
# WIKIPEDIA
# -----------------------------
def wiki(q):
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":q,"format":"json"},
            timeout=6
        ).json()

        results = search.get("query",{}).get("search",[])
        if results:
            title = results[0]["title"]

            res = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}",
                timeout=6
            )

            if res.status_code == 200:
                return res.json().get("extract")
    except:
        pass
    return None

# -----------------------------
# WEB SEARCH
# -----------------------------
def web(q):
    try:
        url = f"https://html.duckduckgo.com/html/?q={q}"
        r = requests.get(url, headers=HEADERS, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")

            if "uddg=" in link:
                import urllib.parse
                link = urllib.parse.parse_qs(
                    urllib.parse.urlparse(link).query
                ).get("uddg", [""])[0]

            page = requests.get(link, headers=HEADERS, timeout=5)
            text = " ".join(p.get_text() for p in BeautifulSoup(page.text, "html.parser").find_all("p")[:5])

            if len(text) > 150:
                return clean(text)
    except:
        pass
    return None

# -----------------------------
# SUMMARIZE
# -----------------------------
def summarize(text):
    parts = re.split(r'(?<=[.!?]) +', text)
    return " ".join(parts[:3])[:500]

# -----------------------------
# MAIN ENGINE 🔥
# -----------------------------
def generate_response(query):

    if not query.strip():
        return "Please type something."

    query = normalize(query)
    query = fix(query)

    # greeting
    if query.split() and query.split()[0] in ["hi","hello","hey","hii"]:
        return "Hello! 😊 How can I help you today?"

    # math
    try:
        if re.fullmatch(r"[0-9+\-*/ ().]+", query):
            return str(eval(query, {"__builtins__":None}, {}))
    except:
        pass

    # 🔥 STEP 1: KNOWLEDGE BASE
    kb = search_kb(query)
    if kb:
        return kb

    # 🔥 STEP 2: DUCKDUCKGO
    d = ddg(query)
    if d:
        ans = summarize(d)
        save_kb(query, ans)
        return ans

    # 🔥 STEP 3: WIKIPEDIA
    w = wiki(query)
    if w:
        ans = summarize(w)
        save_kb(query, ans)
        return ans

    # 🔥 STEP 4: WEB
    web_ans = web(query)
    if web_ans:
        ans = summarize(web_ans)
        save_kb(query, ans)
        return ans

    return "I couldn't find a good answer. Try asking differently."


def generate_response(query):

    if not query.strip():
        return "Please type something."

    original_query = query.lower().strip()

    # -----------------------------
    #  STRONG GREETING DETECTION (FIRST)
    # -----------------------------
    greetings = [
        "hi","hello","hey","hii","hiii","helo","helloo","gello"
    ]

    if any(original_query.startswith(g) for g in greetings):
        return "Hello! 😊 How can I help you today?"

    # -----------------------------
    # NORMAL PROCESSING
    # -----------------------------
    query = normalize(query)
    query = fix(query)

    # -----------------------------
    # MATH
    # -----------------------------
    try:
        if re.fullmatch(r"[0-9+\-*/ ().]+", query):
            return str(eval(query, {"__builtins__":None}, {}))
    except:
        pass

    # -----------------------------
    # 🔥 KNOWLEDGE BASE
    # -----------------------------
    kb = search_kb(query)
    if kb:
        return kb

    # -----------------------------
    # DUCKDUCKGO
    # -----------------------------
    d = ddg(query)
    if d:
        ans = summarize(d)
        save_kb(query, ans)
        return ans

    # -----------------------------
    # WIKIPEDIA
    # -----------------------------
    w = wiki(query)
    if w:
        ans = summarize(w)
        save_kb(query, ans)
        return ans

    # -----------------------------
    # WEB SEARCH
    # -----------------------------
    web_ans = web(query)
    if web_ans:
        ans = summarize(web_ans)
        save_kb(query, ans)
        return ans

    # -----------------------------
    # FINAL FALLBACK
    # -----------------------------
    return f"{query.capitalize()} is a general topic. Please try asking more clearly."
