#!/bin/bash

# Start backend server for document upload service

echo "Starting Document Upload Service backend..."
echo "API will be available at: http://localhost:8002"
echo "API docs at: http://localhost:8002/docs"
echo ""
echo "Note: Port 8002 is used to avoid conflict with Redis Insight on 8001"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before continuing."
    exit 1
fi

# Start uvicorn
uvicorn app.main:app --reload --port 8002
