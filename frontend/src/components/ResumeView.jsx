import React from 'react';
import { Upload, FileText, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

export const ResumeView = ({ 
  file, setFile, uploadResult, candidateProfile, loading, analyzing,
  onUpload, onAnalyze 
}) => {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">My Profile</h1>
        <p className="text-slate-400 mt-1">Upload and manage your parsed career identity.</p>
      </header>

      {!candidateProfile ? (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">
          <div className="border-2 border-dashed border-slate-700/80 hover:border-sky-500/50 transition-colors rounded-2xl p-10 flex flex-col items-center justify-center text-center relative cursor-pointer group">
            <input 
              type="file" 
              accept=".pdf,.docx" 
              onChange={(e) => setFile(e.target.files[0])}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="h-16 w-16 bg-slate-950 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Upload className="h-8 w-8 text-sky-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Upload Resume</h3>
            <p className="text-sm text-slate-400">PDF or DOCX up to 10MB</p>
            {file && <div className="mt-4 text-xs font-mono text-emerald-400">{file.name} selected</div>}
          </div>

          {file && !uploadResult && (
            <button 
              onClick={onUpload} disabled={loading}
              className="w-full mt-4 bg-white text-slate-950 font-semibold py-3 rounded-xl transition hover:bg-slate-200 flex justify-center items-center gap-2"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileText className="h-5 w-5" />}
              {loading ? 'Processing Document...' : 'Extract Profile'}
            </button>
          )}

          {uploadResult && (
            <div className="mt-6 space-y-4">
              <div className="bg-emerald-950/20 border border-emerald-900/30 p-4 rounded-xl flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <span className="text-sm text-emerald-100">Document extracted deterministically.</span>
              </div>
              <button 
                onClick={onAnalyze} disabled={analyzing}
                className="w-full bg-gradient-to-r from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white font-semibold py-3 rounded-xl transition flex justify-center items-center gap-2 shadow-lg shadow-sky-500/20"
              >
                {analyzing ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
                {analyzing ? 'AI Structuring Profile...' : 'Run Gemini Semantic Extraction'}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8">
          <div className="flex items-center gap-4 mb-8">
            <div className="h-16 w-16 bg-gradient-to-br from-sky-500 to-emerald-500 rounded-full flex items-center justify-center text-2xl font-bold text-white shadow-lg">
              {candidateProfile.name.charAt(0)}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{candidateProfile.name}</h2>
              <p className="text-sm text-slate-400 font-mono">{candidateProfile.email}</p>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">Professional Summary</h3>
              <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-2xl border border-slate-800/80">
                {candidateProfile.summary}
              </p>
            </div>

            <div>
              <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">Verified Skills</h3>
              <div className="flex flex-wrap gap-2">
                {[...candidateProfile.skills.programming_languages, ...candidateProfile.skills.frameworks, ...candidateProfile.skills.ai_and_ml].map((skill, i) => (
                  <span key={i} className="bg-slate-800 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-700">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};