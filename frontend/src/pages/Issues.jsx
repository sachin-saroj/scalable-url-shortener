import { useState } from 'react';

const mockIssues = [
  {
    id: '101',
    title: 'AsyncSession closed during BackgroundTasks analytics recording',
    status: 'Closed',
    badgeClass: 'badge-active',
    date: 'Jun 8, 2026',
    author: 'sachin-saroj',
    comments: 3,
    description: 'The request-scoped AsyncSession is passed into a background task after the request completes, resulting in closed session errors during analytics resolution. We need to create a fresh session inside the background task using the database session factory.',
    discussion: [
      { user: 'sachin-saroj', date: 'Jun 8, 2026', text: 'Verified the issue in redirect.py. The AsyncSession gets disposed right when the API route returns its response.' },
      { user: 'reviewer', date: 'Jun 8, 2026', text: 'We should ensure that we spawn a fresh transaction inside the background task itself. Let’s refactor the background handler.' }
    ]
  },
  {
    id: '102',
    title: 'Blocking DNS resolution halts Celery thread pool in validator path',
    status: 'Closed',
    badgeClass: 'badge-active',
    date: 'Jun 8, 2026',
    author: 'sachin-saroj',
    comments: 2,
    description: 'Standard socket DNS resolution blocks the event loop thread in validators.py. Refactoring to use an asynchronous DNS resolver (e.g. dnspython) prevents request timeouts under heavy load.',
    discussion: [
      { user: 'sachin-saroj', date: 'Jun 8, 2026', text: 'Swapped standard socket resolver with dns.asyncresolver from dnspython package. Tests pass.' }
    ]
  },
  {
    id: '103',
    title: 'Dashboard statistics incorrect on paginated URLs list',
    status: 'Closed',
    badgeClass: 'badge-active',
    date: 'Jun 9, 2026',
    author: 'sachin-saroj',
    comments: 4,
    description: 'Dashboard calculations (Active Links, Total Clicks, Average Clicks) only compute against currently loaded paginated URLs instead of the entire dataset. We need a dedicated stats API endpoint on the backend.',
    discussion: [
      { user: 'sachin-saroj', date: 'Jun 9, 2026', text: 'Creating `/api/v1/urls/stats` to run backend SQL aggregations. Will fetch stats on mount.' }
    ]
  },
  {
    id: '104',
    title: 'Redundant database lookup on Redis cache hits in redirect resolver',
    status: 'Closed',
    badgeClass: 'badge-active',
    date: 'Jun 9, 2026',
    author: 'sachin-saroj',
    comments: 3,
    description: 'URLService.get_original_url() performs a redundant database query even when cache hit is successful in Redis. We should store complete redirect metadata (is_active, expires_at, id) inside the cached JSON.',
    discussion: [
      { user: 'sachin-saroj', date: 'Jun 9, 2026', text: 'Caching complete url metadata. Re-routing redirect resolution to check dates completely in Redis.' }
    ]
  },
  {
    id: '105',
    title: 'SameSite=None cookie compatibility across localhost and production HTTPS',
    status: 'Closed',
    badgeClass: 'badge-active',
    date: 'Jun 8, 2026',
    author: 'sachin-saroj',
    comments: 1,
    description: 'Cookie auth setup requires flexible SameSite attributes depending on environment. We need configuration rules in environment settings to enforce SameSite=Lax on localhost and SameSite=None on HTTPS.',
    discussion: [
      { user: 'sachin-saroj', date: 'Jun 8, 2026', text: 'Configured environment cookie rules. Works locally and on deployment environments.' }
    ]
  },
  {
    id: '106',
    title: 'Add dark mode ambient color toggle to minimalist layout',
    status: 'Open',
    badgeClass: 'badge-custom',
    date: 'Jun 10, 2026',
    author: 'sachin-saroj',
    comments: 0,
    description: 'Provide an editorial style dark theme switch utilizing CSS custom properties for bone-black conversion.',
    discussion: []
  }
];

export default function Issues() {
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [filterStatus, setFilterStatus] = useState('All');

  const filteredIssues = mockIssues.filter(
    (issue) => filterStatus === 'All' || issue.status === filterStatus
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Issues</h1>
        <p className="page-subtitle">Track and debug architectural bottlenecks and feature proposals.</p>
      </div>

      <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
        {/* Issues List */}
        <div style={{ flex: '1 1 500px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '1.5rem',
            paddingBottom: '0.75rem',
            borderBottom: '1px solid var(--border-color)'
          }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['All', 'Open', 'Closed'].map((status) => (
                <button
                  key={status}
                  className={`btn btn-secondary btn-sm ${filterStatus === status ? 'active' : ''}`}
                  onClick={() => setFilterStatus(status)}
                  style={{
                    borderRadius: '4px',
                    padding: '0.25rem 0.6rem',
                    textTransform: 'none',
                    fontWeight: 500,
                    background: filterStatus === status ? 'var(--accent-primary)' : '#ffffff',
                    color: filterStatus === status ? '#ffffff' : 'var(--text-primary)',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  {status}
                </button>
              ))}
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Total: {filteredIssues.length}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {filteredIssues.map((issue) => (
              <div
                key={issue.id}
                onClick={() => setSelectedIssue(issue)}
                style={{
                  padding: '1.25rem 1.5rem',
                  background: 'var(--bg-secondary)',
                  border: selectedIssue?.id === issue.id 
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
                    {issue.title}
                  </h3>
                  <span className={`badge ${issue.badgeClass}`} style={{ flexShrink: 0 }}>
                    {issue.status}
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
                  <span>#{issue.id}</span>
                  <span>opened by {issue.author}</span>
                  <span>{issue.date}</span>
                  {issue.comments > 0 && <span>{issue.comments} comments</span>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Details View */}
        <div style={{ flex: '1 1 320px', minWidth: '300px' }}>
          {selectedIssue ? (
            <div className="card" style={{ padding: '2rem', position: 'sticky', top: '90px' }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                  Issue #{selectedIssue.id}
                </span>
                <span className={`badge ${selectedIssue.badgeClass}`}>
                  {selectedIssue.status}
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
                {selectedIssue.title}
              </h2>
              <div style={{ 
                fontSize: '0.8rem', 
                color: 'var(--text-secondary)', 
                marginBottom: '1.5rem',
                borderBottom: '1px solid var(--border-color)',
                paddingBottom: '1rem'
              }}>
                Opened by <strong>{selectedIssue.author}</strong> on {selectedIssue.date}
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h4 className="form-label" style={{ fontSize: '0.7rem' }}>Description</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: '1.6' }}>
                  {selectedIssue.description}
                </p>
              </div>

              {selectedIssue.discussion.length > 0 && (
                <div>
                  <h4 className="form-label" style={{ fontSize: '0.7rem', marginBottom: '0.75rem' }}>Discussion</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {selectedIssue.discussion.map((disc, idx) => (
                      <div key={idx} style={{ 
                        padding: '1rem', 
                        background: 'var(--bg-primary)', 
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)'
                      }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          marginBottom: '0.35rem',
                          fontSize: '0.75rem',
                          fontFamily: 'var(--font-mono)',
                          color: 'var(--text-secondary)'
                        }}>
                          <strong>{disc.user}</strong>
                          <span>{disc.date}</span>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: '1.5' }}>
                          {disc.text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
              Select an issue from the list to view discussions
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
