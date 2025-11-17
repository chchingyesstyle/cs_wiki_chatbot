#!/bin/bash
# Docker logs script

SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "Showing logs for all services..."
    echo "================================="
    docker-compose logs -f --tail=100
else
    echo "Showing logs for $SERVICE..."
    echo "================================="
    docker-compose logs -f --tail=100 $SERVICE
fi
