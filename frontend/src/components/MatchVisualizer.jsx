import React from 'react';
import { ArrowLeft, CheckCircle2, XCircle, Check } from 'lucide-react';
import { CompanyInsightsView } from './CompanyInsightsView';

export const MatchVisualizer = ({ analysis, onBack }) => {
  return (
    <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
      <button onClick={onBack} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition">
        <ArrowLeft className="h-4 w-4" /> Back to Feed
      </button>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-20 w-20 rounded-full bg-emerald-500/10 border-8 border-emerald-500/20 mb-4">
            <span className="text-3xl font-bold text-emerald-400">{Math.round(analysis.metrics.composite_score)}</span>
          </div>
          <h2 className="text-2xl font-bold text-white">{analysis.job_title}</h2>
          <p className="text-slate-400 mt-1">{analysis.company}</p>
        </div>

        {/* Integrated Grounded Public Research */}
        <CompanyInsightsView jobId={analysis.job_id} companyName={analysis.company} />

        {/* Visual Progress Rings/Bars */}
        <div className="space-y-4 mb-8">
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Skill Coverage</span>
              <span className="text-emerald-400 font-mono">{(analysis.metrics.skill_coverage * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full transition-all duration-1000"
                style={{ width: `${analysis.metrics.skill_coverage * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Semantic Relevance</span>
              <span className="text-sky-400 font-mono">{(analysis.metrics.semantic_similarity * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-sky-600 to-sky-400 rounded-full transition-all duration-1000"
                style={{ width: `${analysis.metrics.semantic_similarity * 100}%` }}
              />
            </div>
          </div>
        </div>

        <div className="bg-slate-950/50 rounded-2xl p-5 border border-slate-800 mb-8 text-sm text-slate-300 leading-relaxed">
          {analysis.compatibility_explanation}
        </div>

        {/* Skill Evidence (Visual Checklist) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Verified Match
            </h4>
            <ul className="space-y-3">
              {analysis.evidence_breakdown.filter(e => e.in_resume).map((e, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm bg-emerald-950/10 border border-emerald-900/30 p-3 rounded-xl">
                  <Check className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-slate-200 block">{e.skill}</span>
                    <span className="text-xs text-slate-500 italic block mt-1">"{e.evidence_quote}"</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-2">
              <XCircle className="h-4 w-4 text-rose-400" /> Missing / Gap
            </h4>
            <ul className="space-y-3">
              {analysis.skill_gaps.map((gap, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm bg-rose-950/10 border border-rose-900/30 p-3 rounded-xl">
                  <div className="h-1.5 w-1.5 rounded-full bg-rose-500 mt-2 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-slate-200 block">{gap.skill}</span>
                    <span className="text-xs text-slate-400 block mt-0.5">{gap.recommended_learning}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};