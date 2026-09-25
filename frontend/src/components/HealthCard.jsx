import React from 'react';
import { Activity, ShieldCheck, AlertCircle, RefreshCw } from 'lucide-react';

export const HealthCard = ({ healthData, loading, error, onRefresh }) => {
  return (
    <div className="w-full max-w-md bg-slate-800/80 border border-slate-700/60 rounded-xl p-6 shadow-2xl backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-700 pb-4 mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-sky-400" />
          <h2 className="text-lg font-semibold tracking-wide text-slate-100">Core Engine Link</h2>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition disabled:opacity-50"
          title="Refresh Status"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-6 text-slate-400 text-sm">
          <RefreshCw className="h-5 w-5 animate-spin mr-2 text-sky-400" />
          Querying backend status...
        </div>
      )}

      {error && !loading && (
        <div className="rounded-lg bg-red-950/40 border border-red-800/50 p-4">
          <div className="flex items-center space-x-2 text-red-400 font-medium mb-1">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span>Connection Failed</span>
          </div>
          <p className="text-xs text-red-300/80 pl-7">{error}</p>
        </div>
      )}

      {healthData && !loading && !error && (
        <div className="space-y-3">
          <div className="flex justify-between items-center bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">Status</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-950 text-emerald-300 border border-emerald-800">
              <ShieldCheck className="w-3 h-3 mr-1" />
              {healthData.status}
            </span>
          </div>
          <div className="flex justify-between items-center bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">Environment</span>
            <span className="text-xs font-mono text-slate-200">{healthData.environment}</span>
          </div>
          <div className="flex justify-between items-center bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">Engine Version</span>
            <span className="text-xs font-mono text-slate-200">{healthData.version}</span>
          </div>
          <div className="flex justify-between items-center bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-mono">Timestamp</span>
            <span className="text-[11px] font-mono text-slate-400">
              {new Date(healthData.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};