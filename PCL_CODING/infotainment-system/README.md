# Infotainment System

A comprehensive 5-layer infotainment system built with Flask backends and modern web frontends.

## Project Structure

```
infotainment-system/
├── layer1-simulation-ui/
│   ├── frontend/index.html          # Simulation UI Interface
│   └── backend/app.py               # Flask backend for simulation
├── layer2-data-monitoring/
│   └── backend/monitor.py           # Data monitoring and analytics
├── layer3-ai-voice-assistant/
│   └── backend/voice_assistant.py   # AI voice control system
├── layer4-infotainment-control/
│   ├── frontend/index.html          # Infotainment control interface
│   └── backend/control.py           # Infotainment control backend
├── layer5-ui-integration/
│   └── frontend/index.html          # Unified UI integration
└── requirements.txt                 # Python dependencies
```

## System Layers

### Layer 1: Simulation UI
- **Frontend**: Modern web interface for vehicle simulation
- **Backend**: Flask API providing vehicle data simulation
- **Port**: 5001
- **Features**: Real-time vehicle data, media controls, navigation

### Layer 2: Data Monitoring
- **Backend**: System and vehicle monitoring service
- **Port**: 5002
- **Features**: CPU/memory monitoring, vehicle metrics, alerts, logging

### Layer 3: AI Voice Assistant
- **Backend**: Voice recognition and command processing
- **Port**: 5003
- **Features**: Speech recognition, voice commands, text-to-speech

### Layer 4: Infotainment Control
- **Frontend**: Rich infotainment control center
- **Backend**: Complete infotainment system control
- **Port**: 5004
- **Features**: Media control, climate control, navigation, vehicle status

### Layer 5: UI Integration
- **Frontend**: Unified interface integrating all layers
- **Features**: Dashboard view, system overview, layer management

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd infotainment-system
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install additional voice assistant dependencies (optional)**
```bash
# For macOS
brew install portaudio
pip install pyaudio

# For Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# For Windows
pip install pyaudio
```

## Running the System

### Start Individual Layers

**Layer 1 - Simulation UI:**
```bash
cd layer1-simulation-ui/backend
python app.py
```
Then open `layer1-simulation-ui/frontend/index.html` in your browser.

**Layer 2 - Data Monitoring:**
```bash
cd layer2-data-monitoring/backend
python monitor.py
```

**Layer 3 - Voice Assistant:**
```bash
cd layer3-ai-voice-assistant/backend
python voice_assistant.py
```

**Layer 4 - Infotainment Control:**
```bash
cd layer4-infotainment-control/backend
python control.py
```
Then open `layer4-infotainment-control/frontend/index.html` in your browser.

**Layer 5 - UI Integration:**
Open `layer5-ui-integration/frontend/index.html` in your browser.

### Start All Layers at Once

You can create a script to start all backend services:

```bash
#!/bin/bash
# Start all backend services
cd layer1-simulation-ui/backend && python app.py &
cd layer2-data-monitoring/backend && python monitor.py &
cd layer3-ai-voice-assistant/backend && python voice_assistant.py &
cd layer4-infotainment-control/backend && python control.py &
wait
```

## API Endpoints

### Layer 1 (Port 5001)
- `GET /api/vehicle-data` - Get vehicle telemetry
- `GET /api/system-status` - Get system layer status
- `POST /api/simulate-event` - Simulate vehicle events
- `POST /api/media-control` - Control media playback
- `POST /api/navigation` - Handle navigation commands

### Layer 2 (Port 5002)
- `GET /api/monitor` - Get all monitoring data
- `GET /api/system-metrics` - Get system performance metrics
- `GET /api/vehicle-metrics` - Get vehicle metrics
- `GET /api/alerts` - Get recent alerts
- `GET /api/logs` - Get system logs

### Layer 3 (Port 5003)
- `GET /api/voice-assistant` - Get voice assistant status
- `POST /api/start-listening` - Start voice recognition
- `POST /api/stop-listening` - Stop voice recognition
- `POST /api/speak` - Text-to-speech
- `POST /api/process-command` - Process text commands

### Layer 4 (Port 5004)
- `GET /api/control` - Get complete system state
- `POST /api/media/*` - Media control endpoints
- `POST /api/climate/*` - Climate control endpoints
- `POST /api/navigation/*` - Navigation endpoints
- `POST /api/vehicle/*` - Vehicle control endpoints

## Features

### Media Control
- Play/pause/next/previous track controls
- Volume control
- Source selection (Bluetooth, Radio, USB, Spotify)
- Now playing display

### Climate Control
- Temperature adjustment
- Air conditioning and heater controls
- Fan speed control
- Defrost and recirculation

### Navigation
- Destination input
- Quick navigation to home/work
- Nearby location search
- Route display with ETA

### Vehicle Monitoring
- Real-time speed, RPM, fuel level, temperature
- Vehicle diagnostics
- Maintenance scheduling
- Emergency services

### Voice Assistant
- Voice command recognition
- Natural language processing
- Hands-free operation
- Command feedback

### Data Monitoring
- System performance monitoring
- Alert management
- Event logging
- Real-time metrics

## Browser Compatibility

The frontend interfaces are designed to work with modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Features
1. Implement backend API endpoints in the appropriate layer
2. Update frontend interfaces to use new endpoints
3. Add error handling and validation
4. Update documentation

### Testing
- Test individual layers independently
- Verify inter-layer communication
- Test frontend-backend integration
- Validate error handling

## Troubleshooting

### Common Issues

**Voice Assistant Not Working:**
- Ensure microphone permissions are granted
- Install pyaudio dependencies
- Check microphone hardware

**Port Conflicts:**
- Ensure ports 5001-5004 are available
- Modify port numbers in backend files if needed

**Frontend Not Loading:**
- Ensure backends are running
- Check browser console for errors
- Verify CORS settings

**Dependencies Issues:**
- Use virtual environment
- Update pip: `pip install --upgrade pip`
- Install dependencies individually if needed

## License

This project is for educational and demonstration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
