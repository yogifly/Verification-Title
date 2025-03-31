from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz.distance import Levenshtein
from metaphone import doublemetaphone
import faiss
import numpy as np
import re

# Import external lists
from existing_titles import existing_titles
from restricted_words import restricted_words
from forbidden_prefix_suffix import forbidden_prefix_suffix

app = Flask(__name__)
CORS(app)

# Load SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Title Preprocessing
def preprocess_title(title):
    title = title.lower()
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)  # Remove special characters
    title = re.sub(r'\s+', ' ', title).strip()  # Remove extra spaces
    return title

# Phonetic Encoding
def phonetic_encoding(title):
    words = title.split()
    return [doublemetaphone(word) for word in words]  # Returns primary & alternate codes

# Cosine Similarity using SBERT
def calculate_cosine_similarity(title1, title2):
    embeddings = model.encode([title1, title2])
    similarity = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])  # Convert to float
    return similarity

# Jaccard Similarity
def calculate_jaccard_similarity(title1, title2):
    set1, set2 = set(title1.split()), set(title2.split())
    return float(len(set1 & set2) / len(set1 | set2))  # Convert to float

# Levenshtein Distance Calculation
def calculate_levenshtein_distance(title1, title2):
    return float(Levenshtein.normalized_similarity(title1, title2))  # Convert to float

# Check Forbidden Prefix/Suffix
def has_forbidden_prefix_suffix(title):
    words = title.split()
    return any(word in forbidden_prefix_suffix for word in words)

# Check for Restricted Words
def contains_restricted_words(title):
    words = set(title.split())
    return bool(words & restricted_words)

# ---------------------------
# 🔥 FAISS Setup for Fast Search
# ---------------------------

# Create embeddings for existing titles
title_embeddings = model.encode([preprocess_title(title) for title in existing_titles])
title_embeddings = np.array(title_embeddings).astype('float32')

# Define FAISS index
dimension = title_embeddings.shape[1]  # 384 dimensions for SBERT
index = faiss.IndexFlatL2(dimension)  # Using L2 distance for similarity
index.add(title_embeddings)  # Add all embeddings to the FAISS index


# ---------------------------
# 🚀 Final Title Verification with FAISS
# ---------------------------

def verify_title(new_title):
    new_title = preprocess_title(new_title)

    # Check restricted words & prefix/suffix
    if contains_restricted_words(new_title):
        return {"status": "Rejected", "reason": "Contains restricted words"}

    if has_forbidden_prefix_suffix(new_title):
        return {"status": "Rejected", "reason": "Contains forbidden prefix/suffix"}

    # Create embedding for new title
    new_embedding = model.encode([new_title]).astype('float32')

    # Search using FAISS to get top 5 nearest neighbors
    D, I = index.search(new_embedding, 5)  # D = distance, I = index of nearest neighbors

    max_similarity = 0.0
    matched_title = None

    for idx, dist in zip(I[0], D[0]):
        if idx == -1:
            continue

        existing_title = preprocess_title(existing_titles[idx])

        # Calculate other similarities
        cosine_sim = calculate_cosine_similarity(new_title, existing_title)
        jaccard_sim = calculate_jaccard_similarity(new_title, existing_title)
        levenshtein_sim = calculate_levenshtein_distance(new_title, existing_title)

        # Phonetic similarity check
        new_phonetic = phonetic_encoding(new_title)
        existing_phonetic = phonetic_encoding(existing_title)

        phonetic_match = any(
            p1 in existing_phonetic for p1 in new_phonetic
        )  # Check if any phonetic code matches

        # Average similarity score
        final_similarity = (cosine_sim + jaccard_sim + levenshtein_sim) / 3

        if phonetic_match:
            final_similarity += 0.1  # Boost for phonetic match

        if final_similarity > max_similarity:
            max_similarity = final_similarity
            matched_title = existing_titles[idx]

    verification_probability = round(max_similarity * 100, 2)

    # Reject if similarity >= 75%
    if max_similarity >= 0.75:
        return {
            "status": "Rejected",
            "reason": f"Too similar to existing title '{matched_title}'",
            "similarity_score": round(float(max_similarity), 3),
            "verification_probability": verification_probability
        }

    return {
        "status": "Accepted",
        "verification_probability": verification_probability
    }

# ---------------------------
# 🌐 API Route for Title Verification
# ---------------------------

@app.route('/verify_title', methods=['POST'])
def title_verification():
    data = request.json
    new_title = data.get("title", "").strip()

    if not new_title:
        return jsonify({"error": "Title cannot be empty"}), 400

    result = verify_title(new_title)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
