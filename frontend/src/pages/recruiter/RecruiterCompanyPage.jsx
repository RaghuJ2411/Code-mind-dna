import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { getRecruiterCompanyProfile, upsertRecruiterCompanyProfile } from '../../api/recruiter';

export default function RecruiterCompanyPage() {
  const [form, setForm] = useState({
    company_name: '',
    description: '',
    industry: '',
    website: '',
    employees: '',
    location: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await getRecruiterCompanyProfile();
        if (data) {
          setForm({
            company_name: data.company_name || '',
            description: data.description || '',
            industry: data.industry || '',
            website: data.website || '',
            employees: data.employees || '',
            location: data.location || '',
          });
        }
        setError('');
      } catch (err) {
        if (err?.response?.status !== 404) {
          setError(err?.response?.data?.detail || 'Unable to load profile.');
        }
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await upsertRecruiterCompanyProfile(form);
      setSuccess('Company profile saved successfully.');
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to save company profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Company Profile" role="RECRUITER">
      <div className="space-y-6">
        {success ? <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">{success}</div> : null}
        {error ? <div className="rounded-[24px] border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div> : null}
        <section className="panel p-6">
          <div>
            <p className="kicker">Company profile</p>
            <h2 className="section-title">Brand and organization settings</h2>
          </div>
          {loading ? <div className="mt-6 h-40 animate-pulse rounded-[24px] bg-[var(--surface-elevated)]" /> : (
            <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
              <div><label className="block text-sm font-medium">Company name</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} required /></div>
              <div><label className="block text-sm font-medium">Industry</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} /></div>
              <div><label className="block text-sm font-medium">Website</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} /></div>
              <div><label className="block text-sm font-medium">Location</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
              <div><label className="block text-sm font-medium">Employees</label><input className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" value={form.employees} onChange={(e) => setForm({ ...form, employees: e.target.value })} /></div>
              <div className="md:col-span-2"><label className="block text-sm font-medium">Description</label><textarea className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm" rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <div className="md:col-span-2"><button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save Profile'}</button></div>
            </form>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}

