# 🐳 Docker Branch - Deployment Summary

## ✅ What Was Created

### Core Docker Files
1. **Dockerfile** - Container image definition
   - Python 3.9 slim base
   - System dependencies (MySQL client)
   - Python packages from requirements.txt
   - Exposes ports 5000 (API) and 8080 (Web)
   - Health check endpoint

2. **docker-compose.yml** - Multi-container orchestration
   - `chatbot-api` - Flask API service
   - `chatbot-web` - Web UI service
   - Shared network for inter-container communication
   - Volume mounts for data persistence
   - Environment configuration via .env

3. **.dockerignore** - Build optimization
   - Excludes unnecessary files from image
   - Reduces image size

### Management Scripts
1. **docker-build.sh** - Build Docker images
2. **docker-start.sh** - Start all services
3. **docker-stop.sh** - Stop all services
4. **docker-restart.sh** - Restart services
5. **docker-status.sh** - Check service status
6. **docker-logs.sh** - View service logs

### Documentation
1. **DOCKER_DEPLOYMENT.md** - Complete deployment guide (8.5KB)
   - Installation instructions
   - Configuration guide
   - Troubleshooting
   - Production deployment tips
   - Cloud deployment examples

2. **DOCKER_QUICKREF.md** - Quick reference (5KB)
   - Common commands
   - Quick troubleshooting
   - Configuration snippets

3. **BRANCHES.md** - Branch comparison guide
   - Comparison of main/openai/docker branches
   - Use case recommendations
   - Quick start for each branch

4. **README.md** - Updated with Docker-first approach
   - Docker usage highlighted
   - Collapsible manual installation sections

---

## 🎯 Key Features

### 1. One-Command Deployment
```bash
./docker-build.sh    # Build once
./docker-start.sh    # Start anytime
```

### 2. Multi-Container Architecture
- **API Container** (chatbot-api)
  - Flask REST API
  - Database connections
  - OpenAI API integration
  - Health checks
  
- **Web Container** (chatbot-web)
  - Static file server
  - HTML/JS interface
  - Auto-configured API endpoint

### 3. Health Monitoring
- API health check every 30 seconds
- Automatic restart on failure
- Web service depends on API health

### 4. Data Persistence
- `chroma_db/` - Vector database (mounted volume)
- `app.log` - Application logs (mounted file)
- Survives container restarts

### 5. Environment Configuration
All settings via `.env` file:
- Database credentials
- OpenAI API key
- Port configuration
- Feature flags

---

## 🚀 Quick Start

```bash
# 1. Get the code
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker

# 2. Configure
cp .env.example .env
nano .env  # Set DB credentials and OpenAI API key

# 3. Deploy
./docker-build.sh
./docker-start.sh

# 4. Access
# Web UI: http://localhost:8080
# API: http://localhost:5000
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                  Docker Host                    │
│                                                 │
│  ┌──────────────────┐      ┌─────────────────┐ │
│  │  Web Container   │      │  API Container  │ │
│  │  Port 8080      │─────▶│  Port 5000     │ │
│  │  serve_web.py   │      │  app.py        │ │
│  └──────────────────┘      └─────────────────┘ │
│           │                        │            │
│           │                        │            │
│           ▼                        ▼            │
│  ┌─────────────────────────────────────────┐   │
│  │       chatbot-network (bridge)          │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Volumes:                                       │
│  ├─ chroma_db/     (ChromaDB data)            │
│  └─ app.log        (Application logs)          │
└─────────────────────────────────────────────────┘
                    │            │
                    │            │
                    ▼            ▼
          ┌──────────────┐  ┌──────────────┐
          │  MediaWiki   │  │  OpenAI API  │
          │  Database    │  │              │
          └──────────────┘  └──────────────┘
```

---

## 💻 Management Commands

| Task | Command | Description |
|------|---------|-------------|
| Build | `./docker-build.sh` | Build Docker images |
| Start | `./docker-start.sh` | Start all services |
| Stop | `./docker-stop.sh` | Stop all services |
| Restart | `./docker-restart.sh` | Restart services |
| Status | `./docker-status.sh` | Check service status |
| Logs | `./docker-logs.sh` | View all logs |
| API Logs | `./docker-logs.sh chatbot-api` | View API logs only |
| Web Logs | `./docker-logs.sh chatbot-web` | View web logs only |

---

## 🔧 Configuration (.env)

