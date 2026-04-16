#!/bin/bash
# Start both backend and frontend servers for server deployment (BACKGROUND MODE)
# Usage: ./start-server.sh <SERVER_IP> [BACKEND_PORT] [FRONTEND_PORT]
# Example: ./start-server.sh 147.182.245.252 8004 3005
# 
# Runs in background and continues after SSH disconnect
# To stop: ./scripts/stop-server.sh

# Parse arguments
SERVER_IP="${1:-localhost}"
BACKEND_PORT="${2:-8004}"
FRONTEND_PORT="${3:-3005}"

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="${APP_DIR}/.server.pid"
LOG_DIR="${APP_DIR}/logs"

# Create logs directory if needed
mkdir -p "$LOG_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Diversity Metrics System (Background Mode)${NC}"
echo -e "${BLUE}Server IP: ${SERVER_IP}${NC}"
echo -e "${BLUE}Backend Port: ${BACKEND_PORT}${NC}"
echo -e "${BLUE}Frontend Port: ${FRONTEND_PORT}${NC}"
echo ""

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_BACKEND_PID=$(grep "BACKEND=" "$PID_FILE" | cut -d= -f2)
    OLD_FRONTEND_PID=$(grep "FRONTEND=" "$PID_FILE" | cut -d= -f2)
    
    if [ ! -z "$OLD_BACKEND_PID" ] && kill -0 "$OLD_BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠ Servers already running (Backend PID: $OLD_BACKEND_PID, Frontend PID: $OLD_FRONTEND_PID)${NC}"
        echo -e "${YELLOW}To stop: ./scripts/stop-server.sh${NC}"
        exit 1
    fi
fi

cd "$APP_DIR"

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f ".backend_deps_installed" ]; then
    echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
    pip install -q -r backend/requirements.txt
    touch .backend_deps_installed
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⊘ Backend dependencies already installed${NC}"
fi

echo ""

# Configure API endpoints
echo -e "${BLUE}📝 Configuring API endpoints...${NC}"
cat > frontend/.env.production << EOF
VITE_API_BASE=http://${SERVER_IP}:${BACKEND_PORT}/api
EOF
echo -e "${GREEN}✓ API endpoint configured: http://${SERVER_IP}:${BACKEND_PORT}/api${NC}"

echo ""

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
echo -e "${BLUE}🔨 Building frontend for production...${NC}"
cd frontend
VITE_API_BASE="http://${SERVER_IP}:${BACKEND_PORT}/api" npm run build
cd ..
echo -e "${GREEN}✓ Frontend build complete${NC}"

echo ""

# Start services in background with nohup (survives SSH disconnect)
echo -e "${BLUE}📋 Starting services in background...${NC}"

# Start backend using full path to venv python
nohup ${APP_DIR}/venv/bin/python -m uvicorn backend.api:app --host 0.0.0.0 --port ${BACKEND_PORT} > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
sleep 3

# Start frontend server
nohup python3 -m http.server ${FRONTEND_PORT} --bind 0.0.0.0 --directory frontend/dist > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
sleep 1

# Save PIDs for stopping later
echo "BACKEND=${BACKEND_PID}" > "$PID_FILE"
echo "FRONTEND=${FRONTEND_PID}" >> "$PID_FILE"
chmod 644 "$PID_FILE"

echo ""
echo -e "${GREEN}✅ Both servers started in background!${NC}"
echo ""
echo -e "${BLUE}📱 Access Information:${NC}"
echo "Frontend:        http://${SERVER_IP}:${FRONTEND_PORT}"
echo "Backend:         http://${SERVER_IP}:${BACKEND_PORT}"
echo "API Docs:        http://${SERVER_IP}:${BACKEND_PORT}/docs"
echo "API Base:        http://${SERVER_IP}:${BACKEND_PORT}/api"
echo ""
echo -e "${BLUE}📊 Process Information:${NC}"
echo "Backend PID:     ${BACKEND_PID}"
echo "Frontend PID:    ${FRONTEND_PID}"
echo "Logs:"
echo "  Backend:  ${LOG_DIR}/backend.log"
echo "  Frontend: ${LOG_DIR}/frontend.log"
echo ""
echo -e "${YELLOW}💡 Management Commands:${NC}"
echo "Stop servers:    ./scripts/stop-server.sh"
echo "View backend logs: tail -f ${LOG_DIR}/backend.log"
echo "View frontend logs: tail -f ${LOG_DIR}/frontend.log"
echo "Check status:    ps aux | grep -E '(uvicorn|http.server)'"
echo ""
