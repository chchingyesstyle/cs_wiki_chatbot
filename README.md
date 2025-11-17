# CS Wiki Chatbot - Local LLM (docker-local-llm branch)

**Self-hosted chatbot with local LLM - no external API required!**

This branch uses **llama-cpp-python** to run local LLM models (like Llama-2-7B-Chat) instead of OpenAI API.

---

## 🎯 Key Differences from `docker` Branch

| Feature | docker branch | docker-local-llm branch |
|---------|---------------|-------------------------|
| **LLM Backend** | OpenAI API (gpt-4o-mini) | Local GGUF models |
| **API Key Required** | ✅ Yes (OpenAI) | ❌ No |
| **Internet Required** | ✅ Yes (for API calls) | ❌ No (after setup) |
| **Cost per Request** | ~$0.00015/1K tokens | 🆓 Free |
| **Privacy** | Data sent to OpenAI | 🔒 100% Local |
| **Hardware Requirements** | Minimal (2GB RAM) | Higher (8GB+ RAM recommended) |
| **Model Size** | N/A | ~4-7GB per model |
| **Response Speed** | Fast (~1-2s) | Slower (~5-10s, depends on CPU) |

---

## 📋 Prerequisites

- Docker & Docker Compose installed
- **At least 8GB RAM** (16GB recommended)
- **10-15GB free disk space** (for model files)
- MediaWiki database access
- CPU with AVX2 support (most modern CPUs)

**Optional (for faster inference):**
- NVIDIA GPU with CUDA support
- 6GB+ VRAM for GPU acceleration

---

## 🚀 Quick Start

### 1. Download Model File

First, download a GGUF format model. Recommended models:

**Option A: Llama-2-7B-Chat (Recommended)**
```bash
# Create models directory
mkdir -p models

# Download from HuggingFace
cd models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
cd ..
```

**Option B: Other models**
- Browse: https://huggingface.co/TheBloke (search for GGUF models)
- Choose Q4_K_M or Q5_K_M quantization for good balance
- Download to `./models/` directory

### 2. Clone Repository

```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker-local-llm
```

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

**Required settings in `.env`:**

```bash
# Database Configuration
DB_HOST=your_database_host
DB_PORT=3306
DB_NAME=your_wiki_database
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Local LLM Configuration
MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf
MODEL_CONTEXT_LENGTH=4096
MODEL_MAX_TOKENS=512
MODEL_TEMPERATURE=0.7
MODEL_THREADS=4
MODEL_GPU_LAYERS=0  # Set to 35 for GPU acceleration

# Wiki URL
WIKI_BASE_URL=http://your-wiki-url/index.php
```

### 4. Build and Start

```bash
# Build Docker image (this may take 10-15 minutes first time)
./docker-build.sh

# Start services (uses pre-built image)
./docker-start.sh
```

**Note**: `docker-compose.yml` uses `image: cs-wiki-chatbot:latest` instead of `build: .` for faster startups. Always run `./docker-build.sh` first to create the image.

**First startup will be slow** (2-5 minutes) as the model loads into memory.

### 5. Access Chatbot

- **Web UI**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

---

## ⚙️ Configuration Guide

### Model Settings

```bash
# Model file location (inside container)
MODEL_PATH=/app/models/llama-2-7b-chat.Q4_K_M.gguf

# Context window size (tokens)
MODEL_CONTEXT_LENGTH=4096  # Llama-2 supports up to 4096

# Maximum response length (tokens)
MODEL_MAX_TOKENS=512       # Lower = faster, higher = longer answers

# Creativity (0.0 = deterministic, 1.0 = very creative)
MODEL_TEMPERATURE=0.7      # 0.7 is good for Q&A

# Nucleus sampling (keep between 0.9-1.0)
MODEL_TOP_P=0.9

# CPU threads to use
MODEL_THREADS=4            # Set to your CPU core count

# GPU layers (NVIDIA GPU only)
MODEL_GPU_LAYERS=0         # 0 = CPU only, 35 = full GPU (Llama-2-7B)
```

### Performance Tuning

**For faster responses:**
```bash
MODEL_MAX_TOKENS=256       # Shorter answers
MODEL_THREADS=8            # More CPU threads
MODEL_GPU_LAYERS=35        # Use GPU if available
```

**For better quality:**
```bash
MODEL_MAX_TOKENS=1024      # Longer answers
MODEL_TEMPERATURE=0.9      # More creative
MODEL_CONTEXT_LENGTH=4096  # Larger context
```

**For lower RAM usage:**
```bash
MODEL_CONTEXT_LENGTH=2048  # Smaller context
MODEL_MAX_TOKENS=256       # Shorter responses
```

---

