import React, { useState, useEffect } from 'react';
import {
  fetchResumeOptimizations,
  createApplicationDraft,
  applySelectedResumeChanges,
  approveApplicationDraft
} from '../services/applicationService';
import {
  CheckSquare,
  Square,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Mail,
  Loader2,
  Copy,
  Check
} from 'lucide-react';

export const ResumeOptimizationView = ({ candidateId, job, onComplete }) => {
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [draft, setDraft] = useState(null);
  const [version, setVersion] = useState(null);
  const [applying, setApplying] = useState(false);
  const [approving, setApproving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);
      try {
        const [optRes, draftRes] = await Promise.all([
          fetchResumeOptimizations(candidateId, job.job_id),
          createApplicationDraft(candidateId, job.job_id)
        ]);
        setSuggestions(optRes.suggestions);
        setDraft(draftRes);

        // Pre-select non-gap suggestions
        const initial = new Set(
          optRes.suggestions.filter(s => !s.is_skill_gap).map(s => s.id)
        );
        setSelectedIds(initial);
      } catch (err) {
        setError(err.message || 'Failed loading optimization data.');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [candidateId, job.job_id]);

  const toggleSelect = (id, isGap) => {
    if (isGap) return; // Unproven skill gaps cannot be added to resume
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const selectAll = () => {
    const allValid = suggestions.filter(s => !s.is_skill_gap).map(s => s.id);
    setSelectedIds(new Set(allValid));
  };

  const deselectAll = () => {
    setSelectedIds(new Set());
  };

  const handleApplyChanges = async () => {
    if (!draft) return;
    setApplying(true);
    setError(null);
    try {
      const newVersion = await applySelectedResumeChanges(draft.id, Array.from(selectedIds));
      setVersion(newVersion);
      setDraft(prev => ({ ...prev, status: 'READY_FOR_REVIEW', resume_version_id: newVersion.version_id }));
    } catch (err) {
      setError(err.message || 'Failed applying changes.');
    } finally {
      setApplying(false);
    }
  };

  const handleApprove = async () => {
    if (!draft) return;
    setApproving(true);
    setError(null);
    try {
      const approved = await approveApplicationDraft(draft.id);
      setDraft(approved);
      if (onComplete) onComplete(approved);
    } catch (err) {
      setError(err.message || 'Approval failed.');
    } finally {
      setApproving(false);
    }
  };

  const copyEmail = () => {
    if (!draft) return;
    navigator.clipboard.writeText(`Subject: ${draft.subject}\n\n${draft.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center flex flex-col items-center justify-center text-slate-400">
        <Loader2 className="h-8 w-8 animate-spin text-sky-400 mb-3" />
        Auditing resume precision & synthesizing verified application package...
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-200">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-sky-400">
              Application Assembly & Resume Optimization
            </span>
            <h2 className="text-xl font-bold text-white mt-0.5">
              {job.title} <span className="text-slate-400 font-normal">at {job.company}</span>
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs font-mono px-3 py-1 rounded-full border ${
              draft?.status === 'APPROVED'
                ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                : 'bg-slate-800 text-sky-300 border-slate-700'
            }`}>
              Status: {draft?.status}
            </span>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-xs text-red-300 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Step 1: Granular Suggestion Cards */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText className="h-4 w-4 text-sky-400" />
              Granular Resume Suggestions
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Select verifiable edits to produce an immutable tailored resume version.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={selectAll}
              className="text-[11px] font-mono bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded border border-slate-700 transition"
            >
              Select All
            </button>
            <button
              onClick={deselectAll}
              className="text-[11px] font-mono bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded border border-slate-700 transition"
            >
              Deselect All
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {suggestions.map((sug) => {
            const isSelected = selectedIds.has(sug.id);
            return (
              <div
                key={sug.id}
                onClick={() => toggleSelect(sug.id, sug.is_skill_gap)}
                className={`p-4 rounded-xl border text-xs transition cursor-pointer flex items-start gap-3 ${
                  sug.is_skill_gap
                    ? 'bg-amber-950/10 border-amber-900/40 opacity-80 cursor-not-allowed'
                    : isSelected
                    ? 'bg-sky-950/20 border-sky-600/60'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="mt-0.5 flex-shrink-0">
                  {sug.is_skill_gap ? (
                    <AlertTriangle className="h-4 w-4 text-amber-400" />
                  ) : isSelected ? (
                    <CheckSquare className="h-4 w-4 text-sky-400" />
                  ) : (
                    <Square className="h-4 w-4 text-slate-500" />
                  )}
                </div>

                <div className="space-y-1.5 flex-1">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] uppercase text-slate-400">
                      {sug.category.replace(/_/g, ' ')}
                    </span>
                    {sug.is_skill_gap && (
                      <span className="text-[10px] bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-mono">
                        Skill Gap &mdash; Route to Roadmap
                      </span>
                    )}
                  </div>

                  <div>
                    <span className="text-slate-500 font-mono text-[10px]">Original:</span>
                    <p className="text-slate-400 italic">"{sug.original_text}"</p>
                  </div>

                  <div className="text-emerald-300 font-mono bg-slate-950 p-2 rounded border border-slate-800/80">
                    <span className="text-slate-500 text-[10px] block mb-0.5">// Suggested Optimization:</span>
                    • {sug.suggested_text}
                  </div>

                  <p className="text-slate-400 text-[11px]"><strong className="text-slate-300">Reason:</strong> {sug.reason}</p>
                  {sug.evidence && (
                    <p className="text-sky-400 text-[11px]"><strong className="text-slate-300">Grounded Evidence:</strong> {sug.evidence}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="pt-2 flex justify-between items-center border-t border-slate-800">
          <span className="text-xs text-slate-400 font-mono">
            {selectedIds.size} changes selected (These will create an immutable resume version)
          </span>
          <button
            onClick={handleApplyChanges}
            disabled={applying || selectedIds.size === 0}
            className="bg-sky-600 hover:bg-sky-500 text-white font-semibold px-4 py-2 rounded-xl text-xs transition disabled:opacity-50 flex items-center gap-1.5 shadow-lg shadow-sky-600/20"
          >
            {applying ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            {applying ? 'Applying Changes...' : version ? `Version ${version.version_number} Active` : 'Apply Selected Changes'}
          </button>
        </div>
      </div>

      {/* Step 2: Grounded Application Email Package */}
      {draft && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Mail className="h-4 w-4 text-emerald-400" />
              Verified Application Email & Package
            </h3>
            <button
              onClick={copyEmail}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg text-xs font-mono transition flex items-center gap-1.5 border border-slate-700"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
            <div className="flex justify-between border-b border-slate-800/80 pb-2">
              <span className="font-mono text-slate-500">Recipient:</span>
              <span className="font-mono text-slate-300">{draft.recipient}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/80 pb-2">
              <span className="font-mono text-slate-500">Subject:</span>
              <span className="font-medium text-white">{draft.subject}</span>
            </div>
            <div>
              <span className="font-mono text-slate-500 block mb-2">Attached Document:</span>
              <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2.5 py-1 rounded inline-flex items-center gap-1">
                <FileText className="h-3 w-3" />
                {draft.attachment_path ? draft.attachment_path.split('\\').pop().split('/').pop() : 'Original Resume'}
                {version && ` (Linked to Version ${version.version_number})`}
              </span>
            </div>
            <div className="pt-2 whitespace-pre-line leading-relaxed text-slate-300 font-sans border-t border-slate-800/80">
              {draft.body}
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <span className="text-[11px] text-slate-500 font-mono">
              Approval validates package without dispatching external network calls.
            </span>
            <button
              onClick={handleApprove}
              disabled={approving || draft.status === 'APPROVED'}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-5 py-2.5 rounded-xl text-xs transition disabled:opacity-50 flex items-center gap-1.5 shadow-lg shadow-emerald-600/20"
            >
              {approving ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
              {draft.status === 'APPROVED' ? 'Application Package Approved' : 'Approve Application Package'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};