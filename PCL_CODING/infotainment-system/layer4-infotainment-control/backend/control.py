from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
from datetime import datetime
import threading
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Infotainment system state
infotainment_state = {
    "media": {
        "is_playing": False,
        "current_song": "Summer Breeze",
        "current_artist": "Smooth Jazz Collection",
        "volume": 65,
        "progress": 35,
        "source": "bluetooth",
        "playlist": [
            {"title": "Summer Breeze", "artist": "Smooth Jazz Collection", "duration": 225},
            {"title": "Highway Dreams", "artist": "Road Trip Classics", "duration": 198},
            {"title": "Digital Sunset", "artist": "Electronic Vibes", "duration": 267},
            {"title": "City Lights", "artist": "Urban Sounds", "duration": 180}
        ],
        "current_track_index": 0
    },
    "climate": {
        "temperature": 72,
        "ac_enabled": False,
        "heater_enabled": False,
        "fan_speed": "medium",
        "defrost_enabled": False,
        "recirculate_enabled": False,
        "auto_mode": True
    },
    "navigation": {
        "current_destination": "",
        "is_navigating": False,
        "eta": "",
        "distance_remaining": "",
        "current_location": "Downtown",
        "route_active": False
    },
    "vehicle": {
        "speed": 65,
        "fuel_level": 75,
        "engine_rpm": 2400,
        "engine_temperature": 195,
        "engine_status": "normal",
        "maintenance_due": False,
        "warnings": []
    },
    "settings": {
        "theme": "dark",
        "language": "en",
        "units": "imperial",
        "auto_brightness": True,
        "voice_control_enabled": True
    },
    "timestamp": datetime.now().isoformat()
}

class InfotainmentController:
    def __init__(self):
        self.update_thread = None
        self.running = False
    
    def start_updates(self):
        """Start background updates"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            logger.info("Infotainment controller started")
    
    def stop_updates(self):
        """Stop background updates"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Infotainment controller stopped")
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self._update_media_progress()
                self._update_vehicle_data()
                infotainment_state["timestamp"] = datetime.now().isoformat()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
    
    def _update_media_progress(self):
        """Update media playback progress"""
        if infotainment_state["media"]["is_playing"]:
            current_track = infotainment_state["media"]["playlist"][infotainment_state["media"]["current_track_index"]]
            progress = infotainment_state["media"]["progress"]
            
            # Increment progress (simulating 1 second)
            if progress < 100:
                infotainment_state["media"]["progress"] = progress + (100 / current_track["duration"])
            else:
                # Auto-advance to next track
                self._next_track()
    
    def _update_vehicle_data(self):
        """Simulate vehicle data updates"""
        import random
        
        # Simulate slight variations in vehicle data
        infotainment_state["vehicle"]["speed"] = max(0, infotainment_state["vehicle"]["speed"] + random.randint(-2, 2))
        infotainment_state["vehicle"]["engine_rpm"] = max(800, infotainment_state["vehicle"]["engine_rpm"] + random.randint(-50, 50))
        infotainment_state["vehicle"]["fuel_level"] = max(0, infotainment_state["vehicle"]["fuel_level"] - random.uniform(0, 0.01))
    
    def _next_track(self):
        """Advance to next track"""
        playlist = infotainment_state["media"]["playlist"]
        current_index = infotainment_state["media"]["current_track_index"]
        
        next_index = (current_index + 1) % len(playlist)
        infotainment_state["media"]["current_track_index"] = next_index
        infotainment_state["media"]["current_song"] = playlist[next_index]["title"]
        infotainment_state["media"]["current_artist"] = playlist[next_index]["artist"]
        infotainment_state["media"]["progress"] = 0
    
    def _previous_track(self):
        """Go to previous track"""
        playlist = infotainment_state["media"]["playlist"]
        current_index = infotainment_state["media"]["current_track_index"]
        
        prev_index = (current_index - 1) % len(playlist)
        infotainment_state["media"]["current_track_index"] = prev_index
        infotainment_state["media"]["current_song"] = playlist[prev_index]["title"]
        infotainment_state["media"]["current_artist"] = playlist[prev_index]["artist"]
        infotainment_state["media"]["progress"] = 0

