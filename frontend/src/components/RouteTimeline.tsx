import React, { useState } from 'react';
import { Clock, MapPin, CheckCircle2, Circle, AlertCircle, Compass, ChevronDown, ChevronUp, Info, X } from 'lucide-react';
import { LiveStatusStop } from '../types';
import { StatusBadge } from './StatusBadge';
import { getIntermediateStations, estimatePassingTime, IntermediateStation } from '../data/intermediateStations';

interface RouteTimelineProps {
  stops: LiveStatusStop[];
  onSelectStation?: (stationCode: string) => void;
  isLiveAvailable: boolean;
  statusSummary?: string;
  speedKmh?: number | null;
  currentStatusDescription?: string;
  nextStation?: string | null;
  lastReportedStation?: string | null;
}

export const RouteTimeline: React.FC<RouteTimelineProps> = ({
  stops,
  onSelectStation,
  isLiveAvailable,
  statusSummary,
  speedKmh,
  currentStatusDescription,
  nextStation,
  lastReportedStation
}) => {
  const [expandedSegments, setExpandedSegments] = useState<Record<string, boolean>>({});
  const [noIntermediateModal, setNoIntermediateModal] = useState<{
    isOpen: boolean;
    fromStation: string;
    toStation: string;
  } | null>(null);

  if (!stops || stops.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-900/50 rounded-xl border border-slate-800">
        No timetable stops available for this train.
      </div>
    );
  }

  const toggleSegment = (key: string) => {
    setExpandedSegments(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleToggleIntermediate = (
    key: string,
    fromStop: LiveStatusStop,
    toStop: LiveStatusStop,
    list: IntermediateStation[]
  ) => {
    if (list.length === 0) {
      setNoIntermediateModal({
        isOpen: true,
        fromStation: `${fromStop.station_name} (${fromStop.station_code})`,
        toStation: `${toStop.station_name} (${toStop.station_code})`
      });
    } else {
      toggleSegment(key);
    }
  };

  // Find moving segment index (last passed stop before first upcoming stop)
  let activeMovingIndex = -1;
  if (statusSummary === 'RUNNING_ON_TIME' || statusSummary === 'RUNNING_LATE') {
    for (let i = 0; i < stops.length - 1; i++) {
      if (stops[i].status === 'PASSED' && stops[i + 1].status === 'UPCOMING') {
        activeMovingIndex = i;
        break;
      }
    }
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative">
      {/* No Intermediate Stations Modal Popup */}
      {noIntermediateModal && noIntermediateModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl text-center space-y-4 relative">
            <button
              onClick={() => setNoIntermediateModal(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto text-xl font-bold">
              ℹ️
            </div>
            <div className="space-y-2">
              <h3 className="text-base font-bold text-white">No Intermediate Stations</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                There are no crossing or intermediate way stations between{' '}
                <strong className="text-amber-400">{noIntermediateModal.fromStation}</strong> and{' '}
                <strong className="text-amber-400">{noIntermediateModal.toStation}</strong>.
              </p>
              <p className="text-[11px] text-slate-400">
                These two stations are immediately adjacent on this railway corridor with direct point-to-point line tracks.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setNoIntermediateModal(null)}
              className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors shadow-md"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" />
              <span>Route Timetable & Interactive Intermediate Stations</span>
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
              Where Is My Train Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Total {stops.length} scheduled halts • Tap intermediate station pills to expand passing stations along the line
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs flex-wrap">
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>Passed</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
            <span>Live Moving</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-600"></span>
            <span>Upcoming</span>
          </div>
        </div>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-[19px] before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {stops.map((stop, idx) => {
          const isOrigin = idx === 0;
          const isDestination = idx === stops.length - 1;
          const isCurrent = stop.status === 'CURRENT';
          const isPassed = stop.status === 'PASSED';
          const isArrived = statusSummary === 'ARRIVED';
          const isYetToDepart = statusSummary === 'YET_TO_DEPART';

          let dotBg = 'bg-slate-800 border-slate-600 text-slate-400';
          if (isDestination && isArrived) {
            dotBg = 'bg-emerald-500 border-emerald-300 text-slate-950 ring-4 ring-emerald-500/30';
          } else if (isCurrent) {
            dotBg = 'bg-amber-500 border-amber-300 text-slate-950 ring-4 ring-amber-500/20';
          } else if (isPassed) {
            dotBg = 'bg-emerald-600 border-emerald-400 text-white';
          }

          const nextStop = idx < stops.length - 1 ? stops[idx + 1] : null;
          const intermediateList = nextStop
            ? getIntermediateStations(stop.station_code, nextStop.station_code, stop.distance_km, nextStop.distance_km)
            : [];
          const segmentKey = nextStop ? `${stop.station_code}-${nextStop.station_code}-${idx}` : '';
          const isSegmentExpanded = !!expandedSegments[segmentKey];

          return (
            <React.Fragment key={stop.station_code + stop.stop_sequence}>
              <div className="relative group">
                {/* Timeline marker sequence circle */}
                <div
                  className={`absolute -left-[31px] top-1 w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold font-mono transition-transform group-hover:scale-110 ${dotBg}`}
                >
                  {stop.stop_sequence}
                </div>

                {/* Card content */}
                <div className={`p-4 rounded-xl border transition-all ${
                  isDestination && isArrived
                    ? 'bg-emerald-950/20 border-emerald-500/50 shadow-lg shadow-emerald-950/30'
                    : isCurrent
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
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                            isArrived
                              ? 'bg-emerald-900 text-emerald-200 border-emerald-700 font-bold'
                              : 'bg-purple-950 text-purple-300 border-purple-800'
                          }`}>
                            {isArrived ? 'DESTINATION REACHED' : 'DESTINATION'}
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
                          <div className="text-[11px] font-mono text-emerald-400 font-bold">
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
                          <div className="text-[11px] font-mono text-emerald-400 font-bold">
                            Act: {stop.actual_departure}
                          </div>
                        )}
                      </div>

                      {/* Platform */}
                      <div className="pl-4 border-l border-slate-800 flex flex-col items-end">
                        <div className="text-[10px] uppercase font-mono text-slate-500">Platform</div>
                        <div className="text-sm font-mono font-bold text-amber-400">
                          {stop.platform ? `PF #${stop.platform}` : 'PF #1'}
                        </div>
                        <StatusBadge type="platformSource" value={stop.platform_source} />
                      </div>
                    </div>
                  </div>

                  {/* Destination Journey Completed Banner */}
                  {isDestination && isArrived && (
                    <div className="mt-3 pt-3 border-t border-emerald-800/60 flex items-center justify-between text-xs bg-emerald-950/40 p-2.5 rounded-lg">
                      <div className="flex items-center gap-2 text-emerald-300 font-bold">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                        <span>TRAIN HAS REACHED DESTINATION • Journey 100% Completed</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-emerald-500 text-slate-950 font-bold text-[10px] font-mono">
                        ARRIVED
                      </span>
                    </div>
                  )}

                  {/* Origin Yet To Depart Banner */}
                  {isOrigin && isYetToDepart && (
                    <div className="mt-3 pt-3 border-t border-blue-800/60 flex items-center justify-between text-xs bg-blue-950/40 p-2.5 rounded-lg">
                      <div className="flex items-center gap-2 text-blue-300 font-medium">
                        <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-pulse"></span>
                        <span>Positioned at Origin Platform • Awaiting Scheduled Departure</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-blue-500 text-slate-950 font-bold text-[10px] font-mono">
                        AT ORIGIN
                      </span>
                    </div>
                  )}

                  {/* Station Halt Banner */}
                  {isCurrent && statusSummary === 'HALTED' && (
                    <div className="mt-3 pt-3 border-t border-amber-800/60 flex items-center justify-between text-xs bg-amber-950/40 p-2.5 rounded-lg">
                      <div className="flex items-center gap-2 text-amber-300 font-bold">
                        <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
                        <span>HALTED AT STATION • Boarding / De-boarding in Progress</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-amber-500 text-slate-950 font-bold text-[10px] font-mono">
                        HALT
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Where Is My Train Live Moving Train Indicator */}
              {idx === activeMovingIndex && (
                <div className="relative my-2 -ml-2 pl-4 py-2">
                  <div className="p-3.5 rounded-xl border-l-4 border-amber-500 bg-gradient-to-r from-amber-500/20 via-slate-900 to-slate-950 border border-slate-800 shadow-xl flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-amber-500/20 border border-amber-500/60 flex items-center justify-center text-lg shrink-0 animate-bounce">
                        🚆
                      </div>
                      <div>
                        <div className="text-xs font-extrabold text-amber-300 flex items-center gap-2">
                          <span>LIVE TRAIN LOCATION (WHERE IS MY TRAIN)</span>
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                        </div>
                        <div className="text-xs text-slate-200 mt-0.5 font-medium">
                          Departed <strong>{stop.station_name}</strong> ➔ Next stop is <strong>{stops[idx + 1]?.station_name}</strong>
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5 flex items-center gap-3">
                          <span>Speed: <strong className="text-slate-200">{Math.round(speedKmh || 90)} km/h</strong></span>
                          <span>•</span>
                          <span>ETA: <strong className="text-emerald-400">{stops[idx + 1]?.scheduled_arrival}</strong></span>
                          <span>•</span>
                          <span>Platform: <strong className="text-amber-400">PF #{stops[idx + 1]?.platform || '1'}</strong></span>
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 text-right">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-amber-500 text-slate-950 shadow-md">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-950 animate-pulse"></span>
                        IN MOTION
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Where Is My Train Interactive Intermediate Stations Control */}
              {nextStop && (
                <div className="relative my-2 pl-2">
                  {!isSegmentExpanded ? (
                    <button
                      type="button"
                      onClick={() => handleToggleIntermediate(segmentKey, stop, nextStop, intermediateList)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono font-semibold bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-amber-400 border border-slate-800 hover:border-amber-500/50 transition-all shadow-sm group"
                      title="Click to view intermediate crossing stations"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-600 group-hover:bg-amber-400 transition-colors"></span>
                      <span>
                        {intermediateList.length > 0
                          ? `+ ${intermediateList.length} intermediate stations`
                          : 'Show intermediate stations'}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        ({Math.abs(Math.round(nextStop.distance_km - stop.distance_km))} km)
                      </span>
                      <ChevronDown className="w-3 h-3 text-slate-500 group-hover:text-amber-400 transition-transform group-hover:translate-y-0.5" />
                    </button>
                  ) : (
                    <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3.5 space-y-3 my-2 shadow-inner">
                      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                        <div className="flex items-center gap-2 text-xs font-mono text-amber-400 font-bold">
                          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                          <span>
                            {intermediateList.length} Intermediate Crossing Stations ({stop.station_code} ➔ {nextStop.station_code})
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => toggleSegment(segmentKey)}
                          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 shadow-sm"
                        >
                          <span>Hide (Return)</span>
                          <ChevronUp className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="space-y-1 max-h-72 overflow-y-auto pr-1 divide-y divide-slate-900">
                        {intermediateList.map((instation) => {
                          const passTime = estimatePassingTime(
                            instation.distance_km,
                            stop.distance_km,
                            nextStop.distance_km,
                            stop.scheduled_departure || stop.scheduled_arrival,
                            nextStop.scheduled_arrival || nextStop.scheduled_departure
                          );

                          return (
                            <div
                              key={instation.code}
                              className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-slate-900/60 text-xs transition-colors"
                            >
                              <div className="flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                                <span className="font-semibold text-slate-200">{instation.name}</span>
                                <span className="font-mono text-[10px] text-amber-400/90 bg-slate-900 px-1 py-0.5 rounded border border-slate-800">
                                  {instation.code}
                                </span>
                              </div>

                              <div className="flex items-center gap-4 text-right font-mono text-xs">
                                <span className="text-slate-500 text-[11px]">{instation.distance_km} km</span>
                                <span className="text-slate-300">
                                  Passing: <strong className="text-amber-400 font-bold">{passTime}</strong>
                                </span>
                                <span className="text-[10px] text-slate-500 px-1.5 py-0.5 rounded bg-slate-900">
                                  No halt
                                </span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
