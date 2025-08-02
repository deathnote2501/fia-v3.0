#!/bin/bash
set -e

echo "=== FIA v3.0 Startup Script ==="
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"
echo "Environment: ${ENVIRONMENT:-development}"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "ERROR: backend directory not found"
    exit 1
fi

# Change to backend directory
cd backend

# Check if app directory exists
if [ ! -d "app" ]; then
    echo "ERROR: app directory not found in backend"
    exit 1
fi

# Set Python path
export PYTHONPATH="/app/backend:$PYTHONPATH"

echo "Starting FastAPI application..."
echo "Command: python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"

# Start the application
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info