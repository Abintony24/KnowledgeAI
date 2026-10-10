"""
rag_core.py
The core RAG engine, used by the FastAPI app (main.py).

Responsibilities:
  - Load text from uploaded files (.pdf or .txt)
  - Split text into chunks
  - Embed chunks and store them in a FAISS index (persisted to disk)
  - Retrieve relevant chunks for a question
  - Generate an answer using Groq, grounded only in retrieved chunks
"""

import os
import pickle
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

STORAGE_DIR = "storage"
INDEX_FILE = os.path.join(STORAGE_DIR, "vector_store.index")
CHUNKS_FILE = os.path.join(STORAGE_DIR, "chunks.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "openai/gpt-oss-20b"
EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2 output size

CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 50


class RAGEngine:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)

        print("Loading embedding model...")
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")
        self.llm_client = Groq(api_key=api_key)

        # chunks: list of {"text": str, "source": filename}
        self.chunks = []
        self.index = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(CHUNKS_FILE, "rb") as f:
                self.chunks = pickle.load(f)
            print(f"Loaded existing index with {len(self.chunks)} chunks.")
        else:
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
            self.chunks = []
            print("Created a new, empty index.")

    def _save_index(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(CHUNKS_FILE, "wb") as f:
            pickle.dump(self.chunks, f)

    # ---------- Loading documents ----------

    def extract_text(self, file_path):
        if file_path.lower().endswith(".pdf"):
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:  # treat as plain text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        return text

    def chunk_text(self, text):
        words = text.split()
        chunks = []
        step = CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS
        for start in range(0, len(words), step):
            chunk_words = words[start:start + CHUNK_SIZE_WORDS]
            if chunk_words:
                chunks.append(" ".join(chunk_words))
            if start + CHUNK_SIZE_WORDS >= len(words):
                break
        return chunks

    def add_document(self, file_path, filename):
        """Load, chunk, embed, and add a document to the index. Returns chunk count added."""
        text = self.extract_text(file_path)
        if not text.strip():
            return 0

        new_chunks = self.chunk_text(text)
        embeddings = self.embed_model.encode(new_chunks, convert_to_numpy=True)
        self.index.add(embeddings)

        for chunk in new_chunks:
            self.chunks.append({"text": chunk, "source": filename})

        self._save_index()
        return len(new_chunks)

    # ---------- Answering questions ----------

    def retrieve(self, question, k=4):
        if self.index.ntotal == 0:
            return []
        question_embedding = self.embed_model.encode([question], convert_to_numpy=True)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(question_embedding, k)
        return [self.chunks[i] for i in indices[0]]

    def generate_answer(self, question, retrieved_chunks):
        if not retrieved_chunks:
            return "No documents have been uploaded yet, so I have nothing to search.", []

        context = "\n\n".join(c["text"] for c in retrieved_chunks)
        sources = sorted(set(c["source"] for c in retrieved_chunks))

        prompt = f"""Answer the question using ONLY the context below.
If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""

        response = self.llm_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content, sources

    def ask(self, question, k=4):
        retrieved = self.retrieve(question, k=k)
        answer, sources = self.generate_answer(question, retrieved)
        return {
            "answer": answer,
            "sources": sources,
            "chunks_used": [c["text"][:200] for c in retrieved],
        }

    def status(self):
        return {
            "total_chunks": len(self.chunks),
            "documents": sorted(set(c["source"] for c in self.chunks)),
        }
