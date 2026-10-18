"""
KnowledgeAI - FastAPI application with AWS S3 integration.
"""

import os
import tempfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.rag_core import RAGEngine


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_FILE = FRONTEND_DIR / "index.html"

S3_BUCKET_NAME = "knowledgeai-documents-abin2026"
AWS_REGION = "us-east-1"

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


# --------------------------------------------------
# Initialize FastAPI
# --------------------------------------------------

app = FastAPI(
    title="KnowledgeAI",
    description="AI-powered document question-answering application",
    version="1.0.0"
)

# Serve frontend assets if the directory exists.
if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static"
    )

print("Starting up RAG engine...")
engine = RAGEngine()


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get("/")
def home():
    if not FRONTEND_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="frontend/index.html was not found."
        )

    return FileResponse(str(FRONTEND_FILE))


# --------------------------------------------------
# Upload document
# --------------------------------------------------

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a file."
        )

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    temp_path = None

    try:
        # Upload the original document to S3.
        s3.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            filename
        )

        # Create a temporary file for processing.
        with tempfile.NamedTemporaryFile(
            suffix=Path(filename).suffix,
            delete=False
        ) as temp_file:
            temp_path = temp_file.name

        # Download the document temporarily from S3.
        s3.download_file(
            S3_BUCKET_NAME,
            filename,
            temp_path
        )

        # Extract text, create chunks and save the updated index to S3.
        chunks_added = engine.add_document(
            temp_path,
            filename
        )

        if chunks_added == 0:
            return {
                "filename": filename,
                "chunks_added": 0,
                "message": (
                    "The file was uploaded to S3, but no text "
                    "could be extracted."
                )
            }

        return {
            "filename": filename,
            "chunks_added": chunks_added,
            "message": (
                f"Successfully indexed {filename}. "
                f"Added {chunks_added} chunks."
            )
        }

    except ClientError as exc:
        print(f"AWS S3 error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=(
                "S3 operation failed. Check your AWS credentials, "
                "bucket name, region and permissions."
            )
        ) from exc

    except Exception as exc:
        print(f"Document processing error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {exc}"
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


# --------------------------------------------------
# Ask a question
# --------------------------------------------------

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        result = engine.ask(question.strip())

        return result

    except Exception as exc:
        print(f"Question processing error: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Question processing failed: {exc}"
        ) from exc


# --------------------------------------------------
# Application status
# --------------------------------------------------

@app.get("/status")
def status():
    return engine.status()


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "KnowledgeAI"
    }