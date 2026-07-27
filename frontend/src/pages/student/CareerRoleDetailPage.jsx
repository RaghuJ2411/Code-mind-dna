import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getCareerRole } from '../../api/student';

export default function CareerRoleDetailPage() {
  const { roleId } = useParams();
  const navigate = useNavigate();
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadRole = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getCareerRole(roleId);
        setRole(data);
      } catch (err) {
        setError(err?.response?.data?.detail || 'Unable to load role details.');
      } finally {
        setLoading(false);
      }
    };

    loadRole();
  }, [roleId]);

  return (
    <DashboardLayout title="Career Role Details" role="STUDENT">
      <div className="space-y-6">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700"
        >
          Back to career overview
        </button>

        {loading ? (
          <div className="rounded-2xl bg-white p-6 shadow-sm text-slate-500">Loading role details...</div>
        ) : error ? (
          <div className="rounded-2xl bg-rose-50 p-6 shadow-sm text-rose-700">{error}</div>
        ) : (
          <div className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{role.seniority_level}</p>
                <h2 className="text-2xl font-semibold text-slate-900">{role.name}</h2>
              </div>
              <div className="rounded-full bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700">
                Match target {role.target_score_min}% — {role.target_score_max}%
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">Description</h3>
                <p className="mt-2 text-sm text-slate-700">{role.description}</p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-slate-900">Required skills</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {role.required_skills.map((skill) => (
                    <span key={skill} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
