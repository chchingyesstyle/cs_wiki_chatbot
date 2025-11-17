#!/bin/bash
# Docker build script

echo "Building CS Wiki Chatbot Docker images..."
docker-compose build --no-cache

if [ $? -eq 0 ]; then
    echo "✓ Docker images built successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Copy .env.example to .env and configure it"
    echo "  2. Run: ./docker-start.sh"
else
    echo "✗ Docker build failed"
    exit 1
fi
