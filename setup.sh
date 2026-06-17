#!/bin/bash
# Setup script for PriceWatchID development environment

echo "🚀 PriceWatchID Development Setup"
echo "=================================="

# Create backend venv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
pip install -r backend/requirements.txt -q

# Setup frontend
cd frontend
echo "📦 Installing frontend dependencies..."
npm install -q
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 To start development:"
echo "   Backend:  python -m uvicorn backend.main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "Or use: ./run-dev.sh"
