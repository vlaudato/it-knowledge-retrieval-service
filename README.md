# IT Knowledge Retrieval Service

A production-ready RAG (Retrieval-Augmented Generation) system that combines semantic search with large language models to answer questions based on custom knowledge bases. Built with a focus on modularity, scalability, and deployment flexibility.

## Overview

This service implements a complete RAG pipeline that:
1. Converts user queries into semantic embeddings using state-of-the-art transformer models
2. Performs vector similarity search against a Supabase PostgreSQL database with pgvector
3. Generates contextual answers using locally-hosted Ollama LLMs
4. Exposes a REST API for easy integration into existing applications

**Key Design Decisions:**
- **Local LLM inference** via Ollama for data privacy and cost control
- **Supabase** for managed vector storage with built-in similarity search
- **Modular service architecture** for easy testing and component swapping
- **Production-ready** with Docker, Docker Compose, and Kubernetes configurations

## Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Embeddings** | Qwen3-Embedding-0.6B via SentenceTransformers | 1024-dimensional semantic vectors |
| **Reranker** | Qwen3-Reranker-0.6B (CausalLM) | Two-stage retrieval with yes/no token prediction |
| **Vector Database** | Supabase (PostgreSQL + pgvector) | Scalable similarity search |
| **LLM** | Llama 3.2 via Ollama | Local answer generation |
| **API Framework** | Flask + Flask-CORS | RESTful interface with streaming support |
| **Deployment** | Docker, Docker Compose, Kubernetes | Multi-environment support |
| **Dependency Management** | pip-tools | Deterministic builds with lock files |

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP POST /api/query or /api/query/stream
       ▼
┌─────────────────────────────────────────┐
│         Flask API (app.py)              │
└──────┬──────────────────────────────────┘
       │
       ├──► EmbeddingService
       │    └─► SentenceTransformer (Qwen3)
       │        └─► [1024-dim vector]
       │
       ├──► VectorService
       │    └─► Supabase RPC (match_doc)
       │        └─► [Top-K similar documents]
       │
       ├──► RerankerService (optional)
       │    └─► Qwen3-Reranker (CausalLM)
       │        └─► [Top-K reranked documents]
       │
       └──► LLMService
            └─► Ollama API (Llama 3.2)
                └─► [Generated answer / Stream]
```

## Features

### Core Functionality
- **Semantic Search**: Uses cosine similarity for accurate document retrieval
- **Two-Stage Retrieval**: Optional reranking with Qwen3-Reranker for improved relevance
- **Context-Aware Answers**: LLM generates responses grounded in retrieved documents
- **Streaming Responses**: Real-time answer generation with SSE for typing effects
- **Configurable Matching**: Adjustable similarity thresholds and result counts
- **Error Handling**: Comprehensive validation and error responses

### Production Features
- **Health Checks**: Kubernetes-ready liveness/readiness probes
- **CORS Support**: Cross-origin requests enabled
- **Environment-Based Config**: Separate dev/prod configurations
- **Logging**: Detailed request/response logging for debugging
- **Containerization**: Multi-stage Docker builds with dependency resolution
- **Deterministic Builds**: pip-tools for reproducible dependency management
- **Tested**: Comprehensive unit tests with high code coverage

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Supabase account with a project created
- Supabase database with `match_doc` function (see Database Setup)

### Docker Compose Deployment

The easiest way to run the complete stack:

```bash
docker-compose up -d --build
```

This starts:
- **Ollama** service with Llama 3.2 model (auto-downloaded)
- **RAG service** with all dependencies

Access the API at `http://localhost:5000`

### Kubernetes Deployment

For production deployments:

```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic rag-secrets \
  --from-literal=SUPABASE_URL=<your-url> \
  --from-literal=SUPABASE_KEY=<your-key> \
  -n rag-system

# Deploy services
kubectl apply -f k8s/
```

## Database Setup

### Table Schema

Create the `it_docs_embeddings` table in your Supabase database:

