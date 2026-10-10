import React, { useState, useEffect } from 'react';
import { fetchCompanyResearch } from '../services/companyService';
import { Building2, Globe, ShieldCheck, Cpu, Target, ExternalLink, Loader2, AlertCircle } from 'lucide-react';

export const CompanyInsightsView = ({ jobId, companyName }) => {
  const [research, setResearch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadResearch = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchCompanyResearch(jobId);
        setResearch(data);
      } catch (err) {
        setError(err.message || 'Unable to retrieve company intelligence.');
      } finally {
        setLoading(false);
      }
    };
    if (jobId) loadResearch();
  }, [jobId]);

  if (loading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center text-xs text-slate-400 flex flex-col items-center justify-center my-4">
        <Loader2 className="h-5 w-5 animate-spin text-sky-400 mb-2" />
        Performing permitted public research on {companyName}'s official domain...
      </div>
    );
  }

  if (error || !research) {
    return (
      <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 my-4 flex items-center gap-2 text-xs text-slate-400">
        <AlertCircle className="h-4 w-4 text-amber-400 flex-shrink-0" />
        <span>Could not complete web research: {error || 'Target domain restricted.'}</span>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 my-4 space-y-4 text-xs shadow-lg">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Building2 className="h-4 w-4 text-sky-400" />
          <h4 className="font-semibold text-white text-sm">Grounded Company Intelligence</h4>
        </div>
        <a
          href={`https://${research.official_domain}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sky-400 hover:text-white flex items-center gap-1 font-mono text-[11px]"
        >
          <Globe className="h-3.5 w-3.5" />
          {research.official_domain}
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      <p className="text-slate-300 leading-relaxed">{research.description}</p>

      {research.technology_focus?.length > 0 && (
        <div>
          <span className="text-slate-400 font-medium block mb-1.5 flex items-center gap-1">
            <Cpu className="h-3.5 w-3.5 text-purple-400" /> Technology & Architecture Focus:
          </span>
          <div className="flex flex-wrap gap-1">
            {research.technology_focus.map((tech, idx) => (
              <span key={idx} className="bg-slate-800 px-2 py-0.5 rounded text-slate-300 font-mono text-[10px]">
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {research.mission && (
        <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
          <span className="text-slate-400 font-semibold block mb-0.5 flex items-center gap-1">
            <Target className="h-3.5 w-3.5 text-emerald-400" /> Mission & Values:
          </span>
          <p className="text-slate-300 italic">{research.mission}</p>
        </div>
      )}

      {research.relevant_facts?.length > 0 && (
        <div className="space-y-1">
          <span className="text-slate-400 font-medium block">Key Grounded Facts:</span>
          <ul className="list-disc list-inside text-slate-300 space-y-0.5">
            {research.relevant_facts.slice(0, 3).map((f, idx) => (
              <li key={idx}>
                {f.fact} &mdash;{" "}
                <a href={f.source_url} target="_blank" rel="noopener noreferrer" className="text-sky-400 underline">
                  source
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};