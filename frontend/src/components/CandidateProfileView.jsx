import React from 'react';
import { User, Mail, MapPin, Briefcase, GraduationCap, Award, FolderGit2, CheckCircle2 } from 'lucide-react';

export const CandidateProfileView = ({ profile }) => {
  if (!profile) return null;

  const renderBadgeList = (items, color = "sky") => {
    if (!items || items.length === 0) return <span className="text-xs text-slate-500 italic">None listed</span>;
    return (
      <div className="flex flex-wrap gap-1.5 mt-1">
        {items.map((item, idx) => (
          <span
            key={idx}
            className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-sky-300 border border-slate-700 font-mono"
          >
            {item}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6 text-slate-200 mt-6 animate-fade-in">
      {/* Header Info */}
      <div className="border-b border-slate-800 pb-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <User className="h-6 w-6 text-sky-400" />
            {profile.name || "Unknown Candidate"}
          </h2>
          <div className="flex flex-wrap gap-4 text-xs text-slate-400 mt-2">
            {profile.email && (
              <span className="flex items-center gap-1">
                <Mail className="h-3.5 w-3.5 text-slate-400" />
                {profile.email}
              </span>
            )}
            {profile.location && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5 text-slate-400" />
                {profile.location}
              </span>
            )}
          </div>
        </div>
        <div className="text-xs font-mono bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 text-slate-400">
          ID: {profile.candidate_id}
        </div>
      </div>

      {/* Summary */}
      {profile.summary && (
        <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
          <h3 className="text-xs uppercase font-semibold text-slate-400 mb-1">Professional Summary</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{profile.summary}</p>
        </div>
      )}

      {/* Normalized Skills Grid */}
      <div className="bg-slate-950/40 p-5 rounded-lg border border-slate-800/80">
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          Extracted & Normalized Skills
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <span className="text-xs font-semibold text-slate-400">Languages</span>
            {renderBadgeList(profile.skills.programming_languages)}
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400">Frameworks</span>
            {renderBadgeList(profile.skills.frameworks)}
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400">Cloud & Tools</span>
            {renderBadgeList(profile.skills.cloud_and_tools)}
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400">Databases</span>
            {renderBadgeList(profile.skills.databases)}
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400">AI / ML</span>
            {renderBadgeList(profile.skills.ai_and_ml)}
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400">Soft Skills</span>
            {renderBadgeList(profile.skills.soft_skills)}
          </div>
        </div>
      </div>

      {/* Experience & Education Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Experience */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-sky-400" />
            Experience
          </h3>
          {profile.experience?.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No experience entries parsed.</p>
          ) : (
            profile.experience.map((exp, idx) => (
              <div key={idx} className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 text-sm">
                <div className="font-semibold text-slate-100">{exp.role}</div>
                <div className="text-xs text-sky-400">{exp.company} {exp.location ? `• ${exp.location}` : ''}</div>
                <div className="text-[11px] text-slate-500 mb-2">
                  {exp.start_date || 'N/A'} - {exp.end_date || 'Present'}
                </div>
                <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                  {exp.responsibilities.map((resp, rIdx) => (
                    <li key={rIdx}>{resp}</li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>

        {/* Education & Projects */}
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <GraduationCap className="h-4 w-4 text-sky-400" />
              Education
            </h3>
            {profile.education?.map((edu, idx) => (
              <div key={idx} className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 text-sm mb-2">
                <div className="font-semibold text-slate-100">{edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}</div>
                <div className="text-xs text-slate-400">{edu.institution}</div>
                <div className="text-[11px] text-slate-500">{edu.start_year || ''} - {edu.end_year || ''} {edu.grade_or_gpa ? `• GPA: ${edu.grade_or_gpa}` : ''}</div>
              </div>
            ))}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <FolderGit2 className="h-4 w-4 text-sky-400" />
              Projects
            </h3>
            {profile.projects?.map((proj, idx) => (
              <div key={idx} className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 text-sm mb-2">
                <div className="font-semibold text-slate-100">{proj.title}</div>
                <p className="text-xs text-slate-300 mt-1">{proj.description}</p>
                {renderBadgeList(proj.technologies)}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};