#!/bin/bash

# PineOpt Development Server Startup Script
echo "🚀 Starting PineOpt Development Environment"
echo "========================================="

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Python virtual environment not found. Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run: npm install"
    exit 1
fi

echo "📦 Starting Flask API server (port 5001)..."
source .venv/bin/activate && cd api && python server.py &
API_PID=$!

echo "⚛️  Starting React frontend (port 3000)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development environment started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap "echo '🛑 Stopping servers...'; kill $API_PID $FRONTEND_PID; exit 0" INT
wait