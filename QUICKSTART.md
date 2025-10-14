# Quick Start Guide

Get your RAG service running in 5 minutes!

## 🚀 Fast Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` File
```bash
# Copy and edit
cp .env.example .env
```

Add your credentials:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
OPENAI_API_KEY=sk-...
```

### 3. Run the Service
```bash
python app.py
```

### 4. Test It
```bash
# In another terminal
python test_api.py
```

Or use curl:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your question?"}'
```

## 📝 Important Configuration

### If your Supabase function has a different name:

Edit `services/vector_service.py` line 31:
```python
response = self.client.rpc(
    'your_function_name',  # Change this to match your function
    {...}
)
```

### If your table has different column names:

Edit `services/llm_service.py` line 68:
```python
content = doc.get('your_column_name')  # Change 'content' to your column
```

## 🔗 Connect to React

```javascript
const response = await fetch('http://localhost:5000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: userQuestion })
});

const data = await response.json();
console.log(data.answer);
```

## 🐳 Docker (Optional)

```bash
docker-compose up -d
```

## 📚 Full Documentation

- **SETUP.md** - Detailed setup instructions
- **USAGE.md** - API documentation and examples
- **README.md** - Project overview

## ⚡ API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/query` | POST | Ask questions (main endpoint) |
| `/api/embedding` | POST | Generate embeddings (utility) |

## 🎯 What Happens When You Query?

1. **Your question** → Converted to embedding (Qwen model)
2. **Embedding** → Searches Supabase for similar documents
3. **Retrieved docs** → Sent to OpenAI with your question
4. **OpenAI** → Generates answer based on context
5. **Answer** → Returned to your React app

## 🔧 Common Issues

**"Missing environment variables"**
→ Check your `.env` file exists and has all required values

**"Error searching documents"**
→ Verify Supabase credentials and function name

**First request is slow**
→ Normal! Model downloads on first run (~2GB)

**CORS errors**
→ Already handled! Service has CORS enabled

## 💡 Tips

- Use `gpt-3.5-turbo` for faster/cheaper responses
- Use `gpt-4` for better quality (slower/pricier)
- Adjust `MATCH_COUNT` to retrieve more/fewer documents
- Adjust `MATCH_THRESHOLD` to control relevance filtering

## 🎉 You're Ready!

Your RAG service is now running and ready to answer questions based on your knowledge base!
