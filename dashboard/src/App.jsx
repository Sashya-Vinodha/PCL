import React, { useState, useEffect } from 'react';
import MapWidget from './components/MapWidget';
import MediaPlayer from './components/MediaPlayer';
import carImage from './assets/car.png'; // <-- IMPORTING YOUR LOCAL CAR IMAGE

// 100% Glassmorphism Style
const glassStyle = {
  background: 'rgba(30, 35, 50, 0.45)', // Deep tinted glass
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
    odometer: 15235
  });

  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [notification, setNotification] = useState({ show: false, message: '', color: '' });
  const [search, setSearch] = useState({ from: 'Current Location', to: 'Chennai' });
  const [routePath, setRoutePath] = useState([]);
  const [currentPathIndex, setCurrentPathIndex] = useState(0);
  const [currentTime, setCurrentTime] = useState('');

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
    ws.onopen = () => setConnectionStatus('Connected');
    ws.onmessage = (event) => setVehicleData(JSON.parse(event.data));
    ws.onclose = () => setConnectionStatus('Disconnected');
    return () => ws.close();
  }, []);

  // Smart Notifications
  useEffect(() => {
    let msg = ''; let color = '';
    if (vehicleData.harsh_driving) { msg = '⚠️ Harsh Driving Detected!'; color = 'rgba(255, 152, 0, 0.8)'; } 
    else if (vehicleData.harsh_braking) { msg = '🛑 Harsh Braking!'; color = 'rgba(255, 152, 0, 0.8)'; }

    if (msg) {
      setNotification({ show: true, message: msg, color: color });
      const timer = setTimeout(() => setNotification({ show: false, message: '', color: '' }), 5000);
      return () => clearTimeout(timer);
    }
  }, [vehicleData.harsh_driving, vehicleData.harsh_braking]);

  const handleMapClick = async (lat, lng) => {
    try {
      await fetch('http://127.0.0.1:8000/api/update-state', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...vehicleData, latitude: lat, longitude: lng }),
      });
    } catch (e) { console.error(e); }
  };

  const startTrip = async () => {
    if(!search.to) return;
    try {
      const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${search.to}`);
      const geoData = await geoRes.json();
      const dest = { lat: geoData[0].lat, lon: geoData[0].lon };

      const routeRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${vehicleData.longitude},${vehicleData.latitude};${dest.lon},${dest.lat}?overview=full&geometries=geojson`);
      const routeData = await routeRes.json();
      
      const coords = routeData.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
      setRoutePath(coords);
      setCurrentPathIndex(0);

      await fetch('http://127.0.0.1:8000/api/update-state', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...vehicleData, is_navigating: true }),
      });
    } catch (e) { alert("Route not found."); }
  };

  // App Background with vibrant blurred orbs (simulating the image)
  const appBackgroundStyle = {
    height: '100vh',
    width: '100vw',
    backgroundColor: '#0d1117',
    backgroundImage: `
      radial-gradient(circle at 30% 70%, rgba(65, 105, 225, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 40%, rgba(0, 255, 200, 0.1) 0%, transparent 40%),
      radial-gradient(circle at 10% 20%, rgba(138, 43, 226, 0.1) 0%, transparent 40%)
    `,
    color: '#fff',
    fontFamily: '"Inter", sans-serif',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px 30px',
    boxSizing: 'border-box',
    overflow: 'hidden'
  };

  return (
    <div style={appBackgroundStyle}>
      
      {/* SMART NOTIFICATION BANNER */}
      {notification.show && !vehicleData.emergency_trigger && (
        <div style={{ ...glassStyle, position: 'absolute', top: '80px', left: '50%', transform: 'translateX(-50%)', padding: '15px 30px', zIndex: 100, backgroundColor: notification.color }}>
          {notification.message}
        </div>
      )}

      {/* TOP STATUS BAR */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', padding: '0 10px' }}>
        <div style={{ fontSize: '22px', fontWeight: 'bold', letterSpacing: '1px', opacity: 0.9 }}>AI INFOTAINMENT SYSTEM</div>
        
        <div style={{ fontSize: '24px', fontWeight: '400', letterSpacing: '2px', position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
          {currentTime}
        </div>
        
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', opacity: 0.9, fontSize: '22px' }}>
          <span style={{ color: vehicleData.fuel_level > 20 ? '#4caf50' : '#ff4444' }}>🔋</span>
          <span style={{ color: '#4169E1' }}>📶</span>
          <span style={{ color: '#4169E1' }}>🌐</span>
        </div>
      </div>

      {/* MIDDLE GRID (Map + Widgets) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2.5fr 1fr', gap: '25px', flex: 1, minHeight: 0 }}>
        
        {/* MAP SECTION */}
        <div style={{ ...glassStyle, display: 'flex', flexDirection: 'column', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', zIndex: 2 }}>
            <input 
              placeholder="Search Destination..." 
              value={search.to} 
              onChange={(e) => setSearch({...search, to: e.target.value})} 
              style={{ flex: 1, padding: '12px 20px', borderRadius: '20px', border: 'none', background: 'rgba(255,255,255,0.05)', color: '#fff', outline: 'none', boxShadow: 'inset 0 2px 5px rgba(0,0,0,0.2)' }} 
            />
            <button onClick={startTrip} style={{ background: '#4169E1', border: 'none', color: '#fff', padding: '0 30px', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 4px 15px rgba(65, 105, 225, 0.4)' }}>GO</button>
          </div>
          
          <div style={{ flex: 1, borderRadius: '16px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)' }}>
             <MapWidget latitude={vehicleData.latitude} longitude={vehicleData.longitude} routePath={routePath} isNavigating={vehicleData.is_navigating} onLocationChange={handleMapClick} />
          </div>

          {/* EMERGENCY OVERLAY */}
          {vehicleData.emergency_trigger && (
             <div style={{ ...glassStyle, position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(200, 0, 0, 0.85)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 10 }}>
                <div style={{ fontSize: '60px', animation: 'pulse 1s infinite' }}>🚨</div>
                <h1 style={{ margin: '10px 0', letterSpacing: '2px' }}>SOS DISPATCHED</h1>
                <p>LAT: {vehicleData.latitude.toFixed(4)} | LNG: {vehicleData.longitude.toFixed(4)}</p>
             </div>
          )}
        </div>

        {/* RIGHT SIDE WIDGETS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
          
          {/* WEATHER WIDGET */}
          <div style={{ ...glassStyle, padding: '25px 30px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ opacity: 0.7, fontSize: '14px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                   <span style={{ color: '#4169E1' }}>📍</span> Current Location
                </div>
                <div style={{ fontSize: '50px', fontWeight: '300', lineHeight: '1' }}>{Math.round(vehicleData.temperature)}°C</div>
                <div style={{ opacity: 0.9, fontSize: '15px', marginTop: '10px' }}>{vehicleData.weather_desc}</div>
              </div>
              <div style={{ fontSize: '65px', filter: 'drop-shadow(0 0 10px rgba(255, 200, 0, 0.4))' }}>{vehicleData.is_raining ? '🌧️' : '☀️'}</div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '30px', opacity: 0.8, fontSize: '14px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '15px' }}>
              <div style={{ textAlign: 'center' }}>🌧️<br/><span style={{opacity: 0.7, fontSize: '12px'}}>Tue</span></div>
              <div style={{ textAlign: 'center' }}>☀️<br/><span style={{opacity: 0.7, fontSize: '12px'}}>Wed</span></div>
              <div style={{ textAlign: 'center' }}>⛅<br/><span style={{opacity: 0.7, fontSize: '12px'}}>Thu</span></div>
            </div>
          </div>

          {/* CAR STATUS WIDGET */}
          <div style={{ ...glassStyle, padding: '30px', flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
            <div style={{ zIndex: 2, display: 'flex', flexDirection: 'column', gap: '25px', width: '50%' }}>
              <div>
                <div style={{ opacity: 0.7, fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: '#4caf50', fontSize: '20px' }}>🔌</span> Power :
                </div>
                <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{vehicleData.fuel_level.toFixed(0)}%</div>
              </div>
              <div>
                <div style={{ opacity: 0.7, fontSize: '16px' }}>Kilometer :</div>
                <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{vehicleData.odometer.toFixed(0)} km</div>
              </div>
              <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', opacity: 0.9 }}>
                <span style={{ color: '#4169E1' }}>✔️</span> The vehicle is in good condition
              </div>
            </div>
            
            {/* The Transparent Car Overlay Using Imported Local Image */}
            <img 
               src={carImage} 
               alt="Car" 
               style={{ 
                  position: 'absolute', 
                  right: '-70px', 
                  top: '40%', 
                  transform: 'translateY(-50%)', 
                  width: '90%', 
                  objectFit: 'contain',
                  filter: 'drop-shadow(-10px 15px 15px rgba(0,0,0,0.5))',
                  pointerEvents: 'none'
               }} 
            />
          </div>

        </div>
      </div>

      {/* BOTTOM MEDIA PLAYER */}
      <div style={{ marginTop: '25px', height: '110px' }}>
        <MediaPlayer />
      </div>

    </div>
  );
}

export default App;