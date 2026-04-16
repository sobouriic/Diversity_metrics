#!/bin/bash
# Run backend tests

cd backend
pytest tests/ -v --tb=short
