import React, { useState } from 'react';
import { Train as TrainIcon, MapPin, Clock, Bookmark, ChevronRight, Filter, ArrowLeft } from 'lucide-react';
import { Train } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { useSavedTrains } from '../context/SavedTrainsContext';

interface SearchResultsPageProps {
  trains: Train[];
  total: number;
  searchParams: { query?: string; source?: string; destination?: string };
  onSelectTrain: (trainNumber: string) => void;
  onBack: () => void;
}

export const SearchResultsPage: React.FC<SearchResultsPageProps> = ({
  trains,
  total,
  searchParams,
  onSelectTrain,
  onBack
}) => {
  const { isSaved, toggleSave } = useSavedTrains();
  const [selectedType, setSelectedType] = useState<string>('ALL');

  const trainTypes = ['ALL', 'Rajdhani', 'Vande Bharat', 'Shatabdi', 'Superfast'];

  const filteredTrains = trains.filter((t) => {
    if (selectedType === 'ALL') return true;
    return t.train_type.toLowerCase().includes(selectedType.toLowerCase());
  });

  const formatDays = (mask: string) => {
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    if (mask === '1111111') return <span className="text-emerald-400 font-bold">Daily</span>;
    return (
      <div className="flex items-center gap-1 font-mono text-[10px]">
        {days.map((d, i) => {
          const active = mask[i] === '1';
          return (
            <span
              key={i}
              className={`w-4 h-4 rounded flex items-center justify-center ${
                active ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-500'
              }`}
            >
              {d}
            </span>
          );
        })}
      </div>
    );
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Back button and title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <TrainIcon className="w-5 h-5 text-amber-500" />
              <span>Train Search Results</span>
            </h2>
            <p className="text-xs text-slate-400">
              {searchParams.source && searchParams.destination ? (
                <>Route: <strong className="text-slate-200">{searchParams.source}</strong> to <strong className="text-slate-200">{searchParams.destination}</strong></>
              ) : searchParams.query ? (
                <>Query matching: &ldquo;<strong className="text-slate-200">{searchParams.query}</strong>&rdquo;</>
              ) : (
                'All Available Express Trains'
              )} ({total} found)
            </p>
          </div>
        </div>

        {/* Filter by train type */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            Type:
          </span>
          {trainTypes.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                selectedType === type
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Results List */}
      {filteredTrains.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/60 rounded-2xl border border-slate-800 space-y-3">
          <TrainIcon className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-slate-300">No matching trains found</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Try searching for a major terminal code (e.g. NDLS, MMCT, HWH, MAS) or train number (e.g. 12951, 22436, 12002).
          </p>
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 text-slate-950 hover:bg-amber-400 transition-colors"
          >
            Modify Search
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTrains.map((train) => {
            const saved = isSaved(train.train_number);
            const hours = Math.floor(train.duration_minutes / 60);
            const mins = train.duration_minutes % 60;

            return (
              <div
                key={train.train_number}
                onClick={() => onSelectTrain(train.train_number)}
                className="p-5 rounded-2xl bg-slate-900/90 hover:bg-slate-850 border border-slate-800 hover:border-amber-500/50 cursor-pointer transition-all shadow-md group"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Left: Train Info */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="font-mono font-extrabold text-base text-amber-400 bg-slate-950 px-2.5 py-0.5 rounded-md border border-slate-800">
                        {train.train_number}
                      </span>
                      <h3 className="text-base font-bold text-slate-100 group-hover:text-amber-400 transition-colors">
                        {train.train_name}
                      </h3>
                      <StatusBadge type="trainType" value={train.train_type} />
                    </div>

                    <div className="flex items-center gap-4 text-xs text-slate-300 flex-wrap">
                      <div className="flex items-center gap-1.5 font-mono">
                        <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                        <span>
                          {train.source_station?.name || train.source_station_code} ({train.source_station_code})
                          {' → '}
                          {train.destination_station?.name || train.destination_station_code} ({train.destination_station_code})
                        </span>
                      </div>
                      <span>•</span>
                      <span>{train.total_distance_km} km</span>
                      {train.duration_minutes > 0 && (
                        <>
                          <span>•</span>
                          <span>{hours}h {mins}m</span>
                        </>
                      )}
                    </div>

                    {/* Classes & Pantry */}
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span className="text-[11px] text-slate-500 font-mono">Classes:</span>
                      <div className="flex items-center gap-1 font-mono text-[11px]">
                        {train.classes?.map((c) => (
                          <span key={c} className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                            {c}
                          </span>
                        ))}
                      </div>
                      {train.pantry_car && (
                        <span className="text-[11px] text-emerald-400 font-medium">✓ Pantry Car</span>
                      )}
                    </div>
                  </div>

                  {/* Right: Days & Actions */}
                  <div className="flex items-center justify-between md:justify-end gap-6 pt-3 md:pt-0 border-t md:border-t-0 border-slate-800">
                    <div className="text-right">
                      <div className="text-[10px] uppercase font-mono text-slate-500 mb-1">Runs On</div>
                      {formatDays(train.running_days)}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSave(train);
                        }}
                        title={saved ? 'Remove from Saved' : 'Save Train'}
                        className={`p-2 rounded-xl border transition-colors ${
                          saved
                            ? 'bg-amber-500/20 border-amber-500 text-amber-400'
                            : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                        }`}
                      >
                        <Bookmark className="w-4 h-4 fill-current" />
                      </button>

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectTrain(train.train_number);
                        }}
                        className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 flex items-center gap-1 transition-all shadow-sm"
                      >
                        <span>Live Telemetry</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
