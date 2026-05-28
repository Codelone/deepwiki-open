#!/bin/bash
set -e

if [ -f .env ]; then
  export $(grep -v "^#" .env | xargs -r)
fi

if [ -z "$OPENAI_API_KEY" ] || [ -z "$GOOGLE_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY and/or GOOGLE_API_KEY environment variables are not set."
  echo "These are required for DeepWiki to function properly."
  echo "You can provide them via a mounted .env file or as environment variables when running the container."
fi

LOG_DIR="/app/logs"
mkdir -p "$LOG_DIR"

# Start Embedding service
export EMBEDDING_PORT="${EMBEDDING_PORT:-8002}"
export EMBEDDING_DEVICE="${EMBEDDING_DEVICE:-cpu}"
echo "Starting Embedding Service on port $EMBEDDING_PORT..."
python -m api.embedding_service.server > "$LOG_DIR/embedding.log" 2>&1 &

# Start Python API server
echo "Starting API Server on port ${PORT:-8001}..."
python -m api.main --port ${PORT:-8001} > "$LOG_DIR/api.log" 2>&1 &

# Start Next.js server
echo "Starting Next.js Server on port 3000..."
PORT=3000 HOSTNAME=0.0.0.0 node server.js > "$LOG_DIR/nextjs.log" 2>&1 &

# Tail all logs to stdout for docker logs
tail -F "$LOG_DIR/embedding.log" "$LOG_DIR/api.log" "$LOG_DIR/nextjs.log" &

wait -n
exit $?
