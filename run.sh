#!/bin/bash

# Exit on error
set -e

echo "Building Docker image..."
docker build -t document-query-api .

echo "Stopping any existing container..."
docker stop document-query-api 2>/dev/null || true
docker rm document-query-api 2>/dev/null || true

echo "Starting Docker container..."
docker run -d \
  --name document-query-api \
  -p 8080:8080 \
  -e PYTHONUNBUFFERED=1 \
  document-query-api

echo "Container started successfully!"
echo "API is available at http://localhost:8080"
echo "Try: curl http://localhost:8080/hello"

# Show logs
echo ""
echo "Container logs:"
docker logs -f document-query-api
