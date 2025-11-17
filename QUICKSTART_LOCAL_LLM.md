# Quick Setup Guide - docker-local-llm Branch

## Step-by-Step Setup

### 1. Prerequisites
```bash
# Check Docker is installed
docker --version
docker-compose --version

# You need:
# - 8GB+ RAM
# - 10-15GB free disk space
```

### 2. Get the Code
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker-local-llm
```

### 3. Download Model (Choose One)

**Option A: Automatic (Recommended)**
```bash
./download-model.sh
# Downloads Llama-2-7B-Chat Q4_K_M (~4.1GB)
# Takes 5-15 minutes
```

**Option B: Manual**
```bash
mkdir -p models
cd models

# Download from HuggingFace
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

cd ..
```

**Option C: Use Different Model**
```bash
# Browse models at: https://huggingface.co/TheBloke
# Download any GGUF model to ./models/
# Update MODEL_PATH in .env
```

### 4. Configure
```bash
# Copy example config
cp .env.example .env

# Edit with your settings
nano .env
```

**Minimal .env configuration:**
```bash
# Database (REQUIRED)
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_db_user
DB_PASSWORD=your_password

# Model (REQUIRED)
MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf

# Optional tuning
MODEL_THREADS=4         # Set to your CPU cores
MODEL_GPU_LAYERS=0      # Set to 35 for GPU
```

### 5. Build and Start
```bash
# Build Docker image (10-15 minutes first time)
./docker-build.sh

# Start services (uses pre-built image, 2-5 minutes to load model)
./docker-start.sh

# Check status
./docker-status.sh
```

**Note**: docker-compose uses pre-built image for faster startups.

### 6. Access
```bash
# Open in browser
http://localhost:8080

# Or test with curl
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is YesAsia?"}'
```

---

## Common Issues

### "Model file not found"
```bash
# Check if model exists
ls -lh models/

# Verify path in .env matches
cat .env | grep MODEL_PATH

# Should be: MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf
```

### Container fails to start
```bash
# View logs
./docker-logs.sh

# Check memory
free -h

# Need 8GB+ RAM available
```

### Slow responses
```bash
# Edit .env
MODEL_THREADS=8              # More CPU threads
MODEL_CONTEXT_LENGTH=2048    # Smaller context
MODEL_MAX_TOKENS=256         # Shorter answers

# Restart
./docker-restart.sh
```

### Out of memory
```bash
# Edit .env
MODEL_CONTEXT_LENGTH=2048    # Reduce from 4096

# Restart
./docker-restart.sh
```

---

## Performance Tuning

### Fast Responses (CPU)
```bash
MODEL_THREADS=8              # Use more CPU cores
MODEL_MAX_TOKENS=256         # Shorter answers
MODEL_CONTEXT_LENGTH=2048    # Smaller context
```

### GPU Acceleration (NVIDIA only)
```bash
# 1. Install nvidia-docker
# 2. Edit .env
MODEL_GPU_LAYERS=35          # Full GPU for Llama-2-7B
# 3. Update docker-compose.yml (see README_LOCAL_LLM.md)
# 4. Rebuild
./docker-stop.sh
./docker-build.sh
./docker-start.sh
```

### Best Quality
```bash
MODEL_MAX_TOKENS=1024        # Longer answers
MODEL_TEMPERATURE=0.9        # More creative
MODEL_TOP_P=0.95
```

---

## File Structure
```
cs_wiki_chatbot/
├── models/                   # ← Put your .gguf models here
│   └── llama-2-7b-chat.Q4_K_M.gguf
├── .env                      # ← Your configuration
├── llm_model.py             # Local LLM wrapper
├── download-model.sh         # Helper script
└── README_LOCAL_LLM.md      # Full documentation
```

---

## Commands Reference

```bash
# Download model
./download-model.sh

# Build
./docker-build.sh

# Start/Stop/Restart
./docker-start.sh
./docker-stop.sh
./docker-restart.sh

# Monitor
./docker-status.sh
./docker-logs.sh

# Index wiki pages (first time)
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

---

## Need Help?

1. **Read full documentation**: [README_LOCAL_LLM.md](README_LOCAL_LLM.md)
2. **Check logs**: `./docker-logs.sh`
3. **Verify model**: `ls -lh models/`
4. **Test database**: Check DB_* settings in .env

---

## Comparison: OpenAI vs Local LLM

| Feature | OpenAI (docker) | Local (docker-local-llm) |
|---------|-----------------|--------------------------|
| Setup | Easy | Medium |
| Cost | Pay per use | Free after setup |
| Privacy | Cloud | 100% Local |
| Speed | Fast (1-2s) | Slower (5-10s) |
| Quality | Excellent | Good |
| Requirements | 2GB RAM | 8GB+ RAM |

**When to use Local LLM:**
- ✅ Privacy-sensitive data
- ✅ High volume usage (cost savings)
- ✅ Offline/air-gapped environments
- ✅ No internet access

**When to use OpenAI:**
- ✅ Quick setup needed
- ✅ Limited hardware
- ✅ Need best quality
- ✅ Low volume usage

---

**Branch**: docker-local-llm
**For full docs**: See README_LOCAL_LLM.md