```bash
# Database (Required)
DB_HOST=your-database-host.amazonaws.com
DB_PORT=3306
DB_NAME=cs_wiki_poc
DB_USER=cs_wiki
DB_PASSWORD=your_password

# OpenAI (Required)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Ports (Optional - defaults shown)
FLASK_PORT=5000
WEB_SERVER_PORT=8080

# Vector Search (Optional)
USE_VECTOR_SEARCH=True
VECTOR_DB_PATH=/app/chroma_db
VECTOR_TOP_K=3

# Wiki URL (Required)
WIKI_BASE_URL=http://your-wiki-url/index.php
```

---

## 📈 Benefits Over Manual Deployment

| Feature | Manual | Docker |
|---------|--------|--------|
| Environment setup | ⏱️ 30+ min | ⏱️ 5 min |
| Dependency conflicts | ❌ Possible | ✅ Isolated |
| Port management | Manual | Automated |
| Service restart | Manual scripts | Auto-restart |
| Health monitoring | Manual | Built-in |
| Logs | Scattered | Centralized |
| Portability | ❌ OS-dependent | ✅ Works anywhere |
| Scaling | ❌ Complex | ✅ Simple |
| Updates | ❌ Manual | ✅ Rebuild & restart |

---

## 🌐 Deployment Scenarios

### Local Development
```bash
./docker-start.sh
# Access at http://localhost:8080
```

### Production Server
```bash
# With Nginx reverse proxy
./docker-start.sh
# Configure Nginx to proxy to ports 5000/8080
```

### Cloud (AWS/GCP/Azure)
```bash
# Install Docker on cloud instance
# Clone repo
# Configure .env
./docker-build.sh && ./docker-start.sh
```

### Kubernetes (Advanced)
```bash
# Convert docker-compose to k8s manifests
kompose convert
kubectl apply -f .
```

---

## 🐛 Troubleshooting Quick Tips

### Container won't start
```bash
./docker-logs.sh  # Check logs
docker ps -a      # Check container status
```

### Database connection failed
```bash
# Test from container
docker exec -it cs-wiki-chatbot-api python -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
print('OK' if db.connect() else 'FAILED')
"
```

### Port already in use
```bash
# Change ports in .env
nano .env
# Update FLASK_PORT and WEB_SERVER_PORT
./docker-restart.sh
```

### Clear all data
```bash
./docker-stop.sh
docker-compose down -v
rm -rf chroma_db/*
./docker-build.sh && ./docker-start.sh
```

---

## 📚 Documentation Files

1. **DOCKER_DEPLOYMENT.md** - Comprehensive deployment guide
   - Prerequisites
   - Installation steps
   - Configuration details
   - Production deployment
   - Cloud deployment examples
   - Monitoring and maintenance

2. **DOCKER_QUICKREF.md** - Quick reference
   - Common commands
   - Configuration snippets
   - Troubleshooting tips
   - Quick answers

3. **BRANCHES.md** - Branch comparison
   - main vs openai vs docker
   - When to use each
   - Quick start for each

4. **README.md** - Main documentation
   - Feature overview
   - Docker-first approach
   - Architecture details

---

## 🎉 Success Metrics

After successful deployment:

✅ Both containers running  
✅ API health check passing  
✅ Web UI accessible at port 8080  
✅ API accessible at port 5000  
✅ ChromaDB data persisted  
✅ Logs available via docker-logs.sh  
✅ Auto-restart on failure working  

---

## 📞 Support & Resources

- **Full Guide**: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)
- **Quick Ref**: [DOCKER_QUICKREF.md](./DOCKER_QUICKREF.md)
- **Branch Guide**: [BRANCHES.md](./BRANCHES.md)
- **Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
- **Docker Branch**: https://github.com/chchingyesstyle/cs_wiki_chatbot/tree/docker

---

## ✨ Next Steps

1. **Deploy and Test**
   ```bash
   ./docker-start.sh
   # Open http://localhost:8080
   ```

2. **Index Wiki Pages** (Optional)
   ```bash
   docker exec -it cs-wiki-chatbot-api python index_wiki.py
   ```

3. **Monitor Logs**
   ```bash
   ./docker-logs.sh
   ```

4. **Production Deployment**
   - Set up Nginx reverse proxy
   - Enable HTTPS
   - Configure monitoring
   - Set up backup scripts

---

**Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot  
**Branch**: docker  
**Created**: 2024-01-17  
**Status**: ✅ Production Ready
