import React, { useState } from 'react';
import { Train, Navigation, Bell, Bookmark, ShieldCheck, LogIn, LogOut, Menu, X, Radio } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useSavedTrains } from '../context/SavedTrainsContext';

interface NavbarProps {
  currentPage: string;
  onNavigate: (page: string, params?: any) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { savedTrains } = useSavedTrains();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNav = (page: string, params?: any) => {
    onNavigate(page, params);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div
            onClick={() => handleNav('home')}
            className="flex items-center gap-3 cursor-pointer group select-none"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-md shadow-amber-500/20 group-hover:scale-105 transition-transform">
              <Train className="w-6 h-6 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-white">RailTrack</span>
                <span className="font-semibold text-xs px-1.5 py-0.5 rounded bg-amber-500 text-slate-950 uppercase font-mono tracking-wider">India</span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium">CRIS & RailTel Operations Portal</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => handleNav('home')}
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                currentPage === 'home' ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              Train Search
            </button>

            <button
              onClick={() => handleNav('stations')}
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                currentPage === 'stations' ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              Station Live Board
            </button>

            <button
              onClick={() => handleNav('alerts')}
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                currentPage === 'alerts' ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <Bell className="w-4 h-4 text-amber-400" />
              <span>Service Alerts</span>
            </button>

            <button
              onClick={() => handleNav('saved')}
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                currentPage === 'saved' ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-900'
              }`}
            >
              <Bookmark className="w-4 h-4 text-slate-400" />
              <span>Saved Trains</span>
              {savedTrains.length > 0 && (
                <span className="ml-1 px-1.5 py-0.2 rounded-full text-[11px] font-mono font-bold bg-amber-500 text-slate-950">
                  {savedTrains.length}
                </span>
              )}
            </button>

            {isAdmin && (
              <button
                onClick={() => handleNav('admin')}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                  currentPage === 'admin' ? 'bg-purple-950 text-purple-300 border border-purple-800' : 'text-purple-300 hover:bg-purple-950/50'
                }`}
              >
                <ShieldCheck className="w-4 h-4 text-purple-400" />
                <span>Admin Console</span>
              </button>
            )}
          </nav>

          {/* User Profile / Auth buttons */}
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
              <Radio className="w-3 h-3 animate-pulse text-emerald-400" />
              <span>NTES LIVE</span>
            </div>

            {isAuthenticated ? (
              <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
                <div className="text-right">
                  <div className="text-xs font-semibold text-slate-200">{user?.username}</div>
                  <div className="text-[10px] text-amber-400 font-mono capitalize">{user?.role}</div>
                </div>
                <button
                  onClick={logout}
                  title="Sign Out"
                  className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-rose-400 border border-slate-800 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => handleNav('login')}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400 transition-all shadow-sm"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In / Demo</span>
              </button>
            )}
          </div>

          {/* Mobile hamburger button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-800 bg-slate-950 px-4 pt-3 pb-6 space-y-2">
          <button
            onClick={() => handleNav('home')}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-900"
          >
            Train Search
          </button>
          <button
            onClick={() => handleNav('stations')}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-900"
          >
            Station Live Board
          </button>
          <button
            onClick={() => handleNav('alerts')}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-900 flex items-center justify-between"
          >
            <span>Service Alerts</span>
            <Bell className="w-4 h-4 text-amber-400" />
          </button>
          <button
            onClick={() => handleNav('saved')}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-200 hover:bg-slate-900 flex items-center justify-between"
          >
            <span>Saved Trains ({savedTrains.length})</span>
            <Bookmark className="w-4 h-4 text-slate-400" />
          </button>

          {isAdmin && (
            <button
              onClick={() => handleNav('admin')}
              className="w-full text-left px-3 py-2 rounded-lg text-sm text-purple-300 bg-purple-950/40 border border-purple-800"
            >
              Admin Management Console
            </button>
          )}

          <div className="pt-3 border-t border-slate-800">
            {isAuthenticated ? (
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-white">{user?.username}</div>
                  <div className="text-xs text-amber-400 capitalize">{user?.role}</div>
                </div>
                <button
                  onClick={logout}
                  className="px-3 py-1.5 rounded-lg bg-rose-950 text-rose-300 text-xs font-medium"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button
                onClick={() => handleNav('login')}
                className="w-full py-2 rounded-lg text-center text-sm font-semibold bg-amber-500 text-slate-950"
              >
                Sign In / Demo Login
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
