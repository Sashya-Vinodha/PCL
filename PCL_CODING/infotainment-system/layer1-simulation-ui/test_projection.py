#!/usr/bin/env python3
"""
Test script for Layer 1 Simulation UI
Tests the POST endpoint for receiving simulation data
"""

import requests
import json
from datetime import datetime

# Test payload - simulates data from Layer 1 UI
test_payload = {
    "speed": 75,
    "rpm": 2500,
    "fuel_level": 68,
    "temperature": 92,
    "gear": "D",
    "drive_mode": "SPORT",
    "battery": 85,
    "odometer": 12543,
    "timestamp": datetime.now().isoformat(),
    "source": "layer1_simulation_ui"
}

def test_projection():
    """Test the vehicle data projection endpoint"""
    print("=" * 60)
    print("TESTING LAYER 1 SIMULATION DATA PROJECTION")
    print("=" * 60)
    
    try:
        # Send POST request
        print("\n📡 Sending simulation data to backend...")
        print(f"Endpoint: http://localhost:5001/api/vehicle-data")
        print(f"Payload:\n{json.dumps(test_payload, indent=2)}\n")
        
        response = requests.post(
            'http://localhost:5001/api/vehicle-data',
            json=test_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        # Check response
        if response.status_code == 200:
            print("✅ SUCCESS! Data projected successfully")
            print(f"\nResponse:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend")
        print("Make sure the backend is running on http://localhost:5001")
        print("\nTo start backend:")
        print("  cd layer1-simulation-ui/backend")
        print("  python3 app.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_projection()
