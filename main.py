"""
main.py
FastAPI web app for the RAG project.

Run:
    uvicorn main:app --reload

Then open:
    http://127.0.0.1:8000
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from rag_core import RAGEngine

app = FastAPI(title="RAG Document Q&A")

UPLOAD_DIR = "documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

print("Starting up RAG engine (this can take a few seconds on first run)...")
engine = RAGEngine()


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Accepts a PDF or .txt file, adds it to the knowledge base."""
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunk_count = engine.add_document(save_path, file.filename)

    return {
        "filename": file.filename,
        "chunks_added": chunk_count,
        "message": f"Added '{file.filename}' ({chunk_count} chunks indexed)."
        if chunk_count > 0
        else f"Could not extract any text from '{file.filename}'.",
    }


@app.post("/ask")
async def ask_question(question: str = Form(...)):
    """Answers a question using the currently indexed documents."""
    result = engine.ask(question)
    return result


@app.get("/status")
def status():
    """Returns how many chunks/documents are currently indexed."""
    return engine.status()


# Serve the frontend's static assets (css/js) if you add any later
app.mount("/static", StaticFiles(directory="static"), name="static")
