"""
rag_core.py
KnowledgeAI RAG engine with Amazon S3 persistent storage.
"""

import os
import pickle
import tempfile
import threading
from pathlib import Path

import boto3
import faiss
import numpy as np

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
from botocore.exceptions import ClientError


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

S3_BUCKET_NAME = "knowledgeai-documents-abin2026"
AWS_REGION = "us-east-1"

INDEX_KEY = "storage/vector_store.index"
CHUNKS_KEY = "storage/chunks.pkl"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "openai/gpt-oss-20b"
EMBEDDING_DIM = 384

CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 50


class RAGEngine:

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            region_name=AWS_REGION
        )

        # Protect index updates within this application instance.
        self.lock = threading.RLock()

        print("Loading embedding model...")

        self.embed_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set in the project .env file."
            )

        self.llm_client = Groq(api_key=api_key)

        self.chunks = []
        self.index = None

        self._load_or_create_index()

    # --------------------------------------------------
    # Load index and chunks from S3
    # --------------------------------------------------

    def _load_or_create_index(self):
        """
        Load the FAISS index and chunks from S3.
        If neither exists, initialize an empty index.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            index_path = os.path.join(
                temp_dir,
                "vector_store.index"
            )

            chunks_path = os.path.join(
                temp_dir,
                "chunks.pkl"
            )

            try:
                # Download the index and chunks into temporary files.
                self.s3.download_file(
                    S3_BUCKET_NAME,
                    INDEX_KEY,
                    index_path
                )

                self.s3.download_file(
                    S3_BUCKET_NAME,
                    CHUNKS_KEY,
                    chunks_path
                )

                # Load them into application memory.
                self.index = faiss.read_index(index_path)

                with open(chunks_path, "rb") as file:
                    self.chunks = pickle.load(file)

                # Validate that vector and chunk counts match.
                if self.index.ntotal != len(self.chunks):
                    raise ValueError(
                        "The FAISS index and chunk metadata have "
                        "different numbers of entries."
                    )

                print(
                    f"Loaded {len(self.chunks)} chunks from S3."
                )

            except ClientError as exc:

                error_code = exc.response.get(
                    "Error", {}
                ).get("Code")

                if error_code not in (
                    "404",
                    "NoSuchKey",
                    "NotFound",
                ):
                    raise

                # Do not silently discard an existing index if
                # only one of the two S3 objects is missing.
                index_exists = self._s3_object_exists(INDEX_KEY)
                chunks_exist = self._s3_object_exists(CHUNKS_KEY)

                if index_exists or chunks_exist:
                    raise RuntimeError(
                        "Only part of the RAG data exists in S3. "
                        "Restore the missing object before starting."
                    ) from exc

                self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
                self.chunks = []

                print(
                    "No existing index found in S3. "
                    "Initialized an empty index."
                )

    def _s3_object_exists(self, key):
        """Check whether an object exists in S3."""

        try:
            self.s3.head_object(
                Bucket=S3_BUCKET_NAME,
                Key=key
            )
            return True

        except ClientError as exc:

            error_code = exc.response.get(
                "Error", {}
            ).get("Code")

            status_code = exc.response.get(
                "ResponseMetadata", {}
            ).get("HTTPStatusCode")

            if error_code in ("404", "NoSuchKey", "NotFound"):
                return False

            if status_code == 404:
                return False

            raise

    # --------------------------------------------------
    # Save index and chunks to S3
    # --------------------------------------------------

    def _save_index(self):
        """
        Serialize the current index and chunks to temporary files,
        then upload them to S3. No permanent local copies are kept.
        """

        with tempfile.TemporaryDirectory() as temp_dir:

            index_path = os.path.join(
                temp_dir,
                "vector_store.index"
            )

            chunks_path = os.path.join(
                temp_dir,
                "chunks.pkl"
            )

            faiss.write_index(
                self.index,
                index_path
            )

            with open(chunks_path, "wb") as file:
                pickle.dump(self.chunks, file)

            # Upload both objects to S3.
            self.s3.upload_file(
                index_path,
                S3_BUCKET_NAME,
                INDEX_KEY
            )

            self.s3.upload_file(
                chunks_path,
                S3_BUCKET_NAME,
                CHUNKS_KEY
            )

        print("FAISS index and chunks saved to S3.")

    # --------------------------------------------------
    # Extract text
    # --------------------------------------------------

    def extract_text(self, file_path):
        """Extract text from PDF or TXT files."""

        if file_path.lower().endswith(".pdf"):

            reader = PdfReader(file_path)

            return "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return file.read()

    # --------------------------------------------------
    # Split text into chunks
    # --------------------------------------------------

    def chunk_text(self, text):
        """Split text into overlapping chunks."""

        words = text.split()
        chunks = []

        step = CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS

        for start in range(0, len(words), step):

            chunk_words = words[
                start:start + CHUNK_SIZE_WORDS
            ]

            if chunk_words:
                chunks.append(" ".join(chunk_words))

            if start + CHUNK_SIZE_WORDS >= len(words):
                break

        return chunks

    # --------------------------------------------------
    # Process and index a document
    # --------------------------------------------------

    def add_document(self, file_path, filename):
        """Extract, chunk, embed, and index a document."""

        text = self.extract_text(file_path)

        if not text.strip():
            return 0

        new_chunks = self.chunk_text(text)

        if not new_chunks:
            return 0

        embeddings = self.embed_model.encode(
            new_chunks,
            convert_to_numpy=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        with self.lock:

            # Add the new vectors and corresponding text chunks.
            self.index.add(embeddings)

            for chunk in new_chunks:
                self.chunks.append({
                    "text": chunk,
                    "source": filename
                })

            # Persist the updated data in S3.
            self._save_index()

        return len(new_chunks)

    # --------------------------------------------------
    # Retrieve relevant chunks
    # --------------------------------------------------

    def retrieve(self, question, k=4):
        """Find relevant chunks using FAISS."""

        question_embedding = self.embed_model.encode(
            [question],
            convert_to_numpy=True
        )

        question_embedding = np.asarray(
            question_embedding,
            dtype=np.float32
        )

        with self.lock:

            if self.index.ntotal == 0:
                return []

            k = min(k, self.index.ntotal)

            _, indices = self.index.search(
                question_embedding,
                k
            )

            return [
                self.chunks[i]
                for i in indices[0]
                if 0 <= i < len(self.chunks)
            ]

    # --------------------------------------------------
    # Generate answer with Groq
    # --------------------------------------------------

    def generate_answer(self, question, retrieved_chunks):
        """Generate an answer using the retrieved context."""

        if not retrieved_chunks:
            return (
                "No relevant document content was found.",
                []
            )

        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        sources = sorted({
            chunk["source"]
            for chunk in retrieved_chunks
        })

        prompt = f"""Answer the question using ONLY the context below.
If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

        response = self.llm_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content, sources

    # --------------------------------------------------
    # Ask a question
    # --------------------------------------------------

    def ask(self, question, k=4):
        """Retrieve relevant chunks and generate an answer."""

        retrieved = self.retrieve(question, k=k)

        answer, sources = self.generate_answer(
            question,
            retrieved
        )

        return {
            "answer": answer,
            "sources": sources,
            "chunks_used": [
                chunk["text"][:200]
                for chunk in retrieved
            ]
        }

    # --------------------------------------------------
    # Application status
    # --------------------------------------------------

    def status(self):
        """Return the indexed document information."""

        with self.lock:
            return {
                "total_chunks": len(self.chunks),
                "documents": sorted({
                    chunk["source"]
                    for chunk in self.chunks
                })
            }