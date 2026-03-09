import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Get correct file path (important for Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
knowledge_path = os.path.join(BASE_DIR, "security_knowledge.txt")

# Load knowledge base
with open(knowledge_path, "r", encoding="utf-8") as f:
    knowledge_base = f.read().split("\n\n")

# Convert knowledge text into vectors
vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(knowledge_base)


def generate_response(user_input):

    if not user_input:
        return "Please ask a cybersecurity question."

    # Convert user input into vector
    user_vector = vectorizer.transform([user_input])

    # Find similarity
    similarity = cosine_similarity(user_vector, vectors)

    # Get best answer
    best_index = similarity.argmax()

    return knowledge_base[best_index]