#!/bin/bash
# Docker status script

echo "CS Wiki Chatbot - Docker Services Status"
echo "=========================================="
echo ""

# Show running containers
docker ps --filter "name=cs-wiki-chatbot" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Container Details:"
echo "------------------"

# Check API container
if docker ps | grep -q cs-wiki-chatbot-api; then
    echo "✓ API Container: Running"
    API_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' cs-wiki-chatbot-api 2>/dev/null)
    if [ ! -z "$API_HEALTH" ]; then
        echo "  Health: $API_HEALTH"
    fi
else
    echo "✗ API Container: Not Running"
fi

# Check Web container
if docker ps | grep -q cs-wiki-chatbot-web; then
    echo "✓ Web Container: Running"
else
    echo "✗ Web Container: Not Running"
fi

echo ""
echo "Quick Commands:"
echo "  View logs:    ./docker-logs.sh"
echo "  Restart:      ./docker-restart.sh"
echo "  Stop:         ./docker-stop.sh"
