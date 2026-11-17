import React, { useState } from 'react';
import { Train as TrainIcon, MapPin, Clock, Bookmark, ChevronRight, Filter, ArrowLeft, ShieldCheck, Sparkles, Calendar } from 'lucide-react';
import { Train } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { useSavedTrains } from '../context/SavedTrainsContext';

interface SearchResultsPageProps {
  trains: Train[];
  total: number;
  searchParams: { query?: string; source?: string; destination?: string; category?: string };
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
  const [selectedCategory, setSelectedCategory] = useState<string>(searchParams.category || 'ALL');

  const filterCategories = ['ALL', 'Rajdhani', 'Vande Bharat', 'Shatabdi', 'Duronto', 'Superfast', 'Express', 'MEMU', 'DEMU', 'Local', 'Passenger', 'Special'];

  const filteredTrains = trains.filter((t) => {
    if (selectedCategory === 'ALL') return true;
    const cat = (t.train_category || t.train_type || '').toLowerCase();
    const target = selectedCategory.toLowerCase();
    if (target === 'special') return t.is_special || cat.includes('special');
    if (target === 'local') return cat.includes('local') || cat.includes('emu');
    if (target === 'rajdhani') return cat.includes('rajdhani');
    if (target === 'vande bharat') return cat.includes('vande bharat');
    if (target === 'shatabdi') return cat.includes('shatabdi');
    if (target === 'duronto') return cat.includes('duronto');
    return cat.includes(target);
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
                'All Verified Trains'
              )} ({total} found in Indian Railways database)
            </p>
          </div>
        </div>

        {/* Filter by train category */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            Category:
          </span>
          {filterCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                selectedCategory === cat
                  ? 'bg-amber-500 text-slate-950 shadow-sm font-bold'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {cat}
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
            Try searching for a station name (e.g. Boisar, Dahanu Road, Mumbai Central, Vadodara) or service number (e.g. 22961, 93005, 09159, 12951).
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
                      {train.short_name && train.short_name !== train.train_name && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 bg-slate-800 border border-slate-700">
                          {train.short_name}
                        </span>
                      )}
                      <StatusBadge type="trainType" value={train.train_category || train.train_type} />
                      {train.tags && train.tags.length > 0 && train.tags.filter(t => t.toLowerCase() !== (train.train_category || '').toLowerCase()).slice(0, 3).map((tag) => (
                        <span key={tag} className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          {tag}
                        </span>
                      ))}
                      {train.is_special && (
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-amber-400" />
                          Festival Special
                        </span>
                      )}
                      <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400/90 bg-emerald-950/40 border border-emerald-900/50 px-2 py-0.5 rounded font-mono">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        CRIS Timetable
                      </span>
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

                      <div className="flex items-center gap-1 text-slate-400">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>{hours}h {mins}m ({train.total_distance_km} km)</span>
                      </div>

                      {train.validity_start && train.validity_end && (
                        <div className="flex items-center gap-1 text-[11px] text-amber-300/80">
                          <Calendar className="w-3 h-3 text-amber-400" />
                          <span>Valid: {train.validity_start} to {train.validity_end}</span>
                        </div>
                      )}
                    </div>

                    {/* Classes */}
                    {train.classes && train.classes.length > 0 && (
                      <div className="flex items-center gap-1 flex-wrap pt-1">
                        <span className="text-[11px] text-slate-500 mr-1">Classes:</span>
                        {train.classes.map((cls) => (
                          <span
                            key={cls}
                            className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono font-bold text-slate-300 border border-slate-700/60"
                          >
                            {cls}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Right: Operating Days & Save */}
                  <div className="flex md:flex-col items-center md:items-end justify-between gap-3 border-t md:border-t-0 pt-3 md:pt-0 border-slate-800">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSave(train);
                        }}
                        className={`p-2 rounded-xl border transition-colors ${
                          saved
                            ? 'bg-amber-500/20 border-amber-500/50 text-amber-400'
                            : 'bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-400 hover:text-white'
                        }`}
                        title={saved ? 'Remove from Saved' : 'Save Train'}
                      >
                        <Bookmark className={`w-4 h-4 ${saved ? 'fill-amber-400' : ''}`} />
                      </button>

                      <div className="hidden sm:flex items-center gap-1 text-xs text-amber-400 font-bold group-hover:translate-x-1 transition-transform">
                        <span>View Route & Live Telemetry</span>
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-500 font-semibold uppercase">Runs:</span>
                      {formatDays(train.running_days)}
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
