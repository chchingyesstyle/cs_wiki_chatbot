#!/bin/bash
# Docker build script

echo "Building CS Wiki Chatbot Docker images..."

# Build the image using docker build
docker build -t cs-wiki-chatbot:latest .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure .env file is configured"
    echo "  2. Run: ./docker-start.sh"
else
    echo "✗ Docker build failed"
    exit 1
fi
