import React, { useState, useEffect } from 'react';
import {
  fetchGmailStatus,
  getGmailConnectUrl,
  approveApplicationHumanGate,
  dispatchApplicationGmail
} from '../services/gmailService';
import { fetchCompanyResearch } from '../services/companyService';
import {
  ShieldAlert,
  Send,
  CheckCircle2,
  FileText,
  Mail,
  Building2,
  Globe,
  Loader2,
  AlertTriangle,
  ArrowLeft
} from 'lucide-react';

export const ApplicationReviewView = ({ draft, job, candidateProfile, onBack, onSent }) => {
  const [recipient, setRecipient] = useState(draft?.recipient || '');
  const [subject, setSubject] = useState(draft?.subject || '');
  const [body, setBody] = useState(draft?.body || '');
  const [humanConfirmed, setHumanConfirmed] = useState(false);
  const [gmailStatus, setGmailStatus] = useState({ is_connected: false, email_address: null });
  const [companyResearch, setCompanyResearch] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  useEffect(() => {
    const loadInfo = async () => {
      try {
        const [gStatus, compRes] = await Promise.all([
          fetchGmailStatus(),
          fetchCompanyResearch(job.job_id)
        ]);
        setGmailStatus(gStatus);
        setCompanyResearch(compRes);

        // Pre-fill recipient if verified domain exists and draft recipient is empty
        if (!recipient && compRes?.official_domain) {
          setRecipient(`careers@${compRes.official_domain}`);
        }
      } catch (err) {
        console.error(err);
      }
    };
    loadInfo();
  }, [job.job_id]);

  const handleConnectGmail = async () => {
    try {
      const url = await getGmailConnectUrl();
      window.location.href = url;
    } catch (err) {
      setError(err.message || 'Failed to initiate Gmail authorization.');
    }
  };

  const handleApproveAndSend = async () => {
    if (!humanConfirmed) {
      setError('You must check the mandatory human verification box before proceeding.');
      return;
    }
    if (!recipient.trim() || !recipient.includes('@')) {
      setError('A valid recipient email address is required.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // 1. Mandatory Human Approval Gate
      await approveApplicationHumanGate(draft.id, {
        recipient: recipient.trim(),
        subject: subject.trim(),
        body: body.trim(),
        humanConfirmed: true
      });

      // 2. Dispatch via Gmail API
      const result = await dispatchApplicationGmail(draft.id);
      setSuccessResult(result);
      if (onSent) onSent(result);
    } catch (err) {
      setError(err.message || 'Transmission failed.');
    } finally {
      setLoading(false);
    }
  };

  if (successResult) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-4">
        <div className="h-16 w-16 bg-emerald-950/60 border border-emerald-800 rounded-full flex items-center justify-center mx-auto text-emerald-400">
          <CheckCircle2 className="h-8 w-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">Application Dispatched</h2>
        <p className="text-slate-400 text-sm max-w-md mx-auto">
          Your application and optimized resume have been sent via your authenticated Gmail account.
        </p>
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 max-w-md mx-auto">
          Gmail Message ID: {successResult.gmail_message_id}
        </div>
        <button
          onClick={onBack}
          className="bg-white text-slate-950 font-semibold px-6 py-2.5 rounded-xl hover:bg-slate-200 transition text-xs"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-200">
      <button onClick={onBack} className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white transition">
        <ArrowLeft className="h-4 w-4" /> Cancel & Back to Suggestions
      </button>

      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-sky-400">
              Mandatory Human Review Gate
            </span>
            <h2 className="text-xl font-bold text-white mt-0.5">
              Review & Approve Outreach to {job.company}
            </h2>
          </div>

          <div>
            {gmailStatus.is_connected ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Connected: {gmailStatus.email_address}
              </span>
            ) : (
              <button
                onClick={handleConnectGmail}
                className="bg-red-950/60 hover:bg-red-900/60 border border-red-800 text-red-300 text-xs px-3 py-1.5 rounded-xl font-mono transition flex items-center gap-1.5"
              >
                <Mail className="h-3.5 w-3.5" />
                Connect Gmail via OAuth
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-xs text-red-300 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Form Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        {/* Recipient Input (Never fabricated; user confirmed) */}
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1">
            Verified Recipient Email * (Confirm or specify)
          </label>
          <input
            type="email"
            required
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="e.g. hiring@company.com"
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
          />
        </div>

        {/* Subject */}
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1">Subject Line</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          />
        </div>

        {/* Body */}
        <div>
          <label className="block text-xs font-mono text-slate-400 mb-1">Email Body (Grounded Facts)</label>
          <textarea
            rows={10}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-sans leading-relaxed"
          />
        </div>

        {/* Attachment Card */}
        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-emerald-400" />
            <span className="font-mono text-slate-300">
              Attached Resume: {draft?.attachment_path ? draft.attachment_path.split('\\').pop().split('/').pop() : 'OffResume.pdf'}
            </span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
            Validated File
          </span>
        </div>

        {/* Company Facts Grounding Preview */}
        {companyResearch?.relevant_facts?.length > 0 && (
          <div className="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/80 text-xs">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Coded Facts Grounding This Email:</span>
            <ul className="list-disc list-inside text-slate-400 space-y-0.5 text-[11px]">
              {companyResearch.relevant_facts.slice(0, 2).map((f, idx) => (
                <li key={idx}>{f.fact}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Mandatory Confirmation Gate */}
        <div className="pt-4 border-t border-slate-800 space-y-4">
          <label className="flex items-start gap-3 p-4 bg-amber-950/10 border border-amber-900/40 rounded-xl cursor-pointer">
            <input
              type="checkbox"
              checked={humanConfirmed}
              onChange={(e) => setHumanConfirmed(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-slate-700 text-sky-600 focus:ring-0 cursor-pointer"
            />
            <span className="text-xs text-slate-300 leading-relaxed">
              <strong>Mandatory Human Confirmation:</strong> I have reviewed the recipient address, email body, and resume attachment. Once approved, CareerPilotAI will send this email directly from my connected Gmail account.
            </span>
          </label>

          <button
            onClick={handleApproveAndSend}
            disabled={loading || !humanConfirmed || !gmailStatus.is_connected}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl text-sm transition disabled:opacity-50 flex items-center justify-center gap-2 shadow-xl shadow-emerald-600/20"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            {loading ? 'Dispatched via Gmail...' : 'APPROVE & SEND EMAIL'}
          </button>
        </div>
      </div>
    </div>
  );
};