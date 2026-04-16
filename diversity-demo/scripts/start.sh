#!/bin/bash
# Start both backend and frontend servers

set -e

cd "$(dirname "$0")/.."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Diversity Metrics System${NC}"
echo ""

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

# Start backend in background
echo -e "${GREEN}✓ Starting backend on port 8004${NC}"
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8004 &
BACKEND_PID=$!
sleep 2

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
echo -e "${GREEN}✓ Starting frontend on port 3005${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Both servers started!${NC}"
echo ""
echo "Frontend:  http://localhost:3005"
echo "Backend:   http://localhost:8004"
echo "API Docs:  http://localhost:8004/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "✓ Servers stopped"
}

trap cleanup EXIT INT TERM
wait
