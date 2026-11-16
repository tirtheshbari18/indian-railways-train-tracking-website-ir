import React from 'react';
import { Train, Radio, Shield, MapPin, Sparkles, ChevronRight, Bookmark } from 'lucide-react';
import { Station, ServiceAlert } from '../types';
import { TrainSearchCard } from '../components/TrainSearchCard';
import { StationSearchCard } from '../components/StationSearchCard';
import { ServiceAlertBanner } from '../components/ServiceAlertBanner';
import { StatusBadge } from '../components/StatusBadge';
import { useSavedTrains } from '../context/SavedTrainsContext';

interface HomePageProps {
  stations: Station[];
  alerts: ServiceAlert[];
  onSearchTrains: (params: { query?: string; source?: string; destination?: string }) => void;
  onSelectTrain: (trainNumber: string) => void;
  onSelectStation: (stationCode: string) => void;
  onViewAllAlerts: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  stations,
  alerts,
  onSearchTrains,
  onSelectTrain,
  onSelectStation,
  onViewAllAlerts
}) => {
  const { isSaved, toggleSave } = useSavedTrains();

  const featuredTrains = [
    {
      num: '22961',
      name: 'Mumbai Central - Ahmedabad Vande Bharat Express',
      type: 'Vande Bharat',
      route: 'MMCT → ADI',
      dist: '491 km',
      dur: '5h 30m',
      days: '6 Days/Week (Mon-Sat)',
      tag: 'Semi-High Speed'
    },
    {
      num: '22962',
      name: 'Ahmedabad - Mumbai Central Vande Bharat Express',
      type: 'Vande Bharat',
      route: 'ADI → MMCT',
      dist: '491 km',
      dur: '5h 40m',
      days: '6 Days/Week (Mon-Sat)',
      tag: 'Semi-High Speed'
    },
    {
      num: '22954',
      name: 'Gujarat Superfast Express',
      type: 'Superfast',
      route: 'ADI → MMCT',
      dist: '491 km',
      dur: '8h 54m',
      days: 'Daily',
      tag: 'WR Western Lifeline'
    },
    {
      num: '22953',
      name: 'Gujarat Superfast Express',
      type: 'Superfast',
      route: 'MMCT → ADI',
      dist: '491 km',
      dur: '9h 00m',
      days: 'Daily',
      tag: 'WR Western Lifeline'
    },
    {
      num: '12951',
      name: 'Mumbai Tejas Rajdhani Express',
      type: 'Rajdhani',
      route: 'MMCT → NDLS',
      dist: '1384 km',
      dur: '15h 32m',
      days: 'Daily',
      tag: 'Flagship Superfast'
    },
    {
      num: '22436',
      name: 'Vande Bharat Express',
      type: 'Vande Bharat',
      route: 'NDLS → BSB',
      dist: '759 km',
      dur: '8h 00m',
      days: '6 Days/Week',
      tag: 'Semi-High Speed'
    },
    {
      num: '12002',
      name: 'New Delhi - Bhopal Shatabdi',
      type: 'Shatabdi',
      route: 'NDLS → RKMP',
      dist: '707 km',
      dur: '8h 30m',
      days: 'Daily',
      tag: 'Express Day Train'
    },
    {
      num: '12301',
      name: 'Howrah - New Delhi Rajdhani Express',
      type: 'Rajdhani',
      route: 'HWH → NDLS',
      dist: '1451 km',
      dur: '17h 05m',
      days: '6 Days/Week',
      tag: 'Grand Trunk Route'
    },
    {
      num: '20607',
      name: 'Chennai - Mysuru Vande Bharat',
      type: 'Vande Bharat',
      route: 'MAS → MYS',
      dist: '497 km',
      dur: '6h 30m',
      days: '6 Days/Week',
      tag: 'South India Express'
    },
    {
      num: '12009',
      name: 'Mumbai - Ahmedabad Shatabdi Express',
      type: 'Shatabdi',
      route: 'MMCT → ADI',
      dist: '493 km',
      dur: '6h 25m',
      days: '6 Days/Week',
      tag: 'Western Corridor'
    }
  ];

  return (
    <div className="space-y-10 pb-12">
      {/* Hero Section */}
      <section className="relative pt-6 pb-2 text-center md:text-left">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="max-w-2xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Radio className="w-3.5 h-3.5 animate-pulse text-amber-400" />
              <span>INDIAN RAILWAYS PASSENGER INFORMATION & TELEMETRY</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Real-Time Train Tracking & <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600">Operational Schedules</span>
            </h1>

            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              Engineered to standards inspired by CRIS (Centre for Railway Information Systems) and RailTel. Search any train by number, name, or route; inspect verified stop-by-stop timetables, platforms, delays, and interactive Leaflet track maps.
            </p>

            <div className="flex items-center gap-3 pt-2 text-xs font-mono text-slate-400 flex-wrap">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>Verified NTES Adapter</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                <span>Demo Simulator</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-500"></span>
                <span>Static Timetable Baseline</span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Badges */}
          <div className="grid grid-cols-2 gap-3 w-full md:w-auto shrink-0 font-mono text-center">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="text-2xl font-extrabold text-amber-400">25+</div>
              <div className="text-[11px] text-slate-400 uppercase tracking-wider mt-0.5">Junctions</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="text-2xl font-extrabold text-emerald-400">99.4%</div>
              <div className="text-[11px] text-slate-400 uppercase tracking-wider mt-0.5">Telemetry Feed</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="text-2xl font-extrabold text-blue-400">8+</div>
              <div className="text-[11px] text-slate-400 uppercase tracking-wider mt-0.5">Flagships</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
              <div className="text-2xl font-extrabold text-purple-400">24x7</div>
              <div className="text-[11px] text-slate-400 uppercase tracking-wider mt-0.5">CRIS Architecture</div>
            </div>
          </div>
        </div>
      </section>

      {/* Service Alert Banner */}
      <ServiceAlertBanner
        alerts={alerts}
        onViewAll={onViewAllAlerts}
        onSelectTrain={onSelectTrain}
      />

      {/* Main Search Card */}
      <section>
        <TrainSearchCard
          stations={stations}
          onSearch={onSearchTrains}
          onSelectTrainDirect={onSelectTrain}
        />
      </section>

      {/* Featured Flagship Trains */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <span>Indian Railways Flagship Express Trains</span>
            </h2>
            <p className="text-xs text-slate-400">Instant live telemetry and route visualization</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {featuredTrains.map((t) => (
            <div
              key={t.num}
              onClick={() => onSelectTrain(t.num)}
              className="p-5 rounded-2xl bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-amber-500/50 cursor-pointer transition-all shadow-md group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-mono font-extrabold text-base text-amber-400 bg-slate-950 px-2.5 py-0.5 rounded-md border border-slate-800">
                    {t.num}
                  </span>
                  <StatusBadge type="trainType" value={t.type} />
                </div>

                <h3 className="text-sm font-bold text-slate-100 group-hover:text-amber-400 transition-colors line-clamp-1">
                  {t.name}
                </h3>

                <div className="mt-3 flex items-center gap-2 text-xs font-mono text-slate-300">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{t.route}</span>
                </div>

                <div className="mt-2 flex items-center gap-4 text-xs text-slate-400">
                  <span>Dist: <strong className="text-slate-300">{t.dist}</strong></span>
                  <span>•</span>
                  <span>Time: <strong className="text-slate-300">{t.dur}</strong></span>
                  <span>•</span>
                  <span>{t.days}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[11px] font-mono text-slate-500">{t.tag}</span>
                <span className="text-amber-400 font-semibold group-hover:translate-x-1 transition-transform flex items-center gap-0.5">
                  <span>Track Live</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Station Live Board Explorer */}
      <section>
        <StationSearchCard
          stations={stations}
          onSelectStation={onSelectStation}
        />
      </section>
    </div>
  );
};
