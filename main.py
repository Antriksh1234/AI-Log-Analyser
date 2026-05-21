from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from app.models.incident import (
    IncidentDocument,
    IncidentMetadata
)
from app.parsers.log_parser import (
    parse_log,
    group_logs_by_service,
    create_incident_chunks
)

from app.services.opensearch_service import (
    create_index,
    index_incident
)

from app.services.retrieval_service import (
    retrieve_incidents
)

from app.services.llm_service import ask_mistral

app = FastAPI()

# Embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Group logs into chunks
# Removing since this is fixed size chunking
# def chunk_logs(lines, chunk_size=5):

#     chunks = []

#     for i in range(0, len(lines), chunk_size):

#         chunk = lines[i:i+chunk_size]

#         combined = "\n".join(chunk)

#         chunks.append(combined)

#     return chunks


@app.get("/")
def home():

    return {
        "message": "AI Log Analyzer Running"
    }

# Load logs
@app.post("/load-logs")
def load_logs():

    create_index()

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
    service_groups = group_logs_by_service(
        parsed_logs
    )

    # Create incident chunks
    chunks = create_incident_chunks(
        service_groups
    )

    # Generate embeddings
    for chunk_data in chunks:

        incident = IncidentDocument(
            incident=chunk_data["incident"],
            metadata=IncidentMetadata(
                service=chunk_data["service"],
                severity=chunk_data["severity"],
                source="app.log"
            )
        )

        embedding = model.encode(
            chunk_data["incident"]
        )

        index_incident(incident, embedding)

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

    results = []

    results = retrieve_incidents(
        query=query,
        model=model,
        service=service,
        severity=severity
    )

    return results[:min(3, len(results))]


# Ask AI
@app.get("/ask")
def ask(query: str):

    results = retrieve_incidents(
        query=query,
        model=model
    )

    top_chunks = results[:min(5, len(results))]

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