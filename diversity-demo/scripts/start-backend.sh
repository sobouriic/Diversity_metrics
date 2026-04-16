#!/bin/bash
# Start FastAPI backend server

set -euo pipefail

cd "$(dirname "$0")/.."

BACKEND_PORT="${BACKEND_PORT:-8005}"
VENV_PYTHON="venv/bin/python"

if [ ! -x "${VENV_PYTHON}" ]; then
  echo "Virtual environment not found. Run ./scripts/start.sh first."
  exit 1
fi

cd backend
"../${VENV_PYTHON}" -m uvicorn api:app --reload --host 127.0.0.1 --port "${BACKEND_PORT}"
