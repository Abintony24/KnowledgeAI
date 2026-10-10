# RAG Demo (Phase 1: local, no DevOps yet)

This is a minimal, working Retrieval-Augmented Generation pipeline you run
on your own machine. No PDFs yet — it uses sample text about
Docker/Kubernetes/Jenkins so you can test the full flow first.

## How it maps to the RAG pipeline

```
sample_docs.py  -> the raw documents
ingest.py       -> Load -> Chunk -> Embed -> Store in FAISS   (run once)
rag.py          -> Retrieve -> Send to LLM -> Answer          (the core logic)
app.py          -> CLI loop to ask questions                  (the demo)
```

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free Groq API key:**
   - Go to https://console.groq.com/keys
   - Sign up (free) and create an API key
   - Copy `.env.example` to `.env`, and paste your key in:
     ```
     GROQ_API_KEY=your_actual_key_here
     ```

4. **Build the vector store** (run this once):
   ```bash
   python ingest.py
   ```
   This downloads a small free embedding model (~80MB, first run only),
   embeds the sample documents, and saves a FAISS index to disk.

5. **Ask questions:**
   ```bash
   python app.py
   ```
   Try things like:
   - "What is Docker?"
   - "What's the difference between the control plane and worker nodes?"
   - "What does Jenkins do?"

## What's next (once this works)

- Swap `sample_docs.py` for real PDF loading (`pypdf` or `unstructured`)
- Wrap `rag.py` in a FastAPI endpoint (`POST /ask`)
- Then: Docker -> GitHub -> Jenkins CI/CD -> AWS ECR -> Kubernetes/EKS -> monitoring

Don't move to deployment until `python app.py` reliably gives good answers
on your own real documents — that's the actual "AI" part of the project,
and everything after it is just packaging and shipping this same logic.
