import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { LiveStatusStop } from '../types';

interface RouteMapProps {
  stops: LiveStatusStop[];
  currentLat?: number | null;
  currentLng?: number | null;
  trainNumber: string;
  trainName: string;
  isLiveAvailable: boolean;
}

export const RouteMap: React.FC<RouteMapProps> = ({
  stops,
  currentLat,
  currentLng,
  trainNumber,
  trainName,
  isLiveAvailable
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Filter valid coordinates
    const validStops = stops.filter(
      (s) => s.latitude && s.longitude && s.latitude !== 0 && s.longitude !== 0
    );

    if (validStops.length === 0) return;

    // Initialize map if not yet created
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
        scrollWheelZoom: false,
      }).setView([validStops[0].latitude, validStops[0].longitude], 6);

      // CartoDB Dark Matter tiles (modern sleek dark railway theme)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 18,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear existing layers except tiles
    map.eachLayer((layer) => {
      if (!(layer instanceof L.TileLayer)) {
        map.removeLayer(layer);
      }
    });

    const latLngs: L.LatLngExpression[] = validStops.map((s) => [s.latitude, s.longitude]);

    // 1. Draw route railway line
    const routeLine = L.polyline(latLngs, {
      color: '#0284c7',
      weight: 5,
      opacity: 0.85,
      dashArray: '1, 8',
      lineCap: 'round',
    }).addTo(map);

    // Overlay continuous smooth line
    L.polyline(latLngs, {
      color: '#f59e0b',
      weight: 3,
      opacity: 0.9,
    }).addTo(map);

    // 2. Add Station Markers
    validStops.forEach((stop, index) => {
      const isOrigin = index === 0;
      const isDestination = index === validStops.length - 1;
      const isCurrent = stop.status === 'CURRENT';

      const color = isCurrent ? '#f59e0b' : isOrigin ? '#10b981' : isDestination ? '#a855f7' : '#38bdf8';
      const radius = isOrigin || isDestination || isCurrent ? 8 : 5;

      const marker = L.circleMarker([stop.latitude, stop.longitude], {
        radius,
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.95,
      }).addTo(map);

      const popupHtml = `
        <div style="font-family: sans-serif; min-width: 170px;">
          <div style="font-size: 13px; font-weight: bold; color: #0f172a; margin-bottom: 2px;">
            ${stop.station_name} (${stop.station_code})
          </div>
          <div style="font-size: 11px; color: #475569; margin-bottom: 6px;">
            Stop #${stop.stop_sequence} • Day ${stop.day_number} • ${stop.distance_km} km
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 11px; border-top: 1px solid #e2e8f0; padding-top: 4px;">
            <div>Arr: <strong>${stop.scheduled_arrival || 'Origin'}</strong></div>
            <div>Dep: <strong>${stop.scheduled_departure || 'Terminus'}</strong></div>
          </div>
          <div style="margin-top: 4px; font-size: 11px; color: #0284c7; font-weight: bold;">
            Platform: ${stop.platform ? `#${stop.platform}` : 'TBA'}
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);
    });

    // 3. Add Live Train Marker if coordinates are available
    if (isLiveAvailable && currentLat && currentLng) {
      const trainIcon = L.divIcon({
        className: 'custom-live-train-marker',
        html: `
          <div style="position: relative; width: 34px; height: 34px;">
            <div style="position: absolute; inset: 0; border-radius: 9999px; background-color: rgba(245, 158, 11, 0.4); animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
            <div style="position: relative; width: 34px; height: 34px; border-radius: 9999px; background: #0c2340; border: 2.5px solid #f59e0b; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b">
                <path d="M4 15.5C4 17.43 5.57 19 7.5 19L6 20.5v.5h12v-.5L16.5 19c1.93 0 3.5-1.57 3.5-3.5V5c0-3.5-3.58-4-8-4s-8 .5-8 4v10.5zm8 1.5c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm6-7H6V5h12v5z"/>
              </svg>
            </div>
          </div>
        `,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      });

      const liveMarker = L.marker([currentLat, currentLng], { icon: trainIcon }).addTo(map);
      liveMarker.bindPopup(`
        <div style="font-family: sans-serif; min-width: 180px;">
          <div style="color: #b45309; font-weight: 800; font-size: 11px; text-transform: uppercase;">
            ● Live Position Telemetry
          </div>
          <div style="font-size: 13px; font-weight: bold; color: #0f172a; margin-top: 2px;">
            ${trainNumber} - ${trainName}
          </div>
          <div style="font-size: 11px; color: #475569; margin-top: 4px;">
            Track Lat: ${currentLat.toFixed(4)}, Lng: ${currentLng.toFixed(4)}
          </div>
        </div>
      `).openPopup();
    }

    // Fit bounds nicely with padding
    if (latLngs.length > 0) {
      map.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
    }

  }, [stops, currentLat, currentLng, trainNumber, trainName, isLiveAvailable]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 px-2">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse"></span>
          <h4 className="text-sm font-bold text-slate-100">Geospatial Railway Route Map</h4>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Origin
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500"></span> Terminus
          </span>
          {isLiveAvailable && (
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Live Telemetry Marker
            </span>
          )}
        </div>
      </div>

      <div
        ref={mapContainerRef}
        style={{ height: '460px', width: '100%' }}
        className="rounded-xl overflow-hidden border border-slate-800 shadow-inner"
      />
    </div>
  );
};
