import React from 'react';
import { Train, Shield, Activity, MapPin, Database, Server } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-20 border-t border-slate-800 bg-slate-950 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand & Purpose */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center text-slate-950">
                <Train className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-100 text-base">RailTrack India</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Enterprise portfolio application designed for Indian Railways operational monitoring organizations: CRIS, RailTel, and RDSO.
            </p>
            <div className="text-[11px] text-slate-500 font-mono">
              FastAPI • PostgreSQL • React TS • Leaflet
            </div>
          </div>

          {/* Data Provenance & Ethics */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-amber-400" />
              <span>Data Provenance Policy</span>
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              All live positions, delays, and platforms strictly distinguish verified telemetry feeds from static timetable baselines. No synthetic data is fabricated without clear disclosure.
            </p>
          </div>

          {/* Architecture Highlights */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-blue-400" />
              <span>System Architecture</span>
            </h4>
            <ul className="space-y-1 text-slate-400">
              <li>• Pluggable Provider Adapters (NTES/RailTel)</li>
              <li>• CSV / JSON 2-Stage Validation Engine</li>
              <li>• Audit Trail & RBAC Authorization</li>
              <li>• Geospatial Track Polyline Interpolation</li>
            </ul>
          </div>

          {/* Technology Organizations */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              <span>Relevant Organizations</span>
            </h4>
            <div className="space-y-1 text-xs text-slate-400">
              <div><strong className="text-slate-300">CRIS:</strong> Centre for Railway Information Systems</div>
              <div><strong className="text-slate-300">RailTel:</strong> RailTel Corporation of India Ltd</div>
              <div><strong className="text-slate-300">RDSO:</strong> Research Designs & Standards Organisation</div>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <p className="text-slate-500">
            © 2026 RailTrack India. Portfolio-grade engineering demonstration.
          </p>
          <div className="flex items-center gap-4 text-slate-500">
            <span>ISO 9001 CRIS Guidelines Compatible</span>
            <span>•</span>
            <span>REST API v1</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
