import { useEffect, useState, useRef } from 'react';
import DashboardLayout from '../../layouts/DashboardLayout';
import { chatWithMentor, getChatHistory, generateInterviewQuestions, reviewResume, explainCode, fixBug } from '../../api/aiMentor';

const FEATURES = [
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'interview', label: 'Interview Questions', icon: '🎯' },
  { id: 'resume', label: 'Resume Review', icon: '📄' },
  { id: 'code', label: 'Code Explanation', icon: '🔍' },
  { id: 'bugfix', label: 'Bug Fix', icon: '🐛' },
];

export default function AIMentorPage() {
  const [activeFeature, setActiveFeature] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const [roleName, setRoleName] = useState('');
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [interviewLoading, setInterviewLoading] = useState(false);
  const [resumeContent, setResumeContent] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [resumeResult, setResumeResult] = useState(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [codeInput, setCodeInput] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('python');
  const [codeContext, setCodeContext] = useState('');
  const [codeExplanation, setCodeExplanation] = useState(null);
  const [codeLoading, setCodeLoading] = useState(false);
  const [bugCode, setBugCode] = useState('');
  const [bugError, setBugError] = useState('');
  const [bugLanguage, setBugLanguage] = useState('python');
  const [bugResult, setBugResult] = useState(null);
  const [bugLoading, setBugLoading] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (activeFeature === 'chat') {
      getChatHistory()
        .then((history) => {
          if (history.length > 0) {
            setConversationId(history[0].conversation_id);
            setMessages(history[0].messages || []);
          }
        })
        .catch(() => {});
    }
  }, [activeFeature]);

  const handleChat = async (e) => {
    e.preventDefault();
    if (!input.trim() || chatLoading) return;
    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);
    try {
      const response = await chatWithMentor(userMessage, conversationId);
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, { role: 'assistant', content: response.reply }]);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Chat failed');
    } finally {
      setChatLoading(false);
    }
  };

  const handleInterview = async () => {
    if (!roleName.trim()) return;
    setInterviewLoading(true);
    try {
      const result = await generateInterviewQuestions(roleName);
      setInterviewQuestions(result.questions || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to generate questions');
    } finally {
      setInterviewLoading(false);
    }
  };

  const handleResumeReview = async () => {
    if (!resumeContent.trim()) return;
    setResumeLoading(true);
    try {
      const result = await reviewResume(resumeContent, targetRole);
      setResumeResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to review resume');
    } finally {
      setResumeLoading(false);
    }
  };

  const handleCodeExplain = async () => {
    if (!codeInput.trim()) return;
    setCodeLoading(true);
    try {
      const result = await explainCode(codeInput, codeLanguage, codeContext);
      setCodeExplanation(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to explain code');
    } finally {
      setCodeLoading(false);
    }
  };

  const handleBugFix = async () => {
    if (!bugCode.trim()) return;
    setBugLoading(true);
    try {
      const result = await fixBug(bugCode, bugError, bugLanguage);
      setBugResult(result);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to fix bug');
    } finally {
      setBugLoading(false);
    }
  };

  return (
    <DashboardLayout title="AI Mentor" role="STUDENT">
      <div className="space-y-6">
        {error && <div className="rounded-[24px] border border-red-200 bg-red-50 p-4 text-sm text-red-600">{error}</div>}

        <section className="panel p-3 sm:p-4">
          <div className="flex flex-wrap gap-2">
            {FEATURES.map((f) => (
              <button key={f.id} onClick={() => setActiveFeature(f.id)} className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeFeature === f.id ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-secondary)] hover:bg-[var(--surface-interactive)]'}`}>{f.icon} {f.label}</button>
            ))}
          </div>
        </section>

        {activeFeature === 'chat' && (
          <section className="panel flex flex-col" style={{ height: '500px' }}>
            <div className="flex-1 space-y-3 overflow-y-auto p-4">
              {messages.length === 0 && (
                <div className="flex h-full items-center justify-center">
                  <div className="text-center">
                    <p className="text-3xl">🤖</p>
                    <p className="mt-2 text-sm text-[var(--text-muted)]">Ask me anything about coding, career, or learning!</p>
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-[24px] p-4 text-sm ${msg.role === 'user' ? 'bg-[var(--brand-primary)] text-white' : 'bg-[var(--surface-elevated)] text-[var(--text-primary)]'}`}>
                    <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleChat} className="flex gap-3 border-t border-[var(--border-subtle)] p-4">
              <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type your message..." className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" disabled={chatLoading} />
              <button type="submit" disabled={chatLoading || !input.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{chatLoading ? 'Thinking...' : 'Send'}</button>
            </form>
          </section>
        )}

        {activeFeature === 'interview' && (
          <section className="panel p-6">
            <div className="flex gap-3">
              <input value={roleName} onChange={(e) => setRoleName(e.target.value)} placeholder="Enter target role (e.g., Software Engineer)" className="flex-1 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
              <button onClick={handleInterview} disabled={interviewLoading || !roleName.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{interviewLoading ? 'Generating...' : 'Generate Questions'}</button>
            </div>
            <div className="mt-6 space-y-4">
              {interviewQuestions.map((q, i) => (
                <div key={i} className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <div className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--brand-primary)] text-xs font-semibold text-white">{i + 1}</span>
                    <p className="text-sm text-[var(--text-primary)]">{q}</p>
                  </div>
                </div>
              ))}
              {interviewQuestions.length === 0 && !interviewLoading && <p className="body-copy text-center">Enter a role to get interview questions.</p>}
            </div>
          </section>
        )}

        {activeFeature === 'resume' && (
          <section className="panel p-6">
            <div className="space-y-4">
              <textarea value={resumeContent} onChange={(e) => setResumeContent(e.target.value)} placeholder="Paste your resume content here..." rows={8} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3 text-sm outline-none focus:border-[var(--brand-primary)]" />
              <input value={targetRole} onChange={(e) => setTargetRole(e.target.value)} placeholder="Target role (optional)" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
              <button onClick={handleResumeReview} disabled={resumeLoading || !resumeContent.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{resumeLoading ? 'Reviewing...' : 'Review Resume'}</button>
            </div>
            {resumeResult && (
              <div className="mt-6 space-y-4">
                <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4">
                  <p className="font-semibold text-emerald-800">Match Score: {resumeResult.match_score}%</p>
                  <p className="mt-2 text-sm text-emerald-700">{resumeResult.feedback}</p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Strengths</p>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-emerald-600">
                    {resumeResult.strengths?.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Improvements</p>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-600">
                    {resumeResult.improvements?.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              </div>
            )}
          </section>
        )}

        {activeFeature === 'code' && (
          <section className="panel p-6">
            <div className="space-y-4">
              <select value={codeLanguage} onChange={(e) => setCodeLanguage(e.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
              <textarea value={codeInput} onChange={(e) => setCodeInput(e.target.value)} placeholder="Paste your code here..." rows={8} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3 font-mono text-sm outline-none focus:border-[var(--brand-primary)]" />
              <input value={codeContext} onChange={(e) => setCodeContext(e.target.value)} placeholder="Context (optional, e.g., 'This is a sorting algorithm')" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
              <button onClick={handleCodeExplain} disabled={codeLoading || !codeInput.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{codeLoading ? 'Analyzing...' : 'Explain Code'}</button>
            </div>
            {codeExplanation && (
              <div className="mt-6 space-y-4">
                <div className="rounded-[24px] border border-[var(--border-subtle)] bg-[var(--surface-elevated)] p-4">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">Explanation</p>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">{codeExplanation.explanation}</p>
                </div>
                {codeExplanation.key_concepts?.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-[var(--text-primary)]">Key Concepts</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {codeExplanation.key_concepts.map((c, i) => <span key={i} className="rounded-full bg-[var(--brand-primary)]/10 px-3 py-1 text-xs text-[var(--brand-primary)]">{c}</span>)}
                    </div>
                  </div>
                )}
                {codeExplanation.suggestions?.length > 0 && (
                  <div>
                    <p className="text-sm font-semibold text-[var(--text-primary)]">Suggestions</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-secondary)]">
                      {codeExplanation.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {activeFeature === 'bugfix' && (
          <section className="panel p-6">
            <div className="space-y-4">
              <select value={bugLanguage} onChange={(e) => setBugLanguage(e.target.value)} className="rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]">
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
              </select>
              <textarea value={bugCode} onChange={(e) => setBugCode(e.target.value)} placeholder="Paste your code with the bug..." rows={8} className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-3 font-mono text-sm outline-none focus:border-[var(--brand-primary)]" />
              <input value={bugError} onChange={(e) => setBugError(e.target.value)} placeholder="Error message (optional)" className="w-full rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-elevated)] px-4 py-2.5 text-sm outline-none focus:border-[var(--brand-primary)]" />
              <button onClick={handleBugFix} disabled={bugLoading || !bugCode.trim()} className="rounded-2xl bg-[var(--brand-primary)] px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{bugLoading ? 'Analyzing...' : 'Fix Bug'}</button>
            </div>
            {bugResult && (
              <div className="mt-6 space-y-4">
                {bugResult.root_cause && (
                  <div className="rounded-[24px] border border-red-200 bg-red-50 p-4">
                    <p className="text-sm font-semibold text-red-800">Root Cause</p>
                    <p className="mt-1 text-sm text-red-700">{bugResult.root_cause}</p>
                  </div>
                )}
                <div className="rounded-[24px] border border-emerald-200 bg-emerald-50 p-4">
                  <p className="text-sm font-semibold text-emerald-800">Fix</p>
                  <p className="mt-1 text-sm text-emerald-700">{bugResult.explanation}</p>
                </div>
                {bugResult.fixed_code && (
                  <div>
                    <p className="text-sm font-semibold text-[var(--text-primary)]">Fixed Code</p>
                    <pre className="mt-2 overflow-x-auto rounded-[24px] bg-[var(--surface)] p-4 text-sm">{bugResult.fixed_code}</pre>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

