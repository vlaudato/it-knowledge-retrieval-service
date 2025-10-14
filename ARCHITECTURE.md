# Architecture Overview

## System Flow

```
┌─────────────────┐
│   React App     │
│  (Your Frontend)│
└────────┬────────┘
         │ HTTP POST /api/query
         │ {"question": "..."}
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask API Server                         │
│                        (app.py)                              │
└─────────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────┐
         │                                          │
         ▼                                          ▼
┌──────────────────────┐                 ┌──────────────────────┐
│  Embedding Service   │                 │   Config Manager     │
│ (embedding_service)  │                 │    (config.py)       │
│                      │                 │                      │
│ - Loads Qwen model   │                 │ - Loads .env vars    │
│ - Generates vectors  │                 │ - Validates config   │
└──────────┬───────────┘                 └──────────────────────┘
           │
           │ Query Embedding
           │ [768-dim vector]
           ▼
┌──────────────────────┐
│   Vector Service     │
│  (vector_service)    │
│                      │
│ - Connects Supabase  │
│ - Calls RPC function │
│ - Returns top-k docs │
└──────────┬───────────┘
           │
           │ Similar Documents
           │ [{content, similarity}, ...]
           ▼
┌──────────────────────┐
│    LLM Service       │
│   (llm_service)      │
│                      │
│ - Builds context     │
│ - Prompts OpenAI     │
│ - Returns answer     │
└──────────┬───────────┘
           │
           │ Generated Answer
           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Response to React                        │
│  {                                                           │
│    "answer": "...",                                          │
│    "sources": [...],                                         │
│    "metadata": {...}                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Flask API (`app.py`)
**Responsibilities:**
- Receives HTTP requests from frontend
- Orchestrates the RAG pipeline
- Handles errors and validation
- Returns formatted responses

**Key Endpoints:**
- `POST /api/query` - Main RAG endpoint
- `GET /health` - Health check
- `POST /api/embedding` - Utility endpoint

### 2. Embedding Service (`services/embedding_service.py`)
**Responsibilities:**
- Loads and caches the Qwen embedding model
- Converts text to vector embeddings
- Ensures consistent embedding generation

**Key Methods:**
- `generate_embedding(text)` - Single text to vector
- `generate_embeddings(texts)` - Batch processing
- `get_embedding_dimension()` - Returns vector size

### 3. Vector Service (`services/vector_service.py`)
**Responsibilities:**
- Connects to Supabase
- Executes semantic search via RPC
- Retrieves relevant document chunks

**Key Methods:**
- `search_similar_documents()` - Semantic search
- `get_document_by_id()` - Direct retrieval

### 4. LLM Service (`services/llm_service.py`)
**Responsibilities:**
- Formats retrieved documents as context
- Constructs prompts for OpenAI
- Generates final answers

**Key Methods:**
- `generate_answer()` - Main answer generation
- `_build_context()` - Context formatting

### 5. Config Manager (`config.py`)
**Responsibilities:**
- Loads environment variables
- Validates configuration
- Provides centralized settings

## Data Flow Example

### User asks: "What is the remote work policy?"

```
Step 1: Embedding Generation
─────────────────────────────
Input:  "What is the remote work policy?"
Output: [0.123, -0.456, 0.789, ..., 0.234]  (768 dimensions)

Step 2: Vector Search
─────────────────────────────
Query:  [0.123, -0.456, ...]
Search: Supabase vector database
Output: [
  {
    "content": "Remote work is allowed 3 days per week...",
    "similarity": 0.89
  },
  {
    "content": "Employees must notify their manager...",
    "similarity": 0.85
  },
  ...
]

Step 3: Context Building
─────────────────────────────
Format: "[Document 1]\nRemote work is allowed...\n\n[Document 2]\n..."

Step 4: LLM Prompting
─────────────────────────────
System: "You are a helpful assistant..."
User:   "Context: [documents]\n\nQuestion: What is the remote work policy?"
LLM:    "According to the company policy, remote work is allowed..."

Step 5: Response
─────────────────────────────
{
  "success": true,
  "answer": "According to the company policy...",
  "sources": [...],
  "metadata": {...}
}
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Flask | HTTP API server |
| **Embeddings** | SentenceTransformers + Qwen | Text to vector conversion |
| **Vector DB** | Supabase (PostgreSQL + pgvector) | Semantic search |
| **LLM** | OpenAI GPT | Answer generation |
| **Environment** | python-dotenv | Configuration |
| **CORS** | flask-cors | Frontend integration |
| **Production Server** | Gunicorn | Production deployment |

## Deployment Options

### Option 1: Local Development
```bash
python app.py
```
- Fast iteration
- Easy debugging
- Single process

### Option 2: Docker
```bash
docker build -t rag-service .
docker run -p 5000:5000 --env-file .env rag-service
```
- Consistent environment
- Easy deployment
- Isolated dependencies

### Option 3: Docker Compose
```bash
docker-compose up -d
```
- Multi-service orchestration
- Volume management
- Health checks

### Option 4: Production (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```
- Multiple workers
- Better performance
- Production-ready

## Performance Considerations

### Model Loading
- **First request**: ~30-60 seconds (model download)
- **Subsequent requests**: <1 second (cached)
- **Memory usage**: ~2GB for embedding model

### Request Latency
- **Embedding generation**: ~50-200ms
- **Vector search**: ~10-50ms (depends on DB size)
- **LLM generation**: ~1-5 seconds (depends on model)
- **Total**: ~2-6 seconds per query

### Optimization Tips
1. **Cache embeddings** for frequent queries
2. **Use smaller models** if speed is critical
3. **Batch requests** when possible
4. **Add Redis** for caching
5. **Use streaming** for LLM responses

## Security Considerations

### Current Implementation
✅ Environment variables for secrets
✅ CORS enabled for frontend
✅ Input validation
✅ Error handling

### Production Recommendations
- [ ] Add API key authentication
- [ ] Rate limiting
- [ ] Request logging
- [ ] HTTPS only
- [ ] Input sanitization
- [ ] Secrets management (e.g., AWS Secrets Manager)

## Scaling Strategy

### Vertical Scaling
- Increase server resources
- More RAM for model caching
- Faster CPU for embeddings

### Horizontal Scaling
- Multiple Gunicorn workers
- Load balancer (nginx, AWS ALB)
- Separate embedding service
- Cache layer (Redis)

### Microservices Architecture
```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   API       │────▶│  Embedding       │────▶│  Vector     │
│   Gateway   │     │  Service         │     │  Service    │
└─────────────┘     └──────────────────┘     └─────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  LLM Service     │
                    └──────────────────┘
```

## Monitoring & Observability

### Recommended Metrics
- Request count
- Response time (p50, p95, p99)
- Error rate
- Token usage (OpenAI)
- Cache hit rate
- Model inference time

### Logging
- Request/response logging
- Error tracking (Sentry)
- Performance monitoring (New Relic, DataDog)

## Future Enhancements

1. **Streaming responses** - Real-time answer generation
2. **Multi-model support** - Allow different LLMs
3. **Conversation history** - Multi-turn conversations
4. **Advanced RAG** - Hybrid search, re-ranking
5. **Analytics dashboard** - Usage statistics
6. **A/B testing** - Compare different prompts/models
