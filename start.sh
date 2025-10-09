#!/bin/bash

# Navigate to Tenddr directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Load environment variables
if [ -f .env ]; then
    echo "🔑 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: No .env file found!"
fi

# Start backend
echo "🚀 Starting Tenddr backend..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000

