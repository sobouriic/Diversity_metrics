#!/bin/bash
# Setup: Install all dependencies
cd "$(dirname "$0")/.."

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  bash scripts/start-backend.sh"
echo ""
echo "To run tests:"
echo "  bash scripts/test-backend.sh"
