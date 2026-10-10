"""
app.py
Simple command-line demo for the RAG pipeline.

(A FastAPI version of this comes later, in the deployment phase.)

Run:
    python app.py
"""

from rag import RAGPipeline


def main():
    print("Initializing RAG pipeline...\n")
    pipeline = RAGPipeline()

    print("RAG demo ready. Ask questions about Docker, Kubernetes, Jenkins, ECR, EKS.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        answer = pipeline.ask(question, k=3, verbose=True)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
