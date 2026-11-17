import React, { useState, useEffect } from 'react';
import { Building, MapPin, Radio, RefreshCw, ArrowLeft, AlertCircle, Layers, CheckCircle2, ShieldCheck, Tag } from 'lucide-react';
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
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [error, setError] = useState<string | null>(null);

  const categories = ['ALL', 'Superfast', 'Express', 'MEMU', 'DEMU', 'Local', 'Passenger', 'Special'];

  const fetchBoard = async (provider = selectedProvider, category = selectedCategory) => {
    try {
      setError(null);
      const catParam = category !== 'ALL' ? category : undefined;
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
    fetchBoard(selectedProvider, selectedCategory);
  }, [stationCode, selectedProvider]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchBoard(selectedProvider, selectedCategory);
  };

  const filterTrains = (items: StationLiveBoardItem[]) => {
    if (selectedCategory === 'ALL') return items;
    const target = selectedCategory.toLowerCase();
    return items.filter((item) => {
      const type = (item.train_type || '').toLowerCase();
      const cat = (item.train_category || '').toLowerCase();
      if (target === 'special') return type.includes('special') || cat.includes('special');
      if (target === 'local') return type.includes('local') || type.includes('emu') || cat.includes('local');
      return type.includes(target) || cat.includes(target);
    });
  };

  const filteredArrivals = filterTrains(arrivals);
  const filteredDepartures = filterTrains(departures);

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
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                  <span>{station.name}</span>
                </h1>
                {station.category && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    {station.category}
                  </span>
                )}
                {station.operational_status && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    {station.operational_status}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 mt-1 text-xs text-slate-400 flex-wrap">
                <span className="font-mono text-amber-400 font-semibold">{station.zone} Zone</span>
                {station.division && (
                  <>
                    <span>•</span>
                    <span>{station.division} Division</span>
                  </>
                )}
                {station.district && (
                  <>
                    <span>•</span>
                    <span>District: {station.district}</span>
                  </>
                )}
                {station.state && (
                  <>
                    <span>•</span>
                    <span>{station.state}</span>
                  </>
                )}
              </div>

              {/* Station Facilities Tags */}
              {station.facilities && station.facilities.length > 0 && (
                <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold flex items-center gap-1">
                    <Tag className="w-3 h-3 text-slate-500" />
                    Facilities:
                  </span>
                  {station.facilities.map((fac) => (
                    <span
                      key={fac}
                      className="px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 text-[10px] font-medium border border-slate-700/60"
                    >
                      {fac}
                    </span>
                  ))}
                </div>
              )}
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
            <div className="text-[10px] uppercase font-mono text-slate-500">Active Scheduled Trains</div>
            <div className="text-amber-400 font-bold mt-0.5 text-sm">
              {arrivals.length + departures.length} Calling at Station
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter Pills for Live Board */}
      <div className="flex items-center justify-between gap-4 flex-wrap bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1 font-semibold">
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            Filter Services:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                selectedCategory === cat
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
        <span className="text-xs font-mono text-slate-500">
          Showing {filteredArrivals.length} arrivals, {filteredDepartures.length} departures
        </span>
      </div>

      {/* Live Board Table */}
      <LiveBoardTable
        arrivals={filteredArrivals}
        departures={filteredDepartures}
        onSelectTrain={onSelectTrain}
        stationName={`${station.name} (${station.code})`}
      />
    </div>
  );
};
