#!/bin/bash
# Stop the background servers started by start-server.sh
# Usage: ./stop-server.sh

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="${APP_DIR}/.server.pid"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Diversity Metrics Services${NC}"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠ No running servers found (PID file not found)${NC}"
    echo "Checking for processes anyway..."
    echo ""
fi

# Extract PIDs if file exists
if [ -f "$PID_FILE" ]; then
    BACKEND_PID=$(grep "BACKEND=" "$PID_FILE" | cut -d= -f2)
    FRONTEND_PID=$(grep "FRONTEND=" "$PID_FILE" | cut -d= -f2)
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${BLUE}Killing backend (PID: $BACKEND_PID)...${NC}"
            kill -TERM "$BACKEND_PID"
            sleep 1
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                kill -9 "$BACKEND_PID"
            fi
            echo -e "${GREEN}✓ Backend stopped${NC}"
        else
            echo -e "${YELLOW}⊘ Backend (PID: $BACKEND_PID) not running${NC}"
        fi
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo -e "${BLUE}Killing frontend (PID: $FRONTEND_PID)...${NC}"
            kill -TERM "$FRONTEND_PID"
            sleep 1
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                kill -9 "$FRONTEND_PID"
            fi
            echo -e "${GREEN}✓ Frontend stopped${NC}"
        else
            echo -e "${YELLOW}⊘ Frontend (PID: $FRONTEND_PID) not running${NC}"
        fi
    fi
    
    # Remove PID file
    rm -f "$PID_FILE"
    echo -e "${GREEN}✓ PID file cleaned${NC}"
else
    # Fallback: kill by port if PID file doesn't exist
    echo -e "${YELLOW}Attempting to stop by port...${NC}"
    
    # Kill processes on known ports
    lsof -ti:8004 2>/dev/null | xargs -r kill -9 2>/dev/null && echo -e "${GREEN}✓ Backend (port 8004) stopped${NC}" || echo -e "${YELLOW}⊘ No process on port 8004${NC}"
    lsof -ti:3005 2>/dev/null | xargs -r kill -9 2>/dev/null && echo -e "${GREEN}✓ Frontend (port 3005) stopped${NC}" || echo -e "${YELLOW}⊘ No process on port 3005${NC}"
fi

echo ""
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""
echo -e "${BLUE}💡 Restart command:${NC}"
echo "  ./scripts/start-server.sh 147.182.245.252"
echo ""
