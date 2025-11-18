# Migration Guide: docker → docker-local-llm

How to switch from OpenAI API to Local LLM deployment.

---

## Why Migrate?

| Reason | Benefit |
|--------|---------|
| **Privacy** | Data never leaves your infrastructure |
| **Cost** | No per-request charges (free after setup) |
| **Compliance** | HIPAA/GDPR friendly |
| **Offline** | Works without internet |
| **Control** | Use any GGUF model |

---

## Prerequisites

Before migrating:
- ✅ 8GB+ RAM available (16GB recommended)
- ✅ 10-15GB free disk space
- ✅ CPU with AVX2 support
- ✅ Current docker branch working

---

## Migration Steps

### 1. Backup Current Setup
```bash
# Stop current services
./docker-stop.sh

# Backup .env and database
cp .env .env.openai.backup
tar -czf chroma_db_backup.tar.gz chroma_db/
```

### 2. Switch Branch
```bash
# Stash any local changes
git stash

# Switch to docker-local-llm
git checkout docker-local-llm

# Verify branch
git branch
# Should show: * docker-local-llm
```

### 3. Download Model
```bash
# Option A: Automatic (recommended)
./download-model.sh

# Option B: Manual
mkdir -p models
cd models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
cd ..
```

### 4. Update Configuration
```bash
# Copy your old config
cp .env.openai.backup .env

# Edit to use local LLM
nano .env
```

**Changes needed in .env:**

REMOVE these lines:
```bash
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini
# OPENAI_MAX_TOKENS=1024
# OPENAI_TEMPERATURE=0.9
```

ADD these lines:
```bash
# Local LLM Configuration
MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf
MODEL_CONTEXT_LENGTH=4096
MODEL_MAX_TOKENS=512
MODEL_TEMPERATURE=0.5
MODEL_TOP_P=0.9
MODEL_THREADS=4
MODEL_GPU_LAYERS=0
```

**Keep these (unchanged):**
```bash
# Database Configuration (same)
DB_HOST=your_host
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password

# Web Server (same)
WEB_SERVER_PORT=8080
FLASK_PORT=5000

# Vector Store (same)
USE_VECTOR_SEARCH=True
VECTOR_DB_PATH=./chroma_db
VECTOR_TOP_K=5

# Wiki URL (same)
WIKI_BASE_URL=http://your-wiki-url/index.php
```

### 5. Rebuild Docker Images
```bash
# Clean build (recommended for branch switch)
./docker-stop.sh
docker-compose down
./docker-build.sh

# This takes 10-15 minutes (first time)
```

### 6. Start Services
```bash
./docker-start.sh

# First startup is slow (2-5 minutes to load model)
# Watch logs:
./docker-logs.sh
```

### 7. Verify It Works
```bash
# Check status
./docker-status.sh

# Test in browser
# http://localhost:8080

# Or test with curl
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, are you working?"}'
```

---

## Troubleshooting Migration

### "Model file not found"
```bash
# Check model exists
ls -lh models/

# Verify path in .env
cat .env | grep MODEL_PATH

# Should show: MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf
```

### "Container fails to start"
```bash
# Check logs
./docker-logs.sh

# Common issues:
# 1. Not enough RAM (need 8GB+)
# 2. Model path wrong in .env
# 3. Old Docker cache - try: docker system prune
```

### "Out of memory during startup"
```bash
# Edit .env - reduce context
MODEL_CONTEXT_LENGTH=2048  # Was 4096

# Restart
./docker-restart.sh
```

### "Very slow responses (>30 seconds)"
```bash
# Increase CPU threads
MODEL_THREADS=8  # Or your CPU core count

# Reduce output length
MODEL_MAX_TOKENS=256

# Or enable GPU (if you have NVIDIA GPU)
MODEL_GPU_LAYERS=35
```

### "Responses are worse quality than OpenAI"
```bash
# This is expected - local 7B models are not as good as GPT-4
# But they're good enough for most wikis

# To improve quality:
# 1. Use larger model (13B instead of 7B)
# 2. Increase temperature for creativity
# 3. Use Q5 quantization instead of Q4
# 4. Ensure vector search is working (VECTOR_TOP_K=5)
```

---

## Performance Comparison

### Response Time
| Setup | Time |
|-------|------|
| docker (OpenAI) | 1-2 seconds |
| docker-local-llm (CPU) | 5-10 seconds |
| docker-local-llm (GPU) | 2-3 seconds |

### Quality
| Setup | Quality |
|-------|---------|
| docker (gpt-4o-mini) | Excellent ★★★★★ |
| docker-local-llm (Llama-2-7B) | Good ★★★★☆ |
| docker-local-llm (Llama-2-13B) | Better ★★★★½ |

### Cost
| Setup | Monthly Cost (1000 queries/day) |
|-------|--------------------------------|
| docker (OpenAI) | ~$4.50 |
| docker-local-llm | $0.00 |

**Break-even:** ~5000-10000 queries/month

---

## Rollback to OpenAI

If you need to go back:

```bash
# Stop services
./docker-stop.sh

# Switch back to docker branch
git checkout docker

# Restore old config
cp .env.openai.backup .env

# Rebuild
./docker-build.sh

# Start
./docker-start.sh
```

Your ChromaDB and data will be preserved.

---

## Side-by-Side Comparison

You can keep both branches and switch as needed:

```bash
# Use OpenAI for production
git checkout docker
./docker-start.sh

# Use Local LLM for development/testing
git checkout docker-local-llm
./docker-start.sh
```

Both can run on **different ports**:
- docker: Port 8080
- docker-local-llm: Port 8081 (change WEB_SERVER_PORT in .env)

---

## FAQ

### Q: Do I need to reindex ChromaDB?
**A:** No, vector database is compatible. Both branches use the same format.

### Q: Can I use both OpenAI and Local LLM?
**A:** Not simultaneously in same deployment. Choose one branch.

### Q: Which models are supported?
**A:** Any GGUF format model from HuggingFace (Llama-2, Mistral, etc.)
   Browse: https://huggingface.co/TheBloke

### Q: How much faster is GPU?
**A:** 2-5x faster. Example: 10s (CPU) → 2-3s (GPU)

### Q: Can I switch models without rebuilding?
**A:** Yes! Just change MODEL_PATH in .env and restart:
```bash
./docker-restart.sh
```

### Q: What if my wiki has sensitive data?
**A:** docker-local-llm is perfect - data never leaves your server.

---

## Next Steps

After successful migration:

1. **Tune performance** - Adjust MODEL_THREADS, MODEL_MAX_TOKENS
2. **Try different models** - Experiment with Mistral, Llama-2-13B
3. **Enable GPU** - If you have NVIDIA GPU
4. **Monitor usage** - Check response times and quality
5. **Read full docs** - See README_LOCAL_LLM.md

---

## Support

- **Full Documentation**: README_LOCAL_LLM.md
- **Quick Start**: QUICKSTART_LOCAL_LLM.md
- **Branch Comparison**: BRANCHES.md
- **Troubleshooting**: README_LOCAL_LLM.md (section 8)

---

**Happy migration! 🚀**
