#!/bin/bash

BASE="/Users/sashya/Documents/PCL/PCL_IMPLEMENTATION/PCL_CODING/infotainment-system"
VENV="/Users/sashya/Documents/PCL/PCL_IMPLEMENTATION/PCL_CODING/.venv/bin/activate"

tmux new-session -d -s infotainment

# Layer 1 backend
tmux send-keys -t infotainment "cd $BASE/layer1-simulation-ui/backend && source $VENV && python app.py" C-m

# Split + Layer 2
tmux split-window -h -t infotainment
tmux send-keys -t infotainment "cd $BASE/layer2-data-monitoring/backend && source $VENV && python monitor.py" C-m

# Split + Layer 3
tmux split-window -v -t infotainment
tmux send-keys -t infotainment "cd $BASE/layer3-ai-voice-assistant/backend && source $VENV && python voice_assistant.py" C-m

# New window for frontends
tmux new-window -t infotainment

# Layer 1 frontend
tmux send-keys -t infotainment "cd $BASE/layer1-simulation-ui/frontend && python -m http.server 8080" C-m

# Split + Layer 5 frontend
tmux split-window -h -t infotainment
tmux send-keys -t infotainment "cd $BASE/layer5-ui-integration/frontend && python -m http.server 8081" C-m

tmux attach-session -t infotainment