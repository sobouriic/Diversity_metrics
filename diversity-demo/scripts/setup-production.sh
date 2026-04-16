
set -e

if [ "$EUID" -ne 0 ]; then 
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

PUBLIC_HOST="${1:-localhost}"
SERVICE_USER="${2:-www-data}"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Production Systemd Services${NC}"
echo -e "Public Host: ${PUBLIC_HOST}"
echo -e "App Directory: ${APP_DIR}"
echo -e "Service User: ${SERVICE_USER}"
echo ""

# Create backend service file
echo -e "${BLUE}📝 Creating backend systemd service...${NC}"
cat > /etc/systemd/system/diversity-backend.service << EOF
[Unit]
Description=Diversity Metrics Backend API
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=${APP_DIR}/venv/bin/python -m uvicorn backend.api:app --host 0.0.0.0 --port 8005 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Backend service created${NC}"

# Create frontend service file
echo -e "${BLUE}📝 Creating frontend build and server systemd service...${NC}"
cat > /etc/systemd/system/diversity-frontend.service << EOF
[Unit]
Description=Diversity Metrics Frontend
After=network.target
PartOf=diversity-metrics.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${APP_DIR}/frontend
ExecStart=/usr/bin/npx http-server ./dist -p 3008 -c-1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Frontend service created${NC}"

# Create target for both services
echo -e "${BLUE}📝 Creating service group target...${NC}"
cat > /etc/systemd/system/diversity-metrics.target << EOF
[Unit]
Description=Diversity Metrics Complete System
Requires=diversity-backend.service diversity-frontend.service
After=network.target

[Install]
WantedBy=multi-user.target
EOF
echo -e "${GREEN}✓ Service target created${NC}"

# Setup the application
echo ""
echo -e "${BLUE}🔨 Building frontend...${NC}"
cd "${APP_DIR}/frontend"
VITE_API_BASE="http://${PUBLIC_HOST}:8005/api" npm run build
cd "${APP_DIR}"
echo -e "${GREEN}✓ Frontend built${NC}"

# Install frontend server dependencies
echo -e "${BLUE}📦 Installing frontend server dependencies...${NC}"
npm install -g http-server
echo -e "${GREEN}✓ http-server installed${NC}"

# Ensure proper ownership
echo -e "${BLUE}🔐 Setting proper permissions...${NC}"
chown -R ${SERVICE_USER}:${SERVICE_USER} "${APP_DIR}"
chmod 755 "${APP_DIR}"
echo -e "${GREEN}✓ Permissions set${NC}"

# Reload systemd and enable services
echo ""
echo -e "${BLUE}🚀 Enabling systemd services...${NC}"
systemctl daemon-reload
systemctl enable diversity-backend.service
systemctl enable diversity-frontend.service
systemctl enable diversity-metrics.target
echo -e "${GREEN}✓ Services enabled${NC}"

echo ""
echo -e "${GREEN}✅ Production setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Available Commands:${NC}"
echo "  Start all services:     sudo systemctl start diversity-metrics.target"
echo "  Stop all services:      sudo systemctl stop diversity-metrics.target"
echo "  Restart all services:   sudo systemctl restart diversity-metrics.target"
echo "  Status:                 sudo systemctl status diversity-metrics.target"
echo "  View backend logs:      sudo journalctl -u diversity-backend.service -f"
echo "  View frontend logs:     sudo journalctl -u diversity-frontend.service -f"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "  1. Review the services: systemctl status diversity-metrics.target"
echo "  2. Start services: sudo systemctl start diversity-metrics.target"
echo "  3. Access the app at: http://${PUBLIC_HOST}:3008"
echo "  4. (Optional) Set up Nginx as reverse proxy (see SERVER_DEPLOYMENT.md)"
echo ""
