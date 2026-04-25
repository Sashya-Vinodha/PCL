
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import random
import time
import requests
from datetime import datetime, timedelta
import json
import threading

app = Flask(__name__)
CORS(app)

# Emergency contacts storage
emergency_contacts = []

# New endpoint to set emergency contacts
@app.route('/api/set-emergency-contacts', methods=['POST'])
def set_contacts():
    data = request.get_json()
    contacts = data.get("contacts", [])
    valid_contacts = [c for c in contacts if isinstance(c, str) and len(c) == 10 and c.isdigit()]
    if not valid_contacts:
        return jsonify({"status": "error", "message": "Invalid contacts"}), 400
    global emergency_contacts
    emergency_contacts = valid_contacts
    return jsonify({"status": "success", "contacts": emergency_contacts})

FAST2SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"
FAST2SMS_API_KEY = "YOUR_API_KEY"
FAST2SMS_PHONE_NUMBER = "YOUR_PHONE_NUMBER"

SPEED_ALERT_THRESHOLD = 90
TEMP_ALERT_THRESHOLD = 95
WEATHER_ALERT_CONDITIONS = {"rain", "fog", "snow", "storm"}

total_distance = 100
distance_to_destination = total_distance
distance_to_weather_event = 60  # Start > 30
app = Flask(__name__)
CORS(app)

# Enhanced vehicle data with comprehensive metrics
vehicle_data = {
    "speed": 65,
    "rpm": 2400,
    "fuel_level": 75,
    "temperature": 72,
    "engine_status": "running",
    "timestamp": datetime.now().isoformat(),
    # Enhanced metrics for AI triggers
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 52,
        "heading": 45  # degrees
    },
    "safety_metrics": {
        "lane_position": "center",  # center, left, right
        "following_distance": 3.2,  # seconds
        "brake_pressure": 0,  # 0-100%
        "acceleration": 0.1,  # m/s²
        "steering_angle": 0  # degrees
    }
}

# Enhanced weather data for AI warnings and UI visuals
weather_data = {
    "condition": "clear",  # clear, rain, fog, snow, storm
    "temperature": 72,
    "humidity": 45,
    "wind_speed": 8.5,  # mph - for AI speed warnings
    "wind_direction": 180,  # degrees
    "visibility": 10.0,  # miles - for fog warnings
    "precipitation": 0,  # mm/hr
    "uv_index": 5,
    "atmospheric_pressure": 1013.25,  # hPa
    "timestamp": datetime.now().isoformat(),
    # Enhanced for UI animations
    "rain_intensity": 0,  # 0-100 for rain streak animation
    "fog_density": 0,  # 0-100 for fog overlay
    "snow_rate": 0,  # 0-100 for snow particle effects
    "storm_activity": False  # for lightning effects
}

# Driver behavior simulation for AI analysis
driver_behavior = {
    "alertness_status": "alert",  # alert, drowsy, distracted, impaired
    "eye_tracking": {
        "gaze_direction": "road",  # road, dashboard, mirror, phone
        "blink_rate": 15,  # blinks per minute
        "pupil_dilation": 3.5  # mm
    },
    "driving_patterns": {
        "lane_changes": 0,  # count in last 10 minutes
        "hard_braking_events": 0,
        "rapid_acceleration": 0,
        "speed_variance": 2.1,  # mph standard deviation
        "steering_smoothness": 85  # 0-100 score
    },
    "biometric_data": {
        "heart_rate": 72,  # bpm
        "stress_level": 20,  # 0-100
        "fatigue_score": 15  # 0-100
    },
    "timestamp": datetime.now().isoformat()
}

# Haptic and sound cue definitions for Layer 3-5 communication
haptic_sound_cues = {
    "available_haptic_types": [
        "gentle_pulse",  # soft vibration for notifications
        "alert_thump",   # strong single pulse for warnings
        "rhythm_tap",    # pattern for navigation
        "urgency_buzz",  # rapid vibration for emergencies
        "confirmation_tap"  # light tap for confirmations
    ],
    "available_sound_types": [
        "notification_chime",  # gentle notification sound
        "warning_beep",       # attention-getting beep
        "alert_tone",         # urgent alert sound
        "navigation_ping",    # turn-by-turn navigation
        "confirmation_click", # action confirmation
        "ambient_hum"        # background ambient sound
    ],
    "current_feedback": {
        "haptic_feedback_type": None,
        "haptic_intensity": 0,  # 0-100
        "haptic_duration": 0,   # milliseconds
        "sound_cue_type": None,
        "sound_volume": 50,     # 0-100
        "sound_duration": 0     # milliseconds
    }
}

