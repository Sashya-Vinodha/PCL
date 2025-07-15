from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import random
import time
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Simulated vehicle data
vehicle_data = {
    "speed": 65,
    "rpm": 2400,
    "fuel_level": 75,
    "temperature": 72,
    "engine_status": "running",
    "timestamp": datetime.now().isoformat()
}

# System layers status
system_status = {
    "layer1": {"status": "active", "name": "Simulation UI"},
    "layer2": {"status": "active", "name": "Data Monitoring"},
    "layer3": {"status": "active", "name": "AI Voice Assistant"},
    "layer4": {"status": "active", "name": "Infotainment Control"},
    "layer5": {"status": "active", "name": "UI Integration"}
}

@app.route('/')
def home():
    return jsonify({
        "message": "Infotainment System - Layer 1 Backend",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/vehicle-data')
def get_vehicle_data():
    """Get current vehicle telemetry data"""
    # Simulate real-time data changes
    vehicle_data["speed"] = random.randint(50, 90)
    vehicle_data["rpm"] = random.randint(2000, 3000)
    vehicle_data["fuel_level"] = random.randint(60, 90)
    vehicle_data["temperature"] = random.randint(68, 78)
    vehicle_data["timestamp"] = datetime.now().isoformat()
    
    return jsonify(vehicle_data)

@app.route('/api/system-status')
def get_system_status():
    """Get status of all system layers"""
    return jsonify(system_status)

@app.route('/api/simulate-event', methods=['POST'])
def simulate_event():
    """Simulate various vehicle events"""
    data = request.get_json()
    event_type = data.get('event_type', 'default')
    
    events = {
        "low_fuel": {
            "message": "Low fuel warning activated",
            "fuel_level": 15,
            "warning": True
        },
        "high_speed": {
            "message": "High speed alert",
            "speed": 95,
            "warning": True
        },
        "engine_check": {
            "message": "Engine check required",
            "engine_status": "check_required",
            "warning": True
        },
        "normal": {
            "message": "All systems normal",
            "warning": False
        }
    }
    
    event = events.get(event_type, events["normal"])
    
    # Update vehicle data based on event
    if event_type == "low_fuel":
        vehicle_data["fuel_level"] = event["fuel_level"]
    elif event_type == "high_speed":
        vehicle_data["speed"] = event["speed"]
    elif event_type == "engine_check":
        vehicle_data["engine_status"] = event["engine_status"]
    
    return jsonify({
        "event": event,
        "updated_data": vehicle_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/media-control', methods=['POST'])
def media_control():
    """Handle media control commands"""
    data = request.get_json()
    action = data.get('action', 'play')
    
    media_actions = {
        "play": "Playing media",
        "pause": "Media paused",
        "next": "Next track",
        "prev": "Previous track",
        "stop": "Media stopped"
    }
    
    return jsonify({
        "action": action,
        "message": media_actions.get(action, "Unknown action"),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/navigation', methods=['POST'])
def navigation_control():
    """Handle navigation commands"""
    data = request.get_json()
    destination = data.get('destination', 'Unknown')
    
    return jsonify({
        "navigation": {
            "destination": destination,
            "status": "route_calculated",
            "eta": f"{random.randint(10, 30)} minutes",
            "distance": f"{random.randint(5, 25)} miles"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/connect-layer/<layer_id>')
def connect_to_layer(layer_id):
    """Simulate connection to other layers"""
    layer_endpoints = {
        "layer2": "http://localhost:5002/api/monitor",
        "layer3": "http://localhost:5003/api/voice-assistant",
        "layer4": "http://localhost:5004/api/control",
        "layer5": "http://localhost:5005/api/integration"
    }
    
    if layer_id in layer_endpoints:
        return jsonify({
            "connection": f"Connected to {layer_id}",
            "endpoint": layer_endpoints[layer_id],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": f"Layer {layer_id} not found",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "layer": "Layer 1 - Simulation UI Backend",
        "uptime": "Running",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Infotainment System - Layer 1 Backend")
    print("Available endpoints:")
    print("- GET  /api/vehicle-data")
    print("- GET  /api/system-status")
    print("- POST /api/simulate-event")
    print("- POST /api/media-control")
    print("- POST /api/navigation")
    print("- GET  /api/connect-layer/<layer_id>")
    print("- GET  /api/health")
    print("\nStarting server on http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
