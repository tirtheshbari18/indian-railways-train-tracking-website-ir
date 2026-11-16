import React, { useState } from 'react';
import { Search, MapPin, Building, ChevronRight } from 'lucide-react';
import { Station } from '../types';

interface StationSearchCardProps {
  stations: Station[];
  onSelectStation: (code: string) => void;
}

export const StationSearchCard: React.FC<StationSearchCardProps> = ({
  stations,
  onSelectStation
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedZone, setSelectedZone] = useState('ALL');

  const zones = ['ALL', 'NR', 'WR', 'CR', 'ER', 'SR', 'SWR', 'NCR', 'WCR', 'ECR', 'NER'];

  const filteredStations = stations.filter((s) => {
    const matchesSearch =
      s.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.state && s.state.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesZone = selectedZone === 'ALL' || s.zone === selectedZone;

    return matchesSearch && matchesZone;
  });

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Building className="w-5 h-5 text-amber-500" />
            <span>Station Live Telemetry & Arrivals/Departures Board</span>
          </h3>
          <p className="text-xs text-slate-400">Search 25+ major Indian railway junctions and terminal stations</p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search Station (e.g. NDLS, Mumbai, Howrah)..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
        </div>
      </div>

      {/* Zone filter pills */}
      <div className="flex items-center gap-1.5 flex-wrap mb-4 pb-2 border-b border-slate-800">
        <span className="text-[11px] font-semibold text-slate-400 mr-1">Zone:</span>
        {zones.map((z) => (
          <button
            key={z}
            onClick={() => setSelectedZone(z)}
            className={`px-2.5 py-1 rounded-md text-xs font-mono transition-colors ${
              selectedZone === z
                ? 'bg-amber-500 text-slate-950 font-bold'
                : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700'
            }`}
          >
            {z}
          </button>
        ))}
      </div>

      {/* Grid of Station Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto pr-1">
        {filteredStations.map((station) => (
          <div
            key={station.code}
            onClick={() => onSelectStation(station.code)}
            className="p-3.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-amber-500/50 cursor-pointer transition-all flex items-center justify-between group"
          >
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-slate-900 border border-slate-800 group-hover:border-amber-500/40 flex items-center justify-center font-mono font-bold text-amber-400 text-sm">
                {station.code}
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-200 group-hover:text-amber-400 transition-colors">
                  {station.name}
                </h4>
                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span className="font-mono text-slate-300">{station.zone} Zone</span>
                  {station.state && (
                    <>
                      <span>•</span>
                      <span>{station.state}</span>
                    </>
                  )}
                  {station.platforms_count && (
                    <>
                      <span>•</span>
                      <span>{station.platforms_count} Plat.</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all" />
          </div>
        ))}
      </div>
    </div>
  );
};
