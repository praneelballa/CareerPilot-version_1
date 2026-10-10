import React from 'react';
import { Building2, MapPin, ExternalLink, Sparkles, Clock, FileEdit } from 'lucide-react';

export const JobCard = ({ job, onAnalyze, onTailor, isMatching }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 hover:border-slate-700 transition-colors shadow-sm mb-5">
      {/* Header: Company & Meta */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
            <Building2 className="h-5 w-5 text-slate-400" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200">{job.company}</h4>
            <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-0.5">
              <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {job.location}</span>
              <span>•</span>
              <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {job.employment_type || 'Full Time'}</span>
            </div>
          </div>
        </div>
        {job.composite_score && (
          <div className="flex flex-col items-end">
            <span className="text-lg font-bold text-emerald-400">{Math.round(job.composite_score)}%</span>
            <span className="text-[9px] uppercase tracking-wider font-mono text-slate-500">Match Fit</span>
          </div>
        )}
      </div>

      {/* Body: Title & Desc */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-white mb-1.5 leading-tight">{job.title}</h3>
        <p className="text-sm text-slate-400 line-clamp-2 leading-relaxed">{job.description}</p>
      </div>

      {/* Tags */}
      {job.required_skills?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-5">
          {job.required_skills.slice(0, 5).map((skill, idx) => (
            <span key={idx} className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-[10px] font-medium text-slate-300 font-mono">
              {skill}
            </span>
          ))}
          {job.required_skills.length > 5 && (
            <span className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-[10px] font-medium text-slate-500 font-mono">
              +{job.required_skills.length - 5}
            </span>
          )}
        </div>
      )}

      {/* Action Bar */}
      <div className="flex items-center gap-2 pt-4 border-t border-slate-800/60">
        <button
          onClick={() => onAnalyze(job.job_id)}
          disabled={isMatching}
          className="flex-1 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 px-4 py-2.5 rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2"
        >
          {isMatching ? <Sparkles className="h-4 w-4 animate-pulse" /> : <Sparkles className="h-4 w-4" />}
          {isMatching ? 'Analyzing...' : 'AI Match Analysis'}
        </button>
        
        <button
          onClick={() => onTailor(job)}
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2.5 rounded-xl text-xs font-medium transition flex items-center justify-center gap-2"
        >
          <FileEdit className="h-4 w-4" />
          Tailor
        </button>

        <a
          href={job.application_url}
          target="_blank"
          rel="noopener noreferrer"
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2.5 rounded-xl transition flex items-center justify-center"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </div>
  );
};