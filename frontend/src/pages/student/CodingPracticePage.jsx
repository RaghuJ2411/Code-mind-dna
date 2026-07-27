import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../layouts/DashboardLayout';

export default function CodingPracticePage() {
  const navigate = useNavigate();

  return (
    <DashboardLayout title="Coding Practice" role="STUDENT">
      <div className="space-y-6">
        <section className="panel p-5 sm:p-6">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="kicker">Coding Challenges</p>
              <h2 className="section-title">Practice coding problems</h2>
              <p className="mt-1 body-copy">Choose from a wide range of coding challenges across different difficulties and topics.</p>
            </div>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <button onClick={() => navigate('/student/problems')} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-left transition hover:shadow-md">
              <p className="text-2xl">📚</p>
              <p className="mt-3 font-semibold text-[var(--text-primary)]">Problem Bank</p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Browse all available problems, search by topic or difficulty.</p>
            </button>
            <button onClick={() => navigate('/student/assessments')} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-left transition hover:shadow-md">
              <p className="text-2xl">📝</p>
              <p className="mt-3 font-semibold text-[var(--text-primary)]">Coding Assessments</p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Take timed coding assessments to test your skills.</p>
            </button>
            <button onClick={() => navigate('/student/progress')} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-6 text-left transition hover:shadow-md">
              <p className="text-2xl">📊</p>
              <p className="mt-3 font-semibold text-[var(--text-primary)]">Practice Analytics</p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Track your coding progress and identify areas for improvement.</p>
            </button>
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}

