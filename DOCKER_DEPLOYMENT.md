# CS Wiki Chatbot - Docker Deployment Guide

Complete guide for deploying the CS Wiki Chatbot using Docker containers.

## 📋 Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 1.29+ installed
- OpenAI API key (or access to MediaWiki database)
- At least 2GB RAM available

### Install Docker (if not installed)

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Amazon Linux 2:**
```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

**Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot
git checkout docker
```

### 2. Configure Environment
```bash
# Copy example configuration
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

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Ports (optional, defaults shown)
FLASK_PORT=5000
WEB_SERVER_PORT=8080

# Wiki URL
WIKI_BASE_URL=http://your-wiki-url/index.php
```

### 3. Build Docker Images
```bash
./docker-build.sh
```

### 4. Start Services
```bash
./docker-start.sh
```

### 5. Access the Chatbot
- **Web UI**: http://localhost:8080
- **API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health

## 📦 Docker Architecture

The deployment consists of 2 containers:

### Container 1: API Server (`chatbot-api`)
- Runs Flask REST API on port 5000
- Handles chat requests and database queries
- Connects to OpenAI API
- Includes health check endpoint

### Container 2: Web Server (`chatbot-web`)
- Serves HTML/JS interface on port 8080
- Automatically configures API endpoint
- Lightweight HTTP server

### Networking
- Both containers communicate via `chatbot-network`
- Web container depends on API health check
- Ports are configurable via `.env`

### Data Persistence
- `chroma_db/` - Vector database (mounted volume)
- `app.log` - Application logs (mounted volume)

## 🛠️ Management Scripts

All management is done through simple shell scripts:

| Script | Purpose |
|--------|---------|
| `./docker-build.sh` | Build Docker images |
| `./docker-start.sh` | Start all services |
| `./docker-stop.sh` | Stop all services |
| `./docker-restart.sh` | Restart all services |
| `./docker-status.sh` | Check service status |
| `./docker-logs.sh` | View logs (all services) |
| `./docker-logs.sh chatbot-api` | View API logs only |
| `./docker-logs.sh chatbot-web` | View Web logs only |

## 📝 Common Operations

### View Service Status
```bash
./docker-status.sh
```

### View Logs
```bash
# All services
./docker-logs.sh

# API only
./docker-logs.sh chatbot-api

# Web only
./docker-logs.sh chatbot-web
```

### Restart Services
```bash
./docker-restart.sh
```

### Stop Services
```bash
./docker-stop.sh
```

### Rebuild After Code Changes
```bash
./docker-stop.sh
./docker-build.sh
./docker-start.sh
```

## 🔧 Advanced Configuration

### Custom Ports
Edit `.env` file:
```bash
FLASK_PORT=5001
WEB_SERVER_PORT=8081
```
Then restart:
```bash
./docker-restart.sh
```

### Use Different OpenAI Model
Edit `.env`:
```bash
OPENAI_MODEL=gpt-4  # More capable but more expensive
# or
OPENAI_MODEL=gpt-3.5-turbo  # Faster and cheaper
```

### Enable Vector Search
Edit `.env`:
```bash
USE_VECTOR_SEARCH=True
VECTOR_DB_PATH=/app/chroma_db
```

Then index your wiki (run once):
```bash
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
./docker-logs.sh

# Check if ports are in use
sudo netstat -tuln | grep -E '5000|8080'

# Remove and rebuild
docker-compose down
./docker-build.sh
./docker-start.sh
```

### API Health Check Failing
```bash
# Check API logs
./docker-logs.sh chatbot-api

# Common issues:
# - Database connection failed (check DB_HOST, credentials)
# - OpenAI API key invalid (check OPENAI_API_KEY)
# - Port conflict (change FLASK_PORT in .env)
```

### Database Connection Issues
```bash
# Test from container
docker exec -it cs-wiki-chatbot-api python -c "
from db_connector import WikiDBConnector
db = WikiDBConnector()
print('Connected!' if db.connect() else 'Failed!')
"
```

### OpenAI API Issues
```bash
# Test from container
docker exec -it cs-wiki-chatbot-api python -c "
from openai_model import OpenAIModel
m = OpenAIModel()
m.load_model()
print(m.generate_response('Hello'))
"
```

### Clear ChromaDB and Re-index
```bash
# Stop services
./docker-stop.sh

# Remove ChromaDB
rm -rf chroma_db/*

# Start services
./docker-start.sh

# Re-index
docker exec -it cs-wiki-chatbot-api python index_wiki.py
```

## 🌐 Production Deployment

### Using Docker Compose (Recommended)
```bash
# Use docker-compose.yml as-is
./docker-start.sh
```

### Behind Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/chatbot
server {
    listen 80;
    server_name chatbot.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment-Specific Configuration
Create multiple `.env` files:
- `.env.development`
- `.env.staging`
- `.env.production`

Use different compose files:
```bash
docker-compose --env-file .env.production up -d
```

## 📊 Monitoring

### Check Container Health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Monitor Resource Usage
```bash
docker stats
```

### Check Logs Continuously
```bash
./docker-logs.sh  # Press Ctrl+C to exit
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use secrets management** - Consider Docker secrets or vault
3. **Limit container privileges** - Run as non-root user
4. **Keep images updated** - Rebuild regularly
5. **Use specific Python version** - Pin in Dockerfile
6. **Enable firewall** - Only expose necessary ports
7. **Use HTTPS** - Deploy behind nginx with SSL

## 🚢 Deployment to Cloud

### AWS EC2
```bash
# SSH to instance
ssh -i key.pem ec2-user@your-instance

# Install Docker
sudo yum update -y && sudo yum install -y docker
sudo systemctl start docker

# Clone and deploy
git clone https://github.com/chchingyesstyle/cs_wiki_chatbot.git
cd cs_wiki_chatbot && git checkout docker
cp .env.example .env
nano .env  # Configure
./docker-build.sh && ./docker-start.sh
```

### Docker Hub (Optional)
```bash
# Build and tag
docker build -t your-username/cs-wiki-chatbot:latest .

# Push to Docker Hub
docker push your-username/cs-wiki-chatbot:latest

# Pull and run on any server
docker pull your-username/cs-wiki-chatbot:latest
docker-compose up -d
```

## 🔄 Updates and Maintenance

### Update Application Code
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

### Backup Data
```bash
# Backup ChromaDB
tar -czf chroma_db_backup.tar.gz chroma_db/

# Backup logs
cp app.log app.log.backup
```

## 📚 Additional Resources

- **Repository**: https://github.com/chchingyesstyle/cs_wiki_chatbot
- **Docker Branch**: https://github.com/chchingyesstyle/cs_wiki_chatbot/tree/docker
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **OpenAI API**: https://platform.openai.com/docs/

## 💡 Tips

- Use `gpt-3.5-turbo` for development (faster, cheaper)
- Use `gpt-4` for production (better quality)
- Monitor OpenAI usage at https://platform.openai.com/usage
- Set up alerts for container health checks
- Use `.env` for environment-specific configs
- Keep ChromaDB backed up if you've indexed many pages

## ❓ Support

For issues or questions:
1. Check logs: `./docker-logs.sh`
2. Check status: `./docker-status.sh`
3. Review this guide
4. Check GitHub issues

## 📄 License

MIT License - See repository for details
