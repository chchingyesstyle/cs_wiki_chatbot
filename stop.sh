#!/bin/bash
# Stop script for MediaWiki Chatbot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/chatbot.pid"
WEB_PID_FILE="$SCRIPT_DIR/web.pid"

cd "$SCRIPT_DIR"

# Flag to track if chatbot was stopped
CHATBOT_STOPPED=0

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Chatbot is not running (no PID file found)"
else
    PID=$(cat "$PID_FILE")
    
    # Check if process is running
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Chatbot is not running (process not found)"
        rm -f "$PID_FILE"
    else
        # Stop the process
        echo "Stopping MediaWiki Chatbot (PID: $PID)..."
        kill $PID
        
        # Wait for process to stop (max 10 seconds)
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "Chatbot stopped successfully"
                rm -f "$PID_FILE"
                CHATBOT_STOPPED=1
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Force killing chatbot..."
            kill -9 $PID
            rm -f "$PID_FILE"
            echo "Chatbot force stopped"
            CHATBOT_STOPPED=1
        fi
    fi
fi

# Stop web server
if [ -f "$WEB_PID_FILE" ]; then
    WEB_PID=$(cat "$WEB_PID_FILE")
    
    if ps -p $WEB_PID > /dev/null 2>&1; then
        echo "Stopping web server (PID: $WEB_PID)..."
        kill $WEB_PID 2>/dev/null
        sleep 1
        
        # Force kill if needed
        if ps -p $WEB_PID > /dev/null 2>&1; then
            kill -9 $WEB_PID 2>/dev/null
        fi
        echo "Web server stopped"
    fi
    
    rm -f "$WEB_PID_FILE"
fi

# Kill any remaining http.server processes on port 8080
WEB_PIDS=$(ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}')
if [ ! -z "$WEB_PIDS" ]; then
    echo "Cleaning up remaining web server processes..."
    echo "$WEB_PIDS" | xargs kill -9 2>/dev/null
fi
