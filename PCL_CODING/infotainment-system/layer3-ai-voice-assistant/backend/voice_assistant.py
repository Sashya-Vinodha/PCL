from flask import Flask, jsonify, request
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import threading
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
import queue
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced voice assistant state with new capabilities
assistant_state = {
    "is_listening": False,
    "is_speaking": False,
    "last_command": "",
    "last_response": "",
    "voice_enabled": True,
    "language": "en-US",
    "current_voice_profile": "DriverVoice",
    "anticipatory_enabled": True,
    "sentiment_detection_enabled": True,
    "driver_fatigue_detected": False,
    "last_anticipatory_action": None,
    "last_alert_timestamp": None,
    "pattern_learning_active": True,
    "timestamp": datetime.now().isoformat()
}

# Command processing queue
command_queue = queue.Queue()
response_queue = queue.Queue()

# Layer integration configuration
layer_config = {
    "layer2_url": "http://localhost:5002",
    "layer4_url": "http://localhost:5004",
    "integration_enabled": True,
    "data_sync_interval": 5
}

@dataclass
class RoutineRoute:
    """Data class for routine routes"""
    name: str
    start_location: str
    end_location: str
    typical_times: List[str]  # e.g., ["08:00", "17:30"]
    days_of_week: List[str]   # e.g., ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    last_used: Optional[str] = None
    usage_count: int = 0

@dataclass 
class VoiceProfile:
    """Data class for voice profiles"""
    name: str
    rate: int
    volume: float
    voice_index: int
    pitch_modifier: float = 1.0
    tone_description: str = "neutral"

# Routine routes for anticipatory interface
routine_routes = [
    RoutineRoute(
        name="Home to Office",
        start_location="home",
        end_location="office",
        typical_times=["07:30", "08:00", "08:30"],
        days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ),
    RoutineRoute(
        name="Office to Home", 
        start_location="office",
        end_location="home",
        typical_times=["17:00", "17:30", "18:00"],
        days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ),
    RoutineRoute(
        name="Home to Gym",
        start_location="home", 
        end_location="gym",
        typical_times=["06:00", "18:30", "19:00"],
        days_of_week=["Monday", "Wednesday", "Friday", "Saturday"]
    ),
    RoutineRoute(
        name="Weekend Shopping",
        start_location="home",
        end_location="shopping_center", 
        typical_times=["10:00", "14:00"],
        days_of_week=["Saturday", "Sunday"]
    )
]

# Voice profiles for multi-voice simulation
voice_profiles = {
    "DriverVoice": VoiceProfile(
        name="DriverVoice",
        rate=150,
        volume=0.8,
        voice_index=0,
        pitch_modifier=1.0,
        tone_description="confident and clear"
    ),
    "PassengerVoice": VoiceProfile(
        name="PassengerVoice", 
        rate=140,
        volume=0.7,
        voice_index=1,
        pitch_modifier=1.2,
        tone_description="gentle and friendly"
    ),
    "NavigationVoice": VoiceProfile(
        name="NavigationVoice",
        rate=160,
        volume=0.9,
        voice_index=0,
        pitch_modifier=0.9,
        tone_description="authoritative and precise"
    ),
    "AlertVoice": VoiceProfile(
        name="AlertVoice",
        rate=130,
        volume=1.0,
        voice_index=1,
        pitch_modifier=0.8,
        tone_description="urgent and attention-grabbing"
    )
}

# Sentiment detection patterns
sentiment_patterns = {
    "fatigue_indicators": [
        "tired", "sleepy", "exhausted", "drowsy", "yawn", "rest", "break"
    ],
    "stress_indicators": [
        "stressed", "anxious", "frustrated", "angry", "traffic", "late", "hurry"
    ],
    "positive_indicators": [
        "good", "great", "happy", "excellent", "perfect", "love", "awesome"
    ]
}

class EnhancedVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        try:
            self.tts_engine = pyttsx3.init()
        except Exception as e:
            self.tts_engine = None
            logger.error(f"TTS engine init failed, falling back to system TTS: {e}")
        self.listening_thread = None
        self.processing_thread = None
        self.anticipatory_thread = None
        self.sentiment_thread = None
        self.alerts_thread = None
        self.is_running = False
        
        # Initialize voice profiles
        self.setup_voice_profiles()
        
        # Pattern learning data
        self.user_patterns = {
            "command_frequency": {},
            "time_patterns": {},
            "location_patterns": {},
            "preference_learning": {}
        }
        # Cooldown and last spoken alert tracking
        self.last_spoken_time = 0
        self.COOLDOWN_SECONDS = 8
        self.last_spoken_message = None
        
        # Layer 2 data cache
        self.layer2_data = {}
        self.last_layer2_sync = None
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def setup_voice_profiles(self):
        """Initialize TTS engine with voice profiles"""
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Configure default voice profile
            self.apply_voice_profile("DriverVoice")
            
            logger.info(f"Voice profiles initialized. Available voices: {len(voices) if voices else 0}")
        except Exception as e:
            logger.error(f"Error setting up voice profiles: {e}")
    
    def apply_voice_profile(self, profile_name: str):
        """Apply a specific voice profile"""
        if profile_name in voice_profiles:
            profile = voice_profiles[profile_name]
            
            try:
                # Get available voices
                voices = self.tts_engine.getProperty('voices')
                if voices and len(voices) > profile.voice_index:
                    self.tts_engine.setProperty('voice', voices[profile.voice_index].id)
                
                self.tts_engine.setProperty('rate', profile.rate)
                self.tts_engine.setProperty('volume', profile.volume)
                
                assistant_state["current_voice_profile"] = profile_name
                logger.info(f"Applied voice profile: {profile_name} - {profile.tone_description}")
                
            except Exception as e:
                logger.error(f"Error applying voice profile {profile_name}: {e}")
    
    def start_listening(self):
        """Start enhanced voice recognition with anticipatory features"""
        if not self.is_running:
            self.is_running = True
            
            # Start main threads
            self.listening_thread = threading.Thread(target=self._listen_loop)
            self.processing_thread = threading.Thread(target=self._process_commands)
            
            # Start enhancement threads
            self.anticipatory_thread = threading.Thread(target=self._anticipatory_loop)
            self.sentiment_thread = threading.Thread(target=self._sentiment_monitoring_loop)
            self.alerts_thread = threading.Thread(target=self._alerts_loop)
            
            # Set as daemon threads
            for thread in [self.listening_thread, self.processing_thread,
                          self.anticipatory_thread, self.sentiment_thread,
                          self.alerts_thread]:
                thread.daemon = True
                thread.start()
            
            logger.info("Enhanced voice assistant started with anticipatory intelligence")
    
    def stop_listening(self):
        """Stop voice recognition and all enhancement features"""
        self.is_running = False
        assistant_state["is_listening"] = False
        logger.info("Enhanced voice assistant stopped")
    
    def _listen_loop(self):
        """Enhanced listening loop with sentiment analysis"""
        while self.is_running:
            try:
                assistant_state["is_listening"] = True
                with self.microphone as source:
                    logger.info("Listening for commands...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                try:
                    command = self.recognizer.recognize_google(audio, language=assistant_state["language"])
                    logger.info(f"Recognized command: {command}")
                    
                    # Perform sentiment analysis
                    self._analyze_sentiment(command)
                    
                    # Learn from user patterns
                    self._learn_user_patterns(command)
                    
                    command_queue.put(command)
                    assistant_state["last_command"] = command
                    assistant_state["timestamp"] = datetime.now().isoformat()
                    
                except sr.UnknownValueError:
                    logger.debug("Could not understand audio")
                except sr.RequestError as e:
                    logger.error(f"Error with speech recognition service: {e}")
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in listening loop: {e}")
                time.sleep(1)
            
            assistant_state["is_listening"] = False
            time.sleep(0.1)
    
    def _anticipatory_loop(self):
        """Anticipatory interface logic with pattern learning"""
        while self.is_running:
            try:
                if assistant_state["anticipatory_enabled"]:
                    # Sync with Layer 2 data
                    self._sync_layer2_data()
                    
                    # Check for routine pattern matches
                    self._check_routine_patterns()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in anticipatory loop: {e}")
                time.sleep(5)
    
    def _sentiment_monitoring_loop(self):
        """Continuous sentiment monitoring and fatigue detection"""
        while self.is_running:
            try:
                if assistant_state["sentiment_detection_enabled"]:
                    # Check for fatigue indicators from various sources
                    self._monitor_driver_fatigue()
                
                time.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Error in sentiment monitoring: {e}")
                time.sleep(5)

    def _alerts_loop(self):
        """Poll Layer 2 alerts and speak new warnings"""
        while self.is_running:
            try:
                self._check_layer2_alerts()
                time.sleep(3)
            except Exception as e:
                logger.error(f"Error in alerts loop: {e}")
                time.sleep(3)

    def _check_layer2_alerts(self):
        """Fetch latest alert from Layer 2 and speak if new, with cooldown and deduplication"""
        try:
            response = requests.get(f"{layer_config['layer2_url']}/api/alerts", timeout=3)
            if response.status_code != 200:
                print("Layer 2 not responding")
                logger.error(f"Layer 2 not responding: status={response.status_code}")
                return

            data = response.json()
            alerts = data.get("alerts", [])
            if not alerts:
                return

            latest = alerts[-1]
            alert_type = latest.get("type")
            alert_message = latest.get("message")
            alert_timestamp = latest.get("timestamp")

            if not alert_timestamp or alert_timestamp == assistant_state.get("last_alert_timestamp"):
                return
            if not alert_type or not alert_message:
                return

            # Cooldown and deduplication logic
            import time as _time
            now = _time.time()
            should_speak = False
            if (self.last_spoken_message != alert_message) or (now - self.last_spoken_time > self.COOLDOWN_SECONDS):
                should_speak = True

            if should_speak:
                print(f"[ALERT RECEIVED] {alert_type} {alert_message}")
                if alert_type == "weather":
                    self._speak("Heads up — rain expected ahead.")
                elif alert_type == "driver":
                    self._speak("Your driving seems aggressive. Stay smooth.")
                elif alert_type == "accident":
                    self._speak("Emergency detected. Alerting your contacts now.")
                self.last_spoken_time = now
                self.last_spoken_message = alert_message

            assistant_state["last_alert_timestamp"] = alert_timestamp
        except Exception as e:
            logger.error(f"Could not fetch Layer 2 alerts: {e}")
    
    def _sync_layer2_data(self):
        """Sync data from Layer 2 monitoring"""
        try:
            if layer_config["integration_enabled"]:
                response = requests.get(f"{layer_config['layer2_url']}/api/monitor", timeout=3)
                if response.status_code == 200:
                    self.layer2_data = response.json()
                    self.last_layer2_sync = datetime.now()
                    logger.debug("Layer 2 data synced successfully")
        except Exception as e:
            logger.debug(f"Could not sync Layer 2 data: {e}")
    
    def _check_routine_patterns(self):
        """Check current conditions against routine routes for anticipatory actions"""
        if not self.layer2_data:
            return
            
        current_time = datetime.now()
        current_day = current_time.strftime("%A")
        current_time_str = current_time.strftime("%H:%M")
        
        # Get simulated location (in real system, this would come from GPS)
        current_location = self._get_current_location_context()
        
        for route in routine_routes:
            if self._matches_routine_pattern(route, current_day, current_time_str, current_location):
                # Check if navigation is currently inactive
                if not self._is_navigation_active():
                    self._trigger_anticipatory_navigation(route)
                    break
    
    def _matches_routine_pattern(self, route: RoutineRoute, day: str, time: str, location: str) -> bool:
        """Check if current conditions match a routine pattern"""
        # Check day of week
        if day not in route.days_of_week:
            return False
        
        # Check time proximity (within 15 minutes of typical times)
        current_minutes = int(time.split(':')[0]) * 60 + int(time.split(':')[1])
        
        for typical_time in route.typical_times:
            typical_minutes = int(typical_time.split(':')[0]) * 60 + int(typical_time.split(':')[1])
            if abs(current_minutes - typical_minutes) <= 15:  # Within 15 minutes
                # Check location context
                if location.lower() == route.start_location.lower():
                    return True
        
        return False
    
    def _get_current_location_context(self) -> str:
        """Get current location context (simulated)"""
        # In a real system, this would use GPS/location services
        # For simulation, we'll use time-based logic
        current_hour = datetime.now().hour
        
        if 6 <= current_hour <= 9:
            return "home"  # Morning at home
        elif 9 <= current_hour <= 17:
            return "office"  # Work hours
        elif 17 <= current_hour <= 19:
            return "office"  # Evening leaving office
        elif 19 <= current_hour <= 22:
            return "home"  # Evening at home
        else:
            return "home"  # Night/early morning
    
    def _is_navigation_active(self) -> bool:
        """Check if navigation is currently active"""
        # This would integrate with navigation system
        # For now, simulate based on recent commands
        if assistant_state.get("last_command"):
            return "navigate" in assistant_state["last_command"].lower()
        return False
    
    def _trigger_anticipatory_navigation(self, route: RoutineRoute):
        """Trigger anticipatory navigation prompt"""
        # Avoid repeated prompts within 30 minutes
        last_action = assistant_state.get("last_anticipatory_action")
        if last_action:
            last_time = datetime.fromisoformat(last_action)
            if datetime.now() - last_time < timedelta(minutes=30):
                return
        
        # Use NavigationVoice for anticipatory prompts
        self.apply_voice_profile("NavigationVoice")
        
        prompt = f"I notice it's time for your usual trip. Launching navigation to {route.end_location}. Accept?"
        
        # Speak the prompt
        self._speak(prompt)
        
        # Update learning data
        route.usage_count += 1
        route.last_used = datetime.now().isoformat()
        
        assistant_state["last_anticipatory_action"] = datetime.now().isoformat()
        
        logger.info(f"Triggered anticipatory navigation: {route.name}")
        
        # Return to default voice profile
        self.apply_voice_profile("DriverVoice")
    
    def _analyze_sentiment(self, command: str):
        """Analyze sentiment and detect fatigue/stress indicators"""
        command_lower = command.lower()
        
        # Check for fatigue indicators
        fatigue_score = sum(1 for indicator in sentiment_patterns["fatigue_indicators"] 
                          if indicator in command_lower)
        
        # Check for stress indicators  
        stress_score = sum(1 for indicator in sentiment_patterns["stress_indicators"]
                         if indicator in command_lower)
        
        # Update fatigue detection
        if fatigue_score > 0:
            assistant_state["driver_fatigue_detected"] = True
            self._handle_fatigue_detection()
        elif stress_score > 0:
            self._handle_stress_detection()
        elif any(indicator in command_lower for indicator in sentiment_patterns["positive_indicators"]):
            assistant_state["driver_fatigue_detected"] = False
    
    def _monitor_driver_fatigue(self):
        """Monitor for signs of driver fatigue from various sources"""
        # Check Layer 2 data for fatigue indicators
        if self.layer2_data:
            vehicle_metrics = self.layer2_data.get("vehicle_metrics", {})
            
            # Simulate fatigue detection based on driving patterns
            speed = vehicle_metrics.get("speed", 0)
            current_hour = datetime.now().hour
            
            # Detect potential fatigue conditions
            if (22 <= current_hour or current_hour <= 6) and speed > 50:
                # Late night/early morning driving
                if not assistant_state["driver_fatigue_detected"]:
                    assistant_state["driver_fatigue_detected"] = True
                    self._handle_fatigue_detection()
    
    def _handle_fatigue_detection(self):
        """Handle detected driver fatigue"""
        logger.info("Driver fatigue detected - triggering ambient design change")
        
        # Use AlertVoice for fatigue warnings
        self.apply_voice_profile("AlertVoice") 
        
        # Send command to Layer 4 for ambient design change
        self._send_layer4_command("bright_alert_theme", {
            "reason": "fatigue_detected",
            "theme": "bright_alertness",
            "brightness_increase": 30,
            "color_temperature": "cool"
        })
        
        # Speak fatigue warning
        warning = "I've detected signs of fatigue. I'm adjusting the display for better alertness. Consider taking a break if needed."
        self._speak(warning)
        
        # Return to default voice
        self.apply_voice_profile("DriverVoice")
    
    def _handle_stress_detection(self):
        """Handle detected driver stress"""
        logger.info("Driver stress detected - suggesting calming measures")
        
        # Use PassengerVoice for calming responses
        self.apply_voice_profile("PassengerVoice")
        
        # Send calming ambient command to Layer 4
        self._send_layer4_command("calming_theme", {
            "reason": "stress_detected", 
            "theme": "calming_ambience",
            "brightness_decrease": 10,
            "color_temperature": "warm"
        })
        
        response = "I sense you might be feeling stressed. I've adjusted the ambience to be more calming. Would you like me to play some relaxing music?"
        self._speak(response)
        
        # Return to default voice
        self.apply_voice_profile("DriverVoice")
    
    def _send_layer4_command(self, command_type: str, parameters: Dict[str, Any]):
        """Send command to Layer 4 for ambient design changes"""
        try:
            if layer_config["integration_enabled"]:
                payload = {
                    "command_type": command_type,
                    "parameters": parameters,
                    "source": "layer3_voice_assistant",
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{layer_config['layer4_url']}/api/ambient-control",
                    json=payload,
                    timeout=3
                )
                
                if response.status_code == 200:
                    logger.info(f"Layer 4 command sent successfully: {command_type}")
                else:
                    logger.warning(f"Layer 4 command failed: {response.status_code}")
                    
        except Exception as e:
            logger.debug(f"Could not send Layer 4 command: {e}")
    
    def _learn_user_patterns(self, command: str):
        """Learn from user command patterns"""
        if not assistant_state["pattern_learning_active"]:
            return
            
        current_time = datetime.now()
        hour = current_time.hour
        
        # Update command frequency
        if command in self.user_patterns["command_frequency"]:
            self.user_patterns["command_frequency"][command] += 1
        else:
            self.user_patterns["command_frequency"][command] = 1
        
        # Update time patterns
        if hour not in self.user_patterns["time_patterns"]:
            self.user_patterns["time_patterns"][hour] = []
        self.user_patterns["time_patterns"][hour].append(command)
        
        # Limit pattern storage
        if len(self.user_patterns["time_patterns"][hour]) > 20:
            self.user_patterns["time_patterns"][hour] = self.user_patterns["time_patterns"][hour][-20:]
    
    def _process_commands(self):
        """Enhanced command processing with multi-voice responses"""
        while self.is_running:
            try:
                if not command_queue.empty():
                    command = command_queue.get()
                    
                    # Determine appropriate voice profile based on command type
                    voice_profile = self._select_voice_profile(command)
                    self.apply_voice_profile(voice_profile)
                    
                    response = self._execute_command(command)
                    response_queue.put(response)
                    
                    if assistant_state["voice_enabled"]:
                        self._speak(response)
                    
                    # Return to default voice profile
                    self.apply_voice_profile("DriverVoice")
                
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def _select_voice_profile(self, command: str) -> str:
        """Select appropriate voice profile based on command type"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["navigate", "directions", "route", "turn", "exit"]):
            return "NavigationVoice"
        elif any(word in command_lower for word in ["alert", "warning", "danger", "emergency"]):
            return "AlertVoice"
        elif any(word in command_lower for word in ["music", "relax", "comfort", "passenger"]):
            return "PassengerVoice"
        else:
            return "DriverVoice"
    
    def _execute_command(self, command):
        """Enhanced command execution with anticipatory features"""
        command_lower = command.lower()
        
        # Handle anticipatory responses (Yes/No to suggestions)
        if any(word in command_lower for word in ["yes", "ok", "okay", "sure", "accept"]):
            if assistant_state.get("last_anticipatory_action"):
                return self._handle_anticipatory_acceptance()
        elif any(word in command_lower for word in ["no", "cancel", "dismiss", "not now"]):
            if assistant_state.get("last_anticipatory_action"):
                return self._handle_anticipatory_rejection()
        
        # Navigation commands with enhanced context
        if any(word in command_lower for word in ["navigate", "directions", "route"]):
            return self._handle_enhanced_navigation_command(command)
        
        # Media commands with voice profile awareness
        elif any(word in command_lower for word in ["play", "music", "song", "radio"]):
            return self._handle_enhanced_media_command(command)
        
        # Vehicle information with Layer 2 integration
        elif any(word in command_lower for word in ["speed", "fuel", "temperature", "status"]):
            return self._handle_enhanced_vehicle_info_command(command)
        
        # Climate control with sentiment awareness
        elif any(word in command_lower for word in ["temperature", "climate", "air", "heat", "cool"]):
            return self._handle_enhanced_climate_command(command)
        
        # Fatigue management commands
        elif any(word in command_lower for word in ["tired", "fatigue", "rest", "break"]):
            return self._handle_fatigue_command(command)
        
        # Phone commands
        elif any(word in command_lower for word in ["call", "phone", "dial"]):
            return self._handle_phone_command(command)
        
        # Voice profile commands
        elif any(word in command_lower for word in ["voice", "profile", "change voice"]):
            return self._handle_voice_profile_command(command)
        
        # Learning and pattern commands
        elif any(word in command_lower for word in ["learn", "remember", "routine"]):
            return self._handle_learning_command(command)
        
        # General help
        elif any(word in command_lower for word in ["help", "what can you do"]):
            return self._handle_enhanced_help_command()
        
        else:
            return self._handle_unknown_command(command)
    
    def _handle_anticipatory_acceptance(self):
        """Handle user acceptance of anticipatory suggestion"""
        assistant_state["last_anticipatory_action"] = None
        return "Navigation started! I'll guide you to your destination."
    
    def _handle_anticipatory_rejection(self):
        """Handle user rejection of anticipatory suggestion"""
        assistant_state["last_anticipatory_action"] = None
        return "No problem! Let me know if you need navigation later."
    
    def _handle_enhanced_navigation_command(self, command):
        """Enhanced navigation with pattern learning"""
        if "home" in command.lower():
            # Learn this as a frequent destination
            self._learn_destination_preference("home")
            return "Setting navigation to home address. Estimated arrival time is 25 minutes."
        elif "work" in command.lower() or "office" in command.lower():
            self._learn_destination_preference("office")
            return "Setting navigation to your office. I'll find the fastest route avoiding current traffic."
        elif "gym" in command.lower():
            self._learn_destination_preference("gym")
            return "Navigating to your gym. Don't forget your water bottle!"
        else:
            return "Please specify a destination for navigation, or I can suggest based on your usual routes."
    
    def _handle_enhanced_media_command(self, command):
        """Enhanced media commands with mood awareness"""
        # Check current sentiment for music recommendations
        if assistant_state.get("driver_fatigue_detected"):
            if "play" in command.lower():
                return "Playing energizing music to help keep you alert. Stay safe out there!"
        
        if "play" in command.lower():
            return "Playing music from your preferred playlist. Enjoy the drive!"
        elif "pause" in command.lower():
            return "Music paused. Everything okay?"
        elif "next" in command.lower():
            return "Skipping to the next track."
        elif "previous" in command.lower():
            return "Going back to the previous song."
        elif "radio" in command.lower():
            return "Switching to radio mode. Finding a station with good signal."
        elif "volume" in command.lower():
            if "up" in command.lower() or "increase" in command.lower():
                return "Increasing volume."
            elif "down" in command.lower() or "decrease" in command.lower():
                return "Decreasing volume."
        else:
            return "Media command executed. Is there anything specific you'd like to hear?"
    
    def _handle_enhanced_vehicle_info_command(self, command):
        """Enhanced vehicle information with Layer 2 data integration"""
        if self.layer2_data and "vehicle_metrics" in self.layer2_data:
            metrics = self.layer2_data["vehicle_metrics"]
            
            if "speed" in command.lower():
                speed = metrics.get("speed", 0)
                return f"Current speed is {speed} miles per hour."
            elif "fuel" in command.lower():
                fuel = metrics.get("fuel_level", 0)
                if fuel < 25:
                    return f"Fuel level is at {fuel:.1f} percent. You should consider refueling soon."
                return f"Fuel level is at {fuel:.1f} percent."
            elif "temperature" in command.lower():
                temp = metrics.get("temperature", 0)
                return f"Engine temperature is {temp} degrees Fahrenheit."
            elif "status" in command.lower():
                return self._get_comprehensive_vehicle_status(metrics)
        else:
            # Fallback responses when Layer 2 is unavailable
            if "speed" in command.lower():
                return "Current speed is 65 miles per hour."
            elif "fuel" in command.lower():
                return "Fuel level is at 75 percent."
            elif "temperature" in command.lower():
                return "Engine temperature is normal at 195 degrees Fahrenheit."
            elif "status" in command.lower():
                return "All vehicle systems are operating normally."
        
        return "Vehicle information retrieved."
    
    def _get_comprehensive_vehicle_status(self, metrics):
        """Get comprehensive vehicle status from Layer 2 data"""
        status_parts = []
        
        speed = metrics.get("speed", 0)
        fuel = metrics.get("fuel_level", 0)
        temp = metrics.get("temperature", 0)
        
        if fuel < 25:
            status_parts.append(f"Low fuel at {fuel:.1f}%")
        if temp > 85:
            status_parts.append(f"High engine temperature at {temp}°F")
        if speed > 80:
            status_parts.append("Currently exceeding recommended speed")
        
        if status_parts:
            return f"Vehicle status: {', '.join(status_parts)}. Please drive safely."
        else:
            return "All vehicle systems are operating normally. Safe travels!"
    
    def _handle_enhanced_climate_command(self, command):
        """Enhanced climate control with comfort learning"""
        if "increase" in command.lower() or "warmer" in command.lower() or "heat" in command.lower():
            self._send_layer4_command("climate_control", {"action": "increase_temp", "amount": 2})
            return "Increasing cabin temperature. Getting cozy!"
        elif "decrease" in command.lower() or "cooler" in command.lower() or "cold" in command.lower():
            self._send_layer4_command("climate_control", {"action": "decrease_temp", "amount": 2})
            return "Decreasing cabin temperature. Cooling things down!"
        elif "air conditioning" in command.lower() or "ac" in command.lower():
            self._send_layer4_command("climate_control", {"action": "ac_on"})
            return "Air conditioning activated. Perfect driving weather coming up!"
        elif "heat" in command.lower():
            self._send_layer4_command("climate_control", {"action": "heat_on"})
            return "Heating system activated. Stay warm!"
        elif "auto" in command.lower():
            self._send_layer4_command("climate_control", {"action": "auto_mode"})
            return "Climate control set to automatic. I'll maintain a comfortable temperature."
        else:
            return "Climate control adjusted to your preference."
    
    def _handle_fatigue_command(self, command):
        """Handle fatigue-related commands"""
        assistant_state["driver_fatigue_detected"] = True
        
        if "break" in command.lower() or "rest" in command.lower():
            return "I understand you need a break. Let me find nearby rest stops or safe parking areas."
        elif "tired" in command.lower():
            self._handle_fatigue_detection()
            return "I've detected you're feeling tired. I'm adjusting the environment to help you stay alert."
        else:
            return "If you're feeling tired, please consider taking a break. Your safety is the priority."
    
    def _handle_voice_profile_command(self, command):
        """Handle voice profile changes"""
        if "driver" in command.lower():
            self.apply_voice_profile("DriverVoice")
            return "Switched to driver voice profile."
        elif "passenger" in command.lower():
            self.apply_voice_profile("PassengerVoice")
            return "Switched to passenger voice profile."
        elif "navigation" in command.lower():
            self.apply_voice_profile("NavigationVoice")
            return "Switched to navigation voice profile."
        elif "alert" in command.lower():
            self.apply_voice_profile("AlertVoice") 
            return "Switched to alert voice profile."
        else:
            profiles = list(voice_profiles.keys())
            return f"Available voice profiles: {', '.join(profiles)}. Which would you like to use?"
    
    def _handle_learning_command(self, command):
        """Handle learning and routine-related commands"""
        if "routine" in command.lower():
            return "I'm continuously learning your driving patterns. I can suggest navigation based on your usual routes and times."
        elif "remember" in command.lower():
            return "I'll remember your preferences. You can ask me to change voice profiles or suggest routes based on your patterns."
        else:
            return "I'm always learning to serve you better. Your patterns help me provide more personalized assistance."
    
    def _handle_enhanced_help_command(self):
        """Enhanced help with new capabilities"""
        return ("I can help you with navigation with anticipatory suggestions, music control with mood awareness, "
                "vehicle information from real-time data, climate control with learning, fatigue detection, "
                "voice profile changes, and routine learning. I'm also monitoring for your safety and comfort. "
                "What would you like me to help you with?")
    
    def _handle_unknown_command(self, command):
        """Handle unknown commands with learning opportunity"""
        # Log unknown command for future learning
        logger.info(f"Unknown command for learning: {command}")
        return f"I didn't understand '{command}'. I'm learning new commands - could you rephrase or say 'help' for available commands?"
    
    def _learn_destination_preference(self, destination):
        """Learn destination preferences"""
        if "destination_preferences" not in self.user_patterns:
            self.user_patterns["destination_preferences"] = {}
        
        if destination in self.user_patterns["destination_preferences"]:
            self.user_patterns["destination_preferences"][destination] += 1
        else:
            self.user_patterns["destination_preferences"][destination] = 1
    
    def _speak(self, text):
        """Single-threaded text-to-speech with debug logging and default voice. No overlapping allowed."""
        if getattr(self, 'speaking', False):
            print("[VOICE] Speak called while already speaking. Skipping.")
            return
        self.speaking = True
        try:
            assistant_state["is_speaking"] = True
            assistant_state["last_response"] = text
            # Use default system voice, slower rate
            if self.tts_engine is not None:
                self.tts_engine.setProperty('rate', 160)
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                subprocess.run(["say", text], check=False)
            print(f"[VOICE] Spoke: {text}")
            assistant_state["is_speaking"] = False
        except Exception as e:
            print(f"[VOICE] Error in text-to-speech: {e}")
            assistant_state["is_speaking"] = False
        self.speaking = False
    
    def _enhance_speech_with_personality(self, text: str, profile_name: str) -> str:
        """Add personality touches based on voice profile"""
        if profile_name == "PassengerVoice":
            # More gentle and friendly
            if text.endswith("."):
                text = text[:-1] + " 😊"
        elif profile_name == "AlertVoice":
            # More urgent
            if not text.endswith("!"):
                text += "!"
        elif profile_name == "NavigationVoice":
            # More precise and authoritative
            pass  # Keep navigation speech clear and direct
        
        return text

# Initialize enhanced voice assistant
voice_assistant = EnhancedVoiceAssistant()

@app.route('/')
def home():
    return jsonify({
        "message": "Infotainment System - Layer 3 AI Voice Assistant",
        "status": "running",
        "voice_enabled": assistant_state["voice_enabled"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/voice-assistant')
def get_assistant_status():
    """Get enhanced voice assistant status"""
    return jsonify({
        **assistant_state,
        "available_voice_profiles": list(voice_profiles.keys()),
        "routine_routes_count": len(routine_routes),
        "layer2_sync_status": "connected" if voice_assistant.last_layer2_sync else "disconnected",
        "pattern_learning_data": {
            "learned_commands": len(voice_assistant.user_patterns.get("command_frequency", {})),
            "time_patterns": len(voice_assistant.user_patterns.get("time_patterns", {})),
            "destination_preferences": len(voice_assistant.user_patterns.get("destination_preferences", {}))
        }
    })

@app.route('/api/start-listening', methods=['POST'])
def start_listening():
    """Start enhanced voice recognition"""
    voice_assistant.start_listening()
    return jsonify({
        "message": "Enhanced voice assistant started with anticipatory intelligence",
        "status": "success",
        "features_enabled": {
            "anticipatory_interface": assistant_state["anticipatory_enabled"],
            "sentiment_detection": assistant_state["sentiment_detection_enabled"],
            "pattern_learning": assistant_state["pattern_learning_active"],
            "multi_voice": True
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stop-listening', methods=['POST'])
def stop_listening():
    """Stop voice recognition"""
    voice_assistant.stop_listening()
    return jsonify({
        "message": "Enhanced voice assistant stopped",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Make the assistant speak with specified voice profile"""
    data = request.get_json()
    text = data.get('text', '')
    voice_profile = data.get('voice_profile', 'DriverVoice')
    
    if text:
        # Apply requested voice profile
        if voice_profile in voice_profiles:
            voice_assistant.apply_voice_profile(voice_profile)
        
        voice_assistant._speak(text)
        
        # Return to default profile
        voice_assistant.apply_voice_profile("DriverVoice")
        
        return jsonify({
            "message": f"Speaking with {voice_profile}: {text}",
            "status": "success",
            "voice_profile_used": voice_profile,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "No text provided",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/process-command', methods=['POST'])
def process_text_command():
    """Process a text command with enhanced features"""
    data = request.get_json()
    command = data.get('command', '')
    simulate_voice_profile = data.get('simulate_voice_profile', True)
    
    if command:
        # Simulate voice profile selection if requested
        if simulate_voice_profile:
            voice_profile = voice_assistant._select_voice_profile(command)
            voice_assistant.apply_voice_profile(voice_profile)
        
        # Analyze sentiment
        voice_assistant._analyze_sentiment(command)
        
        # Learn patterns
        voice_assistant._learn_user_patterns(command)
        
        response = voice_assistant._execute_command(command)
        assistant_state["last_command"] = command
        assistant_state["last_response"] = response
        assistant_state["timestamp"] = datetime.now().isoformat()
        
        # Return to default profile
        voice_assistant.apply_voice_profile("DriverVoice")
        
        return jsonify({
            "command": command,
            "response": response,
            "voice_profile_used": voice_assistant.assistant_state.get("current_voice_profile", "DriverVoice"),
            "sentiment_analysis": {
                "fatigue_detected": assistant_state["driver_fatigue_detected"]
            },
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "No command provided",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/voice-profiles', methods=['GET', 'POST'])
def manage_voice_profiles():
    """Get or set voice profiles"""
    if request.method == 'GET':
        return jsonify({
            "voice_profiles": {name: {
                "name": profile.name,
                "rate": profile.rate,
                "volume": profile.volume,
                "tone_description": profile.tone_description
            } for name, profile in voice_profiles.items()},
            "current_profile": assistant_state.get("current_voice_profile", "DriverVoice")
        })
    else:
        data = request.get_json()
        profile_name = data.get('profile_name', 'DriverVoice')
        
        if profile_name in voice_profiles:
            voice_assistant.apply_voice_profile(profile_name)
            return jsonify({
                "message": f"Voice profile changed to {profile_name}",
                "current_profile": profile_name,
                "profile_details": voice_profiles[profile_name].tone_description,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "error": f"Voice profile '{profile_name}' not found",
                "available_profiles": list(voice_profiles.keys()),
                "timestamp": datetime.now().isoformat()
            }), 400

@app.route('/api/anticipatory-settings', methods=['GET', 'POST'])
def manage_anticipatory_settings():
    """Get or update anticipatory interface settings"""
    if request.method == 'GET':
        return jsonify({
            "anticipatory_enabled": assistant_state["anticipatory_enabled"],
            "routine_routes": [{
                "name": route.name,
                "start_location": route.start_location,
                "end_location": route.end_location,
                "typical_times": route.typical_times,
                "days_of_week": route.days_of_week,
                "usage_count": route.usage_count,
                "last_used": route.last_used
            } for route in routine_routes],
            "last_anticipatory_action": assistant_state.get("last_anticipatory_action")
        })
    else:
        data = request.get_json()
        assistant_state["anticipatory_enabled"] = data.get("anticipatory_enabled", True)
        assistant_state["pattern_learning_active"] = data.get("pattern_learning_active", True)
        
        return jsonify({
            "message": "Anticipatory settings updated",
            "anticipatory_enabled": assistant_state["anticipatory_enabled"],
            "pattern_learning_active": assistant_state["pattern_learning_active"],
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/sentiment-status', methods=['GET', 'POST'])
def manage_sentiment_detection():
    """Get or update sentiment detection settings"""
    if request.method == 'GET':
        return jsonify({
            "sentiment_detection_enabled": assistant_state["sentiment_detection_enabled"],
            "driver_fatigue_detected": assistant_state["driver_fatigue_detected"],
            "layer2_integration": {
                "connected": voice_assistant.last_layer2_sync is not None,
                "last_sync": voice_assistant.last_layer2_sync.isoformat() if voice_assistant.last_layer2_sync else None
            },
            "layer4_integration": layer_config["integration_enabled"]
        })
    else:
        data = request.get_json()
        assistant_state["sentiment_detection_enabled"] = data.get("sentiment_detection_enabled", True)
        assistant_state["driver_fatigue_detected"] = data.get("driver_fatigue_detected", False)
        
        return jsonify({
            "message": "Sentiment detection settings updated",
            "sentiment_detection_enabled": assistant_state["sentiment_detection_enabled"],
            "driver_fatigue_detected": assistant_state["driver_fatigue_detected"],
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/trigger-anticipatory', methods=['POST'])
def trigger_anticipatory_test():
    """Manually trigger anticipatory navigation (for testing)"""
    data = request.get_json()
    route_name = data.get('route_name', 'Home to Office')
    
    # Find the route
    target_route = None
    for route in routine_routes:
        if route.name == route_name:
            target_route = route
            break
    
    if target_route:
        voice_assistant._trigger_anticipatory_navigation(target_route)
        return jsonify({
            "message": f"Anticipatory navigation triggered for {route_name}",
            "route": route_name,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": f"Route '{route_name}' not found",
            "available_routes": [route.name for route in routine_routes],
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/layer-integration')
def get_layer_integration_status():
    """Get integration status with other layers"""
    return jsonify({
        "layer2_integration": {
            "enabled": layer_config["integration_enabled"],
            "url": layer_config["layer2_url"],
            "connected": voice_assistant.last_layer2_sync is not None,
            "last_sync": voice_assistant.last_layer2_sync.isoformat() if voice_assistant.last_layer2_sync else None,
            "sync_interval": layer_config["data_sync_interval"]
        },
        "layer4_integration": {
            "enabled": layer_config["integration_enabled"],
            "url": layer_config["layer4_url"]
        },
        "current_data": {
            "vehicle_metrics_available": "vehicle_metrics" in voice_assistant.layer2_data,
            "alerts_count": len(voice_assistant.layer2_data.get("alerts", []))
        }
    })

@app.route('/api/user-patterns')
def get_user_patterns():
    """Get learned user patterns"""
    return jsonify({
        "pattern_learning_active": assistant_state["pattern_learning_active"],
        "patterns": {
            "command_frequency": dict(list(voice_assistant.user_patterns.get("command_frequency", {}).items())[:10]),  # Top 10
            "time_patterns": {hour: len(commands) for hour, commands in voice_assistant.user_patterns.get("time_patterns", {}).items()},
            "destination_preferences": voice_assistant.user_patterns.get("destination_preferences", {}),
            "preference_learning": voice_assistant.user_patterns.get("preference_learning", {})
        },
        "total_learned_commands": len(voice_assistant.user_patterns.get("command_frequency", {})),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/toggle-voice', methods=['POST'])
def toggle_voice():
    """Toggle voice output on/off (legacy compatibility)"""
    assistant_state["voice_enabled"] = not assistant_state["voice_enabled"]
    return jsonify({
        "message": f"Voice output {'enabled' if assistant_state['voice_enabled'] else 'disabled'}",
        "voice_enabled": assistant_state["voice_enabled"],
        "current_voice_profile": assistant_state.get("current_voice_profile", "DriverVoice"),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set recognition language (legacy compatibility)"""
    data = request.get_json()
    language = data.get('language', 'en-US')
    assistant_state["language"] = language
    
    return jsonify({
        "message": f"Language set to {language}",
        "language": language,
        "voice_profiles_available": list(voice_profiles.keys()),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/commands')
def get_available_commands():
    """Get list of available voice commands with enhanced features"""
    commands = {
        "navigation": [
            "Navigate to home",
            "Navigate to work", 
            "Navigate to gym",
            "Get directions to [destination]",
            "Yes (accept anticipatory suggestion)",
            "No (reject anticipatory suggestion)"
        ],
        "media": [
            "Play music",
            "Pause music", 
            "Next song",
            "Previous song",
            "Turn on radio",
            "Volume up/down"
        ],
        "vehicle": [
            "What's my speed?",
            "Check fuel level",
            "Vehicle status",
            "Engine temperature"
        ],
        "climate": [
            "Increase temperature",
            "Decrease temperature", 
            "Turn on air conditioning",
            "Set to auto mode"
        ],
        "fatigue_management": [
            "I'm tired",
            "I need a break",
            "Find rest stops"
        ],
        "voice_control": [
            "Change to driver voice",
            "Change to passenger voice",
            "Change to navigation voice",
            "Change to alert voice"
        ],
        "learning": [
            "Remember this route",
            "Learn my routine",
            "What are my patterns?"
        ],
        "general": [
            "Help",
            "What can you do?",
            "What features do you have?"
        ]
    }
    
    return jsonify({
        "available_commands": commands,
        "enhanced_features": [
            "Anticipatory navigation suggestions",
            "Multi-voice profiles (DriverVoice, PassengerVoice, NavigationVoice, AlertVoice)",
            "Sentiment detection and fatigue monitoring",
            "Pattern learning and routine recognition",
            "Layer 2 data integration for real-time vehicle status",
            "Layer 4 integration for ambient design control"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    return jsonify({
        "status": "healthy",
        "layer": "Layer 3 - Enhanced AI Voice Assistant",
        "core_features": {
            "listening": assistant_state["is_listening"],
            "voice_enabled": assistant_state["voice_enabled"],
            "current_voice_profile": assistant_state.get("current_voice_profile", "DriverVoice")
        },
        "enhanced_features": {
            "anticipatory_enabled": assistant_state["anticipatory_enabled"],
            "sentiment_detection": assistant_state["sentiment_detection_enabled"],
            "pattern_learning": assistant_state["pattern_learning_active"],
            "fatigue_detected": assistant_state["driver_fatigue_detected"]
        },
        "integration_status": {
            "layer2_connected": voice_assistant.last_layer2_sync is not None,
            "layer4_enabled": layer_config["integration_enabled"]
        },
        "learned_data": {
            "routine_routes": len(routine_routes),
            "user_patterns": len(voice_assistant.user_patterns.get("command_frequency", {}))
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚗 Starting Enhanced Infotainment System - Layer 3 AI Voice Assistant")
    print("=" * 70)
    print("🎯 ENHANCED FEATURES:")
    print("   • Anticipatory Interface Logic with Pattern Learning")
    print("   • Sentiment Detection & Driver Fatigue Monitoring") 
    print("   • Multi-Voice Simulation (Driver/Passenger/Navigation/Alert)")
    print("   • Layer 2 Data Integration for Real-time Vehicle Metrics")
    print("   • Layer 4 Communication for Ambient Design Control")
    print("   • Routine Route Recognition & Proactive Suggestions")
    print("   • Advanced Pattern Learning & User Preference Adaptation")
    print()
    print("🔗 LAYER INTEGRATION:")
    print(f"   • Layer 2 (Data Monitoring): {layer_config['layer2_url']}")
    print(f"   • Layer 4 (Infotainment Control): {layer_config['layer4_url']}")
    print()
    print("📡 API ENDPOINTS:")
    print("   Core Features:")
    print("   - GET  /api/voice-assistant       (Enhanced status)")
    print("   - POST /api/start-listening       (Start with anticipatory)")
    print("   - POST /api/stop-listening        (Stop enhanced features)")
    print("   - POST /api/speak                 (Multi-voice TTS)")
    print("   - POST /api/process-command       (Enhanced processing)")
    print("   - GET  /api/commands              (Extended command list)")
    print("   - GET  /api/health                (Comprehensive health)")
    print()
    print("   Enhanced Features:")
    print("   - GET/POST /api/voice-profiles    (Multi-voice management)")
    print("   - GET/POST /api/anticipatory-settings (Pattern learning)")
    print("   - GET/POST /api/sentiment-status  (Fatigue detection)")
    print("   - POST /api/trigger-anticipatory   (Test anticipatory)")
    print("   - GET  /api/layer-integration     (Integration status)")
    print("   - GET  /api/user-patterns         (Learned patterns)")
    print()
    print("   Legacy Compatibility:")
    print("   - POST /api/toggle-voice")
    print("   - POST /api/set-language")
    print()
    print("🎙️  VOICE PROFILES AVAILABLE:")
    for name, profile in voice_profiles.items():
        print(f"   • {name}: {profile.tone_description}")
    print()
    print("🛣️  ROUTINE ROUTES CONFIGURED:")
    for route in routine_routes:
        print(f"   • {route.name}: {route.start_location} → {route.end_location}")
        print(f"     Times: {', '.join(route.typical_times)} | Days: {', '.join(route.days_of_week[:3])}...")
    print()
    print("⚠️  REQUIREMENTS:")
    print("   Install: pip install SpeechRecognition pyttsx3 pyaudio flask flask-cors requests")
    print("   Note: Requires microphone access and speech recognition libraries")
    print()
    print("🚀 Starting Enhanced Voice Assistant Server on http://localhost:5003")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5003)
