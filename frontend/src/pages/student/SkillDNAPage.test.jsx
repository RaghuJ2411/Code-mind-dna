import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SkillDNAPage from './SkillDNAPage';

vi.mock('../../api/student', () => ({
  getDashboardOverview: vi.fn().mockResolvedValue({
    coding_dna: { overall_score: 79, confidence_label: 'Growing' },
    activity: { problems_attempted: 12, solve_rate: 0.75 },
  }),
  getDnaProfile: vi.fn().mockResolvedValue({ profile_status: 'GENERATED', overall_score: 79, overall_confidence: 0.84 }),
  getDnaProfileHistory: vi.fn().mockResolvedValue({ total: 1, data: [] }),
}));

describe('SkillDNAPage', () => {
  it('renders the skill dna workspace', async () => {
    render(
      <MemoryRouter>
        <SkillDNAPage />
      </MemoryRouter>
    );

    expect(await screen.findByRole('heading', { name: /skilldna/i, level: 2 })).toBeInTheDocument();
    expect(screen.getByText(/coding dna profile/i)).toBeInTheDocument();
  });
});
