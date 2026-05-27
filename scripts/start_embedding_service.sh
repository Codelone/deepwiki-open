#!/bin/bash
# Start the nomic-embed-text embedding service

set -e

# Default configuration
export EMBEDDING_MODEL_NAME="${EMBEDDING_MODEL_NAME:-nomic-ai/nomic-embed-text-v1.5}"
export EMBEDDING_PORT="${EMBEDDING_PORT:-8002}"
export EMBEDDING_DEVICE="${EMBEDDING_DEVICE:-cpu}"

echo "Starting Nomic Embed Text Service..."
echo "Model: $EMBEDDING_MODEL_NAME"
echo "Port: $EMBEDDING_PORT"
echo "Device: $EMBEDDING_DEVICE"

# Get the Python interpreter from poetry or use system python
if command -v poetry &> /dev/null; then
    VENV_PATH=$(poetry -C api env info --path 2>/dev/null || echo "")
    if [ -n "$VENV_PATH" ]; then
        PYTHON="$VENV_PATH/bin/python"
    else
        PYTHON="python3"
    fi
else
    PYTHON="python3"
fi

# Start the service
$PYTHON -m api.embedding_service.server