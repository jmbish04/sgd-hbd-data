#!/bin/bash
set -e

# Configuration
BUCKET_NAME="${R2_BUCKET_NAME}"
ACCOUNT_ID="${R2_ACCOUNT_ID}"
MOUNT_POINT="/mnt/data"

if [ -z "$BUCKET_NAME" ] || [ -z "$ACCOUNT_ID" ]; then
    echo "Warning: R2_BUCKET_NAME or R2_ACCOUNT_ID is not set. Skipping mount."
else
    echo "Mounting R2 bucket '${BUCKET_NAME}' to '${MOUNT_POINT}'..."
    mkdir -p "$MOUNT_POINT"
    
    R2_ENDPOINT="https://${ACCOUNT_ID}.r2.cloudflarestorage.com"
    
    # Run TigrisFS in background (assumes AWS_ACCESS_KEY_ID/SECRET are in env)
    /usr/local/bin/tigrisfs --endpoint "${R2_ENDPOINT}" -f "${BUCKET_NAME}" "${MOUNT_POINT}" &
    
    # Wait strictly for mount
    sleep 3
fi

echo "Starting Uvicorn with Process Monitor..."
# Pass MOUNT_POINT as env var to app if needed
export DATA_DIR="$MOUNT_POINT"

# Start application via Process Monitor
export PORT="${PORT:-8080}"
echo "Starting on port $PORT..."

exec bun run container_tools/cli-tools.ts process start \
  --instance-id "main-app" \
  --port $PORT \
  -- uvicorn src.main:app --host 0.0.0.0 --port $PORT
