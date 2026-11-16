import React, { useState } from 'react';
import { Train, LogIn, UserPlus, ShieldCheck, UserCheck, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface LoginPageProps {
  onSuccess: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess }) => {
  const { login, register } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isRegisterMode) {
        await register({ username, email, password, role: 'passenger' });
      } else {
        await login(username, password);
      }
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Authentication error');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (u: string, p: string) => {
    setLoading(true);
    setError(null);
    try {
      await login(u, p);
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-amber-500 text-slate-950 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/20">
          <Train className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-extrabold text-white">
          {isRegisterMode ? 'Passenger Registration' : 'CRIS & RailTrack Portal'}
        </h2>
        <p className="text-xs text-slate-400">
          {isRegisterMode ? 'Create a passenger profile to save favorite trains' : 'Sign in to access admin tools & saved trains'}
        </p>
      </div>

      {/* One-Click Demo Logins */}
      <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-2.5">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-center">
          Instant Evaluator One-Click Logins
        </div>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            disabled={loading}
            onClick={() => handleQuickLogin('admin', 'RailAdmin@2026')}
            className="p-2.5 rounded-xl bg-purple-950/60 hover:bg-purple-900/60 border border-purple-800/80 text-purple-200 text-xs font-semibold flex flex-col items-center justify-center gap-1 transition-colors"
          >
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span>Demo Admin</span>
            <span className="text-[9px] text-purple-400 font-mono">admin role</span>
          </button>

          <button
            type="button"
            disabled={loading}
            onClick={() => handleQuickLogin('passenger', 'Passenger@2026')}
            className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold flex flex-col items-center justify-center gap-1 transition-colors"
          >
            <UserCheck className="w-4 h-4 text-emerald-400" />
            <span>Demo Passenger</span>
            <span className="text-[9px] text-emerald-400 font-mono">passenger role</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Manual Login/Register Form */}
      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        <div>
          <label className="block text-slate-300 font-semibold mb-1">Username</label>
          <input
            type="text"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. admin or passenger"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
        </div>

        {isRegisterMode && (
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. passenger@railtrack.gov.in"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>
        )}

        <div>
          <label className="block text-slate-300 font-semibold mb-1">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold py-3 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-xs"
        >
          {isRegisterMode ? <UserPlus className="w-4 h-4" /> : <LogIn className="w-4 h-4" />}
          <span>{loading ? 'Authenticating...' : isRegisterMode ? 'Create Account' : 'Sign In'}</span>
        </button>
      </form>

      <div className="text-center pt-2">
        <button
          type="button"
          onClick={() => {
            setIsRegisterMode(!isRegisterMode);
            setError(null);
          }}
          className="text-xs text-amber-400 hover:text-amber-300 transition-colors"
        >
          {isRegisterMode ? 'Already have an account? Sign in' : "Don't have an account? Register as Passenger"}
        </button>
      </div>
    </div>
  );
};
