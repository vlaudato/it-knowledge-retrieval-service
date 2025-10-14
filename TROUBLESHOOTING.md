# Troubleshooting Guide

Common issues and their solutions.

## 🔴 Startup Issues

### Error: "Missing required environment variables"

**Cause:** `.env` file is missing or incomplete

**Solution:**
```bash
# 1. Check if .env exists
ls .env

# 2. If not, create it from example
cp .env.example .env

# 3. Edit and add your credentials
# Make sure these are set:
# - SUPABASE_URL
# - SUPABASE_KEY
# - OPENAI_API_KEY
```

### Error: "No module named 'flask'"

**Cause:** Dependencies not installed

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or if using virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Error: "Failed to load model"

**Cause:** Model download failed or insufficient disk space

**Solution:**
```bash
# 1. Check internet connection
# 2. Check disk space (need ~2GB)
# 3. Try downloading manually:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Qwen/Qwen2-0.5B-Instruct')"
```

## 🔴 Database Issues

### Error: "Error searching documents"

**Cause:** Supabase connection or function issue

**Solution:**

1. **Verify credentials:**
```bash
# Check your .env file
cat .env | grep SUPABASE
```

2. **Test Supabase connection:**
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print("Connected successfully!")
```

3. **Check function exists:**
```sql
-- Run in Supabase SQL editor
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_name = 'match_documents';
```

4. **Update function name if different:**
Edit `services/vector_service.py` line 31:
```python
response = self.client.rpc(
    'your_actual_function_name',  # Change this
    {...}
)
```

### Error: "No matching documents found"

**Cause:** Threshold too high or no relevant data

**Solution:**

1. **Lower the threshold:**
```env
# In .env
MATCH_THRESHOLD=0.5  # Lower from 0.7
```

2. **Check if data exists:**
```sql
-- In Supabase SQL editor
SELECT COUNT(*) FROM documents;
SELECT * FROM documents LIMIT 5;
```

3. **Verify embeddings are populated:**
```sql
SELECT id, embedding IS NOT NULL as has_embedding 
FROM documents 
LIMIT 10;
```

## 🔴 API Issues

### Error: "CORS policy blocked"

**Cause:** Frontend trying to access API from different origin

**Solution:**

The app already has CORS enabled. If still having issues:

1. **Check the URL:**
```javascript
// Make sure you're using the correct URL
const API_URL = 'http://localhost:5000';  // Not https
```

2. **Verify CORS is enabled:**
In `app.py`, check:
```python
from flask_cors import CORS
CORS(app)  # This should be present
```

3. **For specific origins:**
```python
# In app.py, replace CORS(app) with:
CORS(app, origins=['http://localhost:3000'])  # Your React app URL
```

### Error: 404 Not Found

**Cause:** Wrong endpoint URL

**Solution:**

Check your endpoint:
```javascript
// Correct endpoints:
POST http://localhost:5000/api/query      ✅
GET  http://localhost:5000/health         ✅

// Wrong:
POST http://localhost:5000/query          ❌
POST http://localhost:5000/api/ask        ❌
```

### Error: 500 Internal Server Error

**Cause:** Various server-side issues

**Solution:**

1. **Check server logs:**
```bash
# Look at the console where you ran python app.py
# Error details will be printed there
```

2. **Enable debug mode:**
```env
# In .env
FLASK_ENV=development
```

3. **Test individual components:**
```bash
python test_api.py
```

## 🔴 OpenAI Issues

### Error: "Invalid API key"

**Cause:** Wrong or expired OpenAI API key

**Solution:**

1. **Verify API key:**
```bash
# Check .env
cat .env | grep OPENAI_API_KEY

# Test it
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

2. **Get new key:**
- Go to https://platform.openai.com/api-keys
- Create new secret key
- Update `.env`

### Error: "Rate limit exceeded"

**Cause:** Too many requests to OpenAI

**Solution:**

1. **Wait a bit** - Rate limits reset over time

2. **Upgrade OpenAI plan** - Get higher limits

3. **Add rate limiting:**
```python
# In app.py, add:
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["10 per minute"])
```

### Error: "Insufficient quota"

**Cause:** No credits in OpenAI account

**Solution:**

1. **Check balance:**
- Go to https://platform.openai.com/account/billing
- Add credits if needed

2. **Use cheaper model:**
```env
# In .env
LLM_MODEL=gpt-3.5-turbo  # Cheaper than gpt-4
```

## 🔴 Performance Issues

### Issue: First request is very slow (30-60 seconds)

**Cause:** Model downloading on first run

**Solution:**

This is **normal**! The embedding model (~2GB) downloads on first run.

**To pre-download:**
```python
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Qwen/Qwen2-0.5B-Instruct')"
```

Subsequent requests will be much faster (<1 second).

### Issue: All requests are slow

**Cause:** Various performance bottlenecks

**Solution:**

1. **Check OpenAI model:**
```env
LLM_MODEL=gpt-3.5-turbo  # Faster than gpt-4
```

2. **Reduce match count:**
```env
MATCH_COUNT=3  # Fewer documents = faster
```

3. **Use production server:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Issue: High memory usage

**Cause:** Embedding model in memory

**Solution:**

