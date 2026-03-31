#!/bin/bash

# VLM-ARB Interactive UI Launcher
# Starts the Streamlit dashboard for evaluation demo

echo "🚀 Starting VLM-ARB Interactive Dashboard..."
echo ""

# Check if we're in the right directory
if [ ! -f "ui/app.py" ]; then
    echo "❌ Error: ui/app.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "📦 Activating Python environment..."
    source venv/bin/activate
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    pip install streamlit matplotlib pandas
fi

# Launch Streamlit
echo "🌐 Opening dashboard at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run ui/app.py
