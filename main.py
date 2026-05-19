from fastapi import FastAPI
from sentence_transformers import SentenceTransformer

import numpy as np
import requests
import re

app = FastAPI()

# Embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

incident_db = []
embeddings_db = []

# Cosine similarity
def cosine_similarity(vec1, vec2):

    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )

# Clean noisy logs
def clean_log(line):

    # Remove timestamps
    line = re.sub(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        "",
        line
    )

    return line.strip()

# Group logs into chunks
def chunk_logs(lines, chunk_size=5):

    chunks = []

    for i in range(0, len(lines), chunk_size):

        chunk = lines[i:i+chunk_size]

        combined = "\n".join(chunk)

        chunks.append(combined)

    return chunks

# Ollama call
def ask_mistral(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"]

@app.get("/")
def home():

    return {
        "message": "AI Log Analyzer Running"
    }

# Load logs
@app.post("/load-logs")
def load_logs():

    global incident_db
    global embeddings_db

    incident_db.clear()
    embeddings_db.clear()

    with open("logs/app.log") as file:

        raw_lines = file.readlines()

    # Clean logs
    cleaned_lines = []

    for line in raw_lines:

        line = line.strip()

        if line:
            cleaned_lines.append(
                clean_log(line)
            )

    # Create incident chunks
    chunks = chunk_logs(cleaned_lines)

    # Generate embeddings
    for chunk in chunks:

        incident_db.append(chunk)

        embedding = model.encode(chunk)

        embeddings_db.append(embedding)

    return {
        "message": "Logs indexed successfully",
        "incident_chunks": len(chunks)
    }

# Search logs
@app.get("/search")
def search(query: str):

    query_embedding = model.encode(query)

    results = []

    for chunk, embedding in zip(
        incident_db,
        embeddings_db
    ):

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        results.append({
            "incident": chunk,
            "score": float(score)
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:3]

# Ask AI
@app.get("/ask")
def ask(query: str):

    query_embedding = model.encode(query)

    results = []

    for chunk, embedding in zip(
        incident_db,
        embeddings_db
    ):

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        if score > 0.2:

            results.append({
                "incident": chunk,
                "score": float(score)
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top_chunks = results[:3]

    context = "\n\n".join(
        [
            chunk["incident"]
            for chunk in top_chunks
        ]
    )

    prompt = f"""
Analyze the following logs and answer the question.

Logs:
{context}

Question:
{query}

Answer:
"""

    answer = ask_mistral(prompt)

    return {
        "question": query,
        "answer": answer,
        "context_used": top_chunks
    }