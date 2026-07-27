import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await login(form);
      const role = response.user.role;
      navigate(`/${role.toLowerCase()}/dashboard`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)]">
      <div className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
        <section className="auth-hero hidden lg:flex lg:flex-col lg:justify-between">
          <div>
            <p className="kicker text-white/80">AI-powered developer intelligence</p>
            <h1 className="mt-6 text-4xl font-semibold leading-tight">Build skills. Prove them. Grow with evidence.</h1>
            <p className="mt-4 max-w-xl text-base text-white/80">Transform coding activity, debugging behavior, projects, roadmaps, and career evidence into a precise growth workspace.</p>
          </div>
          <div className="mt-8 rounded-[24px] border border-white/20 bg-white/10 p-5 backdrop-blur">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <p className="text-3xl font-semibold">5</p>
                <p className="mt-1 text-sm text-white/70">intelligence modes</p>
              </div>
              <div>
                <p className="text-3xl font-semibold">100%</p>
                <p className="mt-1 text-sm text-white/70">evidence-first</p>
              </div>
              <div>
                <p className="text-3xl font-semibold">24/7</p>
                <p className="mt-1 text-sm text-white/70">growth guidance</p>
              </div>
            </div>
          </div>
        </section>

        <section className="flex items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
          <div className="auth-card w-full max-w-md">
            <p className="kicker">Welcome back</p>
            <h2 className="mt-3 text-3xl font-semibold">Sign in to your workspace</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">Continue your learning journey with structured intelligence and actionable feedback.</p>

            <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Email</span>
                <input
                  className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 text-[var(--text-primary)] outline-none ring-0 transition focus:border-[var(--brand-primary)]"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </label>
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                <span className="mb-1 block">Password</span>
                <div className="relative">
                  <input
                    className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-3 py-3 pr-20 text-[var(--text-primary)] outline-none transition focus:border-[var(--brand-primary)]"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    required
                  />
                  <button type="button" className="absolute inset-y-0 right-3 text-sm font-medium text-[var(--text-muted)]" onClick={() => setShowPassword((current) => !current)}>
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </label>

              {error ? <p className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p> : null}
              <button className="btn-primary w-full" type="submit" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </form>

            <p className="mt-6 text-sm text-[var(--text-secondary)]">
              New here? <Link className="font-semibold text-[var(--brand-primary)]" to="/register">Create an account</Link>
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
