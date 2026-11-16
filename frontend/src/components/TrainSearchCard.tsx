import React, { useState } from 'react';
import { Search, ArrowRightLeft, Train, MapPin, Calendar, Sparkles } from 'lucide-react';
import { Station } from '../types';

interface TrainSearchCardProps {
  stations: Station[];
  onSearch: (params: { query?: string; source?: string; destination?: string }) => void;
  onSelectTrainDirect?: (trainNumber: string) => void;
}

export const TrainSearchCard: React.FC<TrainSearchCardProps> = ({
  stations,
  onSearch,
  onSelectTrainDirect
}) => {
  const [activeTab, setActiveTab] = useState<'number' | 'route'>('number');
  const [query, setQuery] = useState('');
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');

  const handleSwap = () => {
    const tmp = source;
    setSource(destination);
    setDestination(tmp);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'number') {
      if (!query.trim()) return;
      onSearch({ query: query.trim() });
    } else {
      if (!source.trim() && !destination.trim()) return;
      onSearch({ source: source.trim(), destination: destination.trim() });
    }
  };

  const quickTrains = [
    { num: '22961', name: 'Mumbai-ADI Vande Bharat' },
    { num: '22962', name: 'ADI-Mumbai Vande Bharat' },
    { num: '22954', name: 'Gujarat SF Express' },
    { num: '12951', name: 'Mumbai Tejas Rajdhani' },
    { num: '22436', name: 'NDLS-Varanasi Vande Bharat' },
    { num: '12002', name: 'Bhopal Shatabdi' }
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-md">
      {/* Tabs */}
      <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-3">
        <button
          type="button"
          onClick={() => setActiveTab('number')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            activeTab === 'number'
              ? 'bg-amber-500 text-slate-950 shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Train className="w-4 h-4" />
          <span>By Train Number / Name</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('route')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            activeTab === 'route'
              ? 'bg-amber-500 text-slate-950 shadow-md'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <MapPin className="w-4 h-4" />
          <span>By Stations (From - To)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === 'number' ? (
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Train Number or Train Name
            </label>
            <div className="relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. 12951, Rajdhani, 22436, Vande Bharat, Shatabdi..."
                className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-12 pr-4 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-sm"
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-11 gap-3 items-center">
            <div className="md:col-span-5">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Origin Station (From)
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-emerald-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  list="stations-list-from"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="e.g. NDLS (New Delhi) or MMCT"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm"
                />
                <datalist id="stations-list-from">
                  {stations.map((s) => (
                    <option key={s.code} value={s.code}>
                      {s.code} - {s.name} ({s.zone})
                    </option>
                  ))}
                </datalist>
              </div>
            </div>

            <div className="md:col-span-1 flex justify-center pt-5">
              <button
                type="button"
                onClick={handleSwap}
                title="Swap Stations"
                className="p-2.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors"
              >
                <ArrowRightLeft className="w-4 h-4" />
              </button>
            </div>

            <div className="md:col-span-5">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Destination Station (To)
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-rose-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  list="stations-list-to"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="e.g. BSB (Varanasi) or HWH"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm"
                />
                <datalist id="stations-list-to">
                  {stations.map((s) => (
                    <option key={s.code} value={s.code}>
                      {s.code} - {s.name} ({s.zone})
                    </option>
                  ))}
                </datalist>
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-amber-500/10 flex items-center justify-center gap-2 text-sm tracking-wide"
        >
          <Search className="w-4 h-4" />
          <span>Find Trains & Live Telemetry</span>
        </button>
      </form>

      {/* Quick Search Chips */}
      <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center gap-2 flex-wrap text-xs text-slate-400">
        <span className="flex items-center gap-1 text-slate-500 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Popular Trains:
        </span>
        {quickTrains.map((item) => (
          <button
            key={item.num}
            type="button"
            onClick={() => onSelectTrainDirect?.(item.num)}
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-amber-300 border border-slate-700/60 transition-colors font-mono"
          >
            {item.num} <span className="font-sans text-[11px] text-slate-400">({item.name})</span>
          </button>
        ))}
      </div>
    </div>
  );
};
