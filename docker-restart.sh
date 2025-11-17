#!/bin/bash
# Docker restart script

echo "Restarting CS Wiki Chatbot services..."

docker-compose restart

if [ $? -eq 0 ]; then
    echo "✓ Services restarted successfully!"
else
    echo "✗ Failed to restart services"
    exit 1
fi