# System layers status
system_status = {
    "layer1": {"status": "active", "name": "Enhanced Simulation UI"},
    "layer2": {"status": "active", "name": "Data Monitoring"},
    "layer3": {"status": "active", "name": "AI Voice Assistant"},
    "layer4": {"status": "active", "name": "Infotainment Control"},
    "layer5": {"status": "active", "name": "UI Integration"}
}

# Real-time weather API configuration
weather_api_config = {
    "enabled": True,
    "api_key": "demo_key_12345",  # In production, use environment variable
    "provider": "enhanced_weather_service",
    "update_interval": 300,  # 5 minutes
    "location": {
        "latitude": 37.7749,  # San Francisco coordinates
        "longitude": -122.4194,
        "city": "San Francisco",
        "state": "CA"
    },
    "features": [
        "current_conditions",
        "wind_data",
        "visibility_data", 
        "precipitation_data",
        "weather_alerts",
        "ai_trigger_analysis"
    ]
}

# Enhanced weather simulation for comprehensive testing
weather_simulation_presets = {
    "clear_day": {
        "condition": "clear",
        "temperature": 75,
        "humidity": 45,
        "wind_speed": 5.2,
        "visibility": 10.0,
        "precipitation": 0,
        "ai_triggers": []
    },
    "foggy_morning": {
        "condition": "fog",
        "temperature": 58,
        "humidity": 95,
        "wind_speed": 3.1,
        "visibility": 0.3,  # Dense fog
        "precipitation": 0,
        "ai_triggers": ["fog_speed_warning"]
    },
    "heavy_rain": {
        "condition": "rain",
        "temperature": 65,
        "humidity": 88,
        "wind_speed": 12.5,
        "visibility": 2.5,
        "precipitation": 8.2,
        "ai_triggers": ["rain_traction_warning", "visibility_warning"]
    },
    "high_winds": {
        "condition": "partly_cloudy",
        "temperature": 70,
        "humidity": 60,
        "wind_speed": 28.3,  # High winds
        "visibility": 8.0,
        "precipitation": 0,
        "ai_triggers": ["wind_stability_warning"]
    },
    "severe_weather": {
        "condition": "rain",
        "temperature": 62,
        "humidity": 92,
        "wind_speed": 35.7,  # Very high winds
        "visibility": 0.8,   # Poor visibility
        "precipitation": 15.5,  # Heavy rain
        "ai_triggers": ["fog_speed_warning", "wind_stability_warning", "rain_traction_warning"]
    }
}

