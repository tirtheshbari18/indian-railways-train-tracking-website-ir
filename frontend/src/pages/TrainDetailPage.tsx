import React, { useState, useEffect } from 'react';
import {
  Train as TrainIcon,
  MapPin,
  Clock,
  Navigation,
  Gauge,
  Calendar,
  Bookmark,
  Radio,
  Share2,
  RefreshCw,
  ArrowLeft,
  AlertTriangle,
  Layers,
  Map as MapIcon
} from 'lucide-react';
import { Train, LiveStatusResponse } from '../types';
import { api } from '../services/api';
import { RouteTimeline } from '../components/RouteTimeline';
import { RouteMap } from '../components/RouteMap';
import { StatusBadge } from '../components/StatusBadge';
import { ProvenanceDisclaimer } from '../components/ProvenanceDisclaimer';
import { useSavedTrains } from '../context/SavedTrainsContext';

interface TrainDetailPageProps {
  trainNumber: string;
  onBack: () => void;
  onSelectStation: (code: string) => void;
}

export const TrainDetailPage: React.FC<TrainDetailPageProps> = ({
  trainNumber,
  onBack,
  onSelectStation
}) => {
  const { isSaved, toggleSave } = useSavedTrains();
  const [train, setTrain] = useState<Train | null>(null);
  const [liveStatus, setLiveStatus] = useState<LiveStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string>('mock');
  const [activeView, setActiveView] = useState<'timeline' | 'map'>('timeline');
  const [error, setError] = useState<string | null>(null);

  const fetchDetails = async (provider = selectedProvider) => {
    try {
      setError(null);
      const [trainData, statusData] = await Promise.all([
        api.getTrainDetail(trainNumber),
        api.getLiveStatus(trainNumber, { provider })
      ]);
      setTrain(trainData);
      setLiveStatus(statusData);
    } catch (err: any) {
      setError(err.message || 'Failed to load train details');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchDetails(selectedProvider);
  }, [trainNumber, selectedProvider]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDetails(selectedProvider);
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <div className="text-sm font-semibold text-slate-300">
          Querying CRIS Timetable & Telemetry Stream...
        </div>
        <div className="text-xs text-slate-500 font-mono">Train #{trainNumber}</div>
      </div>
    );
  }

  if (error || !train || !liveStatus) {
    return (
      <div className="p-8 max-w-lg mx-auto bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4 my-12">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">Train Not Found</h3>
        <p className="text-xs text-slate-400">{error || 'Unable to retrieve train records.'}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 text-slate-200 hover:bg-slate-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  const saved = isSaved(train.train_number);

  return (
    <div className="space-y-6 pb-16">
      {/* Top Bar Navigation & Provider Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Search</span>
        </button>

        {/* Live Provider Adapter Selector */}
        <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 p-1.5 rounded-xl text-xs">
          <span className="text-[11px] font-mono text-slate-400 px-2 flex items-center gap-1">
            <Radio className="w-3 h-3 text-amber-500" />
            Provider Feed:
          </span>
          {[
            { id: 'mock', label: 'CRIS NTES Sim (Demo)' },
            { id: 'api', label: 'IR API Gateway' },
            { id: 'null', label: 'Offline / Timetable Only' }
          ].map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedProvider(p.id)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                selectedProvider === p.id
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Train Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono font-extrabold text-xl text-amber-400 bg-slate-950 px-3 py-1 rounded-lg border border-slate-800">
                {train.train_number}
              </span>
              <h1 className="text-xl sm:text-2xl font-extrabold text-white">
                {train.train_name}
              </h1>
              <StatusBadge type="trainType" value={train.train_type} />
            </div>

            <div className="flex items-center gap-2 text-sm text-slate-300 font-mono">
              <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                {train.source_station?.name} ({train.source_station_code})
                {' → '}
                {train.destination_station?.name} ({train.destination_station_code})
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors flex items-center gap-1 text-xs font-semibold"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-amber-400' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            <button
              onClick={() => toggleSave(train)}
              className={`p-2.5 rounded-xl border transition-colors flex items-center gap-1.5 text-xs font-semibold ${
                saved
                  ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
              }`}
            >
              <Bookmark className="w-4 h-4 fill-current" />
              <span>{saved ? 'Saved' : 'Save Train'}</span>
            </button>
          </div>
        </div>

        {/* Train Details Bar */}
        <div className="pt-4 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-slate-400">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Total Distance</div>
            <div className="text-slate-200 font-semibold mt-0.5">{train.total_distance_km} km</div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Scheduled Duration</div>
            <div className="text-slate-200 font-semibold mt-0.5">
              {Math.floor(train.duration_minutes / 60)}h {train.duration_minutes % 60}m
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Pantry Car</div>
            <div className="text-emerald-400 font-semibold mt-0.5">
              {train.pantry_car ? 'Available ✓' : 'Not Available'}
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Pair Return Train</div>
            <div className="text-amber-400 font-mono font-semibold mt-0.5">
              {train.return_train_number ? `#${train.return_train_number}` : 'None'}
            </div>
          </div>
        </div>
      </div>

      {/* Live Running Telemetry Card */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping"></span>
              <h2 className="text-sm uppercase tracking-wider font-extrabold text-slate-200">
                Live Running Status & Telemetry
              </h2>
            </div>
            <p className="text-base font-semibold text-slate-100">
              {liveStatus.current_status_description}
            </p>
          </div>

          <div>
            <StatusBadge
              type="runningStatus"
              value={liveStatus.status_summary}
              delayMinutes={liveStatus.delay_minutes}
            />
          </div>
        </div>

        {/* Telemetry Metrics Grid */}
        {liveStatus.is_live_available && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>Current Delay</span>
              </div>
              <div className="text-base font-mono font-bold mt-1 text-amber-400">
                {liveStatus.delay_minutes === 0 ? 'Right Time' : `+${liveStatus.delay_minutes} mins late`}
              </div>
            </div>

            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 flex items-center gap-1">
                <Gauge className="w-3 h-3 text-slate-400" />
                <span>Instant Speed</span>
              </div>
              <div className="text-base font-mono font-bold mt-1 text-slate-200">
                {liveStatus.speed_kmh ? `${Math.round(liveStatus.speed_kmh)} km/h` : 'Station Halt'}
              </div>
            </div>

            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 flex items-center gap-1">
                <MapPin className="w-3 h-3 text-emerald-400" />
                <span>Last Reported</span>
              </div>
              <div className="text-xs font-semibold mt-1 text-slate-200 truncate">
                {liveStatus.last_reported_station || 'Origin'}
              </div>
            </div>

            <div>
              <div className="text-[10px] uppercase font-mono text-slate-500 flex items-center gap-1">
                <Navigation className="w-3 h-3 text-blue-400" />
                <span>Next Station & ETA</span>
              </div>
              <div className="text-xs font-semibold mt-1 text-slate-200 truncate">
                {liveStatus.next_station ? `${liveStatus.next_station} (${liveStatus.eta_next_station || ''})` : 'Terminus'}
              </div>
            </div>
          </div>
        )}

        {/* Journey Progress Bar */}
        {liveStatus.is_live_available && (
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>{train.source_station_code} (Origin)</span>
              <span className="font-bold text-amber-400">{liveStatus.progress_percentage}% Journey Completed</span>
              <span>{train.destination_station_code} (Terminus)</span>
            </div>
            <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-amber-600 rounded-full transition-all duration-700"
                style={{ width: `${liveStatus.progress_percentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Data Provenance Disclaimer */}
        <ProvenanceDisclaimer
          provenance={liveStatus.data_provenance}
          providerName={liveStatus.provider_name}
          lastUpdated={liveStatus.last_updated_timestamp}
          isLiveAvailable={liveStatus.is_live_available}
        />
      </div>

      {/* Tabs: Route Timeline vs Geospatial Map */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveView('timeline')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeView === 'timeline'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>Route Timetable & Halts ({liveStatus.stops.length})</span>
          </button>

          <button
            onClick={() => setActiveView('map')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              activeView === 'map'
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <MapIcon className="w-4 h-4" />
            <span>Interactive Leaflet Map</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeView === 'timeline' ? (
        <RouteTimeline
          stops={liveStatus.stops}
          onSelectStation={onSelectStation}
          isLiveAvailable={liveStatus.is_live_available}
        />
      ) : (
        <RouteMap
          stops={liveStatus.stops}
          currentLat={liveStatus.current_latitude}
          currentLng={liveStatus.current_longitude}
          trainNumber={train.train_number}
          trainName={train.train_name}
          isLiveAvailable={liveStatus.is_live_available}
        />
      )}
    </div>
  );
};