## 🎮 GPU Acceleration (Optional)

### NVIDIA GPU Setup

1. **Install NVIDIA Docker runtime:**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Update docker-compose.yml:**
   ```yaml
   chatbot-api:
     deploy:
       resources:
         reservations:
           devices:
             - driver: nvidia
               count: 1
               capabilities: [gpu]
   ```

3. **Update .env:**
   ```bash
   MODEL_GPU_LAYERS=35  # Llama-2-7B fits fully on 6GB+ VRAM
   ```

4. **Rebuild and restart:**
   ```bash
   ./docker-stop.sh
   ./docker-build.sh
   ./docker-start.sh
   ```

---

## 📊 Recommended Models

| Model | Size | RAM Required | Quality | Speed | Best For |
|-------|------|--------------|---------|-------|----------|
| **Llama-2-7B-Chat-Q4_K_M** | 4.1GB | 8GB | Good | Medium | **Recommended** |
| Llama-2-7B-Chat-Q5_K_M | 4.8GB | 10GB | Better | Slower | Higher quality |
| Llama-2-13B-Chat-Q4_K_M | 7.4GB | 16GB | Best | Slow | Max quality |
| Mistral-7B-Instruct-Q4_K_M | 4.1GB | 8GB | Good | Fast | Alternative |

**Download from**: https://huggingface.co/TheBloke

---

## 🔧 Troubleshooting

### Container Fails to Start

```bash
# Check logs
./docker-logs.sh

# Common issues:
# - Model file not found: Check MODEL_PATH in .env
# - Out of memory: Reduce MODEL_CONTEXT_LENGTH
# - Model corrupted: Re-download model file
```

### Model Not Found Error

```bash
# Verify model file exists
ls -lh models/

# Check model path in .env
cat .env | grep MODEL_PATH

# Model path should be: /app/models/your-model.gguf
```

### Slow Responses (> 30 seconds)

```bash
# Increase CPU threads
MODEL_THREADS=8

# Reduce context length
MODEL_CONTEXT_LENGTH=2048

# Use smaller/faster model
# Or enable GPU acceleration
```

### Out of Memory

```bash
# Use smaller context window
MODEL_CONTEXT_LENGTH=2048

# Use Q4 quantization instead of Q5
# Close other applications
# Add more RAM or swap
```

---

## 📚 Directory Structure

```
cs_wiki_chatbot/
├── models/                          # Model files (must download)
│   └── llama-2-7b-chat.Q4_K_M.gguf # Local LLM model
├── chroma_db/                       # Vector database
├── llm_model.py                     # Local LLM wrapper (NEW)
├── chatbot.py                       # Uses LLMModel instead of OpenAI
├── config.py                        # Local LLM configs (UPDATED)
├── requirements.txt                 # Added llama-cpp-python
├── Dockerfile                       # Added model directory
├── docker-compose.yml               # Uses pre-built image
└── .env.example                     # Local LLM config template
```

---

## 🔒 Privacy & Security

✅ **100% Local** - No data sent to external APIs
✅ **Offline capable** - Works without internet (after setup)
✅ **HIPAA/GDPR friendly** - Data stays on your infrastructure
✅ **No API costs** - Free unlimited usage
✅ **Open source** - Transparent and auditable

---

## 💰 Cost Comparison

| Scenario | OpenAI (docker) | Local LLM (docker-local-llm) |
|----------|-----------------|------------------------------|
| **Setup** | Free | Free |
| **Infrastructure** | $20-50/month (small server) | $50-100/month (larger server) |
| **Per Request** | ~$0.00015 | $0.00 |
| **1000 questions/day** | ~$4.50/month | $0.00 |
| **10000 questions/day** | ~$45/month | $0.00 |

**Break-even:** ~5000-10000 questions/month

---

## 🆘 Support

- **Full Docker Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Quick Reference**: [DOCKER_QUICKREF.md](DOCKER_QUICKREF.md)
- **Branch Comparison**: [BRANCHES.md](BRANCHES.md)
- **Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
- **This Branch**: https://github.com/chchingyesstyle/cs_wiki_chatbot/tree/docker-local-llm

---

## 🔄 Switching to/from Other Branches

### To OpenAI version (docker branch):
```bash
git checkout docker
cp .env.example .env
# Add OPENAI_API_KEY to .env
./docker-build.sh
./docker-start.sh
```

### From OpenAI to Local LLM (this branch):
```bash
git checkout docker-local-llm
# Download model to ./models/
cp .env.example .env
# Configure MODEL_PATH in .env
./docker-build.sh
./docker-start.sh
```

---

**Branch**: docker-local-llm
**Status**: ✅ Ready for testing
**Last Updated**: 2025-01-17