# Initialize controller
controller = InfotainmentController()

@app.route('/')
def home():
    return jsonify({
        "message": "Infotainment System - Layer 4 Control Backend",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control')
def get_system_state():
    """Get complete infotainment system state"""
    return jsonify(infotainment_state)

# Media Control Endpoints
@app.route('/api/media/play', methods=['POST'])
def media_play():
    """Play/pause media"""
    infotainment_state["media"]["is_playing"] = not infotainment_state["media"]["is_playing"]
    action = "playing" if infotainment_state["media"]["is_playing"] else "paused"
    
    return jsonify({
        "action": action,
        "is_playing": infotainment_state["media"]["is_playing"],
        "current_song": infotainment_state["media"]["current_song"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/media/next', methods=['POST'])
def media_next():
    """Next track"""
    controller._next_track()
    return jsonify({
        "action": "next_track",
        "current_song": infotainment_state["media"]["current_song"],
        "current_artist": infotainment_state["media"]["current_artist"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/media/previous', methods=['POST'])
def media_previous():
    """Previous track"""
    controller._previous_track()
    return jsonify({
        "action": "previous_track",
        "current_song": infotainment_state["media"]["current_song"],
        "current_artist": infotainment_state["media"]["current_artist"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/media/volume', methods=['POST'])
def set_volume():
    """Set media volume"""
    data = request.get_json()
    volume = data.get('volume', 50)
    volume = max(0, min(100, volume))  # Clamp between 0-100
    
    infotainment_state["media"]["volume"] = volume
    
    return jsonify({
        "action": "volume_changed",
        "volume": volume,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/media/source', methods=['POST'])
def set_media_source():
    """Change media source"""
    data = request.get_json()
    source = data.get('source', 'bluetooth')
    
    valid_sources = ['bluetooth', 'radio', 'usb', 'spotify', 'aux']
    if source in valid_sources:
        infotainment_state["media"]["source"] = source
        return jsonify({
            "action": "source_changed",
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "Invalid media source",
            "valid_sources": valid_sources,
            "timestamp": datetime.now().isoformat()
        }), 400

# Climate Control Endpoints
@app.route('/api/climate/temperature', methods=['POST'])
def set_temperature():
    """Set cabin temperature"""
    data = request.get_json()
    temp = data.get('temperature', 72)
    temp = max(60, min(85, temp))  # Clamp between 60-85°F
    
    infotainment_state["climate"]["temperature"] = temp
    
    return jsonify({
        "action": "temperature_changed",
        "temperature": temp,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/climate/ac', methods=['POST'])
def toggle_ac():
    """Toggle air conditioning"""
    infotainment_state["climate"]["ac_enabled"] = not infotainment_state["climate"]["ac_enabled"]
    
    # If AC is turned on, turn off heater
    if infotainment_state["climate"]["ac_enabled"]:
        infotainment_state["climate"]["heater_enabled"] = False
    
    return jsonify({
        "action": "ac_toggled",
        "ac_enabled": infotainment_state["climate"]["ac_enabled"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/climate/heater', methods=['POST'])
def toggle_heater():
    """Toggle heater"""
    infotainment_state["climate"]["heater_enabled"] = not infotainment_state["climate"]["heater_enabled"]
    
    # If heater is turned on, turn off AC
    if infotainment_state["climate"]["heater_enabled"]:
        infotainment_state["climate"]["ac_enabled"] = False
    
    return jsonify({
        "action": "heater_toggled",
        "heater_enabled": infotainment_state["climate"]["heater_enabled"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/climate/fan', methods=['POST'])
def set_fan_speed():
    """Set fan speed"""
    data = request.get_json()
    speed = data.get('speed', 'medium')
    
    valid_speeds = ['low', 'medium', 'high', 'auto']
    if speed in valid_speeds:
        infotainment_state["climate"]["fan_speed"] = speed
        return jsonify({
            "action": "fan_speed_changed",
            "fan_speed": speed,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "Invalid fan speed",
            "valid_speeds": valid_speeds,
            "timestamp": datetime.now().isoformat()
        }), 400

# Navigation Endpoints
@app.route('/api/navigation/destination', methods=['POST'])
def set_destination():
    """Set navigation destination"""
    data = request.get_json()
    destination = data.get('destination', '')
    
    if destination:
        infotainment_state["navigation"]["current_destination"] = destination
        infotainment_state["navigation"]["is_navigating"] = True
        infotainment_state["navigation"]["route_active"] = True
        infotainment_state["navigation"]["eta"] = "15 minutes"
        infotainment_state["navigation"]["distance_remaining"] = "8.5 miles"
        
        return jsonify({
            "action": "destination_set",
            "destination": destination,
            "eta": infotainment_state["navigation"]["eta"],
            "distance": infotainment_state["navigation"]["distance_remaining"],
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "Destination cannot be empty",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/navigation/stop', methods=['POST'])
def stop_navigation():
    """Stop current navigation"""
    infotainment_state["navigation"]["is_navigating"] = False
    infotainment_state["navigation"]["route_active"] = False
    infotainment_state["navigation"]["current_destination"] = ""
    
    return jsonify({
        "action": "navigation_stopped",
        "timestamp": datetime.now().isoformat()
    })

# Vehicle Control Endpoints
@app.route('/api/vehicle/diagnostics', methods=['POST'])
def run_diagnostics():
    """Run vehicle diagnostics"""
    # Simulate diagnostic check
    import random
    
    diagnostic_results = {
        "engine": "OK",
        "transmission": "OK",
        "brakes": "OK",
        "electrical": "OK",
        "emissions": "OK"
    }
    
    # Randomly add a warning
    if random.random() < 0.1:  # 10% chance
        diagnostic_results["maintenance"] = "Service due in 500 miles"
    
    return jsonify({
        "action": "diagnostics_completed",
        "results": diagnostic_results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/vehicle/emergency', methods=['POST'])
def emergency_call():
    """Initiate emergency call"""
    infotainment_state["vehicle"]["warnings"].append({
        "type": "emergency",
        "message": "Emergency call initiated",
        "timestamp": datetime.now().isoformat()
    })
    
    return jsonify({
        "action": "emergency_call_initiated",
        "message": "Emergency services contacted",
        "timestamp": datetime.now().isoformat()
    })

# Settings Endpoints
@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    """Get or update system settings"""
    if request.method == 'GET':
        return jsonify({
            "settings": infotainment_state["settings"],
            "timestamp": datetime.now().isoformat()
        })
    else:
        data = request.get_json()
        infotainment_state["settings"].update(data)
        
        return jsonify({
            "action": "settings_updated",
            "settings": infotainment_state["settings"],
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "layer": "Layer 4 - Infotainment Control",
        "controller_running": controller.running,
        "media_playing": infotainment_state["media"]["is_playing"],
        "navigation_active": infotainment_state["navigation"]["route_active"],
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Infotainment System - Layer 4 Control Backend")
    print("Available endpoints:")
    print("- GET  /api/control")
    print("- POST /api/media/play")
    print("- POST /api/media/next")
    print("- POST /api/media/previous")
    print("- POST /api/media/volume")
    print("- POST /api/media/source")
    print("- POST /api/climate/temperature")
    print("- POST /api/climate/ac")
    print("- POST /api/climate/heater")
    print("- POST /api/climate/fan")
    print("- POST /api/navigation/destination")
    print("- POST /api/navigation/stop")
    print("- POST /api/vehicle/diagnostics")
    print("- POST /api/vehicle/emergency")
    print("- GET/POST /api/settings")
    print("- GET  /api/health")
    print("\nStarting server on http://localhost:5004")
    
    # Start background updates
    controller.start_updates()
    
    app.run(debug=True, host='0.0.0.0', port=5004)
