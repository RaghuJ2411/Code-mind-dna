import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import StudentDashboard from './StudentDashboard';

vi.mock('../../api/student', () => ({
  getDashboardOverview: vi.fn().mockResolvedValue({
    coding_dna: { overall_score: 82, confidence_label: 'Growing' },
    activity: { problems_attempted: 10, solve_rate: 0.8 },
    practice: { pending_recommendations: 2, active_goals: 1 },
    recent_progress: {
      overall_dna_delta: 1.2,
      solve_rate_delta: 0.1,
      attempt_efficiency_delta: 0.2,
      difficulty_progression_delta: 0.3,
    },
  }),
  listRecommendations: vi.fn().mockResolvedValue({ items: [] }),
  listGoals: vi.fn().mockResolvedValue([]),
  refreshRecommendations: vi.fn().mockResolvedValue({ items: [] }),
  startRecommendation: vi.fn(),
  completeRecommendation: vi.fn(),
  dismissRecommendation: vi.fn(),
  createGoal: vi.fn(),
}));

describe('StudentDashboard', () => {
  it('renders the student dashboard shell', async () => {
    render(
      <MemoryRouter>
        <StudentDashboard />
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: /student dashboard/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/coding dna score/i)).toBeInTheDocument();
  });
});
