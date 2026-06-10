import { useState } from 'react';

const mockPRs = [
  {
    id: '1',
    title: 'fix: run BackgroundTasks with clean session factory scope',
    branch: 'fix/background-session-leak',
    status: 'Merged',
    badgeClass: 'badge-active',
    author: 'sachin-saroj',
    date: 'Jun 8, 2026',
    commits: 2,
    filesChanged: 3,
    reviews: [
      { reviewer: 'auditor', status: 'Approved', comment: 'Looks great. Session leaks inside celery are resolved, and transaction scopes are safely scoped inside the worker context.' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Refactored _record_click_background parameters', time: 'Jun 8, 2026' },
      { type: 'review', user: 'auditor', text: 'Approved the PR after regression validation.', time: 'Jun 8, 2026' }
    ]
  },
  {
    id: '2',
    title: 'perf: introduce asynchronous dnspython resolver check',
    branch: 'perf/async-dns-resolver',
    status: 'Merged',
    badgeClass: 'badge-active',
    author: 'sachin-saroj',
    date: 'Jun 8, 2026',
    commits: 3,
    filesChanged: 4,
    reviews: [
      { reviewer: 'auditor', status: 'Approved', comment: 'Successfully resolves blocking threads in validators. Good performance improvement under high click rates.' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Added dnspython async dns validation checks', time: 'Jun 8, 2026' },
      { type: 'review', user: 'auditor', text: 'Code reviews completed, thread blocking is eliminated.', time: 'Jun 8, 2026' }
    ]
  },
  {
    id: '3',
    title: 'auth: support HTTPS cookie auth configuration options',
    branch: 'auth/cookie-secure-rules',
    status: 'Merged',
    badgeClass: 'badge-active',
    author: 'sachin-saroj',
    date: 'Jun 8, 2026',
    commits: 2,
    filesChanged: 5,
    reviews: [
      { reviewer: 'auditor', status: 'Approved', comment: 'Secures JWT delivery via HttpOnly cookies with dynamic SameSite mapping.' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Implemented SameSite Lax/None checks', time: 'Jun 8, 2026' }
    ]
  },
  {
    id: '4',
    title: 'feat: move dashboard calculation endpoint to backend',
    branch: 'feat/backend-stats-aggregation',
    status: 'Merged',
    badgeClass: 'badge-active',
    author: 'sachin-saroj',
    date: 'Jun 9, 2026',
    commits: 4,
    filesChanged: 6,
    reviews: [
      { reviewer: 'qa_reviewer', status: 'Approved', comment: 'Calculations are correct now. Handled division-by-zero on fresh accounts gracefully.' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Implemented dashboard statistics endpoint', time: 'Jun 9, 2026' }
    ]
  },
  {
    id: '5',
    title: 'perf: read redirect URL payload directly from Redis cache',
    branch: 'perf/cache-aside-bypass',
    status: 'Merged',
    badgeClass: 'badge-active',
    author: 'sachin-saroj',
    date: 'Jun 9, 2026',
    commits: 3,
    filesChanged: 4,
    reviews: [
      { reviewer: 'perf_reviewer', status: 'Approved', comment: 'Saves 1 DB query per cache hit. Outstanding speedup for redirection hotspots!' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Cached validation metadata as JSON string in Redis', time: 'Jun 9, 2026' },
      { type: 'review', user: 'perf_reviewer', text: 'Verified queries via logs. Query count on cache hit is now 0.', time: 'Jun 9, 2026' }
    ]
  },
  {
    id: '6',
    title: 'design: migrate layout to Premium Utilitarian Minimalism',
    branch: 'design/minimalist-ui-editorial',
    status: 'Under Review',
    badgeClass: 'badge-warning',
    author: 'sachin-saroj',
    date: 'Jun 10, 2026',
    commits: 4,
    filesChanged: 12,
    reviews: [
      { reviewer: 'designer', status: 'Request Changes', comment: 'Replace all remaining colored icons and emojis with thin SVGs or text.' },
      { reviewer: 'designer', status: 'Approved', comment: 'Redesign satisfies the minimalist directives perfectly. Aesthetics look gorgeous.' }
    ],
    timeline: [
      { type: 'commit', user: 'sachin-saroj', text: 'Updated index.css variables and styling tokens', time: 'Jun 10, 2026' },
      { type: 'commit', user: 'sachin-saroj', text: 'Removed emojis from forms and dashboard grids', time: 'Jun 10, 2026' },
      { type: 'review', user: 'designer', text: 'Looks outstanding now. Warm bone canvas is perfect.', time: 'Jun 10, 2026' }
    ]
  }
];

export default function PullRequests() {
  const [selectedPR, setSelectedPR] = useState(null);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Pull Requests</h1>
        <p className="page-subtitle">Manage branches, code reviews, and releases lifecycle.</p>
      </div>

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* PR List */}
        <div style={{ flex: '1 1 500px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem',
            paddingBottom: '0.75rem',
            borderBottom: '1px solid var(--border-color)'
          }}>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)' }}>
              Developer Branches
            </h2>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Total: {mockPRs.length}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {mockPRs.map((pr) => (
              <div
                key={pr.id}
                onClick={() => setSelectedPR(pr)}
                style={{
                  padding: '1.25rem 1.5rem',
                  background: 'var(--bg-secondary)',
                  border: selectedPR?.id === pr.id 
                    ? '1px solid var(--accent-primary)' 
                    : '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                  <h3 style={{
                    fontSize: '0.95rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    lineHeight: '1.4'
                  }}>
                    {pr.title}
                  </h3>
                  <span className={`badge ${pr.badgeClass}`} style={{ flexShrink: 0 }}>
                    {pr.status}
                  </span>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '1rem',
                  marginTop: '0.75rem',
                  fontSize: '0.75rem',
                  color: 'var(--text-secondary)',
                  fontFamily: 'var(--font-mono)'
                }}>
                  <span>PR #{pr.id}</span>
                  <span>by {pr.author}</span>
                  <span>{pr.branch}</span>
                  <span>{pr.date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* PR Details / Code Review Column */}
        <div style={{ flex: '1 1 320px', minWidth: '300px' }}>
          {selectedPR ? (
            <div className="card" style={{ padding: '2rem', position: 'sticky', top: '90px' }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                  Pull Request #{selectedPR.id}
                </span>
                <span className={`badge ${selectedPR.badgeClass}`}>
                  {selectedPR.status}
                </span>
              </div>
              
              <h2 style={{
                fontFamily: 'var(--font-brand)',
                fontSize: '1.75rem',
                fontWeight: 400,
                lineHeight: '1.2',
                color: 'var(--text-primary)',
                marginBottom: '1rem'
              }}>
                {selectedPR.title}
              </h2>
              
              <div style={{ 
                fontSize: '0.8rem', 
                color: 'var(--text-secondary)', 
                marginBottom: '1.5rem',
                borderBottom: '1px solid var(--border-color)',
                paddingBottom: '1rem'
              }}>
                Branch: <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', background: 'var(--bg-primary)', padding: '0.15rem 0.35rem', borderRadius: '4px' }}>{selectedPR.branch}</code>
              </div>

              {/* Stats Block */}
              <div style={{ 
                display: 'flex', 
                gap: '1.5rem', 
                marginBottom: '1.5rem',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.8rem',
                color: 'var(--text-primary)'
              }}>
                <div>
                  <strong>{selectedPR.commits}</strong> commits
                </div>
                <div>
                  <strong>{selectedPR.filesChanged}</strong> files changed
                </div>
              </div>

              {/* Code Reviews */}
              {selectedPR.reviews.length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                  <h4 className="form-label" style={{ fontSize: '0.7rem', marginBottom: '0.75rem' }}>Code Review</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {selectedPR.reviews.map((rev, idx) => (
                      <div key={idx} style={{ 
                        padding: '1rem', 
                        background: 'var(--bg-primary)', 
                        border: '1px solid var(--border-color)',
                        borderRadius: '6px'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                            {rev.reviewer}
                          </span>
                          <span className={`badge ${rev.status === 'Approved' ? 'badge-active' : 'badge-warning'}`} style={{ fontSize: '0.6rem', padding: '0.15rem 0.45rem' }}>
                            {rev.status}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: '1.5' }}>
                          {rev.comment}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Timeline */}
              <div>
                <h4 className="form-label" style={{ fontSize: '0.7rem', marginBottom: '0.75rem' }}>Timeline</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {selectedPR.timeline.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '0.75rem', fontSize: '0.8rem' }}>
                      <div style={{ 
                        fontFamily: 'var(--font-mono)', 
                        color: 'var(--text-tertiary)',
                        width: '75px',
                        flexShrink: 0
                      }}>
                        {item.time}
                      </div>
                      <div style={{ color: 'var(--text-primary)' }}>
                        <strong>{item.user}</strong> {item.type === 'commit' ? 'committed: ' : 'reviewed: '}
                        <span style={{ color: 'var(--text-secondary)' }}>"{item.text}"</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{
              height: '200px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px dashed var(--border-color)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-tertiary)',
              fontSize: '0.85rem'
            }}>
              Select a pull request to inspect files and code reviews
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
