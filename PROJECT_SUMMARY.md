# Project Summary: IT Knowledge Retrieval Service

## 🎯 What We Built

A complete **RAG (Retrieval-Augmented Generation)** service that:
1. Takes a user's question
2. Converts it to an embedding using Qwen0.6B
3. Searches your Supabase vector database for relevant documents
4. Sends the retrieved context to OpenAI
5. Returns an AI-generated answer to your React frontend

## 📁 Project Structure

```
it-knowledge-retrieval-service/
├── app.py                      # Main Flask application (entry point)
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
│
├── services/                   # Core business logic
│   ├── __init__.py
│   ├── embedding_service.py   # Qwen embedding generation
│   ├── vector_service.py      # Supabase vector search
│   └── llm_service.py         # OpenAI answer generation
│
├── test_api.py                # API testing script
│
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Docker Compose setup
├── .dockerignore             # Docker ignore rules
│
└── Documentation/
    ├── README.md              # Project overview
    ├── QUICKSTART.md          # 5-minute setup guide
    ├── SETUP.md               # Detailed setup instructions
    ├── USAGE.md               # API documentation
    ├── ARCHITECTURE.md        # System architecture
    └── PROJECT_SUMMARY.md     # This file
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Run the service
python app.py

# 4. Test it
python test_api.py
```

## 🔑 Key Files Explained

### Core Application Files

**`app.py`** (Main Application)
- Flask web server
- Defines API endpoints (`/api/query`, `/health`, `/api/embedding`)
- Orchestrates the RAG pipeline
- Handles errors and responses

**`config.py`** (Configuration)
- Loads environment variables from `.env`
- Validates required settings
- Provides centralized configuration

**`requirements.txt`** (Dependencies)
- Flask, Flask-CORS
- sentence-transformers (embeddings)
- supabase (database)
- openai (LLM)
- torch (ML framework)

### Service Layer

**`services/embedding_service.py`**
- Loads Qwen embedding model
- Converts text to 768-dimensional vectors
- Caches model for performance

**`services/vector_service.py`**
- Connects to Supabase
- Executes semantic search via Postgres function
- Returns relevant document chunks

**`services/llm_service.py`**
- Formats retrieved documents as context
- Constructs prompts for OpenAI
- Generates final answers

### Testing & Deployment

**`test_api.py`**
- Tests all endpoints
- Validates the complete flow
- Useful for debugging

**`Dockerfile`**
- Containerizes the application
- Production-ready image
- Uses Gunicorn server

**`docker-compose.yml`**
- One-command deployment
- Includes health checks
- Volume management

### Documentation

**`QUICKSTART.md`** - Get started in 5 minutes
**`SETUP.md`** - Detailed setup with troubleshooting
**`USAGE.md`** - API documentation and examples
**`ARCHITECTURE.md`** - System design and flow
**`README.md`** - Project overview

## 🔄 How It Works

### The RAG Pipeline

```
User Question
    ↓
[1] Generate Embedding (Qwen model)
    ↓
[2] Search Vector DB (Supabase)
    ↓
[3] Retrieve Top-K Documents
    ↓
[4] Build Context from Documents
    ↓
[5] Prompt LLM (OpenAI)
    ↓
[6] Return Answer
```

### Example Request/Response

**Request:**
```bash
POST http://localhost:5000/api/query
Content-Type: application/json

{
  "question": "What is the remote work policy?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "According to the company policy, remote work is allowed up to 3 days per week...",
  "sources": [
    {
      "id": 123,
      "content": "Remote work policy states...",
      "similarity": 0.89
    }
  ],
  "metadata": {
    "question": "What is the remote work policy?",
    "num_sources": 5,
    "match_threshold": 0.7
  }
}
```

## ⚙️ Configuration

