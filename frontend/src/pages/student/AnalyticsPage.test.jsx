import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AnalyticsPage from './AnalyticsPage';

vi.mock('../../api/student', () => ({
  getAnalyticsProfile: vi.fn().mockResolvedValue({
    evidence_status: 'SUFFICIENT_DATA',
    activity: { problems_attempted: 2, problems_solved: 1 },
    success: { solve_rate: 0.5 },
    consistency: { active_days_last_7: 3 },
    progression: { solve_rate_delta: 0.1 },
    topics: [],
    debugging: { total_wrong_answers: 1 },
    difficulty: { easy: { solve_rate: 1 }, medium: { solve_rate: 0.5 }, hard: { solve_rate: 0.2 }, weighted_difficulty: 1.2 },
  }),
  getAnalyticsDaily: vi.fn().mockResolvedValue({ data: [] }),
  getAnalyticsWeekly: vi.fn().mockResolvedValue({ data: [] }),
}));

describe('AnalyticsPage', () => {
  it('renders analytics summary cards', async () => {
    render(
      <MemoryRouter>
        <AnalyticsPage />
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: /analytics overview/i, level: 2 })).toBeInTheDocument();
    expect(screen.getByText(/evidence status/i)).toBeInTheDocument();
    expect(screen.getByText('SUFFICIENT_DATA')).toBeInTheDocument();
  });
});
