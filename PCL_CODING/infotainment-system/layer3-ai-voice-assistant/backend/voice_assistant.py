from flask import Flask, jsonify, request
from flask_cors import CORS
import speech_recognition as sr
import pyttsx3
import threading
import json
import time
from datetime import datetime
import queue
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice assistant state
assistant_state = {
    "is_listening": False,
    "is_speaking": False,
    "last_command": "",
    "last_response": "",
    "voice_enabled": True,
    "language": "en-US",
    "timestamp": datetime.now().isoformat()
}

# Command processing queue
command_queue = queue.Queue()
response_queue = queue.Queue()

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.listening_thread = None
        self.processing_thread = None
        self.is_running = False
        
        # Configure TTS
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def start_listening(self):
        """Start voice recognition"""
        if not self.is_running:
            self.is_running = True
            self.listening_thread = threading.Thread(target=self._listen_loop)
            self.processing_thread = threading.Thread(target=self._process_commands)
            self.listening_thread.daemon = True
            self.processing_thread.daemon = True
            self.listening_thread.start()
            self.processing_thread.start()
            logger.info("Voice assistant started listening")
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.is_running = False
        assistant_state["is_listening"] = False
        logger.info("Voice assistant stopped listening")
    
    def _listen_loop(self):
        """Main listening loop"""
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
    
    def _process_commands(self):
        """Process voice commands"""
        while self.is_running:
            try:
                if not command_queue.empty():
                    command = command_queue.get()
                    response = self._execute_command(command)
                    response_queue.put(response)
                    
                    if assistant_state["voice_enabled"]:
                        self._speak(response)
                
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def _execute_command(self, command):
        """Execute voice command and return response"""
        command_lower = command.lower()
        
        # Navigation commands
        if any(word in command_lower for word in ["navigate", "directions", "route"]):
            return self._handle_navigation_command(command)
        
        # Media commands
        elif any(word in command_lower for word in ["play", "music", "song", "radio"]):
            return self._handle_media_command(command)
        
        # Vehicle information
        elif any(word in command_lower for word in ["speed", "fuel", "temperature", "status"]):
            return self._handle_vehicle_info_command(command)
        
        # Climate control
        elif any(word in command_lower for word in ["temperature", "climate", "air", "heat", "cool"]):
            return self._handle_climate_command(command)
        
        # Phone commands
        elif any(word in command_lower for word in ["call", "phone", "dial"]):
            return self._handle_phone_command(command)
        
        # General help
        elif any(word in command_lower for word in ["help", "what can you do"]):
            return self._handle_help_command()
        
        else:
            return f"I didn't understand the command: {command}. Please try again or say 'help' for available commands."
    
    def _handle_navigation_command(self, command):
        """Handle navigation-related commands"""
        if "home" in command.lower():
            return "Setting navigation to home address."
        elif "work" in command.lower():
            return "Setting navigation to work address."
        else:
            return "Please specify a destination for navigation."
    
    def _handle_media_command(self, command):
        """Handle media-related commands"""
        if "play" in command.lower():
            return "Playing music from your preferred playlist."
        elif "pause" in command.lower():
            return "Music paused."
        elif "next" in command.lower():
            return "Skipping to next track."
        elif "previous" in command.lower():
            return "Going back to previous track."
        elif "radio" in command.lower():
            return "Switching to radio mode."
        else:
            return "Media command executed."
    
    def _handle_vehicle_info_command(self, command):
        """Handle vehicle information requests"""
        if "speed" in command.lower():
            return "Current speed is 65 miles per hour."
        elif "fuel" in command.lower():
            return "Fuel level is at 75 percent."
        elif "temperature" in command.lower():
            return "Engine temperature is normal at 195 degrees Fahrenheit."
        elif "status" in command.lower():
            return "All vehicle systems are operating normally."
        else:
            return "Vehicle information retrieved."
    
    def _handle_climate_command(self, command):
        """Handle climate control commands"""
        if "increase" in command.lower() or "warmer" in command.lower():
            return "Increasing cabin temperature."
        elif "decrease" in command.lower() or "cooler" in command.lower():
            return "Decreasing cabin temperature."
        elif "air conditioning" in command.lower() or "ac" in command.lower():
            return "Air conditioning turned on."
        else:
            return "Climate control adjusted."
    
    def _handle_phone_command(self, command):
        """Handle phone-related commands"""
        return "Phone functionality would be integrated with your device's contacts."
    
    def _handle_help_command(self):
        """Provide help information"""
        return ("I can help you with navigation, music control, vehicle information, "
                "climate control, and phone calls. What would you like me to do?")
    
    def _speak(self, text):
        """Convert text to speech"""
        try:
            assistant_state["is_speaking"] = True
            assistant_state["last_response"] = text
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            assistant_state["is_speaking"] = False
            logger.info(f"Spoke: {text}")
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            assistant_state["is_speaking"] = False

