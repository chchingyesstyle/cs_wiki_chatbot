#!/bin/bash
# Start script for MediaWiki Chatbot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/chatbot.pid"
WEB_PID_FILE="$SCRIPT_DIR/web.pid"
LOG_FILE="$SCRIPT_DIR/app.log"
WEB_LOG_FILE="$SCRIPT_DIR/web.log"

cd "$SCRIPT_DIR"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Chatbot is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Error: .env file not found"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Start the Flask app in background
echo "Starting MediaWiki Chatbot..."
nohup python3 app.py >> "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

# Wait a moment and check if it's running
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo "✓ Chatbot API started successfully (PID: $PID)"
    echo "  Log file: $LOG_FILE"
    echo "  API available at: http://localhost:5001"
else
    echo "Failed to start chatbot. Check $LOG_FILE for errors"
    rm -f "$PID_FILE"
    exit 1
fi

# Start web server for HTML interface
echo "Starting web server for UI..."
cd "$SCRIPT_DIR"
nohup python3 -m http.server 8080 >> "$WEB_LOG_FILE" 2>&1 &
WEB_PID=$!

# Save web server PID
echo $WEB_PID > "$WEB_PID_FILE"

# Wait and check if web server is running
sleep 1
if ps -p $WEB_PID > /dev/null 2>&1; then
    echo "✓ Web server started successfully (PID: $WEB_PID)"
    echo "  Web UI: http://localhost:8080"
    echo ""
    echo "All services started successfully!"
else
    echo "Warning: Web server failed to start. Check $WEB_LOG_FILE"
    rm -f "$WEB_PID_FILE"
fi
