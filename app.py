from flask import Flask, render_template, request, jsonify
from ai_engine import generate_response
from risk_engine import analyze_url
import requests
from bs4 import BeautifulSoup
from search_engine import on_search_click
import os

app = Flask(__name__, static_folder="static")


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHATBOT (UNCHANGED)
# =========================
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"response": "Invalid request"})

    query = str(data.get("query", "")).strip()
    if not query:
        return jsonify({"response": "Please type something."})

    reply = generate_response(query)
    return jsonify({"response": reply})


# =========================
# SMART SEARCH (UNCHANGED)
# =========================
@app.route("/smart-search", methods=["POST"])
def smart_search():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"type": "error", "message": "No query received"})

        query = str(data.get("query", "")).strip().lower()
        if query == "":
            return jsonify({"type": "error", "message": "Empty query"})

        query_words = query.split()
        question_keywords = ["what", "who", "define", "explain", "how", "why"]
        search_keywords = [
            "price", "rate", "buy", "best", "top", "laptop", "phone",
            "under", "review", "compare", "shop"
        ]

        if any(word in query for word in question_keywords):
            response = generate_response(query)
            return jsonify({"type": "answer", "response": response})

        if any(word in query for word in search_keywords):
            return jsonify({"type": "results"})

        if len(query_words) <= 2:
            return jsonify({"type": "results"})

        return jsonify({"type": "results"})

    except Exception as e:
        print("ERROR in smart_search:", e)
        return jsonify({"type": "error", "message": "Server error"})


# =========================
# SECURE SEARCH ENGINE (UNCHANGED)
# =========================
@app.route("/secure-search", methods=["POST"])
def secure_search():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://duckduckgo.com/html/?q={query}"

        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []

        links = soup.find_all("a", class_="result__a")
        for link_tag in links:
            title = link_tag.get_text()
            link = link_tag.get("href")
            if not link:
                continue

            if "uddg=" in link:
                import urllib.parse
                link = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("uddg", [""])[0]

            if not link.startswith("https"):
                continue

            results.append({"title": title, "link": link, "snippet": "Secure result", "status": "safe"})
            if len(results) >= 8:
                break

        if len(results) == 0:
            guessed_url = f"https://www.{query}.com"
            results.append({"title": f"Go to {query}", "link": guessed_url, "snippet": "Direct website access", "status": "safe"})

        results.append({"title": f"Search more results for '{query}'", "link": f"https://duckduckgo.com/?q={query}", "snippet": "View more results securely", "status": "safe"})

        return jsonify({
            "results": results,
            "images": [{"link": f"https://duckduckgo.com/?q={query}&iax=images&ia=images"}],
            "videos": [{"link": f"https://www.youtube.com/results?search_query={query}"}],
            "shopping": [{"link": f"https://duckduckgo.com/?q=buy+{query}"}]
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "results": [{"title": "Open search", "link": f"https://duckduckgo.com/?q={query}", "snippet": "Fallback search", "status": "safe"}],
            "images": [], "videos": [], "shopping": []
        })


# =========================
# SECURE SEARCH PAGE (NEW)
# =========================

@app.route("/secure-search-page")
def secure_search_page():
    query = request.args.get("query", "")
    ai_mode = request.args.get("ai_mode", "True") == "True"

    # Call your search logic
    results_by_tab = on_search_click(query, ai_mode)

    # Render the template with results
    return render_template(
        "secure_search_page.html",
        query=query,
        ai_mode=ai_mode,
        results_by_tab=results_by_tab
    )


# =========================
# URL CHECK (UNCHANGED)
# =========================
@app.route("/url-check")
def url_check_page():
    target = request.args.get("target", "")
    return render_template("url_check.html", target=target)


@app.route("/check_url", methods=["POST"])
def check_url():
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"status": "error"})
        url = data.get("url", "").strip()
        result = analyze_url(url)
        return jsonify(result)
    except Exception as e:
        print("ERROR in check_url:", e)
        return jsonify({"status": "error"})


# =========================
# BLOCKED SITES PAGE (UNCHANGED)
# =========================
@app.route("/blocked-sites")
def blocked_sites():
    return render_template("blocked_sites.html")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)