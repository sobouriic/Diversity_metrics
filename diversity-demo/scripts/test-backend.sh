#!/bin/bash
# Run backend tests

set -euo pipefail

cd backend
../venv/bin/python -m pytest tests/ -v --tb=short
