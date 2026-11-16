import React, { useState } from 'react';
import { Bell, AlertTriangle, ShieldAlert, Info, Calendar, Train, ArrowLeft, Filter } from 'lucide-react';
import { ServiceAlert } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface ServiceAlertsPageProps {
  alerts: ServiceAlert[];
  onSelectTrain: (trainNumber: string) => void;
  onBack: () => void;
}

export const ServiceAlertsPage: React.FC<ServiceAlertsPageProps> = ({
  alerts,
  onSelectTrain,
  onBack
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const filteredAlerts = alerts.filter((a) => {
    if (severityFilter === 'ALL') return true;
    return a.severity.toLowerCase() === severityFilter.toLowerCase();
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
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
              <Bell className="w-5 h-5 text-amber-500" />
              <span>Indian Railways Official Bulletins & Service Notices</span>
            </h2>
            <p className="text-xs text-slate-400">Live disruptions, fog speed restrictions, and track maintenance</p>
          </div>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            Severity:
          </span>
          {['ALL', 'critical', 'warning', 'info'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase transition-colors ${
                severityFilter === sev
                  ? 'bg-amber-500 text-slate-950 font-bold'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Grid */}
      {filteredAlerts.length === 0 ? (
        <div className="p-12 text-center bg-slate-900/60 rounded-2xl border border-slate-800 text-slate-400">
          No service notices active for this filter.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-md space-y-4 hover:border-slate-700 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
                <div className="flex items-center gap-2.5">
                  <StatusBadge type="severity" value={alert.severity} />
                  <span className="text-xs font-mono font-bold uppercase text-amber-400 bg-slate-950 px-2.5 py-0.5 rounded border border-slate-800">
                    {alert.alert_type}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                  <span>
                    Posted: {new Date(alert.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-white mb-2">
                  {alert.title}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {alert.description}
                </p>
              </div>

              {/* Affected Trains & Stations */}
              <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[11px] font-mono text-slate-500">Affected Express Trains:</span>
                  {alert.affected_train_numbers && alert.affected_train_numbers.length > 0 ? (
                    alert.affected_train_numbers.map((t) => (
                      <button
                        key={t}
                        onClick={() => onSelectTrain(t)}
                        className="px-2 py-0.5 rounded bg-slate-800 hover:bg-amber-500 hover:text-slate-950 font-mono font-bold text-amber-300 text-[11px] transition-colors"
                      >
                        #{t}
                      </button>
                    ))
                  ) : (
                    <span className="text-slate-400 italic">General Railway Network Notice</span>
                  )}
                </div>

                {alert.affected_station_codes && alert.affected_station_codes.length > 0 && (
                  <div className="flex items-center gap-1.5 font-mono text-slate-400">
                    <span className="text-[11px] text-slate-500">Divisions/Stations:</span>
                    {alert.affected_station_codes.map((st) => (
                      <span key={st} className="px-1.5 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                        {st}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
