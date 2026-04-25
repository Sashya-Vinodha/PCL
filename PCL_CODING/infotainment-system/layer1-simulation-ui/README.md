# Layer 1 — Vehicle Simulation Control Board

## Quick Start

### 1. Start the Backend
```bash
cd backend
python3 app.py
```
Backend runs on: `http://localhost:5001`

### 2. Start the Frontend
```bash
cd frontend
python3 -m http.server 8080
```
Frontend accessible at: `http://localhost:8080`

### 3. Open in Browser
Navigate to: `http://localhost:8080`

---

## What is Layer 1?

Layer 1 is the **Vehicle Simulation Control Board** - a manual input panel for system-triggered vehicle data.

### Purpose
- Provides manual controls for all vehicle sensor inputs
- Simulates car telemetry data (speed, RPM, fuel, temperature, etc.)
- Projects data to the infotainment system on demand
- **Excludes user interaction controls** (those belong to Layer 4)

---

## Features

### System-Triggered Controls
- ✅ **Speed** (0-200 km/h)
- ✅ **RPM** (0-8000)
- ✅ **Fuel Level** (0-100%)
- ✅ **Engine Temperature** (60-120°C)
- ✅ **Transmission Gear** (P, R, N, D, S, M)
- ✅ **Drive Mode** (ECO, COMFORT, SPORT)
- ✅ **Battery Level** (0-100%)
- ✅ **Odometer** (0-999,999 km)

### User Interface
- Modern glass morphism design
- Inter font family
- Cyan/blue color scheme
- Dual input (sliders + number fields)
- Real-time synchronization
- Visual feedback on projection

---

## How to Use

1. **Adjust Vehicle Parameters**
   - Use sliders or type values directly
   - All inputs have validation and limits
   - Values update in real-time

2. **Project to Infotainment**
   - Click "📡 Project to Infotainment System"
   - Data is sent to backend
   - Success message appears: "✅ Projected Successfully!"
   - View transmitted data in preview panel

3. **Backend Processing**
   - Backend receives data via POST request
   - Logs formatted output to console
   - Updates vehicle_data object
   - Returns success confirmation

---

## API Endpoints

### `GET /api/vehicle-data`
Get current vehicle data (simulated)

### `POST /api/vehicle-data`
Receive simulation data from Layer 1 UI

**Request:**
```json
{
  "speed": 75,
  "rpm": 2500,
  "fuel_level": 68,
  "temperature": 92,
  "gear": "D",
  "drive_mode": "SPORT",
  "battery": 85,
  "odometer": 12543,
  "timestamp": "2025-10-27T18:30:45.123Z",
  "source": "layer1_simulation_ui"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Simulation data received and processed",
  "data_received": { ... },
  "updated_vehicle_data": { ... },
  "timestamp": "2025-10-27T18:30:45.456Z"
}
```

---

## Testing

### Manual Test
1. Start backend and frontend
2. Open browser to `http://localhost:8080`
3. Adjust controls
4. Click "Project to Infotainment"
5. Check console for logged data

### Automated Test
```bash
python3 test_projection.py
```

---

## Architecture

```
┌─────────────────────────────────┐
│   Layer 1 Frontend              │
│   (Manual Control Board)        │
│                                 │
│   - Speed/RPM/Fuel sliders     │
│   - Gear/Mode selectors        │
│   - Project button             │
└────────────┬────────────────────┘
             │
             │ POST /api/vehicle-data
             ▼
┌─────────────────────────────────┐
│   Layer 1 Backend               │
│   (Flask API - Port 5001)       │
│                                 │
│   - Receive simulation data    │
│   - Validate & log payload     │
│   - Forward to Layer 2         │
└─────────────────────────────────┘
```

---

## File Structure

```
layer1-simulation-ui/
├── frontend/
│   └── index.html          # UI control board
├── backend/
│   └── app.py              # Flask API server
├── test_projection.py      # Test script
└── README.md               # This file
```

---

## Next Steps

1. **Layer 2 Integration**
   - Implement data forwarding to Layer 2 bridge
   - Add WebSocket for real-time streaming (optional)

2. **Enhanced Features**
   - Weather simulation controls
   - Safety metrics inputs
   - Preset scenarios

3. **Testing**
   - Unit tests
   - Integration tests
   - E2E tests

---

## Notes

- ⚠️ Backend must be running for projection to work
- ⚠️ CORS is enabled for development
- ⚠️ This is a simulation layer - real vehicle data would come from actual sensors

---

## Support

For detailed documentation, see: `LAYER1_SIMULATION_IMPLEMENTATION.md`

---

**Status:** ✅ Production Ready
**Last Updated:** October 27, 2025
