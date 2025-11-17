#!/bin/bash
# Docker stop script

echo "Stopping CS Wiki Chatbot services..."

# Stop containers
docker stop cs-wiki-chatbot-api cs-wiki-chatbot-web 2>/dev/null

# Remove containers
docker rm cs-wiki-chatbot-api cs-wiki-chatbot-web 2>/dev/null

echo "✓ Services stopped successfully!"
