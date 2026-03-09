import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

session = requests.Session()

def generate_response(prompt):
    try:
        response = session.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
               "options": {
    "num_predict": 250,
    "temperature": 0.7,
    "num_ctx": 1024
}
            },
            timeout=180
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "").strip()

    except Exception as e:
        return f"Error: {str(e)}"