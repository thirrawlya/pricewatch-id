#!/bin/bash
# Development runner script

echo "🚀 Starting PriceWatchID Development Server"
echo "==========================================="

# Check if backend and frontend are running in parallel
# This requires either tmux or running in separate terminals

# Activate venv
source venv/bin/activate

# Start backend in background
echo "Starting backend API on port 8000..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo ""
echo "Starting frontend dev server on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "✅ Both servers running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Handle cleanup
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# Wait for background jobs
wait
