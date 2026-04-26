import pyttsx3
import threading

voice_lock = threading.Lock()

# TRACK PREVIOUS STATE TO PREVENT SPAMMING
previous_state = {
    "emergency": False,
    "driving": False,
    "braking": False,
    "navigating": False # NEW: Track navigation
}

def speak_task(text):
    with voice_lock:
        try:
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', 150)
            temp_engine.say(text)
            temp_engine.runAndWait()
        except Exception as e:
            print(f"Voice Error: {e}")

def process_ai_triggers(state):
    global previous_state

    # 1. Navigation Trigger (Only speaks ONCE when False -> True)
    if state.is_navigating and not previous_state["navigating"]:
        speak_task("Trip started. Following the safest route to your destination.")

    # 2. Emergency Trigger
    if state.emergency_trigger and not previous_state["emergency"]:
        lat = round(state.latitude, 4)
        lng = round(state.longitude, 4)
        speak_task(f"Accident detected. Calling emergency contacts. Sending live GPS coordinates.")

    # 3. Harsh Driving
    if state.harsh_driving and not previous_state["driving"]:
        speak_task("Harsh driving detected. Please go slow.")
        
    # 4. Harsh Braking
    if state.harsh_braking and not previous_state["braking"]:
        speak_task("Harsh braking detected. Slow down gradually.")

    # Update memory for the next loop so it doesn't repeat!
    previous_state["navigating"] = state.is_navigating
    previous_state["emergency"] = state.emergency_trigger
    previous_state["driving"] = state.harsh_driving
    previous_state["braking"] = state.harsh_braking