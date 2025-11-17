# Vector Database Reindexing Guide

This guide explains how to reindex your MediaWiki pages into the ChromaDB vector database.

## 📋 When to Reindex

You should reindex your vector database when:
- ✅ Wiki content has been significantly updated
- ✅ New pages have been added to the wiki
- ✅ Pages have been deleted or renamed
- ✅ First-time setup (initial indexing)
- ✅ Vector search is returning poor results
- ✅ ChromaDB data is corrupted

## 🚀 Reindexing Methods

### Method 1: Docker Deployment (Recommended)

#### Option A: One Command
```bash
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

#### Option B: Interactive Container Shell
```bash
# Enter container
docker exec -it cs-wiki-chatbot-api bash

# Run indexing
python index_wiki.py

# Exit container
exit
```

#### Clear and Reindex
```bash
# Stop services
./docker-stop.sh

# Clear existing ChromaDB
rm -rf chroma_db/*

# Start services
./docker-start.sh

# Reindex
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

---

### Method 2: Manual Deployment

#### Simple Reindex
```bash
# Make sure services are running
./status.sh

# Run indexing script
python3 index_wiki.py
```

#### Clear and Reindex
```bash
# Stop services
./stop.sh

# Clear existing ChromaDB
rm -rf chroma_db/*

# Start services
./start.sh

# Reindex
python3 index_wiki.py
```

---

## 📊 What the Indexing Process Does

1. **Connects to Database** - Reads all wiki pages from MediaWiki database
2. **Cleans Content** - Removes wiki markup and formatting
3. **Creates Embeddings** - Converts text to vector embeddings using sentence-transformers
4. **Stores in ChromaDB** - Saves embeddings for fast semantic search
5. **Shows Progress** - Displays indexing progress

### Sample Output:
```
============================================================
MediaWiki Vector Database Indexer
============================================================

1. Connecting to database...
✓ Database connected

2. Fetching all wiki pages...
✓ Found 250 pages

3. Cleaning wiki content...
✓ Cleaned 250 pages

4. Initializing vector store...
✓ Vector store initialized with 0 documents

5. Indexing pages into vector database...
  Indexed 100/250 pages
  Indexed 200/250 pages
  Indexed 250/250 pages
✓ Indexing complete! Total documents: 250

============================================================
✓ Indexing Complete!
  Total documents: 250
  Storage location: ./chroma_db
============================================================
```

---

## ⏱️ Performance

### Indexing Time
- **Small wiki** (< 100 pages): 1-2 minutes
- **Medium wiki** (100-500 pages): 2-5 minutes
- **Large wiki** (500-1000 pages): 5-10 minutes
- **Very large wiki** (1000+ pages): 10+ minutes

### Resources Required
- **CPU**: Moderate (sentence-transformers model)
- **RAM**: 2GB+ recommended
- **Disk**: ~100MB per 1000 pages

---

## 🔧 Configuration

The indexing script uses settings from `.env`:

```bash
# Vector Store Configuration
USE_VECTOR_SEARCH=True        # Enable/disable vector search
VECTOR_DB_PATH=./chroma_db    # Storage path
VECTOR_TOP_K=3                # Number of results to return

# Database Configuration
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

---

## 🐛 Troubleshooting

### Error: "Database connection failed"
```bash
# Check database credentials in .env
cat .env | grep DB_

# Test connection
python3 -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
print('OK' if db.connect() else 'FAILED')
"
```

### Error: "No pages found in database"
```bash
# Check if pages exist
python3 -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
db.connect()
pages = db.get_all_pages(limit=5)
print(f'Found {len(pages)} pages')
"
```

### Error: "ChromaDB initialization failed"
```bash
# Clear ChromaDB and retry
rm -rf chroma_db/*
python3 index_wiki.py
```

### Error: "Out of memory"
```bash
# Edit index_wiki.py and reduce batch size
nano index_wiki.py
# Find: batch_size=100
# Change to: batch_size=50
```

### Slow indexing
```bash
# Check system resources
top
df -h

# Reduce number of pages
python3 -c "
from index_wiki import main
# This will index only first 500 pages
# Edit index_wiki.py: limit=500 instead of limit=10000
"
```

---

## 📝 Advanced Usage

### Index Specific Number of Pages
Edit `index_wiki.py`:
```python
# Line ~28
pages = db.get_all_pages(limit=10000)  # Change this number
```

### Check Current Index Status
```bash
# Docker
docker exec -it cs-wiki-chatbot-api python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
print(f'Documents: {vs.collection.count()}')
"

# Manual
python3 -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
print(f'Documents: {vs.collection.count()}')
"
```

### Clear Index Without Reindexing
```bash
# Docker
docker exec -it cs-wiki-chatbot-api python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
vs.clear()
print('Index cleared')
"

# Manual
python3 -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
vs.clear()
print('Index cleared')
"
```

### Batch Reindexing (Large Wikis)
For very large wikis, index in batches:

```bash
# Modify index_wiki.py to process in chunks
# Example: Index 1000 pages at a time
python3 -c "
from db_connector import WikiDBConnector
from vector_store import VectorStore
from chatbot import WikiChatbot

db = WikiDBConnector()
db.connect()

# Get total pages
all_pages = db.get_all_pages(limit=10000)
print(f'Total pages: {len(all_pages)}')

# Process in batches of 1000
batch_size = 1000
for i in range(0, len(all_pages), batch_size):
    batch = all_pages[i:i+batch_size]
    print(f'Processing batch {i//batch_size + 1}...')
    # Index this batch
"
```

---

## ✅ Verify Indexing Success

### Check Document Count
```bash
# Docker
docker exec -it cs-wiki-chatbot-api python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
stats = vs.get_stats()
print(f'Status: {stats[\"status\"]}')
print(f'Documents: {stats[\"total_documents\"]}')
"

# Manual
python3 -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
stats = vs.get_stats()
print(f'Status: {stats[\"status\"]}')
print(f'Documents: {stats[\"total_documents\"]}')
"
```

### Test Search
```bash
# Docker
docker exec -it cs-wiki-chatbot-api python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
results = vs.search('test query', top_k=3)
print(f'Search returned {len(results)} results')
for r in results:
    print(f'  - {r[\"title\"]}')
"

# Manual
python3 -c "
from vector_store import VectorStore
vs = VectorStore()
vs.initialize()
results = vs.search('test query', top_k=3)
print(f'Search returned {len(results)} results')
for r in results:
    print(f'  - {r[\"title\"]}')
"
```

---

## 🔄 Automated Reindexing

### Cron Job (Daily Reindex)
```bash
# Edit crontab
crontab -e

# Add line (reindex daily at 2 AM)
0 2 * * * cd /u01/project/chatbot && docker exec cs-wiki-chatbot-api python index_wiki.py >> /var/log/reindex.log 2>&1
```

### Webhook Trigger (After Wiki Update)
Create a webhook script that triggers reindexing when wiki is updated:

```bash
#!/bin/bash
# reindex-webhook.sh
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

---

## 📚 Related Documentation

- **DOCKER_DEPLOYMENT.md** - Docker deployment guide
- **DOCKER_QUICKREF.md** - Quick Docker commands
- **README.md** - Main documentation
- **vector_store.py** - Vector store implementation
- **index_wiki.py** - Indexing script

---

## 🆘 Need Help?

### Common Commands Summary

| Task | Docker | Manual |
|------|--------|--------|
| **Reindex** | `docker exec -it cs-wiki-chatbot-api python index_wiki.py` | `python3 index_wiki.py` |
| **Check count** | `docker exec -it cs-wiki-chatbot-api python -c "from vector_store import VectorStore; vs=VectorStore(); vs.initialize(); print(vs.collection.count())"` | `python3 -c "from vector_store import VectorStore; vs=VectorStore(); vs.initialize(); print(vs.collection.count())"` |
| **Clear index** | `rm -rf chroma_db/*` | `rm -rf chroma_db/*` |
| **Test search** | Use Web UI at http://localhost:8080 | Use Web UI at http://localhost:8080 |

### Support
- Check logs: `./docker-logs.sh` (Docker) or `tail -f app.log` (Manual)
- Review documentation files
- Check GitHub issues: https://github.com/chchingyesstyle/cs_wiki_chatbot/issues

---

**Last Updated**: 2024-01-17  
**Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