This is **expected**. The model needs ~2GB RAM.

**To reduce:**
- Use a smaller embedding model
- Increase server RAM
- Use model quantization

## 🔴 Docker Issues

### Error: "Cannot connect to Docker daemon"

**Cause:** Docker not running

**Solution:**
```bash
# Start Docker Desktop (Windows/Mac)
# Or start Docker service (Linux)
sudo systemctl start docker
```

### Error: "Port 5000 already in use"

**Cause:** Another service using port 5000

**Solution:**

1. **Use different port:**
```bash
docker run -p 5001:5000 --env-file .env rag-service
```

2. **Or stop the other service:**
```bash
# Find what's using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux

# Kill the process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Mac/Linux
```

### Error: "Build failed"

**Cause:** Various Docker build issues

**Solution:**

1. **Check Dockerfile exists:**
```bash
ls Dockerfile
```

2. **Check Docker is running:**
```bash
docker --version
```

3. **Try clean build:**
```bash
docker build --no-cache -t rag-service .
```

## 🔴 Testing Issues

### test_api.py fails with "Connection refused"

**Cause:** Server not running

**Solution:**
```bash
# In one terminal:
python app.py

# In another terminal:
python test_api.py
```

### test_api.py fails with timeout

**Cause:** Server is slow or stuck

**Solution:**

1. **Check server logs** - Look for errors

2. **Increase timeout:**
```python
# In test_api.py, add timeout:
response = requests.post(..., timeout=60)
```

3. **Test health endpoint first:**
```bash
curl http://localhost:5000/health
```

## 🔴 Integration Issues

### React app can't connect to API

**Cause:** Wrong URL or CORS issue

**Solution:**

1. **Check API is running:**
```bash
curl http://localhost:5000/health
```

2. **Use correct URL in React:**
```javascript
const API_URL = 'http://localhost:5000';  // Not https, not 127.0.0.1
```

3. **Check browser console** for detailed error

### Response format unexpected

**Cause:** API response structure changed

**Solution:**

Check response structure:
```javascript
const data = await response.json();
console.log(data);

// Expected structure:
// {
//   success: true,
//   answer: "...",
//   sources: [...],
//   metadata: {...}
// }
```

## 🛠️ Debugging Tips

### Enable Verbose Logging

```python
# In app.py, add at the top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Components Individually

```python
# Test embedding service
from services.embedding_service import EmbeddingService
service = EmbeddingService('Qwen/Qwen2-0.5B-Instruct')
embedding = service.generate_embedding("test")
print(f"Embedding dimension: {len(embedding)}")

# Test vector service
from services.vector_service import VectorService
service = VectorService(SUPABASE_URL, SUPABASE_KEY, 'documents')
results = service.search_similar_documents([0.1] * 768)
print(f"Found {len(results)} documents")

# Test LLM service
from services.llm_service import LLMService
service = LLMService(OPENAI_API_KEY)
answer = service.generate_answer("Test?", [{"content": "Test content"}])
print(answer)
```

### Check Environment Variables

```python
# In Python:
import os
from dotenv import load_dotenv

load_dotenv()
print("SUPABASE_URL:", os.getenv('SUPABASE_URL'))
print("SUPABASE_KEY:", os.getenv('SUPABASE_KEY')[:10] + "...")
print("OPENAI_API_KEY:", os.getenv('OPENAI_API_KEY')[:10] + "...")
```

## 📞 Still Having Issues?

### Checklist

- [ ] `.env` file exists and has all required variables
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Supabase credentials are correct
- [ ] OpenAI API key is valid
- [ ] Postgres function exists in Supabase
- [ ] Port 5000 is available
- [ ] Internet connection is working
- [ ] Sufficient disk space (~2GB)
- [ ] Sufficient RAM (~2GB)

### Get More Help

1. **Check logs** - Console output has detailed errors
2. **Test with curl** - Isolate frontend vs backend issues
3. **Run test script** - `python test_api.py`
4. **Check documentation** - SETUP.md, USAGE.md, ARCHITECTURE.md

### Common Log Messages

| Message | Meaning | Action |
|---------|---------|--------|
| "Loading embedding model" | Model downloading | Wait, this is normal |
| "Connected to Supabase" | DB connection OK | ✅ Good |
| "LLM service initialized" | OpenAI connected | ✅ Good |
| "Error searching documents" | Supabase issue | Check credentials/function |
| "Error generating answer" | OpenAI issue | Check API key/quota |

## 🎯 Quick Fixes

### Reset Everything

```bash
# 1. Stop the server (Ctrl+C)

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# 3. Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# 4. Restart
python app.py
```

### Test Minimal Setup

```python
# Create test.py
from dotenv import load_dotenv
import os

load_dotenv()

# Test 1: Environment variables
print("✓ .env loaded" if os.getenv('SUPABASE_URL') else "✗ .env missing")

# Test 2: Imports
try:
    import flask
    import sentence_transformers
    import supabase
    import openai
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")

# Test 3: Supabase connection
try:
    from supabase import create_client
    client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    print("✓ Supabase connected")
except Exception as e:
    print(f"✗ Supabase failed: {e}")

print("\nIf all tests pass, your setup is correct!")
```

Run it:
```bash
python test.py
```
