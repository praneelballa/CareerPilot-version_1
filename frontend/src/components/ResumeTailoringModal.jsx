import React, { useState, useEffect } from 'react';
import { fetchResumeTailoring, fetchApplicationEmail } from '../services/intelligenceService';
import { X, Sparkles, Mail, FileEdit, Check, Copy, AlertCircle, Loader2 } from 'lucide-react';

export const ResumeTailoringModal = ({ candidateId, jobId, jobTitle, company, onClose }) => {
  const [activeTab, setActiveTab] = useState('tailoring');
  const [tailoring, setTailoring] = useState(null);
  const [emailData, setEmailData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [tailorRes, emailRes] = await Promise.all([
          fetchResumeTailoring(candidateId, jobId),
          fetchApplicationEmail(candidateId, jobId),
        ]);
        setTailoring(tailorRes);
        setEmailData(emailRes);
      } catch (err) {
        setError(err.message || 'Failed generating customized application artifacts.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [candidateId, jobId]);

  const copyEmail = () => {
    if (!emailData) return;
    const fullText = `Subject: ${emailData.subject_line}\n\n${emailData.email_body}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-950/60">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-sky-400">
              Grounded Application Intelligence
            </span>
            <h3 className="text-lg font-bold text-white">
              {jobTitle} <span className="text-slate-400 font-normal">at {company}</span>
            </h3>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-slate-800 bg-slate-950/40 px-5 gap-4">
          <button
            onClick={() => setActiveTab('tailoring')}
            className={`py-3 text-xs font-medium border-b-2 flex items-center gap-1.5 transition ${
              activeTab === 'tailoring'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-white'
            }`}
          >
            <FileEdit className="h-4 w-4" />
            Resume Bullet Re-writes
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`py-3 text-xs font-medium border-b-2 flex items-center gap-1.5 transition ${
              activeTab === 'email'
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-white'
            }`}
          >
            <Mail className="h-4 w-4" />
            Personalized Application Email
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-300">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-400">
              <Loader2 className="h-8 w-8 animate-spin text-sky-400 mb-3" />
              <p className="text-sm">Synthesizing grounded resume improvements and outreach email...</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-950/40 border border-red-800/60 rounded-lg text-xs text-red-300 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Tab 1: Tailoring */}
          {!loading && !error && activeTab === 'tailoring' && tailoring && (
            <div className="space-y-6">
              <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                <span className="text-xs font-semibold text-slate-400 block mb-1">Tailored Profile Summary</span>
                <p className="text-xs text-slate-200 leading-relaxed">{tailoring.targeted_summary}</p>
              </div>

              <div>
                <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-3">
                  Bullet Point Optimizations (Fact-Grounded)
                </h4>
                <div className="space-y-4">
                  {tailoring.bullet_improvements.map((bullet, idx) => (
                    <div key={idx} className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 space-y-2 text-xs">
                      <div>
                        <span className="text-slate-500 font-mono text-[10px] uppercase">Original Bullet:</span>
                        <p className="text-slate-400 italic">"{bullet.original_evidence}"</p>
                      </div>
                      <div className="text-amber-400/90 text-[11px]">
                        <strong>Identified Weakness:</strong> {bullet.weakness}
                      </div>
                      <div className="bg-slate-900 p-2.5 rounded border border-slate-800 text-emerald-300 font-mono">
                        <span className="text-slate-500 block text-[10px] mb-0.5">// Suggested Optimized Bullet:</span>
                        • {bullet.suggested_rewrite}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Email */}
          {!loading && !error && activeTab === 'email' && emailData && (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                <div className="text-xs font-mono">
                  <span className="text-slate-500">Subject: </span>
                  <span className="text-white font-medium">{emailData.subject_line}</span>
                </div>
                <button
                  onClick={copyEmail}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded flex items-center gap-1.5 transition border border-slate-700"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  {copied ? 'Copied' : 'Copy Email'}
                </button>
              </div>

              <div className="bg-slate-950/60 p-5 rounded-lg border border-slate-800 text-xs font-sans whitespace-pre-line leading-relaxed text-slate-200">
                {emailData.email_body}
              </div>

              <div className="p-3 bg-slate-950/30 rounded border border-slate-800/80">
                <span className="text-[11px] font-mono text-slate-400 block mb-1">Key Selling Points Highlighted:</span>
                <ul className="list-disc list-inside text-xs text-slate-300 space-y-0.5">
                  {emailData.key_selling_points.map((pt, pIdx) => (
                    <li key={pIdx}>{pt}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};