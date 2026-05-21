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

def calculate_keyword_score(query, text):

    score = 0

    query_words = query.lower().split()

    text = text.lower()

    for word in query_words:

        if word in text:
            score += 0.1

    return score

# Clean noisy logs
def clean_log(line):

    # Remove timestamps
    line = re.sub(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        "",
        line
    )

    return line.strip()

def parse_log(line):

    parts = line.split()

    if len(parts) < 5:
        return None

    severity = parts[2]
    service = parts[3]

    message = " ".join(parts[4:])

    return {
        "severity": severity,
        "service": service,
        "message": message
    }

# Group logs into chunks
# Removing since this is fixed size chunking
# def chunk_logs(lines, chunk_size=5):

#     chunks = []

#     for i in range(0, len(lines), chunk_size):

#         chunk = lines[i:i+chunk_size]

#         combined = "\n".join(chunk)

#         chunks.append(combined)

#     return chunks

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

    # Parse logs
    parsed_logs = []

    for line in raw_lines:

        line = line.strip()

        if line:

            parsed = parse_log(line)

            if parsed:
                parsed_logs.append(parsed)

    # Group logs by service
    service_groups = {}

    for log in parsed_logs:

        service = log["service"]

        formatted_message = (
            f'{log["severity"]} {log["message"]}'
        )

        if service not in service_groups:

            service_groups[service] = {
                "logs": [],
                "severity": log["severity"]
            }

        service_groups[service]["logs"].append(
            formatted_message
        )

        # Update highest severity
        if log["severity"] == "ERROR":
            service_groups[service]["severity"] = "ERROR"

        elif (
            log["severity"] == "WARN"
            and service_groups[service]["severity"] != "ERROR"
        ):
            service_groups[service]["severity"] = "WARN"

    # Create service-level incident chunks
    chunks = []

    for service, data in service_groups.items():

        combined_logs = "\n".join(
            data["logs"]
        )

        incident_text = (
            f"Service: {service}\n\n{combined_logs}"
        )

        chunks.append({
            "service": service,
            "severity": data["severity"],
            "incident": incident_text
        })

    # Generate embeddings
    for chunk_data in chunks:

        incident_db.append({
            "incident": chunk_data["incident"],
            "metadata": {
                "service": chunk_data["service"],
                "severity": chunk_data["severity"],
                "source": "app.log"
            }
        })

        embedding = model.encode(
            chunk_data["incident"]
        )

        embeddings_db.append(embedding)

    return {
        "message": "Logs indexed successfully",
        "services_indexed": len(chunks)
    }



# Search logs
@app.get("/search")
def search(
    query: str,
    service: str = None,
    severity: str = None
):

    query_embedding = model.encode(query)

    results = []

    for incident, embedding in zip(
        incident_db,
        embeddings_db
    ):
        
        if service:
            if (
                incident["metadata"]["service"]
                != service
            ):
                continue

        if severity:
            if (
                incident["metadata"]["severity"]
                != severity
            ):
                continue

        semantic_score = cosine_similarity(
            query_embedding,
            embedding
        )

        keyword_score = calculate_keyword_score(
            query,
            incident["incident"]
        )

        final_score = semantic_score + keyword_score

        results.append({
            "incident": incident["incident"],
            "metadata": incident["metadata"],
            "final_score": float(final_score)
        })

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results[:3]

# Ask AI
@app.get("/ask")
def ask(query: str):

    query_embedding = model.encode(query)

    results = []

    for incident, embedding in zip(
        incident_db,
        embeddings_db
    ):

        semantic_score = cosine_similarity(
            query_embedding,
            embedding
        )

        keyword_score = calculate_keyword_score(
            query,
            incident["incident"]
        )

        final_score = semantic_score + keyword_score

        if final_score > 0.2:
            results.append({
                "incident": incident["incident"],
                "metadata": incident["metadata"],
                "semantic_score": float(semantic_score),
                "keyword_score": float(keyword_score),
                "final_score": float(final_score)
            })

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    top_chunks = results[:5]

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