# KnowledgeAI — Document Q&A Web Application

KnowledgeAI is an AI-powered document question-answering application built using Retrieval-Augmented Generation (RAG). Users can upload PDF or text documents, ask questions about their content, and receive context-aware answers with source references.

The application uses FastAPI for the backend, Sentence Transformers for generating embeddings, FAISS for similarity search, Groq for answer generation, and Amazon S3 for persistent storage.

## Features

* Upload PDF and text documents.
* Extract text from uploaded documents.
* Split extracted text into smaller chunks.
* Generate embeddings using Sentence Transformers.
* Retrieve relevant document chunks using FAISS.
* Generate answers using the Groq API.
* Display answers with source information.
* Store the FAISS index and chunk data in Amazon S3.
* Provide a browser-based user interface.

## Architecture

```text
User
  |
  v
Web Interface (HTML)
  |
  v
FastAPI Backend
  |
  v
RAG Engine (rag_core.py)
  |
  +----> Document Processing
  |        |
  |        v
  |      Text Extraction and Chunking
  |        |
  |        v
  |      Embedding Generation
  |
  +----> FAISS Vector Search
  |
  +----> Amazon S3
  |        |
  |        +---- FAISS Index
  |        +---- Chunk Data
  |
  +----> Groq API
           |
           v
      Generated Answer
           |
           v
      Answer and Sources
```

## How It Works

### 1. Document Upload

Users upload PDF or text documents through the web interface. The FastAPI backend receives the files and passes them to the RAG engine.

### 2. Text Extraction and Chunking

The application extracts text from the uploaded documents and splits it into smaller chunks. This allows relevant sections to be retrieved without processing the entire document for every question.

### 3. Embedding Generation

The Sentence Transformers model `all-MiniLM-L6-v2` converts document chunks into numerical vectors called embeddings.

### 4. FAISS Indexing and Storage

FAISS indexes the embeddings to support similarity searches. The application stores the FAISS index and chunk data in Amazon S3 for persistent storage.

### 5. Question Retrieval

When a user asks a question, the application converts it into an embedding and searches FAISS for relevant document chunks.

### 6. Answer Generation

The application sends the user's question and retrieved context to the Groq API. The language model generates an answer based on the supplied information.

### 7. Source References

The application returns the answer along with source information associated with the retrieved document chunks.

## Technologies Used

* **Language:** Python
* **Backend:** FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **RAG:** Retrieval-Augmented Generation
* **Embedding Model:** Sentence Transformers (`all-MiniLM-L6-v2`)
* **Vector Search:** FAISS
* **LLM API:** Groq API
* **Document Processing:** PyPDF
* **Cloud Storage:** Amazon S3
* **AWS SDK:** Boto3

## Project Structure

```text
KnowledgeAI/
├── backend/
│   ├── main.py
│   ├── rag_core.py
│   ├── rag.py
│   ├── ingest.py
│   ├── app.py
│   ├── sample_docs.py
│   ├── requirements.txt
│   └── requirements_gui.txt
├── frontend/
│   └── index.html
├── k8s/
├── Dockerfile
├── Jenkinsfile
├── README.md
└── README_GUI.md
```

## Prerequisites

* Python 3.10 or later
* A Groq API key
* An AWS account with access to the configured S3 bucket
* AWS credentials configured for the application

## Setup and Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/Abintony24/KnowledgeAI.git
cd KnowledgeAI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install the packages required by your application using the appropriate requirements file.

```bash
pip install -r backend/requirements_gui.txt
```

If your repository uses a different dependency file for the FastAPI application, use that file instead.

### 4. Configure Environment Variables

Configure the environment variables required by your application, including:

```text
GROQ_API_KEY=your_groq_api_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=your_aws_region
```

Use your actual configuration values. Do not commit API keys, passwords, or AWS credentials to GitHub.

### 5. Configure AWS Access

Configure AWS credentials with the permissions required to access the S3 bucket. On AWS, use an appropriately configured IAM role where possible.

### 6. Run the Application

From the repository root, start the FastAPI application using the appropriate Python module path for your project.

For example:

```bash
uvicorn backend.main:app --reload
```

If `main.py` is run from inside the backend directory, the command may instead be:

```bash
uvicorn main:app --reload
```

Open the local application address configured by your FastAPI setup in a browser.

## Storage

Amazon S3 is used to persist the vector index and associated chunk data.

The configured object keys are:

* `storage/vector_store.index`
* `storage/chunks.pkl`

The application loads and saves these objects through its S3 integration.

## Phase 2 Scope

This phase extends the initial command-line RAG prototype into a web-based document question-answering application. It adds a browser interface, document uploads, a FastAPI backend, and persistent storage through Amazon S3.
