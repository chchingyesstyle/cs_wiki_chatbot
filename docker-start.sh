#!/bin/bash
# Docker start script

echo "Starting CS Wiki Chatbot services..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Start services
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Services started successfully!"
    echo ""
    echo "Services:"
    echo "  - API:     http://localhost:${FLASK_PORT:-5000}"
    echo "  - Web UI:  http://localhost:${WEB_SERVER_PORT:-8080}"
    echo ""
    echo "Check status: ./docker-status.sh"
    echo "View logs:    ./docker-logs.sh"
    echo "Stop:         ./docker-stop.sh"
else
    echo "✗ Failed to start services"
    exit 1
fi
