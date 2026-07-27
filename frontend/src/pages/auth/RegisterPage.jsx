import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const roles = ['STUDENT', 'MENTOR', 'ADMIN', 'RECRUITER'];

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({ full_name: '', email: '', password: '', role: 'STUDENT' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await register(form);
      const role = response.user.role;
      navigate(`/${role.toLowerCase()}/dashboard`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)]">
      <div className="grid min-h-screen lg:grid-cols-[1.02fr_0.98fr]">
        <section className="auth-hero hidden lg:flex lg:flex-col lg:justify-between">
          <div>
            <p className="kicker text-white/80">Start your evidence-backed profile</p>
            <h1 className="mt-6 text-4xl font-semibold leading-tight">Create a workspace that grows with every submission.</h1>
            <p className="mt-4 max-w-xl text-base text-white/80">From first challenge to career readiness and recruiter matching, each milestone becomes visible evidence.</p>
          </div>
          <div className="rounded-[24px] border border-white/20 bg-white/10 p-5 backdrop-blur">
            <p className="text-sm text-white/70">Why teams love it</p>
            <ul className="mt-3 space-y-2 text-sm text-white/80">
              <li>• Evidence-based skill visibility</li>
              <li>• Guidance for mentors and recruiters</li>
              <li>• Protected, role-aware workflows</li>
            </ul>
          </div>
        </section>

        <section className="flex items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
          <div className="auth-card w-full max-w-lg">
            <p className="kicker">Create account</p>
            <h2 className="mt-3 text-3xl font-semibold">Set up your CodeMind DNA profile</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">Start with your name, email, and role so the experience can guide you appropriately.</p>

            <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Full name</span>
                <input className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 text-[var(--text-primary)] outline-none transition focus:border-[var(--brand-primary)]" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
              </label>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Email</span>
                <input className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 text-[var(--text-primary)] outline-none transition focus:border-[var(--brand-primary)]" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </label>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Password</span>
                <div className="relative">
                  <input className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 pr-20 text-[var(--text-primary)] outline-none transition focus:border-[var(--brand-primary)]" type={showPassword ? 'text' : 'password'} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                  <button type="button" className="absolute inset-y-0 right-3 text-sm font-medium text-[var(--text-muted)]" onClick={() => setShowPassword((current) => !current)}>
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </label>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Role</span>
                <select className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 text-[var(--text-primary)] outline-none transition focus:border-[var(--brand-primary)]" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  {roles.map((role) => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </label>
              {error ? <p className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p> : null}
              <button className="btn-primary w-full" type="submit" disabled={loading}>
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </form>
            <p className="mt-6 text-sm text-[var(--text-secondary)]">
              Already have an account? <Link className="font-semibold text-[var(--brand-primary)]" to="/login">Sign in</Link>
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
