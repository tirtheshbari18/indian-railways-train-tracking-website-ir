import React from 'react';
import { Clock, MapPin, CheckCircle2, Circle, AlertCircle } from 'lucide-react';
import { LiveStatusStop } from '../types';
import { StatusBadge } from './StatusBadge';

interface RouteTimelineProps {
  stops: LiveStatusStop[];
  onSelectStation?: (stationCode: string) => void;
  isLiveAvailable: boolean;
}

export const RouteTimeline: React.FC<RouteTimelineProps> = ({
  stops,
  onSelectStation,
  isLiveAvailable
}) => {
  if (!stops || stops.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">
        No timetable stops available for this train.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-500" />
            <span>Scheduled Route Timetable & Live Halts</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Total {stops.length} halts along the route ({stops[stops.length - 1]?.distance_km || 0} km total)
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>Passed</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
            <span>Current / Next</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span>
            <span>Upcoming</span>
          </div>
        </div>
      </div>

      <div className="relative pl-6 space-y-8 before:absolute before:left-[19px] before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {stops.map((stop, idx) => {
          const isOrigin = idx === 0;
          const isDestination = idx === stops.length - 1;
          const isCurrent = stop.status === 'CURRENT';
          const isPassed = stop.status === 'PASSED';

          let dotBg = 'bg-slate-800 border-slate-600 text-slate-400';
          if (isCurrent) {
            dotBg = 'bg-amber-500 border-amber-300 text-slate-950 ring-4 ring-amber-500/20';
          } else if (isPassed) {
            dotBg = 'bg-emerald-600 border-emerald-400 text-white';
          }

          return (
            <div key={stop.station_code + stop.stop_sequence} className="relative group">
              {/* Timeline marker icon */}
              <div
                className={`absolute -left-[31px] top-1 w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold font-mono transition-transform group-hover:scale-110 ${dotBg}`}
              >
                {stop.stop_sequence}
              </div>

              {/* Card content */}
              <div className={`p-4 rounded-xl border transition-all ${
                isCurrent
                  ? 'bg-amber-950/20 border-amber-600/50 shadow-lg shadow-amber-950/20'
                  : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
              }`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  {/* Station info */}
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        onClick={() => onSelectStation?.(stop.station_code)}
                        className="font-bold text-slate-100 hover:text-amber-400 cursor-pointer transition-colors text-sm"
                      >
                        {stop.station_name}
                      </span>
                      <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-800 text-amber-400 border border-slate-700">
                        {stop.station_code}
                      </span>

                      {isOrigin && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                          ORIGIN
                        </span>
                      )}
                      {isDestination && (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                          DESTINATION
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400 flex-wrap">
                      <span>Day {stop.day_number}</span>
                      <span>•</span>
                      <span>{stop.distance_km} km</span>
                      {stop.halt_minutes > 0 && (
                        <>
                          <span>•</span>
                          <span>Halt: <strong className="text-slate-300">{stop.halt_minutes}m</strong></span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Timing & Platform */}
                  <div className="flex items-center gap-6 sm:text-right shrink-0">
                    {/* Arrival */}
                    <div>
                      <div className="text-[10px] uppercase font-mono text-slate-500">Arrival</div>
                      <div className="text-sm font-mono font-semibold text-slate-200">
                        {stop.scheduled_arrival || '—'}
                      </div>
                      {isLiveAvailable && stop.actual_arrival && (
                        <div className="text-[11px] font-mono text-emerald-400">
                          Act: {stop.actual_arrival}
                        </div>
                      )}
                    </div>

                    {/* Departure */}
                    <div>
                      <div className="text-[10px] uppercase font-mono text-slate-500">Departure</div>
                      <div className="text-sm font-mono font-semibold text-slate-200">
                        {stop.scheduled_departure || '—'}
                      </div>
                      {isLiveAvailable && stop.actual_departure && (
                        <div className="text-[11px] font-mono text-emerald-400">
                          Act: {stop.actual_departure}
                        </div>
                      )}
                    </div>

                    {/* Platform */}
                    <div className="pl-4 border-l border-slate-800 flex flex-col items-end">
                      <div className="text-[10px] uppercase font-mono text-slate-500">Platform</div>
                      <div className="text-sm font-mono font-bold text-amber-400">
                        {stop.platform ? `PF #${stop.platform}` : 'TBA'}
                      </div>
                      <StatusBadge type="platformSource" value={stop.platform_source} />
                    </div>
                  </div>
                </div>

                {/* Delay banner if halted/late */}
                {isLiveAvailable && (stop.delay_arrival_minutes > 0 || stop.delay_departure_minutes > 0) && (
                  <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="text-amber-400 font-medium">
                      Delay: +{Math.max(stop.delay_arrival_minutes, stop.delay_departure_minutes)} mins
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      Telemetry synced
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
