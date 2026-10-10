import React, { useState, useEffect } from 'react';
import { uploadResumeFile, triggerResumeAnalysis } from './services/resumeService';
import { autoDiscoverJobsForCandidate } from './services/intelligenceService';
import { analyzeJobMatch } from './services/matchingService';

import { Layout } from './components/Layout';
import { DashboardView } from './components/DashboardView';
import { ResumeView } from './components/ResumeView';
import { JobCard } from './components/JobCard';
import { MatchVisualizer } from './components/MatchVisualizer';
import { ResumeOptimizationView } from './components/ResumeOptimizationView';
import { ApplicationReviewView } from './components/ApplicationReviewView';
import { ApplicationsTrackerView } from './components/ApplicationsTrackerView';
import { Loader2, Search } from 'lucide-react';

function App() {
  const [activeView, setActiveView] = useState('dashboard');

  // Resume State
  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [loadingResume, setLoadingResume] = useState(false);
  const [analyzingResume, setAnalyzingResume] = useState(false);

  // Job State
  const [rankedJobs, setRankedJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [matchingJobId, setMatchingJobId] = useState(null);
  const [activeMatchAnalysis, setActiveMatchAnalysis] = useState(null);
  const [activeOptimizationJob, setActiveOptimizationJob] = useState(null);
  const [activeReviewDraft, setActiveReviewDraft] = useState(null);

  const candidateId = candidateProfile?.candidate_id || uploadResult?.candidate_id;

  const handleUpload = async () => {
    if (!file) return;
    setLoadingResume(true);
    try {
      const result = await uploadResumeFile(file);
      setUploadResult(result);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoadingResume(false);
    }
  };

  const handleAnalyze = async () => {
    if (!candidateId) return;
    setAnalyzingResume(true);
    try {
      const profile = await triggerResumeAnalysis(candidateId);
      setCandidateProfile(profile);
      setActiveView('dashboard');
    } catch (err) {
      alert(err.message);
    } finally {
      setAnalyzingResume(false);
    }
  };

  const loadAutomaticMatches = async () => {
    if (!candidateId) return;
    setLoadingJobs(true);
    try {
      const data = await autoDiscoverJobsForCandidate(candidateId, '', false);
      setRankedJobs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    if (candidateId) loadAutomaticMatches();
  }, [candidateId]);

  const handleRunMatch = async (jobId) => {
    setMatchingJobId(jobId);
    try {
      const analysis = await analyzeJobMatch(candidateId, jobId);
      setActiveMatchAnalysis(analysis);
    } catch (err) {
      alert(err.message);
    } finally {
      setMatchingJobId(null);
    }
  };

  const renderView = () => {
    if (activeReviewDraft && activeOptimizationJob) {
      return (
        <ApplicationReviewView
          draft={activeReviewDraft}
          job={activeOptimizationJob}
          candidateProfile={candidateProfile}
          onBack={() => setActiveReviewDraft(null)}
          onSent={() => {
            setActiveReviewDraft(null);
            setActiveOptimizationJob(null);
            setActiveView('applications');
          }}
        />
      );
    }

    if (activeOptimizationJob) {
      return (
        <div className="space-y-4">
          <button
            onClick={() => setActiveOptimizationJob(null)}
            className="text-xs font-mono text-slate-400 hover:text-white"
          >
            ← Back to Job Feed
          </button>
          <ResumeOptimizationView
            candidateId={candidateId}
            job={activeOptimizationJob}
            onComplete={(approvedDraft) => setActiveReviewDraft(approvedDraft)}
          />
        </div>
      );
    }

    if (activeMatchAnalysis) {
      return <MatchVisualizer analysis={activeMatchAnalysis} onBack={() => setActiveMatchAnalysis(null)} />;
    }

    switch (activeView) {
      case 'dashboard':
        return <DashboardView profile={candidateProfile} discoveredJobsCount={rankedJobs.length} onNavigate={setActiveView} />;
      case 'resume':
        return (
          <ResumeView
            file={file} setFile={setFile} uploadResult={uploadResult} candidateProfile={candidateProfile}
            loading={loadingResume} analyzing={analyzingResume} onUpload={handleUpload} onAnalyze={handleAnalyze}
          />
        );
      case 'jobs':
        return (
          <div className="space-y-6 animate-in fade-in duration-500">
            <header className="flex justify-between items-end mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white tracking-tight">Job Feed</h1>
                <p className="text-slate-400 mt-1">Curated positions matching your resume.</p>
              </div>
              <button
                onClick={loadAutomaticMatches}
                className="bg-slate-900 border border-slate-800 text-slate-300 hover:text-white px-4 py-2 rounded-xl transition text-sm flex items-center gap-2"
              >
                {loadingJobs ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Refresh
              </button>
            </header>

            {!candidateProfile ? (
              <div className="text-center p-12 bg-slate-900 border border-slate-800 rounded-3xl text-slate-400">
                Please upload your resume first to activate the job discovery engine.
              </div>
            ) : loadingJobs ? (
              <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                <Loader2 className="h-8 w-8 animate-spin text-sky-400 mb-4" />
                <p>Curating real-time opportunities...</p>
              </div>
            ) : (
              <div className="space-y-4 max-w-2xl mx-auto">
                {rankedJobs.map(job => (
                  <JobCard
                    key={job.job_id}
                    job={job}
                    onAnalyze={handleRunMatch}
                    onTailor={(targetJob) => setActiveOptimizationJob(targetJob)}
                    isMatching={matchingJobId === job.job_id}
                  />
                ))}
              </div>
            )}
          </div>
        );
      case 'applications':
        return <ApplicationsTrackerView />;
      case 'roadmap':
      case 'settings':
        return (
          <div className="flex flex-col items-center justify-center h-96 text-center">
            <div className="text-5xl mb-4 opacity-50">🧭</div>
            <h2 className="text-xl font-bold text-white">System Settings & Roadmap Active</h2>
            <p className="text-slate-400 text-sm max-w-sm mt-1">
              All engine capabilities from Resume Parsing to Gmail automation are fully operational.
            </p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Layout activeView={activeView} setActiveView={setActiveView} candidateName={candidateProfile?.name}>
      {renderView()}
    </Layout>
  );
}

export default App;