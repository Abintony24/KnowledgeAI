# KnowledgeAI — RAG-Based Knowledge Assistant

KnowledgeAI is an AI-powered document question-answering application built using Retrieval-Augmented Generation (RAG). It allows users to upload PDF and text documents, ask questions about their content, and receive context-aware answers with source references.

The application uses FastAPI for the backend, Sentence Transformers for generating embeddings, FAISS for similarity search, Groq API for answer generation, and Amazon S3 for persistent storage.

## Features

* Upload PDF and text documents.
* Extract text from uploaded documents.
* Split document text into smaller chunks.
* Generate embeddings using Sentence Transformers.
* Retrieve relevant document chunks using FAISS.
* Generate context-aware answers using the Groq API.
* Return answers with source references.
* Store the FAISS index and document chunk data in Amazon S3.
* Provide a browser-based interface for document uploads and questions.

## How It Works

The application follows a Retrieval-Augmented Generation (RAG) workflow.

### 1. Document Upload

Users upload PDF or text documents through the web interface. The FastAPI backend receives the uploaded files and passes them to the RAG engine.

### 2. Text Extraction and Chunking

The application extracts text from the uploaded documents and splits it into smaller chunks. Chunking allows the application to retrieve relevant sections instead of processing an entire document for every question.

### 3. Embedding Generation

The Sentence Transformers model `all-MiniLM-L6-v2` converts document chunks into numerical vectors called embeddings. These vectors represent the semantic meaning of the text.

### 4. Vector Indexing

FAISS indexes the embeddings to support efficient similarity searches. The application can search this index to identify document chunks relevant to a user's question.

### 5. Persistent Storage

Amazon S3 stores the FAISS index and associated chunk data so the application can persist its knowledge base beyond the lifetime of a running process.

### 6. Question Retrieval

When a user asks a question, the application converts it into an embedding and searches FAISS for relevant document chunks.

### 7. Answer Generation

The application sends the user's question and the retrieved context to the Groq API. The language model generates an answer based on the supplied information.

### 8. Source References

The application returns the generated answer along with source information associated with the retrieved document chunks.

## Architecture

```text
                 User
                  |
                  v
          Web Interface
          (HTML, CSS, JS)
                  |
                  v
           FastAPI Backend
             (main.py)
                  |
                  v
              RAG Engine
            (rag_core.py)
                  |
        +---------+---------+
        |         |         |
        v         v         v
   Embedding    FAISS    Amazon S3
     Model     Search   Persistent
        |         |      Storage
        |         |
        +----+----+
             |
             v
        Relevant Text
             |
             v
          Groq API
             |
             v
      Answer and Sources
```

## Technologies Used

| Category             | Technologies                               |
| -------------------- | ------------------------------------------ |
| Programming Language | Python                                     |
| Backend Framework    | FastAPI                                    |
| Frontend             | HTML, CSS, JavaScript                      |
| RAG Architecture     | Retrieval-Augmented Generation             |
| Embedding Model      | Sentence Transformers — `all-MiniLM-L6-v2` |
| Vector Search        | FAISS                                      |
| Language Model API   | Groq API                                   |
| Document Processing  | PyPDF                                      |
| Cloud Storage        | Amazon S3                                  |
| AWS SDK              | Boto3                                      |

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
└── README_DEPLOYMENT.md
```

### Important Files

* **`main.py`** — Provides the FastAPI backend and handles document uploads and question-answering requests.
* **`rag_core.py`** — Implements the main RAG engine used by the web application, including document processing, embeddings, FAISS retrieval, Groq integration, and S3 storage.
* **`rag.py`** — Provides a separate RAG implementation used for testing the workflow with sample documents and a local FAISS index.
* **`ingest.py`** — Creates a local FAISS index from predefined sample documents for testing.
* **`app.py`** — Provides a command-line interface for testing the sample-document RAG pipeline.
* **`sample_docs.py`** — Contains predefined sample documents used for testing.
* **`frontend/index.html`** — Provides the browser-based user interface.
* **`requirements.txt`** — Lists Python dependencies for the relevant application components.
* **`requirements_gui.txt`** — Lists dependencies for the web application, if maintained separately.

## Prerequisites

* Python 3.10 or later.
* A Groq API key.
* An AWS account with access to the configured S3 bucket.
* AWS credentials with the permissions required to access that bucket.

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Abintony24/KnowledgeAI.git
cd KnowledgeAI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the dependencies required by your web application:

```bash
pip install -r backend/requirements_gui.txt
```

If your repository uses a different requirements file for the FastAPI application, use the appropriate file instead.

### 4. Configure Environment Variables

Configure the environment variables required by the application.

Example:

```text
GROQ_API_KEY=your_groq_api_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=your_aws_region
```

Use the actual variable names expected by your code. Do not commit API keys, passwords, or AWS credentials to GitHub.

### 5. Configure AWS Access

Configure AWS credentials with the permissions needed to access your S3 bucket. When running on AWS, an appropriately configured IAM role can be used to grant access.

### 6. Start the FastAPI Application

From the repository root, run:

```bash
uvicorn backend.main:app --reload
```

If your Python import structure requires running from the backend directory, use:

```bash
uvicorn main:app --reload
```

Use the command appropriate for your actual repository structure.

Open the local application address provided by Uvicorn in your browser.

## Storage

Amazon S3 is used to persist the FAISS index and associated document chunk data.

The configured object keys are:

* `storage/vector_store.index` — FAISS vector index.
* `storage/chunks.pkl` — Serialized document chunks and associated information.

The application uses Boto3 to interact with S3. The actual bucket name and AWS region are configured through the application's settings.

## Security

* Keep the Groq API key and AWS credentials out of source control.
* Use environment variables or an appropriate secrets-management mechanism for sensitive configuration.
* Grant the application only the AWS permissions it needs.
* Avoid uploading sensitive documents unless you have permission to store and process them.

## Project Scope

KnowledgeAI demonstrates how Retrieval-Augmented Generation can be used to answer questions from user-provided documents.

The project combines document processing, semantic retrieval, language-model answer generation, a web interface, and persistent cloud storage in one application.

For containerization, CI/CD, Kubernetes deployment, and monitoring details, see `README_DEPLOYMENT.md`.
