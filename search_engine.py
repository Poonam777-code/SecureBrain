# search_engine.py
import requests
from typing import List, Dict

def on_search_click(query: str, ai_mode: bool = True) -> Dict[str, List[Dict]]:
    """
    Perform search across multiple sources and return tabbed results.
    Tabs: All, Shopping, Images, Videos, Short Videos, News
    Each result is a dict: {title/content, link/url, type, final_score}
    """
    tabs = {
        "All": [],
        "Shopping": [],
        "Images": [],
        "Videos": [],
        "Short Videos": [],
        "News": []
    }

    try:
        # ===== EXAMPLE: All/Web =====
        # Replace with your Google/Bing Custom Search API call
        tabs["All"].append({
            "title": f"Result for {query} - All",
            "link": f"https://duckduckgo.com/?q={query}",
            "type": "web",
            "final_score": 1.0
        })

        # ===== Shopping =====
        tabs["Shopping"].append({
            "title": f"Buy {query} - Example Shop",
            "link": f"https://www.ebay.com/sch/i.html?_nkw={query}",
            "type": "shopping",
            "final_score": 1.0
        })

        # ===== Images =====
        tabs["Images"].append({
            "title": f"{query} Image",
            "link": f"https://www.pexels.com/search/{query}/",
            "type": "image",
            "final_score": 1.0
        })

        # ===== Videos =====
        tabs["Videos"].append({
            "title": f"{query} Video",
            "link": f"https://www.youtube.com/results?search_query={query}",
            "type": "video",
            "final_score": 1.0
        })

        # ===== Short Videos =====
        tabs["Short Videos"].append({
            "title": f"{query} Short Video",
            "link": f"https://www.youtube.com/results?search_query={query}+shorts",
            "type": "short_video",
            "final_score": 1.0
        })

        # ===== News =====
        tabs["News"].append({
            "title": f"{query} News",
            "link": f"https://newsapi.org/search?q={query}",
            "type": "news",
            "final_score": 1.0
        })

        # ===== Optional AI Boost =====
        if ai_mode:
            for tab, results in tabs.items():
                for r in results:
                    r["final_score"] *= 1.2  # simple boost example

    except Exception as e:
        print("Error in search_engine:", e)

    return tabs


# Example usage:
if __name__ == "__main__":
    query = "laptop"
    tabs = on_search_click(query, ai_mode=True)
    for tab, results in tabs.items():
        print(f"=== {tab} ===")
        for r in results[:5]:
            print(r)