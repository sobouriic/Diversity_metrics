#!/bin/bash


echo "🛑 Stopping all servers..."
lsof -ti:8004 | xargs -r kill -9 2>/dev/null && echo "✓ Backend (port 8004) stopped" || echo "✓ Backend not running"
lsof -ti:3005 | xargs -r kill -9 2>/dev/null && echo "✓ Frontend (port 3005) stopped" || echo "✓ Frontend not running"
pkill -f "vite" 2>/dev/null || true
pkill -f "npm" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo "✓ All servers stopped"
