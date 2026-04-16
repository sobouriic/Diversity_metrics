#!/bin/bash
# Start backend + frontend in detached background mode for server deployments.
#
# Usage:
#   ./scripts/start-server.sh [PUBLIC_HOST] [BACKEND_PORT] [FRONTEND_PORT]
#
# Environment overrides:
#   PUBLIC_HOST      Hostname used in generated frontend API URL (default: localhost)
#   BACKEND_PORT     Backend port (default: 8005)
#   FRONTEND_PORT    Frontend static server port (default: 3008)
#   BACKEND_BIND_HOST Interface for backend bind (default: 0.0.0.0)
#
# NOTE:
# - Do not hardcode public IPs in this script.
# - Set runtime host values through environment variables or arguments.

set -euo pipefail

PUBLIC_HOST="${PUBLIC_HOST:-${1:-localhost}}"
BACKEND_PORT="${BACKEND_PORT:-${2:-8005}}"
FRONTEND_PORT="${FRONTEND_PORT:-${3:-3008}}"
BACKEND_BIND_HOST="${BACKEND_BIND_HOST:-0.0.0.0}"

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="${APP_DIR}/.server.pid"
LOG_DIR="${APP_DIR}/logs"
VENV_DIR="${APP_DIR}/venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

mkdir -p "${LOG_DIR}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Diversity Metrics System (Server Mode)${NC}"
echo -e "${BLUE}Public Host: ${PUBLIC_HOST}${NC}"
echo -e "${BLUE}Backend: ${BACKEND_BIND_HOST}:${BACKEND_PORT}${NC}"
echo -e "${BLUE}Frontend Port: ${FRONTEND_PORT}${NC}"
echo ""

if [ -f "${PID_FILE}" ]; then
    OLD_BACKEND_PID="$(grep "BACKEND=" "${PID_FILE}" | cut -d= -f2 || true)"
    OLD_FRONTEND_PID="$(grep "FRONTEND=" "${PID_FILE}" | cut -d= -f2 || true)"

    if [ -n "${OLD_BACKEND_PID}" ] && kill -0 "${OLD_BACKEND_PID}" 2>/dev/null; then
        echo -e "${YELLOW}⚠ Services are already running (backend PID: ${OLD_BACKEND_PID}, frontend PID: ${OLD_FRONTEND_PID}).${NC}"
        echo -e "${YELLOW}Use ./scripts/stop-server.sh first if you want to restart.${NC}"
        exit 1
    fi
fi

cd "${APP_DIR}"

if [ ! -x "${VENV_PYTHON}" ]; then
    echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
    python3 -m venv "${VENV_DIR}"
fi

if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Existing virtual environment is invalid. Recreating...${NC}"
    rm -rf "${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi

if ! "${VENV_PYTHON}" -m pip --version >/dev/null 2>&1; then
    echo -e "${YELLOW}❌ Could not initialize pip in virtual environment.${NC}"
    echo -e "${YELLOW}Install python venv tools (Debian/Ubuntu): sudo apt install python3-venv${NC}"
    exit 1
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
echo -e "${BLUE}📝 Configuring frontend API base URL...${NC}"
cat > frontend/.env.production << EOF
VITE_API_BASE=http://${PUBLIC_HOST}:${BACKEND_PORT}/api
EOF
echo -e "${GREEN}✓ API base configured${NC}"

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    (
        cd frontend
        npm install -q
    )
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⊘ Frontend dependencies already installed${NC}"
fi

echo ""
echo -e "${BLUE}🔨 Building frontend...${NC}"
(
    cd frontend
    VITE_API_BASE="http://${PUBLIC_HOST}:${BACKEND_PORT}/api" npm run build
)
echo -e "${GREEN}✓ Frontend build complete${NC}"

echo ""
echo -e "${BLUE}📋 Starting services in background...${NC}"

nohup env CORS_ALLOW_ORIGINS="http://${PUBLIC_HOST}:${FRONTEND_PORT},http://localhost:${FRONTEND_PORT}" "${VENV_PYTHON}" -m uvicorn backend.api:app --host "${BACKEND_BIND_HOST}" --port "${BACKEND_PORT}" > "${LOG_DIR}/backend.log" 2>&1 &
BACKEND_PID=$!
sleep 2

nohup python3 -m http.server "${FRONTEND_PORT}" --bind 0.0.0.0 --directory frontend/dist > "${LOG_DIR}/frontend.log" 2>&1 &
FRONTEND_PID=$!
sleep 1

echo "BACKEND=${BACKEND_PID}" > "${PID_FILE}"
echo "FRONTEND=${FRONTEND_PID}" >> "${PID_FILE}"
chmod 600 "${PID_FILE}"

echo ""
echo -e "${GREEN}✅ Services started in background${NC}"
echo ""
echo "Frontend:   http://${PUBLIC_HOST}:${FRONTEND_PORT}"
echo "Backend:    http://${PUBLIC_HOST}:${BACKEND_PORT}"
echo "API Docs:   http://${PUBLIC_HOST}:${BACKEND_PORT}/docs"
echo ""
echo "PIDs:       backend=${BACKEND_PID}, frontend=${FRONTEND_PID}"
echo "Logs:       ${LOG_DIR}/backend.log | ${LOG_DIR}/frontend.log"
echo ""
echo "Stop:       ./scripts/stop-server.sh"
