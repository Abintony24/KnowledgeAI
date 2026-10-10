# RAG Document Q&A — GUI Version (Phase 2)

A browser-based version of the RAG project: upload PDFs or text files through
a web page, then ask questions and get answers grounded in what you uploaded.

## New files in this phase

```
main.py             -> FastAPI app: serves the page + /upload and /ask endpoints
rag_core.py          -> The RAG engine (chunking, embeddings, FAISS, Groq)
static/index.html    -> The GUI (upload box + chat interface)
requirements_gui.txt -> Dependencies for this version (adds fastapi, uvicorn, pypdf)
documents/            -> Uploaded files are saved here
storage/              -> The FAISS index + chunk metadata are saved here (persists between runs)
```

Your Phase 1 files (`app.py`, `ingest.py`, `rag.py`, `sample_docs.py`) still work
as the terminal-only version — they're untouched. This phase adds a proper web
app on top of the same ideas.

## Setup

1. **Install the extra dependencies** (in the same rag-project folder, same
   virtual environment as before):
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Make sure your `.env` file still has your Groq key:**
   ```
   GROQ_API_KEY=your_actual_key_here
   ```

3. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```
   You should see something like `Uvicorn running on http://127.0.0.1:8000`

4. **Open your browser** to:
   ```
   http://127.0.0.1:8000
   ```

5. **Use it:**
   - Click the upload box (or drag a file in) to add a PDF or `.txt` file
   - Wait for the "chunks indexed" message to update
   - Type a question in the box at the bottom and hit Enter or click Ask
   - The answer appears, along with which document(s) it came from

## How it fits the pipeline you already know

```
Browser (index.html)
   │  upload file
   ▼
POST /upload  →  rag_core.py: extract text → chunk → embed → store in FAISS
   │
   │  ask question
   ▼
POST /ask     →  rag_core.py: embed question → search FAISS → send to Groq → return answer
```

Nothing about the *logic* changed from before — you're just controlling it
through a web page instead of typing commands in a terminal. This is exactly
the "Create FastAPI API" phase from the original roadmap.

## What's next

- Dockerize this (`Dockerfile` for `main.py`)
- Push to GitHub
- Jenkins CI/CD → AWS ECR → Kubernetes/EKS → monitoring

## Troubleshooting

- **"Address already in use"** — a previous `uvicorn` process is still running.
  Close that terminal or use `uvicorn main:app --reload --port 8001` instead.
- **Upload succeeds but "0 chunks_added"** — the PDF might be scanned images
  rather than real text (no OCR yet), or it's genuinely empty.
- **Answers stop improving** — try re-uploading with fewer, cleaner documents
  first to confirm the pipeline works, then scale up.
