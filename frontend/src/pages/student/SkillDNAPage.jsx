import React, { useEffect, useMemo, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getDashboardOverview, getDnaProfile, getDnaProfileHistory } from '../../api/student';

const DIMENSION_COLORS = {
  LOGIC: '#3b82f6',
  DEBUGGING: '#10b981',
  OPTIMIZATION: '#f59e0b',
  CONSISTENCY: '#8b5cf6',
  LEARNING_VELOCITY: '#ec4899',
  PROBLEM_SOLVING_BREADTH: '#14b8a6',
};

const DIMENSION_LABELS = {
  LOGIC: 'Logic & Reasoning',
  DEBUGGING: 'Debugging',
  OPTIMIZATION: 'Optimization',
  CONSISTENCY: 'Consistency',
  LEARNING_VELOCITY: 'Learning Velocity',
  PROBLEM_SOLVING_BREADTH: 'Breadth',
};

function SimpleRadarChart({ dimensions, size = 280 }) {
  if (!dimensions || dimensions.length === 0) return null;

  const center = size / 2;
  const radius = size * 0.38;
  const levels = 5;
  const angleStep = (2 * Math.PI) / dimensions.length;

  const getPoint = (index, value) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = (value / 100) * radius;
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
  };

  // Grid circles
  const gridCircles = Array.from({ length: levels }, (_, i) => {
    const r = ((i + 1) / levels) * radius;
    return { r, label: `${Math.round(((i + 1) / levels) * 100)}` };
  });

  // Data polygon
  const dataPoints = dimensions.map((d, i) => getPoint(i, d.score || 0));
  const polygonPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ') + 'Z';

  // Axis lines
  const axisLines = dimensions.map((_, i) => {
    const end = getPoint(i, 100);
    return { x1: center, y1: center, x2: end.x, y2: end.y };
  });

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="mx-auto">
      {/* Grid circles */}
      {gridCircles.map((circle) => (
        <circle
          key={circle.r}
          cx={center}
          cy={center}
          r={circle.r}
          fill="none"
          stroke="var(--border-subtle)"
          strokeWidth="1"
          strokeDasharray="3,3"
        />
      ))}

      {/* Axis lines */}
      {axisLines.map((line, i) => (
        <line key={i} {...line} stroke="var(--border-subtle)" strokeWidth="1" />
      ))}

      {/* Data polygon fill */}
      <path d={polygonPath} fill="rgba(59, 130, 246, 0.15)" stroke="#3b82f6" strokeWidth="2" />

      {/* Data points */}
      {dataPoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="4" fill={DIMENSION_COLORS[dimensions[i].name] || '#3b82f6'} stroke="white" strokeWidth="2" />
      ))}

      {/* Labels */}
      {dimensions.map((dim, i) => {
        const labelAngle = angleStep * i - Math.PI / 2;
        const labelRadius = radius + 32;
        const lx = center + labelRadius * Math.cos(labelAngle);
        const ly = center + labelRadius * Math.sin(labelAngle);
        const textAnchor = labelAngle > Math.PI / 2 && labelAngle < 3 * Math.PI / 2 ? 'end' : labelAngle === Math.PI / 2 || labelAngle === 3 * Math.PI / 2 ? 'middle' : 'start';
        return (
          <text
            key={i}
            x={lx}
            y={ly}
            textAnchor={textAnchor}
            dominantBaseline="middle"
            fontSize="11"
            fill="var(--text-secondary)"
          >
            {DIMENSION_LABELS[dim.name] || dim.name}
          </text>
        );
      })}
    </svg>
  );
}