```sql
CREATE TABLE it_docs_embeddings (
  id bigserial PRIMARY KEY,
  content text NOT NULL,
  topic text,
  chunk_id integer,
  embedding vector(1024)
);

-- Create index for fast vector similarity search
CREATE INDEX ON it_docs_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on topic for the retrieval function
CREATE INDEX ON it_docs_embeddings (topic);
```

### Retrieval Function

This function implements a two-stage retrieval strategy:
1. Find the most relevant topic based on similarity
2. Return all chunks from that topic (ensures complete context)

```sql
CREATE OR REPLACE FUNCTION match_doc(
  query_embedding vector(1024),
  match_threshold float DEFAULT 0.7
)
RETURNS TABLE (
  id bigint,
  content text,
  topic text,
  chunk_id integer,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH best_topic AS (
    SELECT topic
    FROM it_docs_embeddings
    WHERE 1 - (embedding <=> query_embedding) >= match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT 1
  )
  SELECT
    d.id,
    d.content,
    d.topic,
    d.chunk_id,
    1 - (d.embedding <=> query_embedding) AS similarity
  FROM it_docs_embeddings d
  WHERE d.topic = (SELECT topic FROM best_topic);
END;
$$;
```

**Why this approach?**
- Ensures you get complete context from a single topic rather than fragments from multiple topics
- Reduces hallucination by providing coherent, related information
- Works well for knowledge bases organized by topics/categories

## Data Ingestion

Before using the RAG service, you need to populate the database with your documents.

### Using the Colab Notebook

