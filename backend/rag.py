"""
rag.py
Responsible for the "answer a question" half of RAG:

    Question -> Search vector DB -> Retrieve chunks -> Send to LLM -> Answer
"""

import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads GROQ_API_KEY from a .env file

INDEX_FILE = "vector_store.index"
CHUNKS_FILE = "chunks.pkl"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "openai/gpt-oss-20b"  # fast + free on Groq's developer tier


class RAGPipeline:
    def __init__(self):
        print("Loading embedding model and vector store...")
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = faiss.read_index(INDEX_FILE)

        with open(CHUNKS_FILE, "rb") as f:
            self.chunks = pickle.load(f)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Create a .env file with:\n"
                "GROQ_API_KEY=your_key_here"
            )
        self.llm_client = Groq(api_key=api_key)

    def retrieve(self, question, k=3):
        """Embed the question, search FAISS, return top-k relevant chunks."""
        question_embedding = self.embed_model.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(question_embedding, k)
        retrieved_chunks = [self.chunks[i] for i in indices[0]]
        return retrieved_chunks

    def generate_answer(self, question, retrieved_chunks):
        """Send the question + retrieved context to the LLM."""
        context = "\n\n".join(retrieved_chunks)

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
        return response.choices[0].message.content

    def ask(self, question, k=3, verbose=False):
        """Full pipeline: retrieve + generate, in one call."""
        retrieved_chunks = self.retrieve(question, k=k)
        if verbose:
            print("\n--- Retrieved chunks ---")
            for i, chunk in enumerate(retrieved_chunks, 1):
                print(f"[{i}] {chunk[:100]}...")
            print("------------------------\n")

        answer = self.generate_answer(question, retrieved_chunks)
        return answer
