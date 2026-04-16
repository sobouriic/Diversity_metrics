#!/bin/bash
# Start both backend and frontend servers

set -euo pipefail

cd "$(dirname "$0")/.."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Diversity Metrics System${NC}"
echo ""

VENV_DIR="venv"
VENV_PYTHON="${VENV_DIR}/bin/python"
FRONTEND_PORT="${FRONTEND_PORT:-3008}"
BACKEND_PORT="${BACKEND_PORT:-8005}"
BACKEND_BIND_HOST="${BACKEND_BIND_HOST:-127.0.0.1}"
BACKEND_PID=""
FRONTEND_PID=""

if [ ! -x "${VENV_PYTHON}" ]; then
    echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
    python3 -m venv "${VENV_DIR}"
fi

# Recreate stale/copy-pasted virtualenvs that do not have pip available.
if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Existing virtual environment is invalid on this machine. Recreating...${NC}"
    rm -rf "${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi

if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
    echo -e "${YELLOW}❌ Could not initialize pip in virtual environment.${NC}"
    echo -e "${YELLOW}Install python venv tools (Debian/Ubuntu): sudo apt install python3-venv${NC}"
    exit 1
fi

port_in_use() {
    local port="$1"
    lsof -iTCP:"${port}" -sTCP:LISTEN -t >/dev/null 2>&1
}

if port_in_use "${BACKEND_PORT}"; then
    ORIGINAL_BACKEND_PORT="${BACKEND_PORT}"
    while port_in_use "${BACKEND_PORT}"; do
        BACKEND_PORT=$((BACKEND_PORT + 1))
    done
    echo -e "${YELLOW}⚠ Port ${ORIGINAL_BACKEND_PORT} is in use. Switching backend to ${BACKEND_PORT}.${NC}"
fi

if [ ! -f ".backend_deps_installed" ]; then
    echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
    "${VENV_PYTHON}" -m pip install -q -r backend/requirements.txt
    touch .backend_deps_installed
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⊘ Backend dependencies already installed${NC}"
fi

echo ""

# Start backend in background
echo -e "${GREEN}✓ Starting backend on ${BACKEND_BIND_HOST}:${BACKEND_PORT}${NC}"
"${VENV_PYTHON}" -m uvicorn backend.api:app --host "${BACKEND_BIND_HOST}" --port "${BACKEND_PORT}" &
BACKEND_PID=$!
sleep 2

if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
    echo -e "${YELLOW}❌ Backend failed to start on port ${BACKEND_PORT}.${NC}"
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install -q
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⊘ Frontend dependencies already installed${NC}"
fi

echo ""

# Start frontend in background
echo -e "${GREEN}✓ Starting frontend on port ${FRONTEND_PORT}${NC}"
cd frontend
VITE_API_BASE="http://localhost:${BACKEND_PORT}/api" npm run dev -- --port "${FRONTEND_PORT}" &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Both servers started!${NC}"
echo ""
echo "Frontend:  http://localhost:${FRONTEND_PORT}"
echo "Backend:   http://localhost:${BACKEND_PORT}"
echo "API Docs:  http://localhost:${BACKEND_PORT}/docs"
echo "API Base:  http://localhost:${BACKEND_PORT}/api"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    if [ -n "${BACKEND_PID:-}" ]; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ]; then
        kill "${FRONTEND_PID}" 2>/dev/null || true
        wait "${FRONTEND_PID}" 2>/dev/null || true
    fi
    echo "✓ Servers stopped"
}

trap cleanup EXIT INT TERM
wait
