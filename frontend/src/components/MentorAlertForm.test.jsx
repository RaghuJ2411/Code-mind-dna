import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MentorAlertForm from './MentorAlertForm';

describe('MentorAlertForm', () => {
  const students = [
    { id: 1, full_name: 'Student One', email: 'one@example.com' },
    { id: 2, full_name: 'Student Two', email: 'two@example.com' },
  ];

  it('renders form fields and submits payload', async () => {
    const onSubmit = vi.fn();

    render(<MentorAlertForm students={students} onSubmit={onSubmit} loading={false} />);

    const studentSelect = screen.getByLabelText(/Student/i);
    const alertTypeSelect = screen.getByLabelText(/Alert type/i);
    const severitySelect = screen.getByLabelText(/Severity/i);
    const messageInput = screen.getByRole('textbox');
    const submitButton = screen.getByRole('button', { name: /Create alert/i });

    fireEvent.change(studentSelect, { target: { value: '2' } });
    fireEvent.change(alertTypeSelect, { target: { value: 'LOW_SUCCESS_RATE' } });
    fireEvent.change(severitySelect, { target: { value: 'LOW' } });
    fireEvent.change(messageInput, { target: { value: 'Needs more practice sessions.' } });
    fireEvent.click(submitButton);

    expect(onSubmit).toHaveBeenCalledWith({
      student_id: 2,
      alert_type: 'LOW_SUCCESS_RATE',
      severity: 'LOW',
      message: 'Needs more practice sessions.',
    });
  });
});