export default function SkillDNAPage() {
  const [overview, setOverview] = useState(null);
  const [profile, setProfile] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDimension, setSelectedDimension] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [overviewData, profileData, historyData] = await Promise.all([
          getDashboardOverview(),
          getDnaProfile(),
          getDnaProfileHistory(),
        ]);
        setOverview(overviewData);
        setProfile(profileData);
        setHistory(historyData.data || []);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load SkillDNA data.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const dimensions = useMemo(() => {
    if (!profile?.dimensions) return [];
    return profile.dimensions.map((dim) => ({
      name: dim.name,
      label: DIMENSION_LABELS[dim.name] || dim.name,
      score: dim.score || 0,
      confidence: dim.confidence || 0,
      classification: dim.classification || 'INSUFFICIENT_CONFIDENCE',
      evidence_status: dim.evidence_status,
      explanation: dim.explanation,
      color: DIMENSION_COLORS[dim.name] || '#3b82f6',
    }));
  }, [profile]);

  const scoreLabel = useMemo(() => {
    const score = overview?.coding_dna?.overall_score ?? profile?.overall_score;
    if (score === null || score === undefined) return 'Insufficient evidence';
    if (score >= 80) return 'Strong signal';
    if (score >= 60) return 'Growing signal';
    return 'Emerging signal';
  }, [overview, profile]);

  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'STRENGTH': return 'text-green-600 bg-green-50';
      case 'DEVELOPING_STRENGTH': return 'text-blue-600 bg-blue-50';
      case 'DEVELOPING': return 'text-yellow-600 bg-yellow-50';
      case 'DEVELOPMENT_AREA': return 'text-red-600 bg-red-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  return (
    <DashboardLayout title="SkillDNA" role="STUDENT" headingLevel={2}>
      <div className="space-y-6">
        {/* Header */}
        <section className="panel p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Coding DNA profile</p>
              <h2 className="section-title">Your behavioral intelligence snapshot</h2>
              <p className="mt-1 body-copy">This workspace turns your coding activity into a living profile that highlights strengths, growth areas, and momentum.</p>
            </div>
            <div className="metric-pill">{scoreLabel}</div>
          </div>

          {loading ? (
            <div className="mt-6 grid gap-4 lg:grid-cols-3">
              {[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" />)}
            </div>
          ) : error ? (
            <p className="mt-6 rounded-[24px] border border-red-200 bg-red-50 p-3 text-sm text-red-600">{error}</p>
          ) : (
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Overall score</p>
                <p className="mt-2 text-2xl font-semibold">{overview?.coding_dna?.overall_score ?? profile?.overall_score ?? '—'}</p>
              </div>
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Confidence</p>
                <p className="mt-2 text-2xl font-semibold">{profile?.overall_confidence ? `${(profile.overall_confidence * 100).toFixed(0)}%` : '—'}</p>
              </div>
              <div className="panel-soft p-4">
                <p className="text-sm text-[var(--text-muted)]">Evidence</p>
                <p className="mt-2 text-2xl font-semibold">{profile?.confidence_label || profile?.profile_status || 'Awaiting data'}</p>
              </div>
            </div>
          )}
        </section>

        {/* Radar Chart + Dimension Breakdown */}
        <section className="grid gap-6 lg:grid-cols-5">
          <div className="panel p-6 lg:col-span-2">
            <h3 className="section-title">Dimension radar</h3>
            <div className="mt-4 flex items-center justify-center">
              {dimensions.length > 0 ? (
                <SimpleRadarChart dimensions={dimensions} size={300} />
              ) : (
                <p className="body-copy text-center py-12">No dimension data available yet. Solve more problems to build your profile.</p>
              )}
            </div>
          </div>

          <div className="panel p-6 lg:col-span-3">
            <h3 className="section-title">Dimension breakdown</h3>
            <div className="mt-4 space-y-3">
              {dimensions.length === 0 ? (
                <p className="body-copy">No dimension scores available yet.</p>
              ) : (
                dimensions.map((dim) => (
                  <div
                    key={dim.name}
                    className="cursor-pointer rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 transition hover:border-blue-200 hover:shadow-sm"
                    onClick={() => setSelectedDimension(selectedDimension?.name === dim.name ? null : dim)}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="h-3 w-3 rounded-full" style={{ backgroundColor: dim.color }} />
                        <span className="font-medium text-[var(--text-primary)]">{dim.label}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-lg font-semibold">{dim.score.toFixed(0)}</span>
                        <span className={`rounded-full px-3 py-0.5 text-xs font-medium ${getClassificationColor(dim.classification)}`}>
                          {dim.classification.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                    {selectedDimension?.name === dim.name && (
                      <div className="mt-3 border-t border-[var(--border-subtle)] pt-3 text-sm text-[var(--text-secondary)]">
                        <p><span className="font-medium">Evidence:</span> {dim.evidence_status}</p>
                        <p className="mt-1"><span className="font-medium">Confidence:</span> {(dim.confidence * 100).toFixed(0)}%</p>
                        {dim.explanation && (
                          <p className="mt-2">{dim.explanation}</p>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* Profile Status + History */}
        <section className="grid gap-6 lg:grid-cols-2">
          <div className="panel p-6">
            <h3 className="section-title">Current profile status</h3>
            <div className="mt-4 space-y-3">
              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 text-sm text-[var(--text-secondary)]">
                <p className="font-medium text-[var(--text-primary)]">Profile status</p>
                <p className="mt-1">{profile?.profile_status || 'NOT_GENERATED'}</p>
              </div>
              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 text-sm text-[var(--text-secondary)]">
                <p className="font-medium text-[var(--text-primary)]">Evidence quality</p>
                <p className="mt-1">{overview?.evidence_status || 'Awaiting new activity'}</p>
              </div>
              <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4 text-sm text-[var(--text-secondary)]">
                <p className="font-medium text-[var(--text-primary)]">Scoring version</p>
                <p className="mt-1">{profile?.scoring_version || '—'}</p>
              </div>
            </div>
          </div>

          <div className="panel p-6">
            <h3 className="section-title">History snapshots</h3>
            {history.length === 0 ? (
              <p className="mt-4 body-copy">No DNA history has been generated yet. Practice more problems to build a richer profile.</p>
            ) : (
              <div className="mt-4 space-y-2">
                {history.slice(0, 5).map((item, index) => (
                  <div key={`${item.calculated_at || index}`} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-3 text-sm text-[var(--text-secondary)]">
                    <div className="flex items-center justify-between gap-3">
                      <span>{new Date(item.calculated_at).toLocaleDateString() || 'Snapshot'}</span>
                      <div className="flex items-center gap-3">
                        <span>{item.overall_score ?? '—'} pts</span>
                        {item.overall_confidence && (
                          <span className="text-xs text-[var(--text-muted)]">{(item.overall_confidence * 100).toFixed(0)}% conf</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}

