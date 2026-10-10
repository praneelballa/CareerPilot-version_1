import React, { useState, useEffect } from 'react';
import { autoDiscoverJobsForCandidate } from '../services/intelligenceService';
import { analyzeJobMatch } from '../services/matchingService';
import { JobMatchAnalysisView } from './JobMatchAnalysisView';
import { ResumeTailoringModal } from './ResumeTailoringModal';
import { Sparkles, MapPin, Building2, Loader2, AlertCircle, FileEdit, ExternalLink } from 'lucide-react';

export const JobSearchSection = ({ candidateId }) => {
  const [location, setLocation] = useState('');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rankedJobs, setRankedJobs] = useState([]);
  const [errorMessage, setErrorMessage] = useState(null);

  // Modal / Analysis States
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [matchingJobId, setMatchingJobId] = useState(null);
  const [tailorJob, setTailorJob] = useState(null);

  const loadAutomaticMatches = async () => {
    if (!candidateId) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const data = await autoDiscoverJobsForCandidate(candidateId, location, remoteOnly);
      setRankedJobs(data);
    } catch (err) {
      setErrorMessage(err.message || 'Automated job discovery failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (candidateId) {
      loadAutomaticMatches();
    }
  }, [candidateId]);

  const handleRunMatch = async (jobId) => {
    setMatchingJobId(jobId);
    setErrorMessage(null);
    try {
      const analysis = await analyzeJobMatch(candidateId, jobId);
      setActiveAnalysis(analysis);
    } catch (err) {
      setErrorMessage(err.message || 'Matching analysis failed.');
    } finally {
      setMatchingJobId(null);
    }
  };

  if (activeAnalysis) {
    return (
      <JobMatchAnalysisView
        analysis={activeAnalysis}
        onBack={() => setActiveAnalysis(null)}
      />
    );
  }

  return (
    <div className="w-full max-w-5xl space-y-6 mt-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-sky-400" />
              Resume-Matched Opportunities
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Live roles discovered directly from your uploaded resume's skills, technologies, and projects.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Filter location (optional)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            />
            <button
              onClick={loadAutomaticMatches}
              disabled={loading || !candidateId}
              className="bg-sky-600 hover:bg-sky-500 text-white font-medium py-1.5 px-3.5 rounded-lg text-xs transition disabled:opacity-50 flex items-center gap-1.5"
            >
              {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Refresh Matches
            </button>
          </div>
        </div>

        {errorMessage && (
          <div className="mt-4 p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Ranked Job Cards */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm flex flex-col items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400 mb-2" />
          Analyzing resume context & discovering compatible real opportunities...
        </div>
      ) : rankedJobs.length === 0 ? (
        <div className="p-10 text-center bg-slate-900/40 border border-slate-800 rounded-xl text-slate-400 text-xs">
          No matching live listings found. Try updating your location filter or uploading a more detailed resume.
        </div>
      ) : (
        <div className="space-y-4">
          {rankedJobs.map((job) => (
            <div
              key={job.job_id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 transition rounded-xl p-5 shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
            >
              <div className="space-y-1.5 max-w-3xl">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-base font-semibold text-white">{job.title}</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                    Fit: {job.composite_score}%
                  </span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
                    {job.source}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1 font-medium text-slate-300">
                    <Building2 className="h-3.5 w-3.5 text-slate-400" />
                    {job.company}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-slate-400" />
                    {job.location}
                  </span>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 pt-1">{job.description}</p>
              </div>

              <div className="flex items-center gap-2 w-full md:w-auto flex-shrink-0">
                <button
                  onClick={() => handleRunMatch(job.job_id)}
                  disabled={matchingJobId === job.job_id}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-2 rounded-lg text-xs font-semibold transition disabled:opacity-50 flex items-center justify-center gap-1.5"
                >
                  {matchingJobId === job.job_id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
                  Skill Gap & Roadmap
                </button>

                <button
                  onClick={() => setTailorJob(job)}
                  className="bg-sky-600 hover:bg-sky-500 text-white px-3 py-2 rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5"
                >
                  <FileEdit className="h-3.5 w-3.5" />
                  Tailor & Email
                </button>

                <a
                  href={job.application_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-800 hover:bg-slate-700 text-sky-400 hover:text-white border border-slate-700 p-2 rounded-lg text-xs font-medium transition"
                  title="View Authentic Job Posting"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tailoring & Email Modal */}
      {tailorJob && (
        <ResumeTailoringModal
          candidateId={candidateId}
          jobId={tailorJob.job_id}
          jobTitle={tailorJob.title}
          company={tailorJob.company}
          onClose={() => setTailorJob(null)}
        />
      )}
    </div>
  );
};