# 🚀 START HERE - Your RAG Service Guide

Welcome! This guide will help you get started with your IT Knowledge Retrieval Service.

## 📋 What You Have

A complete **RAG (Retrieval-Augmented Generation)** service that answers questions using your knowledge base.

```
User Question → Embedding → Vector Search → LLM → AI Answer
```

## 🎯 Quick Navigation

### For Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Get running in 5 minutes
2. **[SETUP.md](SETUP.md)** 📖 - Detailed setup instructions

### For Using the API
3. **[USAGE.md](USAGE.md)** 🔌 - API documentation and examples
4. **[test_api.py](test_api.py)** 🧪 - Test script to verify everything works

### For Understanding the System
5. **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ - How everything works together
6. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 📊 - Complete project overview

### For Troubleshooting
7. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 🔧 - Solutions to common issues

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - OPENAI_API_KEY
```

### Step 3: Run
```bash
python app.py
```

That's it! Your service is now running on `http://localhost:5000`

## 🧪 Test It

```bash
# In another terminal
python test_api.py
```

Or with curl:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

## 🔌 Connect to Your React App

```javascript
async function askQuestion(question) {
  const response = await fetch('http://localhost:5000/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  
  const data = await response.json();
  return data.answer;
}
```

## 📁 Project Structure

```
it-knowledge-retrieval-service/
│
├── 🚀 START HERE
│   ├── START_HERE.md          ← You are here!
│   ├── QUICKSTART.md          ← 5-minute setup
│   └── SETUP.md               ← Detailed setup
│
├── 📖 DOCUMENTATION
│   ├── README.md              ← Project overview
│   ├── USAGE.md               ← API documentation
│   ├── ARCHITECTURE.md        ← System design
│   ├── PROJECT_SUMMARY.md     ← Complete summary
│   └── TROUBLESHOOTING.md     ← Problem solving
│
├── 💻 APPLICATION CODE
│   ├── app.py                 ← Main Flask app (entry point)
│   ├── config.py              ← Configuration
│   └── services/              ← Business logic
│       ├── embedding_service.py
│       ├── vector_service.py
│       └── llm_service.py
│
├── 🧪 TESTING
│   └── test_api.py            ← API test script
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
└── ⚙️ CONFIGURATION
    ├── requirements.txt       ← Python dependencies
    ├── .env.example          ← Example config
    └── .gitignore            ← Git ignore rules
```

## 🎓 Understanding the Flow

### What Happens When You Ask a Question?

```
1. React App sends question
   ↓
2. Flask receives POST /api/query
   ↓
3. Embedding Service converts question to vector
   ↓
4. Vector Service searches Supabase for similar documents
   ↓
5. LLM Service sends documents + question to OpenAI
   ↓
6. OpenAI generates answer based on context
   ↓
7. Flask returns answer to React App
```

### Example

**Question:** "What is the remote work policy?"

**Step 1 - Embedding:**
```
"What is the remote work policy?"
→ [0.123, -0.456, 0.789, ..., 0.234]  (768 numbers)
```

**Step 2 - Search:**
```
Find documents similar to [0.123, -0.456, ...]
→ Found 5 relevant documents
```

**Step 3 - Context:**
```
[Document 1]
Remote work is allowed 3 days per week...

[Document 2]
Employees must notify their manager...
```

**Step 4 - LLM:**
```
System: You are a helpful assistant...
User: Context: [documents] Question: What is the remote work policy?
AI: According to the company policy, remote work is allowed...
```

**Step 5 - Response:**
```json
{
  "answer": "According to the company policy...",
  "sources": [...],
  "success": true
}
```

## 🔑 Key Files to Know

### Core Application
- **`app.py`** - Main Flask application, defines API endpoints
- **`config.py`** - Loads environment variables, validates config

### Services (Business Logic)
- **`services/embedding_service.py`** - Converts text to vectors using Qwen
- **`services/vector_service.py`** - Searches Supabase for similar documents
- **`services/llm_service.py`** - Generates answers using OpenAI

### Configuration
- **`.env`** - Your credentials (create this from `.env.example`)
- **`requirements.txt`** - Python packages needed

### Testing & Deployment
- **`test_api.py`** - Tests all endpoints
- **`Dockerfile`** - For Docker deployment
- **`docker-compose.yml`** - One-command deployment

