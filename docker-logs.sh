#!/bin/bash
# Docker logs script

SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "Showing logs for all services..."
    echo "================================="
    echo ""
    echo "=== API Container Logs ==="
    docker logs --tail=50 cs-wiki-chatbot-api 2>&1
    echo ""
    echo "=== Web Container Logs ==="
    docker logs --tail=50 cs-wiki-chatbot-web 2>&1
else
    # Map service names to container names
    case $SERVICE in
        chatbot-api|api)
            CONTAINER="cs-wiki-chatbot-api"
            ;;
        chatbot-web|web)
            CONTAINER="cs-wiki-chatbot-web"
            ;;
        *)
            CONTAINER=$SERVICE
            ;;
    esac
    
    echo "Showing logs for $CONTAINER..."
    echo "================================="
    docker logs -f --tail=100 $CONTAINER
fi
