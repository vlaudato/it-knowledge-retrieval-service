# IT Knowledge Retrieval Service

A RAG (Retrieval-Augmented Generation) service that uses embeddings and vector search to answer questions based on your knowledge base.

## Features

- **Embedding Generation**: Uses Qwen0.6B model via HuggingFace SentenceTransformer
- **Vector Search**: Queries Supabase vector database using cosine similarity
- **LLM Integration**: Generates contextual answers using OpenAI GPT
- **REST API**: Simple Flask endpoint for easy integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `OPENAI_API_KEY`: Your OpenAI API key

### 3. Run the Service

```bash
python app.py
```

The service will start on `http://localhost:5000`

## API Endpoints

### POST /api/query

Ask a question and get an AI-generated answer based on your knowledge base.

**Request:**
```json
{
  "question": "What is the company policy on remote work?"
}
```

**Response:**
```json
{
  "answer": "According to the company policy...",
  "sources": [
    {
      "content": "...",
      "metadata": {...}
    }
  ],
  "success": true
}
```

### GET /health

Health check endpoint.

## Docker Deployment

Build and run with Docker:

```bash
docker build -t rag-service .
docker run -p 5000:5000 --env-file .env rag-service
```

## Architecture

1. **Query Reception**: Flask receives the user's question
2. **Embedding Generation**: Convert question to vector using Qwen0.6B
3. **Vector Search**: Query Supabase for similar document chunks
4. **Context Assembly**: Prepare retrieved chunks as context
5. **LLM Prompting**: Send context + question to OpenAI
6. **Response**: Return generated answer to client

## Project Structure

```
.
├── app.py                 # Flask application entry point
├── services/
│   ├── embedding_service.py    # Embedding generation
│   ├── vector_service.py       # Supabase vector search
│   └── llm_service.py          # LLM integration
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── README.md             # This file
```
