import React from 'react';
import { Target, CheckCircle, XCircle, BookOpen, Quote, Sparkles, Compass, ArrowRight, ShieldAlert } from 'lucide-react';

export const JobMatchAnalysisView = ({ analysis, onBack }) => {
  if (!analysis) return null;

  const { metrics } = analysis;

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-emerald-400 border-emerald-500/40 bg-emerald-950/20';
    if (score >= 50) return 'text-amber-400 border-amber-500/40 bg-amber-950/20';
    return 'text-rose-400 border-rose-500/40 bg-rose-950/20';
  };

  return (
    <div className="w-full max-w-5xl space-y-6 mt-6 animate-fade-in text-slate-200">
      {/* Header & Scoreboard */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-sky-400 mb-1">
              Match Intelligence Dossier
            </div>
            <h2 className="text-2xl font-bold text-white">
              {analysis.job_title} <span className="text-slate-400 text-lg font-normal">at {analysis.company}</span>
            </h2>
          </div>
          <button
            onClick={onBack}
            className="text-xs font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-1.5 rounded-lg border border-slate-700 transition"
          >
            ← Back to Job Results
          </button>
        </div>

        {/* Deterministic Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className={`p-4 rounded-xl border flex flex-col justify-between ${getScoreColor(metrics.composite_score)}`}>
            <span className="text-xs font-mono uppercase">Composite Fit</span>
            <div className="text-3xl font-extrabold my-2">{metrics.composite_score}%</div>
            <span className="text-[10px] opacity-80 font-mono">Weighted Algorithm</span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">Semantic Cosine</span>
            <div className="text-2xl font-bold text-sky-400 my-2">
              {(metrics.semantic_similarity * 100).toFixed(1)}%
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Dense Vector Embeddings</span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">Required Skills</span>
            <div className="text-2xl font-bold text-emerald-400 my-2">
              {(metrics.skill_coverage * 100).toFixed(0)}%
            </div>
            <span className="text-[10px] text-slate-500 font-mono">
              {analysis.matched_skills.length} matched / {analysis.matched_skills.length + analysis.missing_required_skills.length} required
            </span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <span className="text-xs font-mono uppercase text-slate-400">Location Fit</span>
            <div className="text-2xl font-bold text-purple-400 my-2">
              {(metrics.location_alignment * 100).toFixed(0)}%
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Remote / Local Match</span>
          </div>
        </div>

        <div className="mt-3 text-[11px] font-mono text-slate-500 text-center">
          {metrics.calculation_basis}
        </div>
      </div>

      {/* Compatibility Explanation */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
          <Sparkles className="h-4 w-4 text-sky-400" />
          AI Compatibility Evaluation
        </h3>
        <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
          {analysis.compatibility_explanation}
        </p>
      </div>

      {/* Grounded Resume Evidence Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
          <Quote className="h-4 w-4 text-sky-400" />
          Grounded Resume Evidence Verification
        </h3>
        <div className="space-y-3">
          {analysis.evidence_breakdown.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 text-xs flex flex-col md:flex-row justify-between items-start md:items-center gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-200">{item.skill}</span>
                  {item.in_resume ? (
                    <span className="inline-flex items-center text-[10px] text-emerald-400 bg-emerald-950/50 border border-emerald-800 px-2 py-0.5 rounded font-mono">
                      <CheckCircle className="h-3 w-3 mr-1" /> Found in Resume
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-[10px] text-rose-400 bg-rose-950/50 border border-rose-800 px-2 py-0.5 rounded font-mono">
                      <XCircle className="h-3 w-3 mr-1" /> Absent in Resume
                    </span>
                  )}
                </div>
                {item.evidence_quote ? (
                  <p className="text-slate-400 italic font-mono bg-slate-900 p-2 rounded border border-slate-800 mt-1">
                    "{item.evidence_quote}"
                  </p>
                ) : (
                  <p className="text-slate-500 italic mt-1">No explicit project or job bullet validates this skill in your resume.</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Concrete Skill Gaps */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
          <ShieldAlert className="h-4 w-4 text-amber-400" />
          Skill Gap Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysis.skill_gaps.map((gap, idx) => (
            <div key={idx} className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white text-sm">{gap.skill}</span>
                <span className="uppercase text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                  {gap.priority}
                </span>
              </div>
              <p className="text-slate-300"><strong className="text-slate-400">Current Gap:</strong> {gap.current_gap}</p>
              <p className="text-sky-300"><strong className="text-slate-400">Target Study:</strong> {gap.recommended_learning}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Sequenced Project-Based Roadmap */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-4">
          <Compass className="h-4 w-4 text-sky-400" />
          Milestone Career & Project Roadmap
        </h3>
        <div className="space-y-4">
          {analysis.career_roadmap.map((m) => (
            <div key={m.step} className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-[11px]">
                  {m.step}
                </span>
                <h4 className="font-semibold text-white text-sm">{m.title}</h4>
              </div>
              <p className="text-slate-300"><strong className="text-slate-400">Focus Area:</strong> {m.focus_area}</p>
              <p className="text-slate-300">
                <strong className="text-slate-400">Practice Project:</strong> {m.practice_project}
              </p>
              <div className="bg-slate-900 p-2.5 rounded border border-slate-800 font-mono text-[11px] text-emerald-300">
                <span className="text-slate-500 block mb-0.5">// Add this bullet to your resume once built:</span>
                • {m.recommended_resume_bullet}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};