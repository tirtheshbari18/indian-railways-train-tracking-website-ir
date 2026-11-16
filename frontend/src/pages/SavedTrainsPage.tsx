import React from 'react';
import { Bookmark, Train as TrainIcon, MapPin, Trash2, ChevronRight, Search } from 'lucide-react';
import { useSavedTrains } from '../context/SavedTrainsContext';
import { StatusBadge } from '../components/StatusBadge';

interface SavedTrainsPageProps {
  onSelectTrain: (trainNumber: string) => void;
  onExplore: () => void;
}

export const SavedTrainsPage: React.FC<SavedTrainsPageProps> = ({ onSelectTrain, onExplore }) => {
  const { savedTrains, toggleSave } = useSavedTrains();

  return (
    <div className="space-y-6 pb-16">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-amber-500 fill-current" />
            <span>Saved Express Trains ({savedTrains.length})</span>
          </h2>
          <p className="text-xs text-slate-400">Quick access to frequently tracked journeys</p>
        </div>

        {savedTrains.length > 0 && (
          <button
            onClick={onExplore}
            className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors flex items-center gap-1.5"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Find More Trains</span>
          </button>
        )}
      </div>

      {savedTrains.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/60 rounded-2xl border border-slate-800 space-y-4 my-8">
          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-500">
            <Bookmark className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-200">No Saved Trains Yet</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Bookmark your frequent trains (e.g. Mumbai Rajdhani, Vande Bharat) to monitor their live running status in one click.
            </p>
          </div>
          <button
            onClick={onExplore}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all shadow-md"
          >
            Explore Trains
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {savedTrains.map((train) => (
            <div
              key={train.train_number}
              onClick={() => onSelectTrain(train.train_number)}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 cursor-pointer transition-all shadow-md group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-mono font-extrabold text-base text-amber-400 bg-slate-950 px-2.5 py-0.5 rounded-md border border-slate-800">
                    {train.train_number}
                  </span>
                  <div className="flex items-center gap-2">
                    <StatusBadge type="trainType" value={train.train_type} />
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleSave(train);
                      }}
                      title="Remove Bookmark"
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 text-slate-400 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-slate-100 group-hover:text-amber-400 transition-colors line-clamp-1">
                  {train.train_name}
                </h3>

                <div className="mt-3 flex items-center gap-2 text-xs font-mono text-slate-300">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  <span>
                    {train.source_station?.name || train.source_station_code} → {train.destination_station?.name || train.destination_station_code}
                  </span>
                </div>

                <div className="mt-2 text-xs text-slate-400 flex items-center gap-3">
                  <span>{train.total_distance_km} km</span>
                  <span>•</span>
                  <span>{Math.floor(train.duration_minutes / 60)}h {train.duration_minutes % 60}m</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                <span className="text-[11px] font-mono text-emerald-400">● Telemetry Available</span>
                <span className="text-amber-400 font-semibold group-hover:translate-x-1 transition-transform flex items-center gap-0.5">
                  <span>View Live Telemetry</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
