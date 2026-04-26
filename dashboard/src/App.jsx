import React, { useState, useEffect } from 'react';
import MapWidget from './components/MapWidget';
import MediaPlayer from './components/MediaPlayer';
import carImage from './assets/car.png'; 

// 100% Glassmorphism Style
const glassStyle = {
  background: 'rgba(30, 35, 50, 0.45)', 
  backdropFilter: 'blur(24px)',
  WebkitBackdropFilter: 'blur(24px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '24px',
  boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.25)',
};

function App() {
  const [vehicleData, setVehicleData] = useState({
    speed: 0, fuel_level: 100, is_navigating: false, emergency_trigger: false,
    harsh_braking: false, harsh_driving: false, emergency_contacts: [],
    latitude: 12.9716, longitude: 77.5946, temperature: 32, weather_desc: 'Clear skies. Optimal driving.',
    odometer: 15235, tire_pressure: 32, engine_temp: 90
  });

  const [currentTime, setCurrentTime] = useState('');
  const [search, setSearch] = useState({ to: 'Chennai' });
  const [routePath, setRoutePath] = useState([]);

  // Live Clock
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // WebSocket Connection
  useEffect(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/dashboard');
    ws.onmessage = (event) => setVehicleData(JSON.parse(event.data));
    return () => ws.close();
  }, []);

  const handleMapClick = async (lat, lng) => {
    try {
      await fetch('http://127.0.0.1:8000/api/update-state', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...vehicleData, latitude: lat, longitude: lng }),
      });
    } catch (e) { console.error(e); }
  };

  const appBackgroundStyle = {
    height: '100vh', width: '100vw', backgroundColor: '#0d1117',
    backgroundImage: `radial-gradient(circle at 30% 70%, rgba(65, 105, 225, 0.15) 0%, transparent 50%)`,
    color: '#fff', fontFamily: '"Inter", sans-serif', display: 'flex',
    flexDirection: 'column', padding: '20px 30px', boxSizing: 'border-box', overflow: 'hidden'
  };

  return (
    <div style={appBackgroundStyle}>
      {/* STATUS BAR */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ fontSize: '22px', fontWeight: 'bold' }}>AI INFOTAINMENT SYSTEM</div>
        <div style={{ fontSize: '24px', fontWeight: '400' }}>{currentTime}</div>
        <div style={{ display: 'flex', gap: '20px', fontSize: '22px' }}>🔋 📶 🌐</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2.5fr 1fr', gap: '25px', flex: 1, minHeight: 0 }}>
        
        {/* MAP SECTION - Ensure height: 100% is passed to the container */}
        <div style={{ ...glassStyle, padding: '20px', display: 'flex', flexDirection: 'column', position: 'relative' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <input placeholder="Search..." value={search.to} onChange={(e) => setSearch({...search, to: e.target.value})} style={{ flex: 1, padding: '12px 20px', borderRadius: '20px', border: 'none', background: 'rgba(255,255,255,0.05)', color: '#fff' }} />
            <button style={{ background: '#4169E1', border: 'none', color: '#fff', padding: '0 30px', borderRadius: '20px', fontWeight: 'bold' }}>GO</button>
          </div>
          
          <div style={{ flex: 1, width: '100%', height: '100%', borderRadius: '16px', overflow: 'hidden' }}>
             <MapWidget 
                latitude={vehicleData.latitude} 
                longitude={vehicleData.longitude} 
                routePath={routePath} 
                onLocationChange={handleMapClick} 
             />
          </div>
        </div>

        {/* RIGHT SIDE WIDGETS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
          <div style={{ ...glassStyle, padding: '25px' }}>
            <div style={{ opacity: 0.7, fontSize: '14px' }}>📍 Location</div>
            <div style={{ fontSize: '42px', fontWeight: '300' }}>{Math.round(vehicleData.temperature)}°C</div>
            <div style={{ opacity: 0.9, fontSize: '14px' }}>{vehicleData.weather_desc}</div>
          </div>

          {/* CAR STATUS WIDGET */}
          <div style={{ ...glassStyle, padding: '30px', flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
            <div style={{ zIndex: 2, display: 'flex', flexDirection: 'column', gap: '15px', width: '60%' }}>
              <div>
                <div style={{ opacity: 0.7, fontSize: '13px' }}>Power :</div>
                <div style={{ fontSize: '26px', fontWeight: 'bold' }}>{vehicleData.fuel_level.toFixed(0)}%</div>
              </div>
              <div>
                <div style={{ opacity: 0.7, fontSize: '13px' }}>Kilometer :</div>
                <div style={{ fontSize: '26px', fontWeight: 'bold' }}>{vehicleData.odometer.toFixed(0)} km</div>
              </div>

              {/* TIRE & TEMP STATS */}
              <div style={{ display: 'flex', gap: '20px', marginTop: '10px' }}>
                <div>
                   <div style={{ opacity: 0.6, fontSize: '11px' }}>Tire PSI</div>
                   <div style={{ fontSize: '16px', fontWeight: '600', color: '#4caf50' }}>{vehicleData.tire_pressure}</div>
                </div>
                <div>
                   <div style={{ opacity: 0.6, fontSize: '11px' }}>Engine</div>
                   <div style={{ fontSize: '16px', fontWeight: '600' }}>{vehicleData.engine_temp}°C</div>
                </div>
              </div>
              <div style={{ marginTop: 'auto', fontSize: '12px', opacity: 0.8 }}>✔️ Good Condition</div>
            </div>
            
            <img src={carImage} alt="Car" style={{ position: 'absolute', right: '-80px', top: '50%', transform: 'translateY(-50%)', width: '100%', objectFit: 'contain' }} />
          </div>
        </div>
      </div>

      <div style={{ marginTop: '25px', height: '110px' }}>
        <MediaPlayer />
      </div>
    </div>
  );
}

export default App;