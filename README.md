# CS Wiki Chatbot

**An intelligent chatbot that answers questions about your MediaWiki content using OpenAI and semantic search.**

Transform your wiki into an interactive Q&A system. Ask questions in natural language, get accurate answers with source citations.

---

## 🎯 What Does It Do?

```
User asks: "What is YesAsia?"
         ↓
    [Chatbot]
         ↓
1. Searches your wiki for relevant pages (semantic search)
2. Sends context to OpenAI (gpt-4o-mini)
3. Returns answer with source links
         ↓
Answer: "YesAsia is an online retailer specializing in Asian
entertainment products..."

Sources:
📄 YesAsia Overview (http://wiki/YesAsia)
📄 Online Retailers Guide (http://wiki/Retailers)
```

**Key Benefits:**
- 🎯 **Accurate**: Only answers from your wiki content (no hallucinations)
- 🔗 **Transparent**: Shows source pages for every answer
- 🚀 **Fast**: Semantic search finds relevant info instantly
- 🔒 **Secure**: Single-port deployment, API not exposed
- 🐳 **Easy**: One-command Docker deployment

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key ([get one here](https://platform.openai.com/))
- MediaWiki database access

### Deploy in 4 Steps

```bash
# 1. Clone repository
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker

# 2. Configure
cp .env.example .env
nano .env  # Add DB credentials and OpenAI API key

# 3. Build and start
./docker-build.sh
./docker-start.sh

# 4. Open browser
# http://localhost:8080
```

**That's it! Your chatbot is ready.** 🎉

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────┐
│                    User Browser                     │
│              http://localhost:8080                  │
└────────────────────┬────────────────────────────────┘
                     │ Port 8080 (only exposed port)
                     ↓
┌────────────────────────────────────────────────────┐
│              Docker Container 1                    │
│            Web Server + Reverse Proxy              │
│  ┌──────────────────────────────────────────────┐ │
│  │ Serves: HTML/CSS/JS                          │ │
│  │ Proxies: /api/* → Internal API Container    │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────┘
                     │ Internal Docker Network
                     ↓
┌────────────────────────────────────────────────────┐
│              Docker Container 2                    │
│                  Flask API                         │
│  ┌──────────────────────────────────────────────┐ │
│  │ 1. Receives question                         │ │
│  │ 2. Searches ChromaDB (vector search)         │ │
│  │ 3. Retrieves wiki pages from MediaWiki DB    │ │
│  │ 4. Sends context to OpenAI API               │ │
│  │ 5. Returns answer + sources                  │ │
│  └──────────────────────────────────────────────┘ │
└───┬────────────────────────────────────────┬───────┘
    │                                        │
    ↓                                        ↓
┌─────────────┐                      ┌──────────────┐
│  MediaWiki  │                      │  OpenAI API  │
│  Database   │                      │ (gpt-4o-mini)│
│  (MariaDB)  │                      └──────────────┘
└─────────────┘
    ↓
┌─────────────┐
│  ChromaDB   │
│ (vectors)   │
└─────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | HTML/CSS/JavaScript | User interface |
| **Web Server** | Python HTTP + Proxy | Serves UI, proxies API requests |
| **API** | Flask (Python) | REST API, orchestrates workflow |
| **Vector DB** | ChromaDB | Semantic search with embeddings |
| **LLM** | OpenAI gpt-4o-mini | Natural language generation |
| **Database** | MariaDB | MediaWiki 1.43 database |
| **Embeddings** | sentence-transformers | Convert text to vectors |
| **Container** | Docker + Compose | Deployment & orchestration |

### RAG (Retrieval-Augmented Generation) Pipeline

1. **🔍 Retrieval**
   - User asks a question
   - Vector search finds semantically similar wiki pages
   - Returns top 5 most relevant pages

2. **📝 Augmentation**
   - Combines retrieved pages with user question
   - Creates context-rich prompt for OpenAI
   - Includes source references

3. **🤖 Generation**
   - OpenAI generates answer from context only
   - Formats response with source links
   - Returns "I don't know" if context insufficient

**Why RAG?**
- ✅ Prevents hallucinations (only uses your wiki content)
- ✅ Always cites sources
- ✅ Works with your specific domain knowledge
- ✅ No need to fine-tune models

---

## ✨ Features

### Core Features
- ✅ **Natural Language Q&A** - Ask questions in plain English
- ✅ **Semantic Search** - Finds relevant pages even without exact keyword matches
- ✅ **Source Attribution** - Shows which wiki pages were used
- ✅ **Clickable Links** - Direct links to source wiki pages
- ✅ **Smart Filtering** - Automatically skips redirects and outdated pages
- ✅ **Context-Aware** - Understands your domain through wiki content

### Technical Features
- ✅ **Single-Port Deployment** - Only port 8080 exposed (more secure)
- ✅ **Health Checks** - Automatic monitoring and restart
- ✅ **Data Persistence** - Vector DB and logs survive restarts
- ✅ **RESTful API** - Easy integration with other systems
- ✅ **Docker-Based** - Portable, consistent deployment
- ✅ **Environment Config** - All settings via `.env` file

### Quality Features
- ✅ **High-Quality Model** - Uses gpt-4o-mini (better than gpt-3.5, 70% cheaper)
- ✅ **Improved Retrieval** - Retrieves 5 pages for better coverage
- ✅ **Clean Indexing** - Only indexes pages with real content
- ✅ **Creative Responses** - Tuned for natural, conversational answers

---

## 📖 Usage

### Web Interface (Recommended)

1. **Start the chatbot**
   ```bash
   ./docker-start.sh
   ```

2. **Open browser**
   ```
   http://localhost:8080
   ```

3. **Ask questions**
   - Type your question in the chat box
   - Get answers with source links
   - Click sources to view original wiki pages

### API Interface

**POST** `/api/chat`

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is YesAsia?"}'
```

**Response:**
```json
{
  "question": "What is YesAsia?",
  "answer": "YesAsia is an online retailer specializing in...",
  "sources": [
    {
      "title": "YesAsia Overview",
      "url": "http://wiki/index.php?title=YesAsia"
    }
  ],
  "context_used": true
}
```

### Management Commands

| Command | Purpose |
|---------|---------|
| `./docker-start.sh` | Start all services |
| `./docker-stop.sh` | Stop all services |
| `./docker-restart.sh` | Restart services |
| `./docker-status.sh` | Check status |
| `./docker-logs.sh` | View logs |
| `./docker-build.sh` | Build Docker image (only needed after code changes) |

**Note:** Starting/stopping containers doesn't require rebuilding. The `docker-build.sh` script creates a single image `cs-wiki-chatbot:latest` that both containers use.

---

## ⚙️ Configuration

### Required Settings (`.env`)

```bash
# Database Configuration
DB_HOST=your-database-host.com
DB_PORT=3306
DB_NAME=your_wiki_database
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Wiki URL
WIKI_BASE_URL=http://your-wiki-url/index.php
```

### Optional Settings

```bash
# Port Configuration
WEB_SERVER_PORT=8080          # External port (only this is exposed)
FLASK_PORT=5000               # Internal API port (not exposed)

# OpenAI Model Tuning
OPENAI_MAX_TOKENS=1024        # Response length (default: 1024)
OPENAI_TEMPERATURE=0.5        # Creativity (0.0-1.0, default: 0.5)

# Vector Search
USE_VECTOR_SEARCH=True        # Enable semantic search
VECTOR_DB_PATH=/app/chroma_db # Storage location
VECTOR_TOP_K=5                # Number of pages to retrieve
```

### Model Recommendations

| Model | Cost (per 1M tokens) | Quality | Speed | Best For |
|-------|---------------------|---------|-------|----------|
| **gpt-4o-mini** ⭐ | $0.15 / $0.60 | Excellent | Fast | **Recommended** - Best value |
| gpt-3.5-turbo | $0.50 / $1.50 | Good | Very Fast | Budget option (legacy) |
| gpt-4 | $30.00 / $60.00 | Best | Slower | Premium quality needed |

> **Recommendation:** Use `gpt-4o-mini` - it's better quality than gpt-3.5-turbo and 70% cheaper.

---

## 🔄 Reindexing Vector Database

### When to Reindex

Run reindexing when:
- First-time setup
- Wiki content significantly updated
- Pages added/deleted
- Vector search returning poor results

### How to Reindex

```bash
# Docker deployment
docker exec -it cs-wiki-chatbot-api python index_wiki.py

# This will:
# - Connect to your MediaWiki database
# - Skip redirect and outdated pages
# - Create vector embeddings for each page
# - Store in ChromaDB for semantic search
```

**Indexing time:** ~2-5 minutes for 100-500 pages

See [REINDEX_GUIDE.md](REINDEX_GUIDE.md) for detailed instructions.

---

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check logs
./docker-logs.sh

# Check what's using port 8080
sudo lsof -i :8080

# Rebuild from scratch
./docker-stop.sh
docker-compose down -v
./docker-build.sh
./docker-start.sh
```

### Database Connection Failed

```bash
# Test database connection
docker exec -it cs-wiki-chatbot-api python -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
print('✅ OK' if db.connect() else '❌ FAILED')
"

# Check credentials
cat .env | grep DB_
```

### OpenAI API Error

```bash
# Test OpenAI connection
docker exec -it cs-wiki-chatbot-api python -c "
from openai_model import OpenAIModel
m = OpenAIModel()
m.load_model()
print(m.generate_response('test'))
"

# Check API key
cat .env | grep OPENAI_API_KEY

# Check quota at: https://platform.openai.com/usage
```

### Chatbot Says "I don't know" for Valid Questions

1. **Reindex vector database** (most common fix)
   ```bash
   docker exec -it cs-wiki-chatbot-api python index_wiki.py
   ```

2. **Check if pages were indexed**
   ```bash
   docker exec -it cs-wiki-chatbot-api python -c "
   from vector_store import VectorStore
   vs = VectorStore()
   vs.initialize()
   print(f'Documents indexed: {vs.collection.count()}')
   "
   ```

3. **Increase retrieval count** (in `.env`)
   ```bash
   VECTOR_TOP_K=10  # Try retrieving more pages
   ```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** | Complete deployment guide with all details |
| **[DOCKER_QUICKREF.md](DOCKER_QUICKREF.md)** | Quick reference for common commands |
| **[BRANCHES.md](BRANCHES.md)** | Comparison of main/openai/docker branches |
| **[REINDEX_GUIDE.md](REINDEX_GUIDE.md)** | How to reindex vector database |
| **[DOCKER_SUMMARY.md](DOCKER_SUMMARY.md)** | Docker architecture summary |

---

## 🎨 Project Structure

```
cs_wiki_chatbot/
├── app.py                  # Flask API server
├── chatbot.py              # Main chatbot logic (RAG pipeline)
├── config.py               # Configuration loader
├── db_connector.py         # MediaWiki database connector
├── openai_model.py         # OpenAI API wrapper
├── vector_store.py         # ChromaDB vector search
├── index_wiki.py           # Vector database indexing script
├── serve_web.py            # Web server + reverse proxy
├── index.html              # Web UI
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-container orchestration
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
├── docker-build.sh         # Build Docker images
├── docker-start.sh         # Start services
├── docker-stop.sh          # Stop services
├── docker-restart.sh       # Restart services
├── docker-status.sh        # Check status
├── docker-logs.sh          # View logs
└── README.md               # This file
```

---

## 🔐 Security

### Single-Port Architecture

This deployment uses a **reverse proxy pattern** for enhanced security:

- ✅ **Only port 8080 exposed** to the internet
- ✅ **API port 5000 not accessible** externally (internal Docker network only)
- ✅ **All requests** go through the web container first
- ✅ **Firewall management** simplified (one port to manage)

### Best Practices

1. **Never commit `.env`** - Contains sensitive credentials
2. **Use strong passwords** - For database access
3. **Rotate API keys** - Regularly update OpenAI API key
4. **Enable HTTPS** - Use Nginx reverse proxy with SSL in production
5. **Monitor usage** - Check OpenAI API usage regularly
6. **Keep updated** - Rebuild containers after updates

---

## 💡 Performance Tips

### Cost Optimization

- Use `gpt-4o-mini` instead of `gpt-4` (70% cheaper, similar quality)
- Cache frequent queries (future feature)
- Monitor usage at https://platform.openai.com/usage
- Set `OPENAI_MAX_TOKENS` appropriately (lower = cheaper)

### Quality Optimization

- Reindex regularly when wiki content changes
- Use `VECTOR_TOP_K=5` or higher for better retrieval
- Set `OPENAI_TEMPERATURE=0.5` for consistent, accurate responses
- Keep wiki content well-organized and up-to-date
- Remove outdated/redirect pages from wiki

### Speed Optimization

- Use `gpt-4o-mini` (faster than gpt-4)
- Keep vector database on SSD
- Ensure database connection is fast
- Use appropriate hardware (2GB+ RAM recommended)

---

## 🚢 Production Deployment

### Deploy to Cloud (AWS/GCP/Azure)

```bash
# SSH to your server
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and deploy
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker

cp .env.example .env
nano .env  # Configure for production

./docker-build.sh
./docker-start.sh

# Open port 8080 in firewall
sudo ufw allow 8080
```

### Add HTTPS (with Nginx)

```nginx
# /etc/nginx/sites-available/chatbot
server {
    listen 443 ssl;
    server_name chatbot.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See repository for details

---

## 🆘 Support

### Need Help?

1. **Check logs**: `./docker-logs.sh`
2. **Check status**: `./docker-status.sh`
3. **Read docs**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
4. **GitHub Issues**: https://github.com/chchingyesstyle/cs_wiki_chatbot/issues

### Common Questions

**Q: Why does it say "I don't know" for valid questions?**
A: Reindex your vector database: `docker exec -it cs-wiki-chatbot-api python index_wiki.py`

**Q: How much does OpenAI API cost?**
A: With gpt-4o-mini, typically $0.01-$0.10 per day for moderate usage.

**Q: Can I use a different LLM?**
A: Currently supports OpenAI only. Check the `main` branch for local Llama support.

**Q: How do I update the chatbot?**
A: `git pull origin docker && ./docker-stop.sh && ./docker-build.sh && ./docker-start.sh`

---

## 📊 Recent Improvements

<details>
<summary>Click to see detailed improvement history</summary>

### Problem: Chatbot Returning "I don't know" for Valid Questions

**Root Cause:** Out of 431 wiki pages:
- 151 pages (35%) were redirects with no content
- 125 pages (29%) were marked as outdated/expired
- Only 147 pages (34%) had actual useful content

Vector search was retrieving redirect/outdated pages instead of real content.

### Solutions Implemented

1. **Smart Indexing Filter** - Skip redirects and outdated pages
2. **Upgraded to gpt-4o-mini** - Better quality, 70% cheaper
3. **Optimized temperature** - Temperature 0.7 → 0.5 for consistency
4. **Longer responses** - Max tokens 512 → 1024
5. **Better retrieval** - Top-K 3 → 5 pages

### Performance Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Indexed pages | 431 (many redirects) | 147 (real content) | 66% less noise |
| Model | gpt-3.5-turbo | gpt-4o-mini | Better quality |
| API cost | $0.50/1.50 per 1M | $0.15/0.60 per 1M | 70% cheaper |
| Temperature | 0.7 | 0.5 | More consistent |
| Max tokens | 512 | 1024 | 2x longer |
| Pages retrieved | 3 | 5 | Better coverage |
| Answer quality | Often "I don't know" | Accurate answers | ✅ Solved |

</details>

---

**Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
**Branch**: docker
**Status**: ✅ Production Ready
