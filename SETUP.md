# Setup Instructions

Follow these steps to get your RAG service up and running.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Supabase account with vector database set up
- OpenAI API key

## Step-by-Step Setup

### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (for frontend integration)
- sentence-transformers (for embeddings)
- supabase (database client)
- openai (LLM integration)
- python-dotenv (environment variables)
- gunicorn (production server)
- torch (required for embeddings)

### Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Model Configuration (optional, defaults are fine)
EMBEDDING_MODEL=Qwen/Qwen2-0.5B-Instruct
LLM_MODEL=gpt-3.5-turbo

# Database Configuration (adjust if needed)
VECTOR_TABLE_NAME=documents
MATCH_THRESHOLD=0.7
MATCH_COUNT=5
```

### Step 4: Verify Supabase Setup

Make sure your Supabase database has:

1. **A table with embeddings** (e.g., `documents` table with columns):
   - `id` (primary key)
   - `content` (text)
   - `embedding` (vector)
   - Any other metadata columns

2. **A Postgres function for semantic search** (e.g., `match_documents`):

```sql
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(768),  -- Adjust dimension based on your model
  match_count int DEFAULT 5,
  match_threshold float DEFAULT 0.7
)
RETURNS TABLE (
  id bigint,
  content text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    1 - (documents.embedding <=> query_embedding) as similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

**Important Notes:**
- If your function has a different name, update it in `services/vector_service.py`
- Adjust the vector dimension to match your embedding model
- If your table has different column names, update `services/llm_service.py`

### Step 5: Run the Application

```bash
python app.py
```

You should see:
```
Loading embedding model: Qwen/Qwen2-0.5B-Instruct
Embedding model loaded successfully
Connected to Supabase vector database (table: documents)
LLM service initialized with model: gpt-3.5-turbo
All services initialized successfully!

============================================================
Starting Flask server on port 5000...
Environment: development
============================================================
```

### Step 6: Test the Service

In a new terminal, run the test script:

```bash
python test_api.py
```

Or test manually with curl:

```bash
# Health check
curl http://localhost:5000/health

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

### Step 7: Integrate with Your React App

Update your React app to call the API:

```javascript
const API_URL = 'http://localhost:5000';

async function askQuestion(question) {
  const response = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });
  
  const data = await response.json();
  return data;
}
```

## Docker Deployment (Optional)

### Option 1: Docker

```bash
# Build
docker build -t rag-service .

# Run
docker run -p 5000:5000 --env-file .env rag-service
```

### Option 2: Docker Compose

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

### Issue: "Missing required environment variables"
**Solution:** Check that your `.env` file exists and has all required variables.

### Issue: Model download is slow
**Solution:** First run will download the embedding model (~2GB). This is normal and only happens once.

### Issue: "Error searching documents"
**Solution:** 
- Verify Supabase credentials
- Check that your Postgres function exists
- Ensure function name matches in code

### Issue: CORS errors from React
**Solution:** The service has CORS enabled. If issues persist, check that you're using the correct URL.

### Issue: Out of memory
**Solution:** The embedding model requires ~2GB RAM. Consider using a smaller model or increasing available memory.

## Next Steps

1. **Customize the prompt**: Edit `services/llm_service.py` to adjust the system prompt
2. **Add authentication**: Implement API key authentication if needed
3. **Add caching**: Cache frequent queries to reduce costs
4. **Monitor usage**: Add logging and monitoring for production
5. **Scale**: Use gunicorn with multiple workers for production

## Project Structure

```
it-knowledge-retrieval-service/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Example environment file
├── services/
│   ├── __init__.py
│   ├── embedding_service.py   # Embedding generation
│   ├── vector_service.py      # Supabase integration
│   └── llm_service.py         # LLM prompting
├── test_api.py                # Test script
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── README.md                  # Project overview
├── USAGE.md                   # API usage guide
└── SETUP.md                   # This file
```

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all environment variables are set correctly
3. Ensure your Supabase database is properly configured
4. Test each component individually using the test script

Happy coding! 🚀
