import React, { useState } from 'react';
import { Clock, ArrowDownLeft, ArrowUpRight, Search, Train, ChevronRight } from 'lucide-react';
import { StationLiveBoardItem } from '../types';
import { StatusBadge } from './StatusBadge';

interface LiveBoardTableProps {
  arrivals: StationLiveBoardItem[];
  departures: StationLiveBoardItem[];
  onSelectTrain: (trainNumber: string) => void;
  stationName: string;
}

export const LiveBoardTable: React.FC<LiveBoardTableProps> = ({
  arrivals,
  departures,
  onSelectTrain,
  stationName
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'arrivals' | 'departures'>('all');
  const [filterText, setFilterText] = useState('');

  let displayedItems: { item: StationLiveBoardItem; type: 'arrival' | 'departure' }[] = [];

  if (activeTab === 'arrivals' || activeTab === 'all') {
    arrivals.forEach((item) => displayedItems.push({ item, type: 'arrival' }));
  }
  if (activeTab === 'departures' || activeTab === 'all') {
    departures.forEach((item) => {
      // Deduplicate if already added as arrival
      if (activeTab === 'all' && arrivals.some((a) => a.train_number === item.train_number)) {
        return;
      }
      displayedItems.push({ item, type: 'departure' });
    });
  }

  // Filter by query
  if (filterText.trim()) {
    const q = filterText.toLowerCase();
    displayedItems = displayedItems.filter(
      ({ item }) =>
        item.train_number.toLowerCase().includes(q) ||
        item.train_name.toLowerCase().includes(q) ||
        item.source_station_code.toLowerCase().includes(q) ||
        item.destination_station_code.toLowerCase().includes(q)
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-500" />
            <span>Station Arrivals & Departures Board</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Active passenger train movements through {stationName}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Tab buttons */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'all' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              All Trains ({arrivals.length + departures.length})
            </button>
            <button
              onClick={() => setActiveTab('arrivals')}
              className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1 ${
                activeTab === 'arrivals' ? 'bg-emerald-600 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              <ArrowDownLeft className="w-3.5 h-3.5" />
              <span>Arrivals ({arrivals.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('departures')}
              className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1 ${
                activeTab === 'departures' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              <ArrowUpRight className="w-3.5 h-3.5" />
              <span>Departures ({departures.length})</span>
            </button>
          </div>

          {/* Quick filter input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Filter by train..."
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      {displayedItems.length === 0 ? (
        <div className="p-8 text-center text-slate-500 bg-slate-950/40 rounded-xl border border-slate-800">
          No matching trains found for this station.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Train No & Name</th>
                <th className="py-3 px-3">Route (From → To)</th>
                <th className="py-3 px-3">Scheduled Time</th>
                <th className="py-3 px-3">Expected Time</th>
                <th className="py-3 px-3">Delay</th>
                <th className="py-3 px-3">Platform</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {displayedItems.map(({ item, type }) => {
                const schedTime = item.scheduled_departure || item.scheduled_arrival || '—';
                const expTime = item.expected_departure || item.expected_arrival || schedTime;
                const delay = Math.max(item.delay_arrival_minutes, item.delay_departure_minutes);

                return (
                  <tr
                    key={item.train_number + type}
                    className="hover:bg-slate-800/50 transition-colors group cursor-pointer"
                    onClick={() => onSelectTrain(item.train_number)}
                  >
                    {/* Train No & Name */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-amber-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          {item.train_number}
                        </span>
                        <div className="font-semibold text-slate-100 group-hover:text-amber-400 transition-colors line-clamp-1">
                          {item.train_name}
                        </div>
                      </div>
                      <div className="mt-1">
                        <StatusBadge type="trainType" value={item.train_type} />
                      </div>
                    </td>

                    {/* Route */}
                    <td className="py-3.5 px-3">
                      <div className="font-mono text-slate-200">
                        {item.source_station_code} → {item.destination_station_code}
                      </div>
                      <div className="text-[10px] text-slate-500 font-sans uppercase">
                        {item.direction}
                      </div>
                    </td>

                    {/* Sched Time */}
                    <td className="py-3.5 px-3 font-mono text-slate-300 font-medium">
                      {schedTime}
                    </td>

                    {/* Expected Time */}
                    <td className="py-3.5 px-3 font-mono font-semibold text-slate-100">
                      {expTime}
                    </td>

                    {/* Delay */}
                    <td className="py-3.5 px-3">
                      {delay === 0 ? (
                        <span className="text-emerald-400 font-semibold font-mono">RT (0m)</span>
                      ) : (
                        <span className="text-amber-400 font-semibold font-mono">+{delay}m late</span>
                      )}
                    </td>

                    {/* Platform */}
                    <td className="py-3.5 px-3">
                      <div className="font-mono font-bold text-slate-100">
                        {item.platform ? `PF #${item.platform}` : 'TBA'}
                      </div>
                      <StatusBadge type="platformSource" value={item.platform_source} />
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-3">
                      <StatusBadge
                        type="runningStatus"
                        value={delay === 0 ? 'RUNNING_ON_TIME' : 'RUNNING_LATE'}
                        delayMinutes={delay}
                      />
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectTrain(item.train_number);
                        }}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-400 transition-colors inline-flex items-center gap-1"
                        title="View Train Route and Live Telemetry"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
