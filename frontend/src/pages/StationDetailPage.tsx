import React, { useState, useEffect } from 'react';
import { Building, MapPin, Radio, RefreshCw, ArrowLeft, AlertCircle, Layers } from 'lucide-react';
import { Station, StationLiveBoardItem } from '../types';
import { api } from '../services/api';
import { LiveBoardTable } from '../components/LiveBoardTable';

interface StationDetailPageProps {
  stationCode: string;
  onBack: () => void;
  onSelectTrain: (trainNumber: string) => void;
}

export const StationDetailPage: React.FC<StationDetailPageProps> = ({
  stationCode,
  onBack,
  onSelectTrain
}) => {
  const [station, setStation] = useState<Station | null>(null);
  const [arrivals, setArrivals] = useState<StationLiveBoardItem[]>([]);
  const [departures, setDepartures] = useState<StationLiveBoardItem[]>([]);
  const [providerName, setProviderName] = useState('CRIS NTES Telemetry');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string>('mock');
  const [error, setError] = useState<string | null>(null);

  const fetchBoard = async (provider = selectedProvider) => {
    try {
      setError(null);
      const data = await api.getStationLiveBoard(stationCode, provider);
      setStation(data.station);
      setArrivals(data.arrivals || []);
      setDepartures(data.departures || []);
      setProviderName(data.provider);
    } catch (err: any) {
      setError(err.message || 'Failed to load station live board');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchBoard(selectedProvider);
  }, [stationCode, selectedProvider]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchBoard(selectedProvider);
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <div className="text-sm font-semibold text-slate-300">
          Loading Station Telemetry & Passenger Movements...
        </div>
        <div className="text-xs text-slate-500 font-mono">Station Code: {stationCode}</div>
      </div>
    );
  }

  if (error || !station) {
    return (
      <div className="p-8 max-w-lg mx-auto bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4 my-12">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">Station Not Found</h3>
        <p className="text-xs text-slate-400">{error || 'Unable to retrieve station records.'}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 text-slate-200 hover:bg-slate-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-16">
      {/* Back and Provider selection */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Stations</span>
        </button>

        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-1.5 rounded-xl text-xs">
          <span className="text-[11px] font-mono text-slate-400 px-2 flex items-center gap-1">
            <Radio className="w-3 h-3 text-amber-500" />
            Board Mode:
          </span>
          {[
            { id: 'mock', label: 'Simulated Telemetry' },
            { id: 'null', label: 'Static Schedule Only' }
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

      {/* Station Header Banner */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-slate-950 border-2 border-amber-500/40 flex items-center justify-center font-mono font-extrabold text-amber-400 text-xl shadow-lg shadow-amber-500/10">
              {station.code}
            </div>

            <div>
              <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                <span>{station.name}</span>
              </h1>
              <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                <span className="font-mono text-amber-400 font-semibold">{station.zone} Zone</span>
                {station.division && (
                  <>
                    <span>•</span>
                    <span>{station.division} Division</span>
                  </>
                )}
                {station.state && (
                  <>
                    <span>•</span>
                    <span>{station.state}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 text-xs font-semibold"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-amber-400' : ''}`} />
              <span>Refresh Board</span>
            </button>
          </div>
        </div>

        {/* Station Metrics */}
        <div className="pt-4 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Platforms Available</div>
            <div className="text-slate-200 font-bold mt-0.5 text-sm">
              {station.platforms_count || 1} Operational Platforms
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Geospatial Coordinates</div>
            <div className="text-slate-200 font-mono font-medium mt-0.5 text-xs">
              {station.latitude.toFixed(4)}° N, {station.longitude.toFixed(4)}° E
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Telemetry Feed</div>
            <div className="text-emerald-400 font-semibold mt-0.5 text-xs font-mono truncate">
              {providerName}
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase font-mono text-slate-500">Active Express Trains</div>
            <div className="text-amber-400 font-bold mt-0.5 text-sm">
              {arrivals.length + departures.length} Passing Daily
            </div>
          </div>
        </div>
      </div>

      {/* Live Board Table */}
      <LiveBoardTable
        arrivals={arrivals}
        departures={departures}
        onSelectTrain={onSelectTrain}
        stationName={`${station.name} (${station.code})`}
      />
    </div>
  );
};
