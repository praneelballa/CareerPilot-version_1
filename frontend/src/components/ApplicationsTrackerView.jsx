import React, { useState, useEffect } from 'react';
import { fetchAllApplications } from '../services/gmailService';
import { Mail, CheckCircle2, Clock, AlertTriangle, FileText, Loader2 } from 'lucide-react';

export const ApplicationsTrackerView = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchAllApplications();
        setApplications(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SENT':
        return <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">SENT</span>;
      case 'HUMAN_APPROVED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-sky-950 text-sky-300 border border-sky-800">APPROVED</span>;
      case 'READY_FOR_REVIEW':
        return <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-amber-950 text-amber-300 border border-amber-800">IN REVIEW</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-slate-800 text-slate-300 border border-slate-700">{status}</span>;
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Application Tracker</h1>
        <p className="text-slate-400 mt-1">Audit log of prepared, approved, and dispatched applications.</p>
      </header>

      {loading ? (
        <div className="p-16 text-center text-slate-400">
          <Loader2 className="h-6 w-6 animate-spin text-sky-400 mx-auto mb-2" />
          Loading applications log...
        </div>
      ) : applications.length === 0 ? (
        <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-3xl text-slate-400 text-xs">
          No applications created yet. Select a role from the Job Feed to optimize and package your first application.
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => (
            <div key={app.id} className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-xs">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-white">{app.company_name}</h3>
                  {getStatusBadge(app.status)}
                </div>
                <p className="text-slate-300 font-medium">{app.subject}</p>
                <div className="flex items-center gap-3 text-slate-400 text-[11px] font-mono">
                  <span>To: {app.recipient || 'Not specified'}</span>
                  {app.gmail_message_id && <span>• ID: {app.gmail_message_id}</span>}
                </div>
              </div>

              <div className="text-right font-mono text-[10px] text-slate-500">
                {app.sent_at ? `Sent: ${new Date(app.sent_at).toLocaleString()}` : `Created: ${new Date(app.created_at).toLocaleDateString()}`}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};