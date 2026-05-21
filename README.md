# AI Log Analyzer

An AI-powered log analysis and semantic incident retrieval platform built using FastAPI, Sentence Transformers, OpenSearch, and Ollama.

This project allows engineers to:
- Ingest and preprocess application logs
- Generate semantic embeddings
- Persist embeddings inside OpenSearch
- Perform kNN vector-based incident retrieval
- Apply metadata-based filtering
- Ask natural language questions about failures and incidents using a local LLM

The application uses OpenSearch as a persistent vector database and Ollama for fully local LLM inference.

---

# Features

- Semantic log search
- OpenSearch vector indexing
- Persistent semantic retrieval
- kNN vector search
- Metadata-based filtering
- AI-powered incident analysis
- Local LLM inference using Ollama
- FastAPI REST APIs
- Log preprocessing and grouping
- Fully local execution
- Stateless backend architecture

---

# Tech Stack

- Python
- FastAPI
- Sentence Transformers
- OpenSearch
- Docker
- Ollama
- Mistral
- NumPy

---

# Architecture

```text
Log File
   ↓
Log Parsing & Grouping
   ↓
SentenceTransformer Embeddings
   ↓
OpenSearch Vector Index
   ↓
kNN Semantic Retrieval
   ↓
Context Retrieval
   ↓
Mistral (Ollama)
   ↓
AI Analysis Response
```

---

# Prerequisites

## 1. Python

Install Python 3.10 or higher.

Verify:

```bash
python3 --version
```

---

## 2. Docker Desktop

Install Docker Desktop and ensure Docker is running locally.

Verify:

```bash
docker --version
```

---

## 3. Ollama

Install Ollama from:

https://ollama.com

Verify installation:

```bash
ollama --version
```

---

## 4. Pull Mistral Model

Run:

```bash
ollama run mistral
```

This downloads the model locally.

---

# Installation

Clone repository:

```bash
git clone https://github.com/Antriksh1234/AI-Log-Analyser.git
cd AI-Log-Analyser
```

---

## Create Virtual Environment

```bash
python3 -m venv .venv
```

---

## Activate Virtual Environment

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root:

```env
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your_password
```

---

# Project Structure

```text
AI-Log-Analyser/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── models/
│   │   └── incident.py
│   │
│   ├── parsers/
│   │   └── log_parser.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── retrieval_service.py
│   │   └── opensearch_service.py
│   │
│   └── utils/
│       └── similarity.py
│
├── logs/
│   └── app.log
│
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

---

# Running The Application

## Step 1 — Start OpenSearch

```bash
docker compose up
```

Keep it running.

---

## Step 2 — Start Ollama

In another terminal:

```bash
ollama run mistral
```

Keep it running.

---

## Step 3 — Start FastAPI

In another terminal:

```bash
uvicorn app.main:app --reload
```

---

## Step 4 — Open Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

---

# Using The Application

## 1. Add Logs

Place log files inside:

```text
logs/
```

Example:

```text
logs/app.log
```

---

## 2. Load Logs

Run:

```text
POST /load-logs
```

This endpoint:
- reads logs
- parses and groups incidents
- generates embeddings
- indexes incidents into OpenSearch

---

## 3. Semantic Search

Endpoint:

```text
GET /search
```

Example:

```text
/search?query=database timeout
```

Example with filters:

```text
/search?query=redis failure&service=payment-service
```

```text
/search?query=timeout&severity=ERROR
```

---

## 4. Ask Questions

Endpoint:

```text
GET /ask
```

Example:

```text
/ask?query=Why are requests failing?
```

The application:
1. Retrieves semantically relevant incidents
2. Sends context to Mistral
3. Generates AI-powered analysis

---

# Example Questions

- Why are requests failing?
- Which service is timing out?
- What Redis issues occurred?
- What database failures happened?
- Which services have ERROR logs?
- Why are retries happening?
- What incidents are affecting payment-service?

---

# Notes

- This is a learning-focused MVP implementation.
- Retrieval quality heavily depends on log grouping strategy and embedding quality.
- LLM responses may still hallucinate or infer incorrect conclusions.
- Better chunking and reranking can significantly improve accuracy.
- OpenSearch is used as the persistent vector database.

---

# Future Improvements

- BM25 + vector hybrid ranking
- OpenSearch Dashboards integration
- Real-time streaming ingestion
- CloudWatch / Splunk integration
- Request ID based incident grouping
- Root cause clustering
- Reranking models
- Multi-index retrieval
- Streaming AI responses
- Frontend observability dashboard

---

# License

MIT