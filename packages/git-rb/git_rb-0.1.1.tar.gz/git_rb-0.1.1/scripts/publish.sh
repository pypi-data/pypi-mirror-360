#!/bin/bash

set -euo pipefail

ENV_FILE=".env"

# Check if the .env file exists
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "Error loading .env"
  exit 1
fi

# UV_PUBLISH_TOKEN should be available
if [ -z "$UV_PUBLISH_TOKEN" ]; then
  echo "Error: UV_PUBLISH_TOKEN is not set in .env."
  exit 1
fi

# Remove old dist
rm -rf dist || true
uv build
uv publish

if [ $? -eq 0 ]; then
  echo "--- Package Published Successfully! ---"
else
  echo "--- Package Publishing FAILED! ---"
  exit 1
fi