### Required Environment Variables

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
OPENAI_API_KEY=sk-...
```

### Optional Configuration

```env
EMBEDDING_MODEL=Qwen/Qwen2-0.5B-Instruct
LLM_MODEL=gpt-3.5-turbo
VECTOR_TABLE_NAME=documents
MATCH_THRESHOLD=0.7
MATCH_COUNT=5
PORT=5000
```

## 🔌 Integration with React

### Basic Example

```javascript
async function askQuestion(question) {
  const response = await fetch('http://localhost:5000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data.answer;
  } else {
    throw new Error(data.error);
  }
}
```

### With Error Handling

```javascript
import { useState } from 'react';

function ChatComponent() {
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (question) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setAnswer(data.answer);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to connect to the server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {answer && <p>{answer}</p>}
    </div>
  );
}
```

## 🐳 Deployment Options

### Local Development
```bash
python app.py
```
Best for: Development, testing, debugging

### Docker
```bash
docker build -t rag-service .
docker run -p 5000:5000 --env-file .env rag-service
```
Best for: Consistent environment, easy deployment

### Docker Compose
```bash
docker-compose up -d
```
Best for: Production-like setup, multi-service apps

### Production (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```
Best for: Production deployment, better performance

## 📊 API Endpoints

| Endpoint | Method | Purpose | Request Body |
|----------|--------|---------|--------------|
| `/health` | GET | Health check | None |
| `/api/query` | POST | Ask questions | `{"question": "..."}` |
| `/api/embedding` | POST | Generate embedding | `{"text": "..."}` |

## 🛠️ Customization Points

### 1. Change the Supabase Function Name

Edit `services/vector_service.py`:
```python
response = self.client.rpc(
    'your_function_name',  # Change this
    {...}
)
```

### 2. Change Document Field Names

Edit `services/llm_service.py`:
```python
content = doc.get('your_field_name')  # Change 'content'
```

### 3. Customize the Prompt

Edit `services/llm_service.py`:
```python
system_prompt = """Your custom prompt here..."""
```

### 4. Change the LLM Model

Edit `.env`:
```env
LLM_MODEL=gpt-4  # or gpt-3.5-turbo, etc.
```

### 5. Adjust Search Parameters

Edit `.env`:
```env
MATCH_COUNT=10        # Retrieve more documents
MATCH_THRESHOLD=0.8   # Higher threshold = more strict
```

## 🎓 What You Learned

1. **RAG Architecture** - How to build a complete RAG system
2. **Flask API** - Creating REST APIs with Flask
3. **Embeddings** - Using SentenceTransformers for text embeddings
4. **Vector Search** - Semantic search with Supabase
5. **LLM Integration** - Prompting OpenAI with context
6. **Docker** - Containerizing Python applications
7. **Best Practices** - Project structure, error handling, configuration

## 🚦 Next Steps

### Immediate
1. ✅ Set up your `.env` file
2. ✅ Run `python app.py`
3. ✅ Test with `python test_api.py`
4. ✅ Integrate with your React app

### Short Term
- Add authentication (API keys)
- Implement caching for frequent queries
- Add request logging
- Monitor OpenAI token usage

### Long Term
- Add conversation history (multi-turn chat)
- Implement streaming responses
- Add more LLM providers (Anthropic, etc.)
- Build an admin dashboard
- Add analytics and monitoring

## 📚 Resources

### Documentation Files
- **QUICKSTART.md** - Fast 5-minute setup
- **SETUP.md** - Detailed setup guide
- **USAGE.md** - API usage and examples
- **ARCHITECTURE.md** - System design details

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SentenceTransformers](https://www.sbert.net/)
- [Supabase Docs](https://supabase.com/docs)
- [OpenAI API](https://platform.openai.com/docs)

## 🤝 Support

If you encounter issues:

1. **Check the logs** - Console output shows detailed errors
2. **Verify configuration** - Ensure `.env` is correct
3. **Test components** - Use `test_api.py` to isolate issues
4. **Review documentation** - Check SETUP.md for troubleshooting

## 🎉 Congratulations!

You now have a fully functional RAG service that:
- ✅ Generates embeddings using Qwen
- ✅ Searches your vector database
- ✅ Generates AI-powered answers
- ✅ Integrates with your React frontend
- ✅ Is production-ready with Docker

Happy building! 🚀