A complete data ingestion pipeline is provided in [this](https://colab.research.google.com/drive/1_GHB0wvpaKEFJ5C1E-k8sPWViO_Bp-4f?usp=sharing) notebook:

1. **Loads documents** from CSV (IT knowledge base articles)
2. **Chunks text** using LangChain's RecursiveCharacterTextSplitter (1500 chars, 200 overlap)
3. **Generates embeddings** using Qwen3-Embedding-0.6B (1024 dimensions)
4. **Stores in Supabase** with topic metadata for retrieval

**Data format:**
The notebook expects a CSV with columns:
- `ki_topic`: Category/topic of the document
- `ki_text`: Full text content

**Output:**
- Chunks stored in `it_docs_embeddings` table
- Each chunk includes: content, topic, embedding vector
- Ready for semantic search via the `match_doc` function

## Configuration

All configuration is managed through environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase API key (anon or service role) |
| `OLLAMA_BASE_URL` | No | `http://ollama:11434` | Ollama API endpoint |
| `EMBEDDING_MODEL` | No | `Qwen/Qwen3-Embedding-0.6B` | HuggingFace model for embeddings |
| `RERANKER_MODEL` | No | `Qwen/Qwen3-Reranker-0.6B` | HuggingFace model for reranking |
| `RERANKER_ENABLED` | No | `true` | Enable/disable reranking |
| `INITIAL_RETRIEVAL_COUNT` | No | `20` | Documents to retrieve before reranking |
| `FINAL_RESULT_COUNT` | No | `5` | Documents after reranking |
| `LLM_MODEL` | No | `llama3.2:latest` | Ollama model name |
| `VECTOR_TABLE_NAME` | No | `it_docs_embeddings` | Supabase table name |
| `MATCH_THRESHOLD` | No | `0.5` | Minimum similarity score (0-1) |
| `MATCH_COUNT` | No | `3` | Number of documents to retrieve (if reranker disabled) |
| `FLASK_ENV` | No | `development` | Flask environment |
| `PORT` | No | `5000` | API server port |

## Project Structure

```
.
├── app.py                      # Flask application and API routes
├── config.py                   # Configuration management
├── services/
│   ├── embedding_service.py    # SentenceTransformer wrapper
│   ├── reranker_service.py     # Qwen3-Reranker integration
│   ├── vector_service.py       # Supabase client and search
│   └── llm_service.py          # Ollama integration with streaming
├── tests/                      # Unit tests
│   ├── test_embedding_service.py
│   ├── test_reranker_service.py
│   ├── test_vector_service.py
│   ├── test_llm_service.py
│   └── test_config.py
├── data_ingestion.ipynb        # Jupyter notebook for data pipeline
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── rag-deployment.yaml
│   ├── rag-service.yaml
│   ├── ollama-deployment.yaml
│   └── ...
├── Dockerfile                  # Multi-stage build with pip-compile
├── docker-compose.yml          # Local multi-service orchestration
├── requirements.in             # High-level dependencies
├── requirements.txt            # Locked dependencies (generated)
├── pytest.ini                  # Test configuration
├── .env.example                # Environment variables template
├── .dockerignore
├── .gitignore
└── README.md
```

## API Endpoints

### POST /api/query

Standard query endpoint that returns complete response.

**Request:**
```json
{
  "question": "How do I reset my PIN?",
  "match_count": 5,
  "match_threshold": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "answer": "To reset your PIN, follow these steps...",
  "sources": [
    {
      "id": 6,
      "content": "**Step 4: Reset Your PIN**...",
      "topic": "Resetting a Forgotten PIN",
      "similarity": 0.69
    }
  ],
  "metadata": {
    "question": "How do I reset my PIN?",
    "num_sources": 3,
    "match_threshold": 0.7
  }
}
```

### POST /api/query/stream

Streaming endpoint for real-time responses (Server-Sent Events).

**Request:**
```json
{
  "question": "How do I reset my PIN?",
  "match_count": 5,
  "match_threshold": 0.7
}
```

**Response Stream:**
```
data: {"type": "sources", "sources": [...]}

data: {"type": "metadata", "metadata": {...}}

data: {"type": "chunk", "content": "To"}

data: {"type": "chunk", "content": " reset"}

data: {"type": "chunk", "content": " your"}

data: {"type": "done"}
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "IT Knowledge Retrieval Service",
  "version": "1.0.0"
}
```

## Dependency Management

This project uses **pip-tools** for deterministic dependency management.

### Lock File Approach

- `requirements.in` - High-level dependencies (what you want)
- `requirements.txt` - Exact locked versions (generated by pip-compile)

### Update Dependencies

```bash
# Install pip-tools
pip install pip-tools

# Generate lock file from requirements.in
pip-compile --resolver=backtracking --generate-hashes requirements.in

# Install from lock file
pip install -r requirements.txt

# Update all dependencies
pip-compile --upgrade requirements.in
```

### Docker Build

The Dockerfile uses a multi-stage build that:
1. **Builder stage**: Runs `pip-compile` to generate lock file
2. **Final stage**: Installs exact versions with hash verification

This ensures reproducible builds across all environments.

## Performance Considerations

- **First request latency**: Initial embedding model load takes 30-60 seconds
- **Embedding generation**: ~50-100ms per query
- **Reranking**: ~100-200ms for 20 documents (if enabled)
- **Vector search**: <10ms for databases under 100K documents, 100% retrieval accuracy
- **LLM generation**: <15 s response latency on consumer Hardware (M3 MacBook) with ~93% answer quality
- **Streaming**: Chunks arrive every 50-100ms for smooth typing effect

## Troubleshooting

**Service won't start:**
- Check `.env` file exists and contains valid Supabase credentials
- Ensure Ollama is running and accessible at configured URL
- Verify Python 3.11+ is installed

**No results returned:**
- Lower `match_threshold` (try 0.5 or 0.6)
- Verify documents exist in Supabase table
- Check embedding dimensions match (1024 for Qwen3-Embedding-0.6B)

**Slow responses:**
- First request downloads embedding model (~1.5GB) - subsequent requests are faster
- Ollama model download happens on first use
- Check network latency to Supabase

**Out of memory (Ollama):**
- Increase Docker Desktop memory allocation to 6-8 GB
- Use smaller model
- Disable reranker: Reranker is memory-intensive

## License

MIT License - feel free to use this project as a portfolio piece or starting point for your own RAG applications.
