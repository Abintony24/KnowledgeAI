"""
ingest.py
Responsible for the "build the knowledge base" half of RAG:

    Documents -> Chunks -> Embeddings -> Vector Database (FAISS)

Run this once (or whenever your documents change):
    python ingest.py
"""

import pickle
import faiss
from sentence_transformers import SentenceTransformer

from sample_docs import SAMPLE_DOCUMENTS

INDEX_FILE = "vector_store.index"
CHUNKS_FILE = "chunks.pkl"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, free, runs locally


def chunk_documents(documents):
    """
    Each sample "document" is already a small paragraph, so here each one
    just becomes one chunk. With real PDFs, you'd split long text into
    ~300-500 word pieces instead of using the whole page.
    """
    chunks = [doc.strip().replace("\n    ", " ") for doc in documents]
    return chunks


def build_vector_store(chunks, model):
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # simple similarity search index
    index.add(embeddings)

    return index


def main():
    print("Loading embedding model (first run downloads it, ~80MB)...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    chunks = chunk_documents(SAMPLE_DOCUMENTS)
    index = build_vector_store(chunks, model)

    faiss.write_index(index, INDEX_FILE)
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print(f"\nDone. Saved {len(chunks)} chunks to '{CHUNKS_FILE}'")
    print(f"Saved vector index to '{INDEX_FILE}'")
    print("\nNext: run 'python app.py' to ask questions.")


if __name__ == "__main__":
    main()
