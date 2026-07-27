import React, { useState } from 'react';

export default function MentorAlertForm({ students, onSubmit, loading }) {
  const [payload, setPayload] = useState({
    student_id: '',
    alert_type: 'ENGAGEMENT_DROP',
    severity: 'HIGH',
    message: '',
  });

  const handleChange = (key, value) => {
    setPayload((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      student_id: payload.student_id ? Number(payload.student_id) : null,
      alert_type: payload.alert_type,
      severity: payload.severity,
      message: payload.message,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="student_id" className="block text-sm font-medium text-slate-700">
          Student
        </label>
        <select
          id="student_id"
          value={payload.student_id}
          onChange={(event) => handleChange('student_id', event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
        >
          <option value="">All students</option>
          {students.map((student) => (
            <option key={student.id} value={student.id}>
              {student.full_name} ({student.email})
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <label htmlFor="alert_type" className="block text-sm font-medium text-slate-700">
          Alert type
        </label>
          <select
            id="alert_type"
            value={payload.alert_type}
            onChange={(event) => handleChange('alert_type', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="ENGAGEMENT_DROP">Engagement drop</option>
            <option value="LOW_SUCCESS_RATE">Low success rate</option>
            <option value="INCONSISTENT_PRACTICE">Inconsistent practice</option>
            <option value="ATTENDANCE_ISSUE">Attendance issue</option>
          </select>
        </div>
        <div>
          <label htmlFor="severity" className="block text-sm font-medium text-slate-700">
          Severity
        </label>
          <select
            id="severity"
            value={payload.severity}
            onChange={(event) => handleChange('severity', event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="message" className="block text-sm font-medium text-slate-700">
          Message
        </label>
        <textarea
          id="message"
          value={payload.message}
          onChange={(event) => handleChange('message', event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          rows={4}
          required
        />
      </div>

      <button
        type="submit"
        className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        disabled={loading}
      >
        {loading ? 'Creating…' : 'Create alert'}
      </button>
    </form>
  );
}
