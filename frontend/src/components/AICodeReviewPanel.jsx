import { useEffect, useState } from 'react';
import { requestCodeReview, getCodeReview } from '../api/student';

export default function AICodeReviewPanel({ submissionId }) {
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const resp = await getCodeReview(submissionId).catch(() => null);
        if (mounted && resp && resp.status === 'success') setReview(resp.data);
      } catch (err) {
        // ignore
      }
    };
    load();
    return () => { mounted = false; };
  }, [submissionId]);

  const handleRequest = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await requestCodeReview(submissionId);
      if (resp.status === 'success') setReview(resp.data);
      else setError('AI request failed');
    } catch (err) {
      setError(err?.response?.data?.detail || 'AI request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-2 rounded-lg border border-slate-100 bg-white p-3 text-sm">
      {review ? (
        <div>
          <div className="mb-2 font-semibold">AI Code Review</div>
          <div className="mb-2"><strong>Summary:</strong> {review.summary}</div>
          <div className="mb-2"><strong>Correctness:</strong>
            <ul className="list-disc pl-6">{(review.correctness_observations||[]).map((o, i) => <li key={i}>{o}</li>)}</ul>
          </div>
          <div className="mb-2"><strong>Quality:</strong>
            <ul className="list-disc pl-6">{(review.code_quality_observations||[]).map((o, i) => <li key={i}>{o}</li>)}</ul>
          </div>
          <div className="mb-2"><strong>Improvements:</strong>
            <ul className="list-disc pl-6">{(review.improvements||[]).map((it, i) => <li key={i}>{it.title} — {it.reason} ({it.priority})</li>)}</ul>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <div className="text-slate-600">No AI review yet.</div>
          <div>
            <button onClick={handleRequest} disabled={loading} className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-semibold text-white disabled:opacity-60">
              {loading ? 'Requesting...' : 'Get AI Review'}
            </button>
          </div>
        </div>
      )}
      {error && <div className="mt-2 text-rose-600">{error}</div>}
    </div>
  );
}
