from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import requests
import uvicorn

from app.models import VehicleState
from app.ai_logic import process_ai_triggers # The import must match the filename

app = FastAPI(title="AI Infotainment Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_state = VehicleState()
dashboard_clients: List[WebSocket] = []
last_weather_coords = (0.0, 0.0)

@app.get("/")
def read_root():
    return {"status": "Online", "message": "Backend is running"}

def fetch_live_weather(lat, lon):
    """Fetches real-time weather data for safety[cite: 31, 61]."""
    try:
        # Phase 3: Fetching meteorological data [cite: 112, 114]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=3).json()
        temp = response["current_weather"]["temperature"]
        weather_code = response["current_weather"]["weathercode"]
        
        # Monitor condition changes (Layer 2) [cite: 168]
        is_raining = weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]
        desc = "Rainy conditions detected." if is_raining else "Clear skies. Optimal driving."
        return temp, is_raining, desc
    except Exception as e:
        return 26.0, False, "Weather Service Offline"

@app.post("/api/update-state")
async def update_vehicle_state(new_state: VehicleState):
    global current_state, last_weather_coords
    
    # Check for significant location change to refresh weather [cite: 200]
    coord_diff = abs(last_weather_coords[0] - new_state.latitude) + abs(last_weather_coords[1] - new_state.longitude)
    
    if coord_diff > 0.01:
        temp, is_raining, desc = fetch_live_weather(new_state.latitude, new_state.longitude)
        new_state.temperature = temp
        new_state.is_raining = is_raining
        new_state.weather_desc = desc
        last_weather_coords = (new_state.latitude, new_state.longitude)
    else:
        new_state.temperature = current_state.temperature
        new_state.weather_desc = current_state.weather_desc

    current_state = new_state
    
    # Layer 3: AI logic triggered by data monitoring [cite: 162, 216]
    process_ai_triggers(current_state)

    await broadcast_to_dashboards()
    return {"status": "success"}

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """Real-time data streaming for the UI[cite: 158]."""
    await websocket.accept()
    dashboard_clients.append(websocket)
    await websocket.send_text(json.dumps(current_state.dict()))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_clients.remove(websocket)

async def broadcast_to_dashboards():
    if not dashboard_clients: return
    message = json.dumps(current_state.dict())
    for client in dashboard_clients:
        try: await client.send_text(message)
        except: pass

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)