#!/bin/bash

BACKEND_PORT="${BACKEND_PORT:-8005}"
FRONTEND_PORT="${FRONTEND_PORT:-3008}"

echo "🛑 Stopping all servers..."
lsof -ti:"${BACKEND_PORT}" | xargs -r kill -9 2>/dev/null && echo "✓ Backend (port ${BACKEND_PORT}) stopped" || echo "✓ Backend not running on port ${BACKEND_PORT}"
lsof -ti:"${FRONTEND_PORT}" | xargs -r kill -9 2>/dev/null && echo "✓ Frontend (port ${FRONTEND_PORT}) stopped" || echo "✓ Frontend not running on port ${FRONTEND_PORT}"
pkill -f "vite" 2>/dev/null || true
pkill -f "npm" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo "✓ All servers stopped"
