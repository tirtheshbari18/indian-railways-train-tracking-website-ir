import React, { useState } from 'react';
import { Search, ArrowRightLeft, Train, MapPin, Calendar, Sparkles, Filter, Layers } from 'lucide-react';
import { Station } from '../types';

interface TrainSearchCardProps {
  stations: Station[];
  onSearch: (params: { query?: string; source?: string; destination?: string; category?: string }) => void;
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
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const categories = [
    { id: '', label: 'All Services' },
    { id: 'Superfast', label: 'Superfast & Rajdhani' },
    { id: 'Express', label: 'Express' },
    { id: 'MEMU', label: 'MEMU Services' },
    { id: 'DEMU', label: 'DEMU Services' },
    { id: 'Local', label: 'Suburban Locals' },
    { id: 'Passenger', label: 'Passenger Trains' },
    { id: 'Special', label: 'Festival Specials' }
  ];

  const handleSwap = () => {
    const tmp = source;
    setSource(destination);
    setDestination(tmp);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'number') {
      if (!query.trim() && !selectedCategory) return;
      onSearch({ query: query.trim() || undefined, category: selectedCategory || undefined });
    } else {
      if (!source.trim() && !destination.trim() && !selectedCategory) return;
      onSearch({
        source: source.trim() || undefined,
        destination: destination.trim() || undefined,
        category: selectedCategory || undefined
      });
    }
  };

  const quickTrains = [
    { num: '22961', name: 'Mumbai-ADI Vande Bharat', tag: 'VB' },
    { num: '22954', name: 'Gujarat SF Express', tag: 'SF' },
    { num: '12951', name: 'Mumbai Tejas Rajdhani', tag: 'Rajdhani' },
    { num: '09159', name: 'Bandra-Vapi MEMU', tag: 'MEMU' },
    { num: '93005', name: 'Churchgate-Dahanu Local', tag: 'Local' },
    { num: '09001', name: 'MMCT-NDLS AC Special', tag: 'Special' },
    { num: '22436', name: 'NDLS-BSB Vande Bharat', tag: 'VB' }
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-md">
      {/* Tabs */}
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
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

      {/* Category Filter Pills */}
      <div className="mb-5 flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 mr-1 uppercase tracking-wider shrink-0">
          <Layers className="w-3.5 h-3.5 text-amber-400" />
          Category:
        </span>
        {categories.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setSelectedCategory(c.id === selectedCategory ? '' : c.id)}
            className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === c.id
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
                : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-750 border border-slate-700/60'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === 'number' ? (
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Train Number, Name, or Route
            </label>
            <div className="relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. 12951, Rajdhani, 22961, Boisar to Dahanu Road, MEMU..."
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
                  placeholder="e.g. Boisar, MMCT, CCG, NDLS"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm"
                />
                <datalist id="stations-list-from">
                  {stations.map((s) => (
                    <option key={s.code} value={s.name}>
                      {s.code} - {s.name} ({s.zone} / {s.division})
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
                  placeholder="e.g. Dahanu Road, ADI, DRD, HWH"
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 text-sm"
                />
                <datalist id="stations-list-to">
                  {stations.map((s) => (
                    <option key={s.code} value={s.name}>
                      {s.code} - {s.name} ({s.zone} / {s.division})
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
            className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-amber-300 border border-slate-700/60 transition-colors font-mono flex items-center gap-1.5"
          >
            <span>{item.num}</span>
            <span className="font-sans text-[10px] px-1 py-0.2 rounded bg-slate-900 text-amber-400 font-semibold">{item.tag}</span>
            <span className="font-sans text-[11px] text-slate-400">({item.name})</span>
          </button>
        ))}
      </div>
    </div>
  );
};
