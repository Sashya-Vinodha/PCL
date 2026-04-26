import React, { useState, useEffect, useRef } from 'react';
import { updateVehicleState } from './api';

function App() {
  const [vehicleState, setVehicleState] = useState({
    speed: 0, battery: 100, is_raining: false, emergency_trigger: false, 
    harsh_braking: false, harsh_driving: false, 
    latitude: 12.9716, longitude: 77.5946, odometer: 15234.5,
    is_navigating: false, fuel_level: 100,
    tire_pressure: 32, // NEW
    engine_temp: 90    // NEW
  });

  const [autoDrive, setAutoDrive] = useState(false);
  const [targetSpeed, setTargetSpeed] = useState(69); 

  const latestNetworkState = useRef(null);
  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/dashboard');
    ws.onmessage = (event) => {
      latestNetworkState.current = JSON.parse(event.data);
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    updateVehicleState(vehicleState);
  }, [vehicleState]);

  // LIVE PHYSICS ENGINE
  useEffect(() => {
    const interval = setInterval(() => {
      setVehicleState(prev => {
        let currentSpeed = prev.speed;
        let desiredSpeed = targetSpeed;

        if (prev.harsh_braking) {
          desiredSpeed = 0;
        } else if (autoDrive) {
          desiredSpeed = targetSpeed + (Math.sin(Date.now() / 1000) * 5);
        }

        const speedDifference = Math.abs(currentSpeed - desiredSpeed);
        const step = targetSpeed > 0 ? (targetSpeed / 50) : 2; 

        if (speedDifference <= step) {
          currentSpeed = desiredSpeed; 
        } else if (currentSpeed < desiredSpeed) {
          currentSpeed += step; 
        } else if (currentSpeed > desiredSpeed) {
          currentSpeed -= step; 
        }

        const distanceAdded = (currentSpeed / 3600) * 0.1;
        const net = latestNetworkState.current || {};

        return {
          ...prev,
          speed: Math.max(0, Math.round(currentSpeed)), 
          odometer: prev.odometer + distanceAdded,
          battery: prev.battery > 0 ? prev.battery - (currentSpeed > 0 ? 0.0005 : 0) : 0,
          latitude: net.latitude !== undefined ? net.latitude : prev.latitude,
          longitude: net.longitude !== undefined ? net.longitude : prev.longitude,
          is_navigating: net.is_navigating !== undefined ? net.is_navigating : prev.is_navigating,
          fuel_level: net.fuel_level !== undefined ? net.fuel_level : prev.fuel_level
        };
      });
    }, 100); 

    return () => clearInterval(interval);
  }, [targetSpeed, autoDrive]); 

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setVehicleState(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' || name === 'tire_pressure' || name === 'engine_temp' ? Number(value) : value)
    }));
  };

  const triggerCrash = () => setVehicleState(prev => ({ ...prev, emergency_trigger: true }));
  const resetCrash = () => setVehicleState(prev => ({ ...prev, emergency_trigger: false, harsh_braking: false, harsh_driving: false }));

  return (
    <div style={{ padding: '30px', fontFamily: 'sans-serif', maxWidth: '500px', margin: '0 auto', backgroundColor: '#121212', color: 'white', height: '100vh', overflowY: 'auto' }}>
      <h2>Control Room (UI #1)</h2>
      
      <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#222', borderRadius: '8px' }}>
         <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontWeight: 'bold', color: autoDrive ? '#4caf50' : '#fff' }}>
           <input type="checkbox" checked={autoDrive} onChange={(e) => setAutoDrive(e.target.checked)} style={{ width: '20px', height: '20px' }}/>
           {autoDrive ? '🟢 Auto-Drive Active' : '⚪ Enable Auto-Drive Simulation'}
         </label>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* SPEED CONTROL */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <strong>Target Speed: {targetSpeed} km/h</strong>
          <input type="range" min="0" max="200" value={targetSpeed} onChange={(e) => setTargetSpeed(Number(e.target.value))} disabled={autoDrive} />
        </label>

        {/* TIRE PRESSURE CONTROL */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#222', padding: '15px', borderRadius: '8px' }}>
          <strong>🔘 Tire Pressure: {vehicleState.tire_pressure} PSI</strong>
          <input type="range" name="tire_pressure" min="20" max="45" value={vehicleState.tire_pressure} onChange={handleChange} />
        </label>

        {/* ENGINE TEMP CONTROL */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#222', padding: '15px', borderRadius: '8px' }}>
          <strong style={{ color: vehicleState.engine_temp > 100 ? '#ff4444' : '#fff' }}>
            🌡️ Engine Temp: {vehicleState.engine_temp}°C
          </strong>
          <input type="range" name="engine_temp" min="50" max="130" value={vehicleState.engine_temp} onChange={handleChange} />
        </label>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', background: '#333', padding: '10px', borderRadius: '8px', border: vehicleState.harsh_braking ? '2px solid #ff9800' : '2px solid transparent' }}>
            <input type="checkbox" name="harsh_braking" checked={vehicleState.harsh_braking} onChange={handleChange} />
            Harsh Braking
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', background: '#333', padding: '10px', borderRadius: '8px', border: vehicleState.harsh_driving ? '2px solid #ff4444' : '2px solid transparent' }}>
            <input type="checkbox" name="harsh_driving" checked={vehicleState.harsh_driving} onChange={handleChange} />
            Harsh Driving
          </label>
        </div>

        {/* EMERGENCY SYSTEM */}
        <div style={{ padding: '20px', backgroundColor: '#333', borderRadius: '8px', marginTop: '10px' }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#ff4444' }}>Emergency System</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button onClick={triggerCrash} style={{ backgroundColor: '#ff4444', color: 'white', padding: '15px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>
              🚨 TRIGGER EMERGENCY
            </button>
            <button onClick={resetCrash} style={{ backgroundColor: '#555', color: 'white', padding: '10px', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
              Reset All Alerts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;