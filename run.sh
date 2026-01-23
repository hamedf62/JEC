#!/bin/bash
# 🚀 Quick Start Script for Cheque Analysis System

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    🎉 Cheque Analysis System - Quick Start Guide 🎉       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -d "app" ] || [ ! -f "app/streamlit_dashboard.py" ]; then
    echo "❌ Error: app/streamlit_dashboard.py not found!"
    echo "   Please navigate to the project directory first."
    exit 1
fi

echo "✅ Found project directory"
echo ""

# Check for uv package manager
if command -v uv &> /dev/null; then
    echo "✨ uv detected! Using uv for faster environment management..."
    if [ ! -d ".venv" ]; then
        echo "📦 Creating virtual environment with uv..."
        uv venv
    fi
    source .venv/bin/activate
    echo "📚 Syncing dependencies with uv..."
    uv pip install -r requirements.txt
else
    # Check virtual environment
    if [ ! -d ".venv" ]; then
        echo "📦 Creating virtual environment with venv..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    # Check if packages are installed
    echo "📚 Checking dependencies..."
    python -c "import streamlit" 2>/dev/null || {
        echo "📥 Installing required packages with pip..."
        pip install -q -r requirements.txt
    }
fi

echo "✅ All dependencies ready"
echo ""

# Run the app
echo "🚀 Starting Streamlit dashboard..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Dashboard will open at: http://localhost:8501"
echo "📊 Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run app/streamlit_dashboard.py
