import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Upload,
  Database,
  Users,
  Train,
  Building,
  Bell,
  Activity,
  History,
  AlertOctagon,
  PlusCircle,
  FileSpreadsheet,
  CheckCircle2,
  Layers,
  Sparkles,
  PieChart,
  MapPin
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { AdminStats, AuditLog } from '../types';
import { ImportModal } from '../components/ImportModal';

export const AdminConsolePage: React.FC = () => {
  const { user, isAdmin, isAuthenticated } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [alertFormOpen, setAlertFormOpen] = useState(false);

  // New alert form state
  const [alertTitle, setAlertTitle] = useState('');
  const [alertType, setAlertType] = useState('maintenance');
  const [alertSeverity, setAlertSeverity] = useState<'info' | 'warning' | 'critical'>('warning');
  const [alertDescription, setAlertDescription] = useState('');
  const [alertTrains, setAlertTrains] = useState('');
  const [alertStations, setAlertStations] = useState('');
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const fetchAdminData = async () => {
    try {
      const [statsData, logsData] = await Promise.all([
        api.getAdminStats(),
        api.getAuditLogs()
      ]);
      setStats(statsData);
      setAuditLogs(logsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchAdminData();
    } else {
      setLoading(false);
    }
  }, [isAdmin]);

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const trains = alertTrains.split(',').map((t) => t.trim()).filter(Boolean);
      const stations = alertStations.split(',').map((s) => s.trim().toUpperCase()).filter(Boolean);
      const token = localStorage.getItem('railtrack_token');

      const res = await fetch('/api/v1/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: alertTitle,
          alert_type: alertType,
          severity: alertSeverity,
          description: alertDescription,
          affected_train_numbers: trains,
          affected_station_codes: stations,
          is_active: true
        })
      });

      if (!res.ok) throw new Error('Failed to broadcast alert');

      setFormSuccess('Service alert broadcasted successfully across passenger portals.');
      setAlertTitle('');
      setAlertDescription('');
      setAlertTrains('');
      setAlertStations('');
      fetchAdminData();
      setTimeout(() => setFormSuccess(null), 4000);
    } catch (err: any) {
      alert(err.message || 'Error posting alert');
    }
  };

  if (!isAuthenticated || !isAdmin) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-4">
        <ShieldCheck className="w-12 h-12 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">Administrator Access Required</h3>
        <p className="text-xs text-slate-400">
          You must be signed in with administrative credentials (e.g. username <strong>admin</strong>) to access the operations console.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 text-sm font-semibold">
        Loading Administrative Telemetry & Records...
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950 text-purple-300 border border-purple-800">
              CRIS / RAILTEL OPERATIONS CONSOLE
            </span>
          </div>
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-purple-400" />
            <span>Administrative Data & Ingestion Hub</span>
          </h2>
          <p className="text-xs text-slate-400">
            Authenticated as: <strong className="text-slate-200">{user?.username}</strong> ({user?.email})
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setAlertFormOpen(!alertFormOpen)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition-colors flex items-center gap-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Broadcast Service Notice</span>
          </button>

          <button
            onClick={() => setIsImportModalOpen(true)}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 transition-all shadow-md shadow-amber-500/20 flex items-center gap-2"
          >
            <Upload className="w-4 h-4" />
            <span>Launch Bulk Import Console</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: 'Railway Stations', count: stats?.stations_count ?? 0, icon: Building, color: 'text-amber-400' },
          { label: 'Verified Trains', count: stats?.trains_count ?? 0, icon: Train, color: 'text-blue-400' },
          { label: 'Timetable Halts', count: stats?.stops_count ?? 0, icon: Database, color: 'text-emerald-400' },
          { label: 'Active Alerts', count: stats?.alerts_count ?? 0, icon: Bell, color: 'text-rose-400' },
          { label: 'Portal Users', count: stats?.users_count ?? 0, icon: Users, color: 'text-purple-400' },
          { label: 'Audit Trail Records', count: stats?.audit_logs_count ?? 0, icon: History, color: 'text-teal-400' }
        ].map((item, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
            <item.icon className={`w-5 h-5 ${item.color} mb-2`} />
            <div className={`text-2xl font-mono font-extrabold ${item.color}`}>
              {item.count}
            </div>
            <div className="text-[11px] text-slate-400 font-medium mt-0.5">
              {item.label}
            </div>
          </div>
        ))}
      </div>

      {/* Complete Indian Railways Train Category Breakdown */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-amber-500" />
              <span>Train Database Completeness by Category</span>
            </h3>
            <p className="text-xs text-slate-400">
              National inventory of Indian Railways services categorized and verified in the database
            </p>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            100% Verified Routes
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {[
            { name: 'MEMU Services', count: stats?.memu_count ?? 0, desc: 'Mainline Electric Multiple Unit', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
            { name: 'DEMU Services', count: stats?.demu_count ?? 0, desc: 'Diesel Multiple Unit', badge: 'bg-teal-500/10 text-teal-400 border-teal-500/30' },
            { name: 'Suburban Locals', count: stats?.local_count ?? 0, desc: 'Western & Central Suburban EMU', badge: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' },
            { name: 'Superfast Express', count: stats?.superfast_count ?? 0, desc: 'Rajdhani, Tejas, Vande Bharat, SF', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30' },
            { name: 'Express Trains', count: stats?.express_count ?? 0, desc: 'Mail & Intercity Express', badge: 'bg-blue-500/10 text-blue-400 border-blue-500/30' },
            { name: 'Passenger Trains', count: stats?.passenger_count ?? 0, desc: 'Slow & Ordinary Shuttles', badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30' },
            { name: 'Mail Express', count: stats?.mail_count ?? 0, desc: 'Long-distance Mail Services', badge: 'bg-violet-500/10 text-violet-400 border-violet-500/30' },
            { name: 'Weekly Trains', count: stats?.weekly_count ?? 0, desc: 'Biweekly & Triweekly Services', badge: 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30' },
            { name: 'Festival Specials', count: stats?.special_count ?? 0, desc: 'Date-aware Special Trains', badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30' },
            { name: 'Missing Routes', count: stats?.missing_route_trains_count ?? 0, desc: 'Zero Integrity Violations', badge: (stats?.missing_route_trains_count ?? 0) === 0 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30' }
          ].map((cat, idx) => (
            <div key={idx} className={`p-4 rounded-xl border bg-slate-950/60 ${cat.badge}`}>
              <div className="text-xs font-bold uppercase tracking-wider">{cat.name}</div>
              <div className="text-2xl font-mono font-extrabold mt-1">{cat.count}</div>
              <div className="text-[10px] text-slate-400 mt-1">{cat.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Railway Zones & Divisions Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Zones Coverage */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-400" />
              <span>Railway Zone Station Distribution</span>
            </h3>
            <span className="text-xs font-mono text-slate-500">
              {stats?.stations_by_zone ? Object.keys(stats.stations_by_zone).length : 0} Zones
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            {stats?.stations_by_zone &&
              Object.entries(stats.stations_by_zone).map(([zone, count]) => (
                <div
                  key={zone}
                  className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs flex items-center gap-2"
                >
                  <span className="font-bold font-mono text-amber-400">{zone}</span>
                  <span className="text-slate-400 font-mono text-[11px]">({count} stations)</span>
                </div>
              ))}
          </div>
        </div>

        {/* Divisions Coverage */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Building className="w-4 h-4 text-blue-400" />
              <span>Railway Divisions Active</span>
            </h3>
            <span className="text-xs font-mono text-slate-500">
              {stats?.stations_by_division ? Object.keys(stats.stations_by_division).length : 0} Divisions
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            {stats?.stations_by_division &&
              Object.entries(stats.stations_by_division).slice(0, 15).map(([div, count]) => (
                <div
                  key={div}
                  className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs flex items-center gap-2"
                >
                  <span className="font-bold text-slate-200">{div}</span>
                  <span className="text-slate-400 font-mono text-[11px]">({count})</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Broadcast Alert Form (Collapsible) */}
      {alertFormOpen && (
        <form onSubmit={handleCreateAlert} className="p-6 rounded-2xl bg-slate-900 border border-amber-600/40 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Bell className="w-4 h-4 text-amber-500" />
              <span>Broadcast Official Railway Advisory</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Live to all passengers</span>
          </div>

          {formSuccess && (
            <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs">
              {formSuccess}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 mb-1">Notice Title</label>
              <input
                type="text"
                required
                value={alertTitle}
                onChange={(e) => setAlertTitle(e.target.value)}
                placeholder="e.g. Winter Fog Speed Regulation or Platform Remodeling"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Severity & Type</label>
              <div className="grid grid-cols-2 gap-2">
                <select
                  value={alertSeverity}
                  onChange={(e: any) => setAlertSeverity(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-2 py-2 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="warning">Warning</option>
                  <option value="critical">Critical</option>
                  <option value="info">Info</option>
                </select>
                <select
                  value={alertType}
                  onChange={(e) => setAlertType(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-2 py-2 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="weather">Weather/Fog</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="delay">Delay</option>
                  <option value="special">Special</option>
                </select>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Notice Description</label>
            <textarea
              required
              rows={3}
              value={alertDescription}
              onChange={(e) => setAlertDescription(e.target.value)}
              placeholder="Describe operational advisory, anticipated delays, or re-routings..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Affected Train Numbers (comma separated)</label>
              <input
                type="text"
                value={alertTrains}
                onChange={(e) => setAlertTrains(e.target.value)}
                placeholder="e.g. 12951, 22436, 12002"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Affected Station Codes (comma separated)</label>
              <input
                type="text"
                value={alertStations}
                onChange={(e) => setAlertStations(e.target.value)}
                placeholder="e.g. NDLS, CNB, PRYJ"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setAlertFormOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors"
            >
              Publish Advisory
            </button>
          </div>
        </form>
      )}

      {/* Audit Log Trail Table */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-amber-500" />
              <span>CRIS Security & Operations Audit Trail</span>
            </h3>
            <p className="text-xs text-slate-400">Chronological record of imports, modifications, and system events</p>
          </div>
          <span className="text-xs font-mono text-slate-500">{auditLogs.length} logged actions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Timestamp (IST)</th>
                <th className="px-4 py-3">Operator</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Entity Type</th>
                <th className="px-4 py-3">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No audit records registered yet.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}
                    </td>
                    <td className="px-4 py-3 text-amber-400 font-semibold">{log.username || 'System'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-200 border border-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-300 uppercase">{log.entity_type}</td>
                    <td className="px-4 py-3 text-slate-400 max-w-xs truncate">
                      {log.details ? JSON.stringify(log.details) : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bulk Import Modal */}
      <ImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onSuccess={() => {
          fetchAdminData();
        }}
      />
    </div>
  );
};
