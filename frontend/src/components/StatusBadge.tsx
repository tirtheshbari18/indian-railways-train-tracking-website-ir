import React from 'react';

interface StatusBadgeProps {
  type: 'trainType' | 'runningStatus' | 'provenance' | 'platformSource' | 'severity';
  value: string;
  delayMinutes?: number;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  type,
  value,
  delayMinutes = 0,
  className = ''
}) => {
  if (type === 'trainType') {
    const val = value.toLowerCase();
    let bg = 'bg-blue-950/80 text-blue-300 border-blue-700/50';
    if (val.includes('vande')) {
      bg = 'bg-amber-950/80 text-amber-300 border-amber-600/60 font-semibold';
    } else if (val.includes('rajdhani')) {
      bg = 'bg-red-950/80 text-red-300 border-red-700/60 font-semibold';
    } else if (val.includes('shatabdi')) {
      bg = 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60';
    } else if (val.includes('superfast')) {
      bg = 'bg-emerald-950/80 text-emerald-300 border-emerald-700/50';
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${bg} ${className}`}>
        {value}
      </span>
    );
  }

  if (type === 'runningStatus') {
    const val = value.toUpperCase();
    if (val === 'RUNNING_ON_TIME' || val === 'ON_TIME') {
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-700/50 ${className}`}>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Right Time (On Time)
        </span>
      );
    }
    if (val === 'RUNNING_LATE' || val === 'LATE') {
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-700/50 ${className}`}>
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
          Late ({delayMinutes > 0 ? `+${delayMinutes}m` : 'Delayed'})
        </span>
      );
    }
    if (val === 'HALTED') {
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-950 text-blue-400 border border-blue-700/50 ${className}`}>
          <span className="w-2 h-2 rounded-full bg-blue-400"></span>
          Halted at Station
        </span>
      );
    }
    if (val === 'ARRIVED') {
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-teal-950 text-teal-300 border border-teal-700/50 ${className}`}>
          ✓ Journey Completed
        </span>
      );
    }
    if (val === 'NOT_STARTED') {
      return (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700 ${className}`}>
          Yet to Start from Origin
        </span>
      );
    }
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-800 ${className}`}>
        Live Data Unavailable
      </span>
    );
  }

  if (type === 'provenance') {
    if (value === 'verified_live_feed') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-950/90 text-emerald-300 border border-emerald-600/40">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          VERIFIED NTES FEED
        </span>
      );
    }
    if (value === 'demo_simulation') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-amber-950/80 text-amber-300 border border-amber-600/40">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          DEMO SIMULATION FEED
        </span>
      );
    }
    if (value === 'unavailable') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-rose-950/80 text-rose-300 border border-rose-600/40">
          OFFLINE TIMETABLE ONLY
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
        SCHEDULED TIMETABLE
      </span>
    );
  }

  if (type === 'platformSource') {
    if (value === 'verified_feed') {
      return (
        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
          Confirmed
        </span>
      );
    }
    if (value === 'estimated') {
      return (
        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60">
          Estimated
        </span>
      );
    }
    return (
      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
        Scheduled
      </span>
    );
  }

  if (type === 'severity') {
    if (value === 'critical') {
      return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-950 text-red-300 border border-red-700">CRITICAL</span>;
    }
    if (value === 'warning') {
      return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-950 text-amber-300 border border-amber-700">WARNING</span>;
    }
    return <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-950 text-blue-300 border border-blue-700">INFO</span>;
  }

  return <span>{value}</span>;
};
