import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MentorDashboard from './MentorDashboard';

const { mockListMentorAlerts, mockListMentorStudents, mockGenerateMentorAlerts } = vi.hoisted(() => ({
  mockListMentorAlerts: vi.fn(),
  mockListMentorStudents: vi.fn(),
  mockGenerateMentorAlerts: vi.fn(),
}));

vi.mock('../../api/mentor', () => ({
  listMentorAlerts: mockListMentorAlerts,
  acknowledgeMentorAlert: vi.fn(),
  resolveMentorAlert: vi.fn(),
  listMentorStudents: mockListMentorStudents,
  createMentorAlert: vi.fn(),
  generateMentorAlerts: mockGenerateMentorAlerts,
}));

vi.mock('../../layouts/DashboardLayout', () => ({
  default: ({ children }) => <div>{children}</div>,
}));

describe('MentorDashboard', () => {
  beforeEach(() => {
    mockListMentorAlerts.mockReset();
    mockListMentorStudents.mockReset();
    mockGenerateMentorAlerts.mockReset();

    mockListMentorAlerts.mockResolvedValue({ items: [] });
    mockListMentorStudents.mockResolvedValue([]);
    mockGenerateMentorAlerts.mockResolvedValue({ items: [] });
  });

  it('generates mentor alerts from the dashboard', async () => {
    render(<MentorDashboard />);

    const user = userEvent.setup();
    await user.click(await screen.findByRole('button', { name: /generate alerts/i }));

    await waitFor(() => expect(mockGenerateMentorAlerts).toHaveBeenCalledTimes(1));
  });
});
