import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RecruiterWorkflowProvider, useRecruiterWorkflow } from './RecruiterWorkflowContext';

function TestConsumer() {
  const { selectedJob, selectedCandidate, setSelectedJob, setSelectedCandidate, clearSelection } = useRecruiterWorkflow();

  return (
    <div>
      <button onClick={() => setSelectedJob({ id: 101, title: 'Senior Frontend Engineer' })}>select job</button>
      <button onClick={() => setSelectedCandidate({ id: 77, full_name: 'Ava Patel' })}>select candidate</button>
      <button onClick={clearSelection}>clear</button>
      <div data-testid="job">{selectedJob?.title ?? 'none'}</div>
      <div data-testid="candidate">{selectedCandidate?.full_name ?? 'none'}</div>
    </div>
  );
}

describe('RecruiterWorkflowContext', () => {
  it('stores the selected job and candidate across the workflow', async () => {
    const user = userEvent.setup();

    render(
      <RecruiterWorkflowProvider>
        <TestConsumer />
      </RecruiterWorkflowProvider>
    );

    await user.click(screen.getByRole('button', { name: /select job/i }));
    await user.click(screen.getByRole('button', { name: /select candidate/i }));

    expect(screen.getByTestId('job').textContent).toBe('Senior Frontend Engineer');
    expect(screen.getByTestId('candidate').textContent).toBe('Ava Patel');
  });
});
