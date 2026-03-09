import re
import os
from urllib.parse import urlparse

BLACKLIST_PATH = os.path.join("data", "phishing_blacklist.txt")

def load_blacklist():
    if not os.path.exists(BLACKLIST_PATH):
        return []
    with open(BLACKLIST_PATH, "r") as f:
        return [line.strip().lower() for line in f.readlines()]

def analyze_url(url):

    risk = 0
    reasons = []

    if not url:
        return {
            "risk_score": 0,
            "security_level": "Invalid URL",
            "action": "block",
            "reasons": ["No URL entered"]
        }

    if not url.startswith("http"):
        url = "http://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    ##################################
    # HTTPS CHECK
    ##################################

    if not url.startswith("https://"):
        risk += 30
        reasons.append("❌ Connection is not encrypted (HTTP)")

    else:
        reasons.append("✅ Secure HTTPS connection")

    ##################################
    # IP ADDRESS CHECK
    ##################################

    if re.search(r"\d+\.\d+\.\d+\.\d+", domain):
        risk += 20
        reasons.append("⚠ Website uses IP address")

    ##################################
    # SUSPICIOUS KEYWORDS
    ##################################

    phishing_words = [
        "login","verify","update","secure","account",
        "bank","paypal","bonus","free","gift"
    ]

    for word in phishing_words:
        if word in domain:
            risk += 25
            reasons.append(f"⚠ Suspicious keyword detected: {word}")
            break

    ##################################
    # TOO MANY DASHES
    ##################################

    if domain.count("-") > 2:
        risk += 10
        reasons.append("⚠ Too many '-' in domain")

    ##################################
    # LONG DOMAIN
    ##################################

    if len(domain) > 30:
        risk += 10
        reasons.append("⚠ Very long domain name")

    ##################################
    # BLACKLIST CHECK
    ##################################

    blacklist = load_blacklist()

    for bad in blacklist:
        if bad in domain:
            risk += 50
            reasons.append("🚨 Domain found in phishing blacklist")
            break

    ##################################
    # FINAL DECISION
    ##################################

    risk = min(risk,100)

    if risk < 25:
        level = "Safe"
        action = "allow"

    elif risk < 60:
        level = "Suspicious"
        action = "warning"

    else:
        level = "Dangerous"
        action = "block"

    return {
        "risk_score": risk,
        "security_level": level,
        "action": action,
        "reasons": reasons
    }