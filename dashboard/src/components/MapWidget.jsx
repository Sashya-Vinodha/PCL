import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Car Icon for the map
const carIcon = new L.Icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/744/744465.png', // Modern Car Top View
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});

function MapUpdater({ lat, lng }) {
    const map = useMap();
    useEffect(() => { map.setView([lat, lng], map.getZoom()); }, [lat, lng]);
    return null;
}

export default function MapWidget({ latitude, longitude, routePath, isNavigating }) {
    const lat = latitude || 12.9716;
    const lng = longitude || 77.5946;

    return (
        <div style={{ height: '100%', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
            <MapContainer center={[lat, lng]} zoom={14} style={{ height: '100%', width: '100%', backgroundColor: '#1e2130' }}>
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                
                {/* The Blue Route Line */}
                {routePath.length > 0 && (
                    <Polyline positions={routePath} color="#4169E1" weight={6} opacity={0.7} lineCap="round" />
                )}

                {/* The Moving Car or Static Marker */}
                <Marker position={[lat, lng]} icon={isNavigating ? carIcon : new L.Icon.Default()} />
                
                <MapUpdater lat={lat} lng={lng} />
            </MapContainer>
        </div>
    );
}