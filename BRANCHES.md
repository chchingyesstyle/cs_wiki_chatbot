# CS Wiki Chatbot - Branch Guide

This repository has multiple branches for different deployment scenarios. Choose the one that fits your needs.

## 📊 Branch Overview

| Branch | Description | Best For | Requirements |
|--------|-------------|----------|--------------|
| **main** | Local Llama model | Privacy-focused, offline | 4GB+ RAM, Model file |
| **openai** | OpenAI API integration | Quick setup, better quality | OpenAI API key |
| **docker** | Dockerized OpenAI version | Production deployment | Docker, API key |

---

## 🌿 Branch: `main`

**Local Llama Model Deployment**

### Features
- ✅ Runs locally with llama-cpp-python
- ✅ Privacy-focused (no external API)
- ✅ Works offline
- ✅ No per-request costs

### Requirements
- Python 3.9+
- 4GB+ RAM
- Download GGUF model file (2-7GB)
- MediaWiki database access

### Setup
```bash
git checkout main
pip install -r requirements.txt
# Download model file
cp .env.example .env
nano .env  # Configure MODEL_PATH
./start.sh
```

### Best For
- On-premise deployments
- Privacy-sensitive environments
- Offline operations
- Cost-conscious setups

### Documentation
- [README.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/main/README.md)

---

## 🌿 Branch: `openai`

**OpenAI API Integration**

### Features
- ✅ No model downloads needed
- ✅ Better language understanding (GPT-3.5/4)
- ✅ Faster responses
- ✅ Lower system requirements
- ✅ Scalable

### Requirements
- Python 3.9+
- OpenAI API key
- MediaWiki database access
- Internet connection

### Setup
```bash
git checkout openai
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add OPENAI_API_KEY
./start.sh
```

### Costs
- GPT-4o-mini: ~$0.00015/1K tokens (best value, recommended)
- GPT-3.5-turbo: ~$0.0005/1K tokens (legacy)
- GPT-4: ~$0.03/1K tokens (premium)

### Best For
- Quick prototypes
- Better response quality
- Limited hardware
- Variable workloads

### Documentation
- [README.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/openai/README.md)
- [DEPLOYMENT.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/openai/DEPLOYMENT.md)

---

## 🌿 Branch: `docker` ⭐ **RECOMMENDED**

**Dockerized OpenAI Deployment**

### Features
- ✅ One-command deployment
- ✅ Single-port deployment (8080 only, reverse proxy)
- ✅ Multi-container architecture
- ✅ Health checks & auto-restart
- ✅ Data persistence
- ✅ Production-ready
- ✅ Portable across environments
- ✅ Easy scaling
- ✅ More secure (API not directly exposed)

### Requirements
- Docker 20.10+
- Docker Compose 1.29+
- OpenAI API key
- MediaWiki database access

### Setup
```bash
git checkout docker
cp .env.example .env
nano .env  # Configure
./docker-build.sh
./docker-start.sh
```

### Architecture
```
External Access (Port 8080 only)
         ↓
┌─────────────────┐     ┌─────────────────┐
│   Web UI +      │────▶│   API Server    │
│   Reverse Proxy │     │   Port 5000     │
│   Port 8080     │     │   (INTERNAL)    │
│   (EXPOSED)     │     │   (Container)   │
└─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  MediaWiki DB   │
                        │  + OpenAI API   │
                        └─────────────────┘
Note: Single-port deployment for security
```

### Management
```bash
./docker-start.sh      # Start
./docker-stop.sh       # Stop
./docker-status.sh     # Status
./docker-logs.sh       # Logs
./docker-restart.sh    # Restart
```

### Best For
- **Production deployments** ⭐
- Multi-environment setups
- Cloud deployments (AWS, GCP, Azure)
- Team collaboration
- Easy maintenance

### Documentation
- [DOCKER_DEPLOYMENT.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/docker/DOCKER_DEPLOYMENT.md) - Complete guide
- [DOCKER_QUICKREF.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/docker/DOCKER_QUICKREF.md) - Quick reference
- [README.md](https://github.com/chchingyesstyle/cs_wiki_chatbot/blob/docker/README.md)

---

## 🤔 Which Branch Should I Use?

### Use **`main`** if:
- ❌ No internet access required
- ❌ Privacy concerns (no external APIs)
- ❌ Want to avoid per-request costs
- ✅ Have sufficient hardware (4GB+ RAM)
- ✅ Can download/store large models

### Use **`openai`** if:
- ✅ Want quick setup
- ✅ Need better response quality
- ✅ Have limited hardware
- ✅ Don't want to manage models
- ❌ Okay with per-request API costs
- ❌ Have internet access

### Use **`docker`** if: ⭐
- ✅ Want production-ready deployment
- ✅ Need easy environment setup
- ✅ Want container isolation
- ✅ Need to deploy to cloud
- ✅ Want simple management
- ✅ Need scalability
- **👉 RECOMMENDED for most users**

---

## 🔄 Switching Between Branches

### Check Current Branch
```bash
git branch
```

### Switch to Another Branch
```bash
# Switch to main
git checkout main

# Switch to openai
git checkout openai

# Switch to docker
git checkout docker
```

### Compare Branches
```bash
# See differences between branches
git diff main..openai
git diff openai..docker
```

---

## 📦 Installation Comparison

| Step | main | openai | docker |
|------|------|--------|--------|
| Clone repo | ✅ | ✅ | ✅ |
| Install Docker | ❌ | ❌ | ✅ |
| Install Python deps | ✅ | ✅ | ❌ (in container) |
| Download model | ✅ (2-7GB) | ❌ | ❌ |
| Configure .env | ✅ | ✅ | ✅ |
| Get API key | ❌ | ✅ | ✅ |
| Build images | ❌ | ❌ | ✅ |
| Start services | `./start.sh` | `./start.sh` | `./docker-start.sh` |

---

## 🚀 Quick Start Commands

### Main Branch
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout main
pip install -r requirements.txt
# Download model
cp .env.example .env
nano .env
./start.sh
```

### OpenAI Branch
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout openai
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add OPENAI_API_KEY
./start.sh
```

### Docker Branch ⭐
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker
cp .env.example .env
nano .env  # Configure
./docker-build.sh
./docker-start.sh
```

---

## 📚 Additional Resources

- **Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
- **Issues**: https://github.com/chchingyesstyle/cs_wiki_chatbot/issues
- **OpenAI API**: https://platform.openai.com/
- **Docker Docs**: https://docs.docker.com/

---

## 💡 Recommendations

1. **For Development/Testing**: Use `openai` branch
2. **For Production**: Use `docker` branch ⭐
3. **For Privacy/Offline**: Use `main` branch

---

## 🆘 Support

For issues or questions:
1. Check branch-specific README.md
2. Review documentation files
3. Check GitHub Issues
4. Create new issue with branch name in title

---

**Last Updated**: 2024-01-17  
**Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
