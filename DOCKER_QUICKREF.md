# CS Wiki Chatbot - Docker Quick Reference

## 🚀 Quick Commands

### First Time Setup
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker
cp .env.example .env
nano .env  # Configure your settings
./docker-build.sh
./docker-start.sh
```

### Daily Operations
```bash
./docker-start.sh      # Start services
./docker-stop.sh       # Stop services
./docker-restart.sh    # Restart services
./docker-status.sh     # Check status
./docker-logs.sh       # View logs
```

### Access URLs
- Web UI: http://localhost:8080
- API: http://localhost:8080/api/chat (proxied)
- Health: http://localhost:8080/health (proxied)

**Note:** Only port 8080 is exposed. API accessed via reverse proxy for security.

## 📋 Configuration (.env)

### Required Settings
```bash
# Database
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# OpenAI
OPENAI_API_KEY=sk-...your_key_here
```

### Optional Settings
```bash
OPENAI_MODEL=gpt-4o-mini      # Recommended (cheaper & better than gpt-3.5)
FLASK_PORT=5000               # Internal API port (not exposed)
WEB_SERVER_PORT=8080          # External port (only this exposed)
USE_VECTOR_SEARCH=True        # Enable semantic search
```

## 🐳 Docker Commands

### Container Management
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop specific container
docker stop cs-wiki-chatbot-api
docker stop cs-wiki-chatbot-web

# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Logs
```bash
# All logs
./docker-logs.sh

# API logs only
./docker-logs.sh chatbot-api

# Web logs only
./docker-logs.sh chatbot-web

# Last 50 lines
docker-compose logs --tail=50
```

### Rebuild
```bash
# After code changes
./docker-stop.sh
./docker-build.sh
./docker-start.sh

# Force rebuild (no cache)
docker build --no-cache -t cs-wiki-chatbot:latest .
```

**Note:** The build creates a single image `cs-wiki-chatbot:latest` used by both containers. You only rebuild when code changes - starting/stopping containers doesn't require a rebuild.

### Execute Commands in Container
```bash
# Access container shell
docker exec -it cs-wiki-chatbot-api bash

# Run Python command
docker exec -it cs-wiki-chatbot-api python -c "print('Hello')"

# Index wiki pages
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
./docker-logs.sh

# Check ports (only 8080 should be exposed)
sudo netstat -tuln | grep 8080

# Rebuild
docker-compose down
./docker-build.sh
./docker-start.sh
```

### Database Connection Failed
```bash
# Test connection
docker exec -it cs-wiki-chatbot-api python -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
print('OK' if db.connect() else 'FAILED')
"

# Check .env settings
cat .env | grep DB_
```

### OpenAI API Error
```bash
# Test OpenAI
docker exec -it cs-wiki-chatbot-api python -c "
from openai_model import OpenAIModel
m = OpenAIModel()
m.load_model()
print(m.generate_response('test'))
"

# Check API key
cat .env | grep OPENAI_API_KEY
```

### Port Already in Use
```bash
# Find process using port (only 8080 is exposed)
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>

# Or change port in .env
nano .env  # Change WEB_SERVER_PORT
```

### Clear All Data
```bash
# Stop services
./docker-stop.sh

# Remove containers and volumes
docker-compose down -v

# Remove ChromaDB
rm -rf chroma_db/*

# Rebuild and start
./docker-build.sh
./docker-start.sh
```

## 📊 Monitoring

### Check Service Health
```bash
# Status
./docker-status.sh

# Container stats
docker stats

# Health check (via proxy on port 8080)
curl http://localhost:8080/health
```

### View Resource Usage
```bash
# CPU/Memory usage
docker stats --no-stream

# Disk usage
docker system df
```

## 🔄 Updates

### Update Code
```bash
git pull origin docker
./docker-stop.sh
./docker-build.sh
./docker-start.sh
```

### Update Dependencies
```bash
# Edit requirements.txt
nano requirements.txt

# Rebuild
./docker-build.sh
./docker-start.sh
```

## 🌐 Production Tips

1. **Use environment-specific .env files**
   - `.env.development`
   - `.env.production`

2. **Enable HTTPS with Nginx** (Single port - 8080 only)
   ```nginx
   server {
       listen 443 ssl;
       server_name chatbot.yourdomain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Set up monitoring**
   - Health checks
   - Log aggregation
   - Resource alerts

4. **Backup data**
   ```bash
   tar -czf backup.tar.gz chroma_db/ .env app.log
   ```

5. **Use Docker secrets** (instead of .env)
   ```bash
   docker secret create db_password ./db_password.txt
   ```

## 📚 Documentation Links

- Full Docker Guide: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- Main README: [README.md](README.md)
- GitHub: https://github.com/chchingyesstyle/cs_wiki_chatbot
- Docker Branch: https://github.com/chchingyesstyle/cs_wiki_chatbot/tree/docker

## 🆘 Help

### Common Issues
1. Port conflicts → Change ports in .env
2. DB connection → Check DB_HOST and credentials
3. OpenAI error → Verify OPENAI_API_KEY
4. Container crash → Check logs with ./docker-logs.sh

### Support
- Review logs: `./docker-logs.sh`
- Check status: `./docker-status.sh`
- Read docs: DOCKER_DEPLOYMENT.md
- GitHub Issues: https://github.com/chchingyesstyle/cs_wiki_chatbot/issues
