#!/bin/bash

# Face Tracking System - Development Startup Script

echo "🚀 Starting Face Tracking System Backend..."

# Set environment variables for development
export DEBUG=true
export RELOAD=true
export LOG_LEVEL=debug
export ENABLE_DOCS=true

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Initialize database if needed
echo "🗄️  Checking database initialization..."
python scripts/init_database.py

# Start the application
echo "🚀 Starting FastAPI server..."
echo "📡 Server will be available at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python run.py