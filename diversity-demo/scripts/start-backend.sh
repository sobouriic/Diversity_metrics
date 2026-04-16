#!/bin/bash
# Start FastAPI backend server

cd "$(dirname "$0")/.."

cd backend
uvicorn api:app --reload --port 8000
