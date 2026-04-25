#!/bin/bash

# Infotainment System Startup Script
# This script starts all backend services for the infotainment system

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PYTHON_BIN="/usr/local/bin/python3.11"
cd "$SCRIPT_DIR"

echo "🚗 Starting Infotainment System - All Layers"
echo "=============================================="
echo "Working from: $SCRIPT_DIR"

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down all services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

echo "📊 Starting Layer 1 - Simulation UI Backend (Port 5001)..."
cd layer1-simulation-ui/backend
"$PYTHON_BIN" app.py &
LAYER1_PID=$!
cd ../..

echo "📈 Starting Layer 2 - Data Monitoring Backend (Port 5002)..."
cd layer2-data-monitoring/backend
"$PYTHON_BIN" monitor.py &
LAYER2_PID=$!
cd ../..

echo "🎙️ Starting Layer 3 - Voice Assistant Backend (Port 5003)..."
cd layer3-ai-voice-assistant/backend
"$PYTHON_BIN" voice_assistant.py &
LAYER3_PID=$!
cd ../..

echo "🎛️ Starting Layer 4 - Infotainment Control Backend (Port 5004)..."
cd layer4-infotainment-control/backend
"$PYTHON_BIN" control.py &
LAYER4_PID=$!
cd ../..

echo ""
echo "✅ All backend services started!"
echo ""
echo "🌐 Frontend URLs:"
echo "   Layer 1 (Simulation): file://$(pwd)/layer1-simulation-ui/frontend/index.html"
echo "   Layer 4 (Control):    file://$(pwd)/layer4-infotainment-control/frontend/index.html"
echo "   Layer 5 (Integration): file://$(pwd)/layer5-ui-integration/frontend/index.html"
echo ""
echo "🔗 Backend APIs:"
echo "   Layer 1: http://localhost:5001"
echo "   Layer 2: http://localhost:5002"
echo "   Layer 3: http://localhost:5003"
echo "   Layer 4: http://localhost:5004"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for all background processes
wait
