#!/bin/bash
# Status script for MediaWiki Chatbot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/chatbot.pid"

cd "$SCRIPT_DIR"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: Chatbot is NOT running"
    exit 3
fi

PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "Status: Chatbot is RUNNING (PID: $PID)"
    echo ""
    echo "Process info:"
    ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
    echo ""
    echo "API endpoint: http://localhost:5000"
    
    # Check if port is listening
    if command -v netstat &> /dev/null; then
        echo ""
        echo "Port status:"
        netstat -tuln | grep :5000 || echo "Port 5000 not listening"
    fi
    exit 0
else
    echo "Status: Chatbot is NOT running (stale PID file)"
    rm -f "$PID_FILE"
    exit 1
fi
