import React from 'react';
import { TrendingUp, Target, Briefcase, Zap, AlertCircle } from 'lucide-react';

export const DashboardView = ({ profile, discoveredJobsCount, onNavigate }) => {
  if (!profile) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center space-y-4 pt-20">
        <div className="h-16 w-16 bg-slate-900 rounded-full flex items-center justify-center mb-2">
          <AlertCircle className="h-8 w-8 text-sky-400" />
        </div>
        <h2 className="text-2xl font-bold text-white">Welcome to CareerPilotAI</h2>
        <p className="text-slate-400 max-w-sm">Upload your resume to unlock automated job discovery and AI intelligence.</p>
        <button 
          onClick={() => onNavigate('resume')}
          className="bg-white text-slate-950 font-semibold px-6 py-2.5 rounded-full hover:bg-slate-200 transition"
        >
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Overview</h1>
        <p className="text-slate-400 mt-1">Here is your career intelligence snapshot.</p>
      </header>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between">
          <Briefcase className="h-5 w-5 text-sky-400 mb-4" />
          <span className="text-3xl font-bold text-white">{discoveredJobsCount}</span>
          <span className="text-xs text-slate-400 mt-1">Live Compatible Roles</span>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between">
          <Target className="h-5 w-5 text-emerald-400 mb-4" />
          <span className="text-3xl font-bold text-white">{profile.skills.programming_languages.length + profile.skills.frameworks.length}</span>
          <span className="text-xs text-slate-400 mt-1">Verified Core Skills</span>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-900 to-slate-900/50 border border-slate-800 rounded-3xl p-6 relative overflow-hidden">
        <div className="relative z-10">
          <h3 className="text-lg font-bold text-white mb-2">Automated Discovery Active</h3>
          <p className="text-sm text-slate-300 mb-5 max-w-md">
            Your profile has been indexed. The engine is pulling live jobs matching your extracted credentials from Remotive and other sources.
          </p>
          <button 
            onClick={() => onNavigate('jobs')}
            className="bg-sky-500 hover:bg-sky-400 text-white font-semibold px-5 py-2.5 rounded-xl transition shadow-lg shadow-sky-500/20 text-sm"
          >
            View Job Feed
          </button>
        </div>
        <Zap className="absolute -right-6 -bottom-6 h-40 w-40 text-slate-800/50 rotate-12" />
      </div>
    </div>
  );
};