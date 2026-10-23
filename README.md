# KnowledgeAI — RAG Document Q&A (Phase 1)

A simple Retrieval-Augmented Generation (RAG) application that answers questions using sample documents. It uses Sentence Transformers to generate embeddings, FAISS to retrieve relevant text, and the Groq API to generate answers based on the retrieved context.

This phase was developed to test the RAG workflow locally before building the web application.

## How It Works

1. Load sample documents.
2. Split the documents into chunks.
3. Generate embeddings for the chunks using Sentence Transformers.
4. Store the embeddings in a FAISS index.
5. Convert the user's question into an embedding.
6. Retrieve the most relevant chunks from FAISS.
7. Send the question and retrieved context to the Groq API.
8. Return an answer based on the retrieved context.

## Project Structure

```text
KnowledgeAI/
├── backend/
│   ├── app.py              # Command-line interface for asking questions
│   ├── ingest.py           # Builds the local FAISS index from sample documents
│   ├── rag.py              # Retrieves relevant chunks and generates answers
│   ├── rag_core.py         # RAG engine used by the web application
│   ├── main.py             # FastAPI application
│   ├── sample_docs.py      # Sample documents for testing
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Web application interface
├── k8s/                    # Kubernetes configuration files
├── Dockerfile
├── Jenkinsfile
├── README.md
└── README_GUI.md
```

## Technologies Used

* Python
* Retrieval-Augmented Generation (RAG)
* Sentence Transformers (`all-MiniLM-L6-v2`)
* FAISS
* Groq API
* Git and GitHub

## Prerequisites

* Python 3.10 or later
* A Groq API key
* Internet access to download the embedding model on its first run

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Abintony24/KnowledgeAI.git
cd KnowledgeAI
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root and add:

```text
GROQ_API_KEY=your_groq_api_key
```

Do not commit your `.env` file or expose your API key publicly.

## Run the Application

Run these commands from the repository root.

### 1. Build the vector store

```bash
python backend/ingest.py
```

This processes the sample documents, generates embeddings, and saves the FAISS index and chunk data locally.

### 2. Start the command-line application

```bash
python backend/app.py
```

Enter a question when prompted. The application retrieves relevant document chunks and uses Groq to generate an answer.

## Example Questions

* What is Docker?
* What is the difference between the Kubernetes control plane and worker nodes?
* What does Jenkins do?

## Phase 1 Scope

This phase focuses on testing the core RAG pipeline using predefined sample documents and local vector storage.

The browser-based interface, PDF and text uploads, Amazon S3 persistence, and deployment workflow belong to later phases of the project.
