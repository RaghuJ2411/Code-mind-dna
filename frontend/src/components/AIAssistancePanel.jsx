import { useState } from 'react';
import { requestErrorExplanation, requestSkillGap, requestRoadmap } from '../api/student';

const TASK_MAP = {
  ERROR_EXPLANATION: {
    title: 'Explain Error',
    buttonLabel: 'Explain Error',
    helper: 'Explain why this submission failed and how to fix it.',
    requestFn: requestErrorExplanation,
  },
  SKILL_GAP: {
    title: 'Skill Gap Analysis',
    buttonLabel: 'Analyze Skill Gap',
    helper: 'Identify gaps in the student’s current coding skills.',
    requestFn: requestSkillGap,
  },
  ROADMAP: {
    title: 'Learning Roadmap',
    buttonLabel: 'Generate Roadmap',
    helper: 'Create a learning plan to improve on this topic.',
    requestFn: requestRoadmap,
  },
};

function renderResult(taskKey, result) {
  if (!result) {
    return null;
  }

  switch (taskKey) {
    case 'ERROR_EXPLANATION':
      return (
        <div className="space-y-3">
          <p className="text-slate-700"><strong>Summary:</strong> {result.summary}</p>
          <p className="text-slate-700"><strong>Root cause:</strong> {result.root_cause}</p>
          <p className="text-slate-700"><strong>Suggested fix:</strong> {result.suggested_fix}</p>
          <p className="text-slate-700"><strong>Confidence:</strong> {result.confidence}</p>
          <div>
            <strong>Resources:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.learning_resources || []).map((resource, index) => (
                <li key={index}>{resource}</li>
              ))}
            </ul>
          </div>
        </div>
      );
    case 'SKILL_GAP':
      return (
        <div className="space-y-3">
          <p className="text-slate-700"><strong>Summary:</strong> {result.summary}</p>
          <div>
            <strong>Missing Skills:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.missing_skills || []).map((skill, index) => (
                <li key={index}>{skill}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong>Improvement Steps:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.improvement_steps || []).map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong>Recommended Topics:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.recommended_topics || []).map((topic, index) => (
                <li key={index}>{topic}</li>
              ))}
            </ul>
          </div>
        </div>
      );
    case 'ROADMAP':
      return (
        <div className="space-y-3">
          <p className="text-slate-700"><strong>Summary:</strong> {result.summary}</p>
          <div>
            <strong>Milestones:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.milestones || []).map((milestone, index) => (
                <li key={index} className="mb-2">
                  <div><strong>{milestone.milestone}</strong> ({milestone.estimated_weeks} weeks)</div>
                  <div>{milestone.goal}</div>
                </li>
              ))}
            </ul>
          </div>
          <p className="text-slate-700"><strong>Total weeks:</strong> {result.estimated_total_weeks}</p>
          <div>
            <strong>Recommendations:</strong>
            <ul className="list-disc pl-6 text-slate-700">
              {(result.recommendations || []).map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      );
    default:
      return <pre className="whitespace-pre-wrap text-slate-700">{JSON.stringify(result, null, 2)}</pre>;
  }
}

export default function AIAssistancePanel({ submissionId, taskKey }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const task = TASK_MAP[taskKey];
  if (!task) return null;

  const handleRequest = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await task.requestFn(submissionId);
      if (response?.status === 'success') {
        setResult(response.data);
      } else {
        setError('AI request failed');
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'AI request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-slate-100 bg-white p-3 text-sm">
      <div className="mb-2 flex items-start justify-between gap-3">
        <div>
          <div className="mb-1 font-semibold">{task.title}</div>
          <div className="text-slate-500">{task.helper}</div>
        </div>
        <button
          onClick={handleRequest}
          disabled={loading}
          className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-semibold text-white disabled:opacity-60"
        >
          {loading ? 'Requesting...' : task.buttonLabel}
        </button>
      </div>

      {result && <div className="space-y-3">{renderResult(taskKey, result)}</div>}
      {error && <div className="mt-2 text-rose-600">{error}</div>}
    </div>
  );
}
