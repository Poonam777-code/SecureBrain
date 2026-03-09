from flask import Flask, render_template, request, jsonify
from ai_engine import generate_response
from risk_engine import analyze_url

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"response": "Please type something."})

    reply = generate_response(query)
    return jsonify({"response": reply})

# ✅ NEW PAGE ROUTE (YOU WERE MISSING THIS)
@app.route("/url-check")
def url_check_page():
    target = request.args.get("target", "")
    return render_template("url_check.html", target=target)

@app.route("/blocked-sites")
def blocked_sites():
    return render_template("blocked_sites.html")

# ✅ API ROUTE
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url", "").strip()
    result = analyze_url(url)
    return jsonify(result)

import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)