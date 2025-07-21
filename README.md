# Infotainment System Project

A comprehensive 5-layer infotainment system implementation with modern web interfaces and Flask backends.

## 🚗 Project Structure

```
PCL_CODING/infotainment-system/
├── layer1-simulation-ui/
│   ├── frontend/index.html          # Vehicle simulation interface
│   └── backend/app.py               # Simulation backend (Port 5001)
├── layer2-data-monitoring/
│   └── backend/monitor.py           # Data monitoring service (Port 5002)
├── layer3-ai-voice-assistant/
│   └── backend/voice_assistant.py   # AI voice control (Port 5003)
├── layer4-infotainment-control/
│   ├── frontend/index.html          # Infotainment control center
│   └── backend/control.py           # Control backend (Port 5004)
├── layer5-ui-integration/
│   └── frontend/index.html          # Unified dashboard interface
├── requirements.txt                 # Python dependencies
├── package.json                     # Project configuration
├── start_system.sh                  # System startup script
└── README.md                        # Detailed documentation
```

## 🚀 Quick Start

1. **Navigate to the project directory:**
   ```bash
   cd PCL_CODING/infotainment-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start all services:**
   ```bash
   ./start_system.sh
   ```

4. **Access the interfaces:**
   - **Layer 1 Simulation**: Open `layer1-simulation-ui/frontend/index.html`
   - **Layer 4 Control Center**: Open `layer4-infotainment-control/frontend/index.html`
   - **Layer 5 Unified Dashboard**: Open `layer5-ui-integration/frontend/index.html`

## 📋 System Features

### 🎵 Media Control
- Play/pause/skip track controls
- Volume adjustment
- Source selection (Bluetooth, Radio, USB, Spotify)
- Real-time now playing information

### 🌡️ Climate Control
- Temperature adjustment
- Air conditioning and heater controls
- Fan speed management
- Defrost and air recirculation

### 🗺️ Navigation System
- Destination input and routing
- Quick navigation presets
- Nearby location search
- Real-time ETA and distance

### 🚗 Vehicle Monitoring
- Live speed, RPM, fuel, and temperature data
- Vehicle diagnostics and maintenance alerts
- Emergency services integration
- System health monitoring

### 🎙️ Voice Assistant
- Natural language voice commands
- Hands-free operation
- Command recognition and feedback
- Integration with all system layers

### 📊 Data Monitoring
- Real-time system performance metrics
- Alert management and logging
- CPU, memory, and network monitoring
- Event tracking and analysis

## 🔧 Technical Stack

- **Backend**: Python Flask with CORS support
- **Frontend**: Modern HTML5, CSS3, JavaScript
- **Monitoring**: psutil for system metrics
- **Voice**: SpeechRecognition and pyttsx3 (optional)
- **Communication**: RESTful APIs between layers

## 📖 Documentation

For detailed installation instructions, API documentation, and troubleshooting, see the complete README in the `infotainment-system/` directory.