## ⚙️ Configuration

### Required (Must Set)
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...
OPENAI_API_KEY=sk-...
```

### Optional (Has Defaults)
```env
EMBEDDING_MODEL=Qwen/Qwen2-0.5B-Instruct
LLM_MODEL=gpt-3.5-turbo
VECTOR_TABLE_NAME=documents
MATCH_THRESHOLD=0.7
MATCH_COUNT=5
PORT=5000
```

## 🎯 Common Tasks

### Change the LLM Model
Edit `.env`:
```env
LLM_MODEL=gpt-4  # or gpt-3.5-turbo
```

### Retrieve More Documents
Edit `.env`:
```env
MATCH_COUNT=10  # default is 5
```

### Adjust Similarity Threshold
Edit `.env`:
```env
MATCH_THRESHOLD=0.8  # higher = more strict (default 0.7)
```

### Change Supabase Function Name
Edit `services/vector_service.py` line 31:
```python
response = self.client.rpc(
    'your_function_name',  # Change this
    {...}
)
```

### Customize the AI Prompt
Edit `services/llm_service.py` line 28:
```python
system_prompt = """Your custom prompt here..."""
```

## 🐳 Docker Deployment

### Quick Deploy
```bash
docker-compose up -d
```

### Manual Docker
```bash
# Build
docker build -t rag-service .

# Run
docker run -p 5000:5000 --env-file .env rag-service
```

## 🔧 Troubleshooting

### "Missing required environment variables"
→ Create `.env` file from `.env.example` and add your credentials

### "Error searching documents"
→ Check Supabase credentials and function name

### First request is slow (30-60 seconds)
→ Normal! Model downloads on first run. Subsequent requests are fast.

### "CORS policy blocked"
→ Already handled! Make sure you're using `http://localhost:5000` (not https)

**For more issues:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📚 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run the service
3. Test with `test_api.py`
4. Integrate with React

### Intermediate
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Understand each service
3. Customize prompts
4. Adjust parameters

### Advanced
1. Add authentication
2. Implement caching
3. Add monitoring
4. Scale with multiple workers

## 🎉 Next Steps

### Immediate
- [ ] Set up `.env` file
- [ ] Run `python app.py`
- [ ] Test with `python test_api.py`
- [ ] Integrate with your React app

### Short Term
- [ ] Customize the AI prompt
- [ ] Adjust search parameters
- [ ] Add error handling in React
- [ ] Deploy with Docker

### Long Term
- [ ] Add authentication
- [ ] Implement caching
- [ ] Add conversation history
- [ ] Monitor usage and costs

## 💡 Tips

1. **Start simple** - Get it working first, optimize later
2. **Test often** - Use `test_api.py` after changes
3. **Check logs** - Console output shows detailed errors
4. **Read docs** - Each .md file has specific information
5. **Experiment** - Try different models, prompts, parameters

## 🤝 Need Help?

1. **Check logs** - Console shows detailed errors
2. **Run tests** - `python test_api.py`
3. **Read troubleshooting** - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **Review setup** - [SETUP.md](SETUP.md)

## 📖 Documentation Index

| File | Purpose | When to Read |
|------|---------|--------------|
| **START_HERE.md** | Overview and navigation | First time |
| **QUICKSTART.md** | Fast 5-minute setup | Getting started |
| **SETUP.md** | Detailed setup guide | First time setup |
| **USAGE.md** | API documentation | When integrating |
| **ARCHITECTURE.md** | System design | Understanding how it works |
| **PROJECT_SUMMARY.md** | Complete overview | Learning the project |
| **TROUBLESHOOTING.md** | Problem solving | When issues occur |
| **README.md** | Project overview | General reference |

## 🚀 Ready to Start?

### Option 1: Quick Start (5 minutes)
→ Go to [QUICKSTART.md](QUICKSTART.md)

### Option 2: Detailed Setup
→ Go to [SETUP.md](SETUP.md)

### Option 3: Understand First
→ Go to [ARCHITECTURE.md](ARCHITECTURE.md)

---

**You're all set!** Your RAG service is ready to power intelligent Q&A for your React application. 🎉

Happy coding! 🚀
