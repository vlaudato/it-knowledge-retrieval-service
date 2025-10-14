# Usage Guide

## Quick Start

### 1. Setup Environment

Create a `.env` file with your credentials:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-your-api-key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Service

```bash
python app.py
```

The service will start on `http://localhost:5000`

## API Usage

### Query Endpoint

**Endpoint:** `POST /api/query`

**Request:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the company policy on remote work?",
    "match_count": 5,
    "match_threshold": 0.7
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Based on the company policy...",
  "sources": [
    {
      "id": 1,
      "content": "Document content...",
      "similarity": 0.85,
      "metadata": {}
    }
  ],
  "metadata": {
    "question": "What is the company policy on remote work?",
    "num_sources": 5,
    "match_threshold": 0.7
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:5000/health
```

### Generate Embedding (Utility)

**Endpoint:** `POST /api/embedding`

```bash
curl -X POST http://localhost:5000/api/embedding \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text to embed"}'
```

## Integration with React Frontend

### Example React Code

```javascript
async function askQuestion(question) {
  try {
    const response = await fetch('http://localhost:5000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Answer:', data.answer);
      console.log('Sources:', data.sources);
      return data;
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}

// Usage
askQuestion('What is the company policy on remote work?');
```

### Example with Axios

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export const queryRAG = async (question, options = {}) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/query`, {
      question,
      match_count: options.matchCount || 5,
      match_threshold: options.matchThreshold || 0.7,
    });
    
    return response.data;
  } catch (error) {
    console.error('RAG query failed:', error);
    throw error;
  }
};
```

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t rag-service .

# Run the container
docker run -p 5000:5000 --env-file .env rag-service
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Testing

Run the test script to verify everything is working:

```bash
python test_api.py
```

## Configuration Options

All configuration is done through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase API key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `EMBEDDING_MODEL` | HuggingFace model name | `Qwen/Qwen2-0.5B-Instruct` |
| `LLM_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `VECTOR_TABLE_NAME` | Supabase table name | `documents` |
| `MATCH_THRESHOLD` | Minimum similarity score | `0.7` |
| `MATCH_COUNT` | Number of results to retrieve | `5` |
| `PORT` | Server port | `5000` |

## Important Notes

### Supabase Function Name

The code assumes your Postgres function is named `match_documents`. If you named it differently, update `services/vector_service.py`:

```python
response = self.client.rpc(
    'your_function_name',  # Change this
    {
        'query_embedding': query_embedding,
        'match_count': match_count,
        'match_threshold': match_threshold
    }
).execute()
```

### Document Schema

The code expects documents to have a `content` field. If your schema uses different field names (e.g., `text`, `chunk`), update `services/llm_service.py` in the `_build_context` method.

### Model Loading Time

The first request will be slower as the embedding model needs to be downloaded and loaded. Subsequent requests will be much faster.

## Troubleshooting

### "Missing required environment variables"
- Ensure your `.env` file exists and contains all required variables
- Check that variable names match exactly

### "Error searching documents"
- Verify your Supabase credentials are correct
- Ensure your Postgres function exists and has the correct name
- Check that the function signature matches the expected parameters

### Model download issues
- Ensure you have internet connectivity
- The model will be cached after first download
- Check available disk space (~2GB needed for model)

### CORS errors from frontend
- The service has CORS enabled by default
- If issues persist, check your frontend URL configuration
