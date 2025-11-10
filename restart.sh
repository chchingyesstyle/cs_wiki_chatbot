#!/bin/bash
# Restart script for MediaWiki Chatbot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "Restarting MediaWiki Chatbot..."
echo ""

# Stop the chatbot
./stop.sh

# Wait a moment
sleep 1

# Start the chatbot
./start.sh