@app.route('/')
def home():
    return jsonify({
        "message": "Enhanced Infotainment System - Layer 1 Backend",
        "status": "running",
        "features": [
            "Comprehensive vehicle telemetry",
            "Real-time weather data with wind/visibility",
            "Driver behavior simulation and monitoring",
            "Haptic/sound cue protocol",
            "AI trigger data preparation"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/vehicle-data')
def get_vehicle_data():
    """Get enhanced vehicle telemetry data"""
    # Simulate real-time data changes with more complexity
    vehicle_data["speed"] = random.randint(50, 90)
    vehicle_data["rpm"] = random.randint(2000, 3000)
    vehicle_data["fuel_level"] = max(0, vehicle_data["fuel_level"] - random.uniform(0, 0.05))
    vehicle_data["temperature"] = random.randint(68, 78)
    
    # Enhanced safety metrics simulation
    vehicle_data["safety_metrics"]["following_distance"] = round(random.uniform(1.5, 4.0), 1)
    vehicle_data["safety_metrics"]["brake_pressure"] = random.randint(0, 15)
    vehicle_data["safety_metrics"]["acceleration"] = round(random.uniform(-0.5, 0.5), 2)
    vehicle_data["safety_metrics"]["steering_angle"] = random.randint(-5, 5)
    
    # Location updates (simulate movement)
    vehicle_data["location"]["heading"] = (vehicle_data["location"]["heading"] + random.randint(-2, 2)) % 360
    vehicle_data["location"]["latitude"] += random.uniform(-0.0001, 0.0001)
    vehicle_data["location"]["longitude"] += random.uniform(-0.0001, 0.0001)
    
    vehicle_data["timestamp"] = datetime.now().isoformat()
    
    return jsonify(vehicle_data)

@app.route('/api/simulate-event', methods=['POST'])
def simulate_event():
    data = request.get_json()
    event_type = data.get('event_type')
    if event_type == 'reset':
        vehicle_data["accident"] = False
        weather_data["condition"] = "clear"
        driver_behavior["alertness_status"] = "alert"
        return jsonify({"status": "success", "message": "System reset"})
    # ...existing event logic...
    return jsonify({"status": "success", "message": f"Event {event_type} triggered"})
@app.route('/api/vehicle-data', methods=['POST'])
def receive_simulation_data():
    """
    Receive manual simulation data from Layer 1 UI Control Board.
    This endpoint accepts system-triggered vehicle data and forwards it to Layer 2.
    """
    try:
        # Get simulation data from request
        sim_data = request.get_json()

        if not sim_data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400

        # --- Movement simulation logic ---
        global distance_to_destination, distance_to_weather_event
        distance_to_destination = max(0, distance_to_destination - 5)
        distance_to_weather_event = max(0, distance_to_weather_event - 5)

        # Update vehicle_data with simulation values
        vehicle_data.update({
            "speed": sim_data.get("speed", vehicle_data["speed"]),
            "rpm": sim_data.get("rpm", vehicle_data["rpm"]),
            "fuel_level": sim_data.get("fuel_level", vehicle_data["fuel_level"]),
            "temperature": sim_data.get("temperature", vehicle_data["temperature"]),
            "timestamp": sim_data.get("timestamp", datetime.now().isoformat())
        })

        # Add additional simulation-specific fields
        vehicle_data["gear"] = sim_data.get("gear", "P")
        vehicle_data["drive_mode"] = sim_data.get("drive_mode", "ECO")
        vehicle_data["battery"] = sim_data.get("battery", 85)
        vehicle_data["odometer"] = sim_data.get("odometer", 0)
        vehicle_data["source"] = "layer1_simulation_ui"

        if sim_data.get("accident") or sim_data.get("airbag") or sim_data.get("airbag_deployed"):
            vehicle_data["accident"] = True
            vehicle_data["airbag_deployed"] = True

        # Log the received data
        print(f"\n{'='*60}")
        print(f"📡 SIMULATION DATA RECEIVED FROM LAYER 1 UI")
        print(f"{'='*60}")
        print(f"Speed: {sim_data.get('speed')} km/h")
        print(f"RPM: {sim_data.get('rpm')}")
        print(f"Fuel: {sim_data.get('fuel_level')}%")
        print(f"Temperature: {sim_data.get('temperature')}°C")
        print(f"Gear: {sim_data.get('gear')}")
        print(f"Drive Mode: {sim_data.get('drive_mode')}")
        print(f"Battery: {sim_data.get('battery')}%")
        print(f"Odometer: {sim_data.get('odometer')} km")
        print(f"Timestamp: {sim_data.get('timestamp')}")
        print(f"Distance to destination: {distance_to_destination}")
        print(f"Distance to weather event: {distance_to_weather_event}")
        print(f"{'='*60}\n")

        # --- Emergency SMS logic update ---
        # (Insert this block where you send the SMS for accident events)
        if vehicle_data.get("accident"):
            if not emergency_contacts:
                print("No emergency contacts set")
            else:
                phone_numbers = ",".join(emergency_contacts)
                # Example: update payload for SMS
                sms_payload = {
                    # ...other params...
                    "numbers": phone_numbers,
                    # ...other params...
                }
                # ...send SMS as before...

        driver_alert = vehicle_data.get("speed", 0) > SPEED_ALERT_THRESHOLD
        weather_alert = (
            vehicle_data.get("temperature", 0) > TEMP_ALERT_THRESHOLD or
            weather_data.get("condition") in WEATHER_ALERT_CONDITIONS
        )

        forward_payload = {
            "vehicle_data": vehicle_data,
            "weather_data": weather_data,
            "driver_behavior": driver_behavior,
            "incident": {
                "accident": bool(vehicle_data.get("accident"))
            },
            "alert_flags": {
                "driver": driver_alert,
                "weather": weather_alert
            },
            "simulation": {
                "distance_to_destination": distance_to_destination,
                "distance_to_weather_event": distance_to_weather_event
            },
            "timestamp": datetime.now().isoformat()
        }

        try:
            requests.post("http://localhost:5002/api/monitor", json=forward_payload, timeout=3)
        except requests.RequestException as e:
            print(f"❌ Failed to forward data to Layer 2: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Simulation data received and processed",
            "data_received": sim_data,
            "updated_vehicle_data": vehicle_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing simulation data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process simulation data: {str(e)}"
        }), 500

@app.route('/api/weather-data')
def get_weather_data():
    """Get comprehensive weather data for AI triggers and UI visuals"""
    _update_weather_simulation()
    return jsonify(weather_data)

@app.route('/api/driver-behavior')  
def get_driver_behavior():
    """Get driver behavior data for AI analysis"""
    _update_driver_behavior_simulation()
    return jsonify(driver_behavior)

@app.route('/api/haptic-sound-cues')
def get_haptic_sound_cues():
    """Get available haptic and sound cue types"""
    return jsonify(haptic_sound_cues)

@app.route('/api/real-time-weather')
def get_real_time_weather():
    """Get real-time weather data (Phase 3 implementation)"""
    if weather_api_config["enabled"]:
        # Simulate real API call (would be actual API in production)
        enhanced_weather = _fetch_enhanced_weather_data()
        return jsonify(enhanced_weather)
    else:
        return jsonify({"error": "Real-time weather API disabled", "fallback": weather_data})

def _fetch_enhanced_weather_data():
    """Simulate enhanced weather API fetch with wind speed and visibility"""
    # In production, this would make actual API calls
    current_time = datetime.now()
    
    # Simulate weather API response with enhanced data
    api_weather = {
        "location": "San Francisco, CA",
        "current": {
            "condition": random.choice(["clear", "partly_cloudy", "cloudy", "rain", "fog"]),
            "temperature": random.randint(60, 80),
            "humidity": random.randint(40, 80),
            "wind_speed": round(random.uniform(0, 25), 1),  # mph for AI warnings
            "wind_direction": random.randint(0, 360),
            "visibility": round(random.uniform(0.1, 10.0), 1),  # miles for fog warnings
            "precipitation": round(random.uniform(0, 5), 2),  # mm/hr
            "uv_index": random.randint(1, 10),
            "pressure": round(random.uniform(1000, 1020), 2)
        },
        "alerts": [],
        "timestamp": current_time.isoformat(),
        "api_source": "enhanced_weather_api"
    }
    
    # Generate AI-relevant alerts based on conditions
    if api_weather["current"]["visibility"] < 1.0:
        api_weather["alerts"].append({
            "type": "visibility",
            "severity": "high",
            "message": "Dense fog detected - reduce speed",
            "ai_trigger": "fog_speed_warning",
            "recommended_action": "reduce_speed_50_percent"
        })
    
    if api_weather["current"]["wind_speed"] > 20:
        api_weather["alerts"].append({
            "type": "wind",
            "severity": "medium", 
            "message": "High winds detected - maintain control",
            "ai_trigger": "wind_stability_warning",
            "recommended_action": "reduce_speed_increase_following_distance"
        })
    
    if api_weather["current"]["precipitation"] > 2.0:
        api_weather["alerts"].append({
            "type": "precipitation",
            "severity": "medium",
            "message": "Heavy rain - reduced traction",
            "ai_trigger": "rain_traction_warning", 
            "recommended_action": "gentle_braking_increased_distance"
        })
    
    return api_weather

def _update_weather_simulation():
    """Update simulated weather data with enhanced details"""
    conditions = ["clear", "partly_cloudy", "cloudy", "rain", "fog", "snow"]
    current_condition = random.choice(conditions)
    
    weather_data.update({
        "condition": current_condition,
        "temperature": random.randint(60, 80),
        "humidity": random.randint(40, 85),
        "wind_speed": round(random.uniform(0, 30), 1),
        "wind_direction": random.randint(0, 360),
        "visibility": round(random.uniform(0.1, 10.0), 1),
        "precipitation": round(random.uniform(0, 10), 2),
        "timestamp": datetime.now().isoformat()
    })
    
    # Set UI animation parameters based on condition
    if current_condition == "rain":
        weather_data["rain_intensity"] = random.randint(30, 90)
        weather_data["fog_density"] = 0
        weather_data["snow_rate"] = 0
    elif current_condition == "fog":
        weather_data["fog_density"] = random.randint(40, 95)
        weather_data["rain_intensity"] = 0
        weather_data["visibility"] = round(random.uniform(0.1, 2.0), 1)
    elif current_condition == "snow":
        weather_data["snow_rate"] = random.randint(20, 80)
        weather_data["rain_intensity"] = 0
        weather_data["temperature"] = random.randint(25, 35)
    else:
        weather_data["rain_intensity"] = 0
        weather_data["fog_density"] = 0
        weather_data["snow_rate"] = 0

def _update_driver_behavior_simulation():
    """Update driver behavior metrics for AI analysis"""
    # Simulate alertness changes
    alertness_states = ["alert", "drowsy", "distracted"]
    weights = [0.7, 0.2, 0.1]  # Alert most common
    driver_behavior["alertness_status"] = random.choices(alertness_states, weights=weights)[0]
    
    # Update eye tracking based on alertness
    if driver_behavior["alertness_status"] == "drowsy":
        driver_behavior["eye_tracking"]["blink_rate"] = random.randint(20, 30)
        driver_behavior["biometric_data"]["fatigue_score"] = random.randint(60, 90)
    elif driver_behavior["alertness_status"] == "distracted":
        gaze_options = ["dashboard", "mirror", "phone", "road"]
        driver_behavior["eye_tracking"]["gaze_direction"] = random.choice(gaze_options)
        driver_behavior["biometric_data"]["stress_level"] = random.randint(40, 70)
    else:
        driver_behavior["eye_tracking"]["blink_rate"] = random.randint(12, 18)
        driver_behavior["eye_tracking"]["gaze_direction"] = "road"
        driver_behavior["biometric_data"]["fatigue_score"] = random.randint(5, 25)
        driver_behavior["biometric_data"]["stress_level"] = random.randint(10, 30)
    
    # Update driving patterns
    driver_behavior["driving_patterns"]["lane_changes"] = random.randint(0, 5)
    driver_behavior["driving_patterns"]["hard_braking_events"] = random.randint(0, 2)
    driver_behavior["driving_patterns"]["speed_variance"] = round(random.uniform(1.0, 5.0), 1)
    driver_behavior["driving_patterns"]["steering_smoothness"] = random.randint(70, 95)
    
    # Biometric updates
    driver_behavior["biometric_data"]["heart_rate"] = random.randint(65, 85)
    
    driver_behavior["timestamp"] = datetime.now().isoformat()

# Control endpoints for simulation manipulation
@app.route('/api/control/weather', methods=['POST'])
def control_weather():
    """Control weather simulation for testing AI triggers"""
    data = request.get_json()
    
    if "condition" in data:
        valid_conditions = ["clear", "partly_cloudy", "cloudy", "rain", "fog", "snow"]
        if data["condition"] in valid_conditions:
            weather_data["condition"] = data["condition"]
            _update_weather_simulation()  # Apply condition-specific changes
            
    if "wind_speed" in data:
        weather_data["wind_speed"] = max(0, min(50, float(data["wind_speed"])))
        
    if "visibility" in data:
        weather_data["visibility"] = max(0.1, min(10.0, float(data["visibility"])))
        
    if "precipitation" in data:
        weather_data["precipitation"] = max(0, min(20, float(data["precipitation"])))
        
    return jsonify({
        "status": "success",
        "updated_weather": weather_data,
        "message": "Weather simulation updated"
    })

@app.route('/api/control/driver-behavior', methods=['POST'])
def control_driver_behavior():
    """Control driver behavior simulation for AI testing"""
    data = request.get_json()
    
    if "alertness_status" in data:
        valid_states = ["alert", "drowsy", "distracted"] 
        if data["alertness_status"] in valid_states:
            driver_behavior["alertness_status"] = data["alertness_status"]
            _update_driver_behavior_simulation()  # Apply behavior-specific changes
            
    if "fatigue_score" in data:
        driver_behavior["biometric_data"]["fatigue_score"] = max(0, min(100, int(data["fatigue_score"])))
        
    if "stress_level" in data:
        driver_behavior["biometric_data"]["stress_level"] = max(0, min(100, int(data["stress_level"])))
        
    return jsonify({
        "status": "success", 
        "updated_behavior": driver_behavior,
        "message": "Driver behavior simulation updated"
    })

@app.route('/api/control/haptic-feedback', methods=['POST'])
def send_haptic_feedback():
    """Send haptic feedback cue (simulation)"""
    data = request.get_json()
    
    haptic_type = data.get("haptic_type", "gentle_pulse")
    duration = data.get("duration", 500)  # milliseconds
    intensity = data.get("intensity", 50)  # 0-100%
    
    # Validate haptic type
    valid_haptic_types = haptic_sound_cues["haptic_types"]
    if haptic_type not in valid_haptic_types:
        return jsonify({"error": "Invalid haptic type", "valid_types": valid_haptic_types}), 400
        
    # Log/simulate haptic feedback (in production, would control actual haptic devices)
    haptic_log = {
        "type": haptic_type,
        "duration_ms": duration,
        "intensity_percent": intensity,
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }
    
    return jsonify({
        "status": "success",
        "haptic_feedback": haptic_log,
        "message": f"Haptic feedback '{haptic_type}' sent successfully"
    })

@app.route('/api/control/sound-cue', methods=['POST'])
def send_sound_cue():
    """Send sound cue for AI voice assistant integration"""
    data = request.get_json()
    
    sound_type = data.get("sound_type", "notification")
    volume = data.get("volume", 70)  # 0-100%
    priority = data.get("priority", "medium")
    
    # Validate sound type
    valid_sound_types = haptic_sound_cues["sound_types"]
    if sound_type not in valid_sound_types:
        return jsonify({"error": "Invalid sound type", "valid_types": valid_sound_types}), 400
        
    # Log/simulate sound cue (in production, would control actual audio system)
    sound_log = {
        "type": sound_type,
        "volume_percent": volume,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "status": "played"
    }
    
    return jsonify({
        "status": "success",
        "sound_cue": sound_log,
        "message": f"Sound cue '{sound_type}' played successfully"
    })

@app.route('/api/ai-triggers')
def get_ai_triggers():
    """Get current AI trigger conditions based on vehicle/weather/driver data"""
    triggers = []
    
    # Weather-based triggers
    if weather_data["visibility"] < 2.0:
        triggers.append({
            "type": "weather_visibility",
            "severity": "high" if weather_data["visibility"] < 1.0 else "medium",
            "message": "Reduced visibility detected",
            "data": {"visibility": weather_data["visibility"]},
            "recommended_action": "reduce_speed"
        })
        
    if weather_data["wind_speed"] > 20:
        triggers.append({
            "type": "weather_wind",
            "severity": "medium",
            "message": "High winds detected", 
            "data": {"wind_speed": weather_data["wind_speed"]},
            "recommended_action": "maintain_control"
        })
        
    if weather_data["precipitation"] > 3.0:
        triggers.append({
            "type": "weather_precipitation",
            "severity": "medium",
            "message": "Heavy precipitation detected",
            "data": {"precipitation": weather_data["precipitation"]},
            "recommended_action": "increase_following_distance"
        })
    
    # Driver behavior triggers
    if driver_behavior["biometric_data"]["fatigue_score"] > 70:
        triggers.append({
            "type": "driver_fatigue",
            "severity": "high",
            "message": "Driver fatigue detected",
            "data": {"fatigue_score": driver_behavior["biometric_data"]["fatigue_score"]},
            "recommended_action": "suggest_break"
        })
        
    if driver_behavior["alertness_status"] != "alert":
        triggers.append({
            "type": "driver_alertness",
            "severity": "medium",
            "message": f"Driver {driver_behavior['alertness_status']} detected",
            "data": {"alertness_status": driver_behavior["alertness_status"]},
            "recommended_action": "attention_reminder"
        })
    
    # Vehicle safety triggers
    if vehicle_data["safety_metrics"]["following_distance"] < 2.0:
        triggers.append({
            "type": "safety_following_distance",
            "severity": "medium",
            "message": "Following distance too close",
            "data": {"following_distance": vehicle_data["safety_metrics"]["following_distance"]},
            "recommended_action": "increase_distance"
        })
    
    return jsonify({
        "triggers": triggers,
        "trigger_count": len(triggers),
        "timestamp": datetime.now().isoformat()
    })

# Enhanced weather API endpoints
@app.route('/api/weather-presets')
def get_weather_presets():
    """Get available weather simulation presets"""
    return jsonify({
        "presets": list(weather_simulation_presets.keys()),
        "preset_details": weather_simulation_presets,
        "current_preset": "auto_simulation",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/weather-preset/<preset_name>', methods=['POST'])
def apply_weather_preset(preset_name):
    """Apply a specific weather preset for testing"""
    if preset_name not in weather_simulation_presets:
        return jsonify({
            "error": "Invalid preset",
            "available_presets": list(weather_simulation_presets.keys())
        }), 400
    
    preset = weather_simulation_presets[preset_name]
    
    # Apply preset to current weather data
    weather_data.update({
        "condition": preset["condition"],
        "temperature": preset["temperature"],
        "humidity": preset["humidity"],
        "wind_speed": preset["wind_speed"],
        "visibility": preset["visibility"],
        "precipitation": preset["precipitation"],
        "preset_applied": preset_name,
        "timestamp": datetime.now().isoformat()
    })
    
    # Set UI animation parameters based on preset
    if preset["condition"] == "rain":
        weather_data["rain_intensity"] = int(preset["precipitation"] * 10)
        weather_data["fog_density"] = 0
        weather_data["snow_rate"] = 0
    elif preset["condition"] == "fog":
        weather_data["fog_density"] = int((10 - preset["visibility"]) * 10)
        weather_data["rain_intensity"] = 0
        weather_data["snow_rate"] = 0
    else:
        weather_data["rain_intensity"] = 0
        weather_data["fog_density"] = 0
        weather_data["snow_rate"] = 0
    
    return jsonify({
        "status": "success",
        "preset_applied": preset_name,
        "updated_weather": weather_data,
        "ai_triggers": preset["ai_triggers"],
        "message": f"Weather preset '{preset_name}' applied successfully"
    })

@app.route('/api/enhanced-weather-api')
def get_enhanced_weather_api():
    """Get enhanced weather API configuration and status"""
    return jsonify({
        "config": weather_api_config,
        "status": "enabled" if weather_api_config["enabled"] else "simulation_mode",
        "last_update": datetime.now().isoformat(),
        "supported_features": weather_api_config["features"]
    })

@app.route('/api/weather-for-ai')
def get_weather_for_ai():
    """Get weather data optimized for AI voice assistant triggers"""
    ai_weather_data = {
        "current_conditions": {
            "condition": weather_data["condition"],
            "temperature": weather_data["temperature"],
            "visibility": weather_data["visibility"],
            "wind_speed": weather_data["wind_speed"],
            "precipitation": weather_data["precipitation"]
        },
        "safety_assessment": {
            "visibility_safe": weather_data["visibility"] >= 3.0,
            "wind_safe": weather_data["wind_speed"] <= 20.0,
            "precipitation_safe": weather_data["precipitation"] <= 2.0,
            "overall_safety": "good"
        },
        "ui_parameters": {
            "rain_intensity": weather_data.get("rain_intensity", 0),
            "fog_density": weather_data.get("fog_density", 0),
            "snow_rate": weather_data.get("snow_rate", 0),
            "animation_type": weather_data["condition"]
        },
        "voice_notifications": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Determine overall safety
    safety_factors = [
        ai_weather_data["safety_assessment"]["visibility_safe"],
        ai_weather_data["safety_assessment"]["wind_safe"],
        ai_weather_data["safety_assessment"]["precipitation_safe"]
    ]
    
    if all(safety_factors):
        ai_weather_data["safety_assessment"]["overall_safety"] = "good"
    elif sum(safety_factors) >= 2:
        ai_weather_data["safety_assessment"]["overall_safety"] = "caution"
    else:
        ai_weather_data["safety_assessment"]["overall_safety"] = "poor"
    
    # Generate voice notifications for AI
    if not ai_weather_data["safety_assessment"]["visibility_safe"]:
        ai_weather_data["voice_notifications"].append({
            "priority": "high",
            "message": f"Visibility reduced to {weather_data['visibility']} miles. Consider reducing speed.",
            "trigger_type": "visibility_warning"
        })
    
    if not ai_weather_data["safety_assessment"]["wind_safe"]:
        ai_weather_data["voice_notifications"].append({
            "priority": "medium",
            "message": f"High winds at {weather_data['wind_speed']} mph detected. Maintain vehicle control.",
            "trigger_type": "wind_warning"
        })
    
    if not ai_weather_data["safety_assessment"]["precipitation_safe"]:
        ai_weather_data["voice_notifications"].append({
            "priority": "medium",
            "message": f"Heavy precipitation detected. Road conditions may be slippery.",
            "trigger_type": "precipitation_warning"
        })
    
    return jsonify(ai_weather_data)

@app.route('/api/comprehensive-dashboard')
def get_comprehensive_dashboard():
    """Get comprehensive dashboard data for Layer 5 UI"""
    dashboard_data = {
        "vehicle_status": {
            "speed": vehicle_data["speed"],
            "rpm": vehicle_data["rpm"],
            "fuel_level": vehicle_data["fuel_level"],
            "temperature": vehicle_data["temperature"],
            "safety_score": _calculate_safety_score(),
            "location": vehicle_data["location"]
        },
        "weather_display": {
            "condition": weather_data["condition"],
            "temperature": weather_data["temperature"],
            "visibility": weather_data["visibility"],
            "wind_speed": weather_data["wind_speed"],
            "rain_animation": weather_data.get("rain_intensity", 0),
            "fog_animation": weather_data.get("fog_density", 0)
        },
        "driver_status": {
            "alertness": driver_behavior["alertness_status"],
            "fatigue_level": driver_behavior["biometric_data"]["fatigue_score"],
            "performance_indicator": "good" if driver_behavior["biometric_data"]["fatigue_score"] < 50 else "warning"
        },
        "system_notifications": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add system notifications based on conditions
    if weather_data["visibility"] < 2.0:
        dashboard_data["system_notifications"].append({
            "type": "weather_alert",
            "message": "Low visibility conditions",
            "icon": "fog"
        })
    
    if driver_behavior["biometric_data"]["fatigue_score"] > 70:
        dashboard_data["system_notifications"].append({
            "type": "driver_alert", 
            "message": "Driver fatigue detected",
            "icon": "warning"
        })
    
    if vehicle_data["safety_metrics"]["following_distance"] < 2.0:
        dashboard_data["system_notifications"].append({
            "type": "safety_alert",
            "message": "Following distance too close",
            "icon": "distance"
        })
    
    return jsonify(dashboard_data)

def _calculate_safety_score():
    """Calculate overall vehicle safety score"""
    safety_factors = {
        "speed": 100 - max(0, (vehicle_data["speed"] - 80) * 2),  # Penalty for high speed
        "following_distance": min(100, vehicle_data["safety_metrics"]["following_distance"] * 25),
        "weather": 100 - max(0, (20 - weather_data["visibility"]) * 5),  # Weather visibility impact
        "driver": 100 - driver_behavior["biometric_data"]["fatigue_score"]
    }
    
    return int(sum(safety_factors.values()) / len(safety_factors))

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
        "weather": {
            "message": "Weather alert triggered",
            "condition": "rain",
            "warning": True
        },
        "driver": {
            "message": "Driver alert triggered",
            "alertness_status": "distracted",
            "fatigue_score": 80,
            "warning": True
        },
        "accident": {
            "message": "Accident detected",
            "accident": True,
            "airbag": True,
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
    elif event_type == "weather":
        weather_data["condition"] = data.get("condition", event.get("condition", "rain"))
        weather_data["timestamp"] = datetime.now().isoformat()
    elif event_type == "driver":
        driver_behavior["alertness_status"] = event.get("alertness_status", "distracted")
        driver_behavior["biometric_data"]["fatigue_score"] = event.get("fatigue_score", 80)
        driver_behavior["timestamp"] = datetime.now().isoformat()

    accident_triggered = bool(data.get("airbag") or data.get("airbag_deployed") or data.get("accident"))
    if event_type == "accident":
        accident_triggered = True

    if accident_triggered:
        vehicle_data["accident"] = True
        vehicle_data["airbag_deployed"] = True
        location = vehicle_data.get("location", {})
        lat = location.get("latitude") if location.get("latitude") is not None else "0.0"
        lon = location.get("longitude") if location.get("longitude") is not None else "0.0"

        message = (
            "Emergency! Accident detected.\n"
            f"Location: {lat}, {lon}\n"
            f"https://maps.google.com/?q={lat},{lon}"
        )

        headers = {
            "authorization": FAST2SMS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": FAST2SMS_PHONE_NUMBER
        }

        try:
            response = requests.post(FAST2SMS_API_URL, json=payload, headers=headers, timeout=10)
            if response.ok:
                print("SMS sent successfully")
            else:
                print(f"SMS failed: {response.status_code} {response.text}")
        except requests.RequestException as e:
            print(f"SMS failed: {e}")

    try:
        forward_payload = {
            "vehicle_data": vehicle_data,
            "weather_data": weather_data,
            "driver_behavior": driver_behavior,
            "incident": {
                "accident": bool(vehicle_data.get("accident"))
            },
            "alert_flags": {
                "driver": event_type == "driver",
                "weather": event_type == "weather"
            },
            "timestamp": datetime.now().isoformat()
        }
        requests.post("http://localhost:5002/api/monitor", json=forward_payload, timeout=3)
    except requests.RequestException as e:
        print(f"❌ Failed to forward event to Layer 2: {e}")
    
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
