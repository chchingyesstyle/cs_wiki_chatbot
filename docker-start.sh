#!/bin/bash
# Docker start script

echo "Starting CS Wiki Chatbot services..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Create network if it doesn't exist
docker network create chatbot-network 2>/dev/null || true

# Stop and remove existing containers if they exist
docker stop cs-wiki-chatbot-api cs-wiki-chatbot-web 2>/dev/null || true
docker rm cs-wiki-chatbot-api cs-wiki-chatbot-web 2>/dev/null || true

# Start API container
echo "Starting API container..."
docker run -d \
  --name cs-wiki-chatbot-api \
  --network chatbot-network \
  --env-file .env \
  -v "$(pwd)/chroma_db:/app/chroma_db" \
  -v "$(pwd)/models:/app/models" \
  --restart unless-stopped \
  cs-wiki-chatbot:latest python app.py

if [ $? -ne 0 ]; then
    echo "✗ Failed to start API container"
    exit 1
fi

# Wait a bit for API to start
sleep 3

# Start Web container
echo "Starting Web container..."
docker run -d \
  --name cs-wiki-chatbot-web \
  --network chatbot-network \
  --env-file .env \
  -e API_HOST=cs-wiki-chatbot-api \
  -e FLASK_PORT=${FLASK_PORT:-5000} \
  -p ${WEB_SERVER_PORT:-8080}:8080 \
  --restart unless-stopped \
  cs-wiki-chatbot:latest python serve_web.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Services started successfully!"
    echo ""
    echo "Services:"
    echo "  - Web UI:  http://localhost:${WEB_SERVER_PORT:-8080}"
    echo "  - API:     Internal only (port ${FLASK_PORT:-5000})"
    echo ""
    echo "Note: First startup may take 2-5 minutes to load the model"
    echo ""
    echo "Check status: ./docker-status.sh"
    echo "View logs:    ./docker-logs.sh"
    echo "Stop:         ./docker-stop.sh"
else
    echo "✗ Failed to start web container"
    docker stop cs-wiki-chatbot-api
    docker rm cs-wiki-chatbot-api
    exit 1
fi
