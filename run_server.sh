#!/bin/bash
# Quick start script for ACP Demo API

echo "Starting ACP Demo API Server..."
echo "API will be available at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

