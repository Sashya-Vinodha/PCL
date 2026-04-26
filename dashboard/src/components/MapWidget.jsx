import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Car Icon for the map
const carIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/744/744465.png',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});

// Component to handle map clicks for teleportation
function MapEvents({ onLocationChange }) {
    useMapEvents({
        click(e) {
            const { lat, lng } = e.latlng;
            console.log("Map Clicked at:", lat, lng);
            onLocationChange(lat, lng);
        },
    });
    return null;
}

// Component to auto-center the map when coordinates change
function MapUpdater({ lat, lng, isNavigating }) {
    const map = useMap();
    useEffect(() => {
        // Only auto-center if we are navigating or if it's a manual teleport
        map.setView([lat, lng], map.getZoom());
    }, [lat, lng]);
    return null;
}

export default function MapWidget({ latitude, longitude, routePath, isNavigating, onLocationChange }) {
    const lat = latitude || 12.9716;
    const lng = longitude || 77.5946;

    return (
        <div style={{ height: '100%', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
            <MapContainer 
                center={[lat, lng]} 
                zoom={13} 
                style={{ height: '100%', width: '100%', backgroundColor: '#1e2130' }}
            >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                
                {/* Enable clicking on the map to teleport */}
                <MapEvents onLocationChange={onLocationChange} />

                {/* The Blue Route Line */}
                {routePath && routePath.length > 0 && (
                    <Polyline positions={routePath} color="#4169E1" weight={6} opacity={0.7} lineCap="round" />
                )}

                {/* The Moving Car or Static Marker */}
                <Marker position={[lat, lng]} icon={isNavigating ? carIcon : new L.Icon.Default()} />
                
                <MapUpdater lat={lat} lng={lng} isNavigating={isNavigating} />
            </MapContainer>
        </div>
    );
}