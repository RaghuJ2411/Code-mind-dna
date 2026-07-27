import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import {
  createProject,
  createResumeEntry,
  getCareerOverview,
  getCareerRoles,
  getInterviewHistory,
  getProjects,
  getResumeEntries,
  practiceInterview,
} from '../../api/student';
import {
  analyzeSkillGap,
  predictCareerPaths,
  parseResume,
  getInterviewFeedback,
} from '../../api/aiCareer';

const initialResumeForm = {
  section: 'Experience',
  title: '',
  content: '',
  skills: [],
  skillInput: '',
};

const initialProjectForm = {
  title: '',
  description: '',
  technologies: [],
  technologyInput: '',
  outcome: '',
  project_url: '',
};

const initialInterviewForm = {
  role_name: '',
  question: '',
  answer: '',
};

export default function CareerPage() {
  const [overview, setOverview] = useState(null);
  const [roles, setRoles] = useState([]);
  const [resumeEntries, setResumeEntries] = useState([]);
  const [projects, setProjects] = useState([]);
  const [interviewHistory, setInterviewHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // AI State
  const [skillGapResult, setSkillGapResult] = useState(null);
  const [skillGapLoading, setSkillGapLoading] = useState(false);
  const [selectedRoleForGap, setSelectedRoleForGap] = useState('');

  const [careerPrediction, setCareerPrediction] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);

  const [resumeParseResult, setResumeParseResult] = useState(null);
  const [resumeParseLoading, setResumeParseLoading] = useState(false);
  const [resumeText, setResumeText] = useState('');

  const [aiInterviewResult, setAiInterviewResult] = useState(null);
  const [aiInterviewLoading, setAiInterviewLoading] = useState(false);

  // Forms
  const [resumeForm, setResumeForm] = useState(initialResumeForm);
  const [projectForm, setProjectForm] = useState(initialProjectForm);
  const [interviewForm, setInterviewForm] = useState(initialInterviewForm);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, roleData, resumeData, projectData, interviewData] = await Promise.all([
        getCareerOverview(),
        getCareerRoles(),
        getResumeEntries(),
        getProjects(),
        getInterviewHistory(),
      ]);
      setOverview(overviewData);
      setRoles(roleData);
      setResumeEntries(resumeData);
      setProjects(projectData);
      setInterviewHistory(interviewData);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load career intelligence');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // AI: Skill Gap Analysis
  const handleSkillGapAnalysis = async () => {
    if (!selectedRoleForGap) return;
    setSkillGapLoading(true);
    setSkillGapResult(null);
    try {
      const result = await analyzeSkillGap(parseInt(selectedRoleForGap), true);
      setSkillGapResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Skill gap analysis failed');
    } finally {
      setSkillGapLoading(false);
    }
  };

  // AI: Career Prediction
  const handleCareerPrediction = async () => {
    setPredictionLoading(true);
    setCareerPrediction(null);
    try {
      const result = await predictCareerPaths(true);
      setCareerPrediction(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Career prediction failed');
    } finally {
      setPredictionLoading(false);
    }
  };

  // AI: Resume Parse
  const handleResumeParse = async () => {
    if (!resumeText.trim()) return;
    setResumeParseLoading(true);
    setResumeParseResult(null);
    try {
      const result = await parseResume(resumeText);
      setResumeParseResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Resume parsing failed');
    } finally {
      setResumeParseLoading(false);
    }
  };

  // AI: Interview Feedback
  const handleAiInterviewFeedback = async () => {
    if (!interviewForm.question || !interviewForm.answer) return;
    setAiInterviewLoading(true);
    setAiInterviewResult(null);
    try {
      const result = await getInterviewFeedback(
        interviewForm.question,
        interviewForm.answer,
        interviewForm.role_name || null,
        null
      );
      setAiInterviewResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Interview feedback failed');
    } finally {
      setAiInterviewLoading(false);
    }
  };

  // Form handlers
  const handleResumeChange = (key, value) => {
    setResumeForm((current) => ({ ...current, [key]: value }));
  };

  const handleProjectChange = (key, value) => {
    setProjectForm((current) => ({ ...current, [key]: value }));
  };

  const handleInterviewChange = (key, value) => {
    setInterviewForm((current) => ({ ...current, [key]: value }));
  };

  const addResumeSkill = () => {
    if (!resumeForm.skillInput.trim()) return;
    setResumeForm((current) => ({
      ...current,
      skills: [...current.skills, current.skillInput.trim()],
      skillInput: '',
    }));
  };

  const addProjectTechnology = () => {
    if (!projectForm.technologyInput.trim()) return;
    setProjectForm((current) => ({
      ...current,
      technologies: [...current.technologies, current.technologyInput.trim()],
      technologyInput: '',
    }));
  };

  const handleResumeSubmit = async (event) => {
    event.preventDefault();
    try {
      await createResumeEntry({
        section: resumeForm.section,
        title: resumeForm.title,
        content: resumeForm.content,
        skills: resumeForm.skills,
      });
      setResumeForm(initialResumeForm);
      loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save resume entry');
    }
  };

  const handleProjectSubmit = async (event) => {
    event.preventDefault();
    try {
      await createProject({
        title: projectForm.title,
        description: projectForm.description,
        technologies: projectForm.technologies,
        outcome: projectForm.outcome,
        project_url: projectForm.project_url,
      });
      setProjectForm(initialProjectForm);
      loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save project');
    }
  };

  const handleInterviewSubmit = async (event) => {
    event.preventDefault();
    try {
      await practiceInterview({
        role_name: interviewForm.role_name,
        question: interviewForm.question,
        answer: interviewForm.answer,
      });
      setInterviewForm(initialInterviewForm);
      loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to practice interview');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'CRITICAL': return 'text-red-600 bg-red-50';
      case 'IMPORTANT': return 'text-yellow-600 bg-yellow-50';
      case 'NICE_TO_HAVE': return 'text-green-600 bg-green-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  return (
    <DashboardLayout title="Career Intelligence" role="STUDENT">
      {loading ? (
        <p className="rounded-2xl bg-white p-6 text-sm text-slate-500 shadow-sm">Loading career intelligence...</p>
      ) : error ? (
        <p className="rounded-2xl bg-rose-50 p-6 text-sm text-rose-700 shadow-sm">{error}</p>
      ) : (
        <div className="space-y-6">
          {/* Career Readiness Overview */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">Career readiness overview</h2>
            <div className="mt-4 grid gap-4 lg:grid-cols-5">
              {[
                { label: 'Readiness', value: overview.readiness_score, meta: overview.readiness_label },
                { label: 'Resume strength', value: overview.resume_strength, meta: `Entries ${overview.resume_entry_count}` },
                { label: 'Project alignment', value: overview.project_alignment, meta: `Projects ${overview.project_count}` },
                { label: 'Interview readiness', value: overview.interview_readiness, meta: `Sessions ${overview.interview_session_count}` },
                { label: 'Confidence', value: overview.confidence_label, meta: '' },
              ].map((item) => (
                <div key={item.label} className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{item.label}</p>
                  <p className="mt-3 text-3xl font-semibold text-slate-900">{typeof item.value === 'number' ? `${item.value}%` : item.value}</p>
                  <p className="mt-2 text-sm text-slate-600">{item.meta}</p>
                </div>
              ))}
            </div>
            {overview.recommended_actions?.length > 0 && (
              <div className="mt-6 space-y-2">
                <p className="text-sm font-medium text-slate-700">Recommended actions</p>
                {overview.recommended_actions.map((action) => (
                  <div key={action} className="rounded-2xl bg-slate-100 p-4 text-sm text-slate-700">{action}</div>
                ))}
              </div>
            )}
          </section>

          {/* AI: Career Path Prediction */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">AI Career Path Prediction</h2>
                <p className="mt-1 text-sm text-slate-500">Let AI analyze your DNA profile to predict optimal career paths.</p>
              </div>
              <button
                onClick={handleCareerPrediction}
                disabled={predictionLoading}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {predictionLoading ? 'Analyzing...' : 'Predict my career path'}
              </button>
            </div>

            {careerPrediction && (
              <div className="mt-4 space-y-4">
                <div className="rounded-2xl border border-indigo-200 bg-indigo-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-indigo-900">Overall readiness</p>
                    <span className="text-2xl font-bold text-indigo-600">{careerPrediction.overall_readiness_score}%</span>
                  </div>
                  {careerPrediction.ai_summary && (
                    <p className="mt-2 text-sm text-indigo-700">{careerPrediction.ai_summary}</p>
                  )}
                  {careerPrediction.confidence_label && (
                    <p className="mt-1 text-xs text-indigo-500">Confidence: {careerPrediction.confidence_label}</p>
                  )}
                </div>

                {careerPrediction.primary_path && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Primary path: {careerPrediction.primary_path.path_name}</p>
                    {careerPrediction.primary_path.steps?.map((step, i) => (
                      <div key={i} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-900">{step.role_name}</p>
                            <p className="text-sm text-slate-500">{step.seniority_level} · {step.time_to_achieve}</p>
                          </div>
                          <span className="text-lg font-bold text-indigo-600">{step.match_score}%</span>
                        </div>
                        {step.description && <p className="mt-2 text-sm text-slate-600">{step.description}</p>}
                        {step.skills_to_develop?.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {step.skills_to_develop.map((skill) => (
                              <span key={skill} className="rounded-full bg-indigo-100 px-3 py-1 text-xs text-indigo-700">{skill}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {careerPrediction.alternative_paths?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Alternative paths</p>
                    {careerPrediction.alternative_paths.map((path, i) => (
                      <div key={i} className="mt-2 rounded-2xl border border-slate-200 bg-slate-50 p-3">
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-medium text-slate-900">{path.path_name}</span>
                          <span className="text-sm text-indigo-600">{path.confidence}% confidence</span>
                        </div>
                        {path.ai_rationale && <p className="mt-1 text-sm text-slate-600">{path.ai_rationale}</p>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>

          {/* AI: Skill Gap Analysis */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">AI Skill Gap Analysis</h2>
                <p className="mt-1 text-sm text-slate-500">Compare your DNA profile against a target career role.</p>
              </div>
              <div className="flex gap-2">
                <select
                  value={selectedRoleForGap}
                  onChange={(e) => setSelectedRoleForGap(e.target.value)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Select a role</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
                <button
                  onClick={handleSkillGapAnalysis}
                  disabled={skillGapLoading || !selectedRoleForGap}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  {skillGapLoading ? 'Analyzing...' : 'Analyze gaps'}
                </button>
              </div>
            </div>

            {skillGapResult && (
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between gap-3 rounded-2xl border border-indigo-200 bg-indigo-50 p-4">
                  <div>
                    <p className="font-semibold text-indigo-900">{skillGapResult.role_name}</p>
                    <p className="text-sm text-indigo-600">{skillGapResult.role_seniority}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-indigo-600">{skillGapResult.overall_match_percentage}%</p>
                    <p className="text-xs text-indigo-500">match</p>
                  </div>
                </div>

                {skillGapResult.gaps?.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Skill gaps</p>
                    {skillGapResult.gaps.map((gap, i) => (
                      <div key={i} className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-slate-900">{gap.skill}</span>
                            <span className={`rounded-full px-2 py-0.5 text-xs ${getPriorityColor(gap.priority)}`}>{gap.priority}</span>
                          </div>
                          {gap.description && <p className="mt-1 text-xs text-slate-500">{gap.description}</p>}
                          <div className="mt-2 flex items-center gap-2 text-xs">
                            <span>Current: {gap.current_proficiency}%</span>
                            <div className="h-1.5 flex-1 rounded-full bg-slate-200">
                              <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${Math.min(gap.current_proficiency, 100)}%` }} />
                            </div>
                            <span>Required: {gap.required_proficiency}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {skillGapResult.strengths?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-green-700">Strengths</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {skillGapResult.strengths.map((s) => (
                        <span key={s} className="rounded-full bg-green-100 px-3 py-1 text-xs text-green-700">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {skillGapResult.recommendations?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Recommendations</p>
                    <div className="mt-1 space-y-1">
                      {skillGapResult.recommendations.map((rec, i) => (
                        <p key={i} className="text-sm text-slate-600">• {rec}</p>
                      ))}
                    </div>
                  </div>
                )}

                {skillGapResult.ai_insight && (
                  <div className="rounded-2xl bg-indigo-50 p-3 text-sm text-indigo-700">
                    <p className="font-medium">AI Insight</p>
                    <p className="mt-1">{skillGapResult.ai_insight}</p>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Top Career Roles */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">Top career roles</h2>
            <div className="mt-4 grid gap-4 lg:grid-cols-3">
              {roles.map((role) => (
                <Link
                  key={role.id}
                  to={`/student/career/roles/${role.id}`}
                  className="group block rounded-2xl border border-slate-200 p-4 transition hover:border-slate-300 hover:bg-slate-50"
                >
                  <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{role.seniority_level}</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">{role.name}</p>
                  <p className="mt-2 text-sm text-slate-600">{role.description}</p>
                  <div className="mt-4 flex items-center justify-between gap-4 text-sm text-slate-700">
                    <span>Match score: {role.match_score}%</span>
                    <span className="text-slate-400 transition group-hover:text-slate-600">View details →</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* AI: Resume Parse */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">AI Resume Analysis</h2>
                <p className="mt-1 text-sm text-slate-500">Paste your resume content and let AI extract structured data.</p>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume content here..."
                rows={4}
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <button
              onClick={handleResumeParse}
              disabled={resumeParseLoading || !resumeText.trim()}
              className="mt-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {resumeParseLoading ? 'Parsing...' : 'Parse with AI'}
            </button>

            {resumeParseResult && (
              <div className="mt-4 space-y-3">
                {resumeParseResult.extracted_skills?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Extracted skills</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {resumeParseResult.extracted_skills.map((skill) => (
                        <span key={skill} className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-700">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
                {resumeParseResult.suggested_roles?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Suggested roles</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {resumeParseResult.suggested_roles.map((role) => (
                        <span key={role} className="rounded-full bg-green-100 px-3 py-1 text-xs text-green-700">{role}</span>
                      ))}
                    </div>
                  </div>
                )}
                {resumeParseResult.parsed_entries?.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-700">Parsed entries</p>
                    {resumeParseResult.parsed_entries.map((entry, i) => (
                      <div key={i} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-medium text-slate-900">{entry.title}</p>
                          <span className="text-xs text-slate-500">{entry.section}</span>
                        </div>
                        <p className="mt-1 text-sm text-slate-600">{entry.content}</p>
                        {entry.skills?.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {entry.skills.map((skill) => (
                              <span key={skill} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{skill}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                {resumeParseResult.ai_summary && (
                  <div className="rounded-2xl bg-indigo-50 p-3 text-sm text-indigo-700">{resumeParseResult.ai_summary}</div>
                )}
              </div>
            )}
          </section>

          {/* Resume Entries (existing CRUD) */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Resume entries</h2>
                <p className="mt-1 text-sm text-slate-500">Track your resume content and technical skills.</p>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {resumeEntries.map((entry) => (
                <div key={entry.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-slate-900">{entry.title}</p>
                    <span className="text-sm text-slate-500">{entry.section}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-700">{entry.content}</p>
                  <p className="mt-2 text-sm text-slate-500">Skills: {entry.skills.join(', ') || 'None'}</p>
                </div>
              ))}
            </div>
            <form className="mt-6 grid gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4" onSubmit={handleResumeSubmit}>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="block">
                  <span className="text-sm text-slate-700">Section</span>
                  <input value={resumeForm.section} onChange={(event) => handleResumeChange('section', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
                </label>
                <label className="block">
                  <span className="text-sm text-slate-700">Title</span>
                  <input value={resumeForm.title} onChange={(event) => handleResumeChange('title', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
                </label>
              </div>
              <label className="block">
                <span className="text-sm text-slate-700">Content</span>
                <textarea value={resumeForm.content} onChange={(event) => handleResumeChange('content', event.target.value)} rows={3} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="block">
                  <span className="text-sm text-slate-700">Skill</span>
                  <div className="mt-1 flex gap-2">
                    <input value={resumeForm.skillInput} onChange={(event) => handleResumeChange('skillInput', event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2" />
                    <button type="button" onClick={addResumeSkill} className="rounded-lg bg-slate-900 px-4 py-2 text-white">Add</button>
                  </div>
                </label>
                <div className="rounded-lg border border-slate-300 bg-white p-3">
                  <span className="text-sm text-slate-700">Skills added</span>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {resumeForm.skills.map((skill) => (
                      <span key={skill} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>
              <button type="submit" className="rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white">Save resume entry</button>
            </form>
          </section>

          {/* Projects (existing CRUD) */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">Projects</h2>
                <p className="mt-1 text-sm text-slate-500">Capture project work with technology alignment.</p>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="font-semibold text-slate-900">{project.title}</p>
                  <p className="mt-2 text-sm text-slate-700">{project.description}</p>
                  <p className="mt-2 text-sm text-slate-500">Technologies: {project.technologies.join(', ') || 'None'}</p>
                </div>
              ))}
            </div>
            <form className="mt-6 grid gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4" onSubmit={handleProjectSubmit}>
              <label className="block">
                <span className="text-sm text-slate-700">Project title</span>
                <input value={projectForm.title} onChange={(event) => handleProjectChange('title', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <label className="block">
                <span className="text-sm text-slate-700">Description</span>
                <textarea value={projectForm.description} onChange={(event) => handleProjectChange('description', event.target.value)} rows={3} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="block">
                  <span className="text-sm text-slate-700">Technology</span>
                  <div className="mt-1 flex gap-2">
                    <input value={projectForm.technologyInput} onChange={(event) => handleProjectChange('technologyInput', event.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2" />
                    <button type="button" onClick={addProjectTechnology} className="rounded-lg bg-slate-900 px-4 py-2 text-white">Add</button>
                  </div>
                </label>
                <div className="rounded-lg border border-slate-300 bg-white p-3">
                  <span className="text-sm text-slate-700">Technologies</span>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {projectForm.technologies.map((tech) => (
                      <span key={tech} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{tech}</span>
                    ))}
                  </div>
                </div>
              </div>
              <label className="block">
                <span className="text-sm text-slate-700">Outcome</span>
                <input value={projectForm.outcome} onChange={(event) => handleProjectChange('outcome', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <label className="block">
                <span className="text-sm text-slate-700">Project URL</span>
                <input value={projectForm.project_url} onChange={(event) => handleProjectChange('project_url', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <button type="submit" className="rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white">Save project</button>
            </form>
          </section>

          {/* AI Interview Feedback + Practice */}
          <section className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">AI Interview Practice</h2>
                <p className="mt-1 text-sm text-slate-500">Practice and get AI-powered feedback on interview responses.</p>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {interviewHistory.map((session) => (
                <div key={session.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-slate-900">{session.role_name || 'General practice'}</p>
                    <span className="text-sm text-slate-500">Score {session.feedback_score}%</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-700">Q: {session.question}</p>
                  <p className="mt-2 text-sm text-slate-700">A: {session.answer}</p>
                  <p className="mt-2 text-sm text-slate-500">Feedback: {session.feedback_text}</p>
                </div>
              ))}
            </div>

            {/* AI Feedback section */}
            {aiInterviewResult && (
              <div className="mt-4 space-y-3 rounded-2xl border border-indigo-200 bg-indigo-50 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-indigo-900">AI Feedback</p>
                  <span className="text-2xl font-bold text-indigo-600">{aiInterviewResult.overall_score}%</span>
                </div>
                {aiInterviewResult.strengths?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-green-700">Strengths</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {aiInterviewResult.strengths.map((s) => (
                        <span key={s} className="rounded-full bg-green-100 px-3 py-1 text-xs text-green-700">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
                {aiInterviewResult.improvements?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-amber-700">Areas to improve</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {aiInterviewResult.improvements.map((imp) => (
                        <span key={imp} className="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-700">{imp}</span>
                      ))}
                    </div>
                  </div>
                )}
                {aiInterviewResult.ai_feedback && (
                  <p className="text-sm text-indigo-700">{aiInterviewResult.ai_feedback}</p>
                )}
                {aiInterviewResult.suggested_followups?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Follow-up questions</p>
                    <div className="mt-1 space-y-1">
                      {aiInterviewResult.suggested_followups.map((q, i) => (
                        <p key={i} className="text-sm text-slate-600">• {q}</p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <form className="mt-6 grid gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4" onSubmit={handleInterviewSubmit}>
              <label className="block">
                <span className="text-sm text-slate-700">Target role</span>
                <input value={interviewForm.role_name} onChange={(event) => handleInterviewChange('role_name', event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <label className="block">
                <span className="text-sm text-slate-700">Question</span>
                <textarea value={interviewForm.question} onChange={(event) => handleInterviewChange('question', event.target.value)} rows={2} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <label className="block">
                <span className="text-sm text-slate-700">Answer</span>
                <textarea value={interviewForm.answer} onChange={(event) => handleInterviewChange('answer', event.target.value)} rows={3} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" />
              </label>
              <div className="flex gap-2">
                <button type="submit" className="flex-1 rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white">Practice response</button>
                <button
                  type="button"
                  onClick={handleAiInterviewFeedback}
                  disabled={aiInterviewLoading || !interviewForm.question || !interviewForm.answer}
                  className="rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  {aiInterviewLoading ? 'Analyzing...' : 'Get AI Feedback'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </DashboardLayout>
  );
}

