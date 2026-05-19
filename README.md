# AI Log Analyzer

An AI-powered log analysis and semantic incident search application built using FastAPI, Sentence Transformers, and Ollama.

This project allows engineers to:
- Ingest application logs
- Clean and preprocess logs
- Generate semantic embeddings
- Perform vector-based incident retrieval
- Ask natural language questions about failures and incidents using a local LLM

---

# Features

- Semantic log search
- AI-powered incident analysis
- Local LLM inference using Ollama
- FastAPI REST APIs
- Log preprocessing and cleaning
- Incident chunking
- Vector similarity search
- Fully local execution

---

# Tech Stack

- Python
- FastAPI
- Sentence Transformers
- Ollama
- Mistral
- NumPy

---

# Architecture

```text
Log File
   ↓
Preprocessing
   ↓
Incident Chunking
   ↓
Embeddings
   ↓
Vector Search
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

## 2. Ollama

Install Ollama from:

https://ollama.com

Verify installation:

```bash
ollama --version
```

---

## 3. Pull Mistral Model

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
cd ai-log-analyzer
```

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate virtual environment:

## macOS/Linux

```bash
source .venv/bin/activate
```

## Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Project Structure

```text
ai-log-analyzer/
│
├── logs/
│   └── app.log
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Running The Application

## Step 1 — Start Ollama

In Terminal 1:

```bash
ollama run mistral
```

Keep it running.

---

## Step 2 — Start FastAPI

In Terminal 2:

```bash
uvicorn main:app --reload
```

---

## Step 3 — Open Swagger UI

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

This:
- reads logs
- preprocesses lines
- groups incidents
- generates embeddings
- indexes logs

---

## 3. Semantic Search

Endpoint:

```text
GET /search
```

Example query:

```text
database timeout
```

---

## 4. Ask Questions

Endpoint:

```text
GET /ask
```

Example:

```text
Why are requests failing?
```

The application:
1. Retrieves relevant incidents
2. Sends context to Mistral
3. Generates AI-powered analysis

---

# Example Questions

- Why are requests failing?
- What database issues occurred?
- Why did retries happen?
- Which service is timing out?
- What errors are occurring frequently?

---

# Notes

- This is a learning-focused MVP implementation.
- Retrieval quality depends heavily on log preprocessing and chunking strategy.
- LLM responses may still hallucinate or infer incorrect conclusions.
- Better incident grouping and hybrid search can significantly improve accuracy.

---

# Future Improvements

- Request ID based grouping
- Time-window chunking
- FAISS / Elasticsearch vector search
- Real-time streaming ingestion
- CloudWatch / Splunk integration
- Root cause clustering
- Hybrid keyword + vector search
- Observability dashboards
- Streaming AI responses

---

# License

MIT