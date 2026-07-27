import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RecruiterDashboard from './RecruiterDashboard';

const { mockNavigate, mockGetRecruiterDashboard, mockListRecruiterJobs, mockListRecruiterCandidates } = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  mockGetRecruiterDashboard: vi.fn(),
  mockListRecruiterJobs: vi.fn(),
  mockListRecruiterCandidates: vi.fn(),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../../api/recruiter', () => ({
  getRecruiterDashboard: mockGetRecruiterDashboard,
  listRecruiterJobs: mockListRecruiterJobs,
  createRecruiterJob: vi.fn(),
  listRecruiterCandidates: mockListRecruiterCandidates,
}));

vi.mock('../../layouts/DashboardLayout', () => ({
  default: ({ children }) => <div>{children}</div>,
}));

describe('RecruiterDashboard', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    mockGetRecruiterDashboard.mockReset();
    mockListRecruiterJobs.mockReset();
    mockListRecruiterCandidates.mockReset();

    mockGetRecruiterDashboard.mockResolvedValue({
      total_open_jobs: 1,
      total_candidates: 1,
      best_fit_candidate: { id: 7, full_name: 'Ava', email: 'ava@example.com', fit_score: 91, confidence_label: 'High', readiness_label: 'Ready', resume_strength: 'Strong', interview_readiness: 'Ready' },
      top_open_job: { id: 101, title: 'Senior Frontend Engineer', company: 'Acme', location: 'Remote', seniority_level: 'SENIOR', description: 'Build product features' },
    });
    mockListRecruiterJobs.mockResolvedValue([{ id: 101, title: 'Senior Frontend Engineer', company: 'Acme', location: 'Remote', seniority_level: 'SENIOR' }]);
    mockListRecruiterCandidates.mockResolvedValue([]);
  });

  it('navigates to the selected job from the hiring pipeline', async () => {
    render(<RecruiterDashboard />);

    const user = userEvent.setup();
    await user.click(await screen.findByRole('button', { name: /open role workspace senior frontend engineer/i }));

    expect(mockNavigate).toHaveBeenCalledWith('/recruiter/jobs/101');
  });
});
