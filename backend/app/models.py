from pydantic import BaseModel
from typing import List

class VehicleState(BaseModel):
    speed: int = 0
    battery: float = 100.0
    fuel_level: float = 100.0       # NEW: Fuel/Energy Level
    is_raining: bool = False
    emergency_trigger: bool = False
    emergency_contacts: List[str] = ["Mom (+91-9876543210)", "Dad (+91-8765432109)", "112"]
    harsh_braking: bool = False
    harsh_driving: bool = False
    latitude: float = 12.9716
    longitude: float = 77.5946
    temperature: float = 0.0
    weather_desc: str = "Fetching..."
    odometer: float = 15234.5
    is_navigating: bool = False  
    tire_pressure: float = 32.0   # NEW
    engine_temp: float = 90.0  # NEW: Engine temperature