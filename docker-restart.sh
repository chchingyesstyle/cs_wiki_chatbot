#!/bin/bash
# Docker restart script

echo "Restarting CS Wiki Chatbot services..."

# Restart containers
docker restart cs-wiki-chatbot-api cs-wiki-chatbot-web

if [ $? -eq 0 ]; then
    echo "✓ Services restarted successfully!"
else
    echo "✗ Failed to restart services"
    echo "Try stopping and starting: ./docker-stop.sh && ./docker-start.sh"
    exit 1
fi
