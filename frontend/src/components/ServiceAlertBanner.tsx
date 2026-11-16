import React from 'react';
import { AlertTriangle, Info, Bell, ShieldAlert, ChevronRight } from 'lucide-react';
import { ServiceAlert } from '../types';
import { StatusBadge } from './StatusBadge';

interface ServiceAlertBannerProps {
  alerts: ServiceAlert[];
  onViewAll?: () => void;
  onSelectTrain?: (trainNumber: string) => void;
}

export const ServiceAlertBanner: React.FC<ServiceAlertBannerProps> = ({
  alerts,
  onViewAll,
  onSelectTrain
}) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-amber-950/40 via-slate-900/80 to-slate-900 border border-amber-800/40 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-amber-400 animate-bounce" />
          <h4 className="text-xs uppercase tracking-wider font-bold text-amber-300">
            Indian Railways Operational Notices & Alerts ({alerts.length})
          </h4>
        </div>

        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center gap-1 transition-colors"
          >
            <span>View All Notices</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {alerts.slice(0, 3).map((alert) => (
          <div
            key={alert.id}
            className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-amber-700/50 transition-colors flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <StatusBadge type="severity" value={alert.severity} />
                <span className="text-[10px] font-mono uppercase text-slate-400">
                  {alert.alert_type}
                </span>
              </div>
              <h5 className="text-xs font-bold text-slate-100 line-clamp-1 mb-1">
                {alert.title}
              </h5>
              <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                {alert.description}
              </p>
            </div>

            {/* Affected trains chips */}
            {alert.affected_train_numbers && alert.affected_train_numbers.length > 0 && (
              <div className="mt-2.5 pt-2 border-t border-slate-900 flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] text-slate-500 font-mono">Affected:</span>
                {alert.affected_train_numbers.map((t) => (
                  <button
                    key={t}
                    onClick={() => onSelectTrain?.(t)}
                    className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-colors"
                  >
                    #{t}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