# Initialize voice assistant
voice_assistant = VoiceAssistant()

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
    """Get voice assistant status"""
    return jsonify(assistant_state)

@app.route('/api/start-listening', methods=['POST'])
def start_listening():
    """Start voice recognition"""
    voice_assistant.start_listening()
    return jsonify({
        "message": "Voice assistant started listening",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stop-listening', methods=['POST'])
def stop_listening():
    """Stop voice recognition"""
    voice_assistant.stop_listening()
    return jsonify({
        "message": "Voice assistant stopped listening",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Make the assistant speak provided text"""
    data = request.get_json()
    text = data.get('text', '')
    
    if text:
        voice_assistant._speak(text)
        return jsonify({
            "message": f"Speaking: {text}",
            "status": "success",
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
    """Process a text command (for testing without voice)"""
    data = request.get_json()
    command = data.get('command', '')
    
    if command:
        response = voice_assistant._execute_command(command)
        assistant_state["last_command"] = command
        assistant_state["last_response"] = response
        assistant_state["timestamp"] = datetime.now().isoformat()
        
        return jsonify({
            "command": command,
            "response": response,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "No command provided",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 400

@app.route('/api/toggle-voice', methods=['POST'])
def toggle_voice():
    """Toggle voice output on/off"""
    assistant_state["voice_enabled"] = not assistant_state["voice_enabled"]
    return jsonify({
        "message": f"Voice output {'enabled' if assistant_state['voice_enabled'] else 'disabled'}",
        "voice_enabled": assistant_state["voice_enabled"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set recognition language"""
    data = request.get_json()
    language = data.get('language', 'en-US')
    assistant_state["language"] = language
    
    return jsonify({
        "message": f"Language set to {language}",
        "language": language,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/commands')
def get_available_commands():
    """Get list of available voice commands"""
    commands = {
        "navigation": [
            "Navigate to home",
            "Navigate to work",
            "Get directions to [destination]"
        ],
        "media": [
            "Play music",
            "Pause music",
            "Next song",
            "Previous song",
            "Turn on radio"
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
            "Turn on air conditioning"
        ],
        "general": [
            "Help",
            "What can you do?"
        ]
    }
    
    return jsonify({
        "available_commands": commands,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "layer": "Layer 3 - AI Voice Assistant",
        "listening": assistant_state["is_listening"],
        "voice_enabled": assistant_state["voice_enabled"],
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Infotainment System - Layer 3 AI Voice Assistant")
    print("Available endpoints:")
    print("- GET  /api/voice-assistant")
    print("- POST /api/start-listening")
    print("- POST /api/stop-listening")
    print("- POST /api/speak")
    print("- POST /api/process-command")
    print("- POST /api/toggle-voice")
    print("- POST /api/set-language")
    print("- GET  /api/commands")
    print("- GET  /api/health")
    print("\nNote: This requires microphone access and speech recognition libraries")
    print("Install required packages: pip install SpeechRecognition pyttsx3 pyaudio")
    print("\nStarting server on http://localhost:5003")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
