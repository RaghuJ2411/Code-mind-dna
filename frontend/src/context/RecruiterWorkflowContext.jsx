import React, { createContext, useContext, useMemo, useState } from 'react';

const RecruiterWorkflowContext = createContext({
  selectedJob: null,
  selectedCandidate: null,
  setSelectedJob: () => {},
  setSelectedCandidate: () => {},
  clearSelection: () => {},
});

export function RecruiterWorkflowProvider({ children }) {
  const [selectedJob, setSelectedJobState] = useState(null);
  const [selectedCandidate, setSelectedCandidateState] = useState(null);

  const setSelectedJob = (job) => setSelectedJobState(job ?? null);
  const setSelectedCandidate = (candidate) => setSelectedCandidateState(candidate ?? null);
  const clearSelection = () => {
    setSelectedJobState(null);
    setSelectedCandidateState(null);
  };

  const value = useMemo(
    () => ({
      selectedJob,
      selectedCandidate,
      setSelectedJob,
      setSelectedCandidate,
      clearSelection,
    }),
    [selectedJob, selectedCandidate]
  );

  return <RecruiterWorkflowContext.Provider value={value}>{children}</RecruiterWorkflowContext.Provider>;
}

export function useRecruiterWorkflow() {
  return useContext(RecruiterWorkflowContext);
}
