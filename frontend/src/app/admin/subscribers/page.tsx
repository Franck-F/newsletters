'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSubscribers } from '@/lib/api';

export default function SubscribersPage() {
  const router = useRouter();
  const [subscribers, setSubscribers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const jwt = localStorage.getItem('jwt');
    if (!jwt) { router.push('/admin/login'); return; }
    getSubscribers(jwt)
      .then(data => { setSubscribers(data); setLoading(false); })
      .catch(() => router.push('/admin/login'));
  }, [router]);

  const filtered = filter === 'all' ? subscribers : subscribers.filter((s: any) => s.status === filter);

  if (loading) return <div style={{ color: 'var(--text-muted)' }}>Loading…</div>;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 4px' }}>Subscribers</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: 14 }}>{subscribers.length} total</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['all', 'confirmed', 'pending_confirmation', 'inactive'].map(f => (
            <button key={f} id={`filter-${f}`} className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: 12, background: filter === f ? 'var(--border)' : '' }} onClick={() => setFilter(f)}>
              {f === 'all' ? 'All' : f === 'pending_confirmation' ? 'Pending' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        {filtered.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>No subscribers found.</p>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Email</th><th>Name</th><th>Status</th><th>Signed up</th></tr>
            </thead>
            <tbody>
              {filtered.map((sub: any) => (
                <tr key={sub.id}>
                  <td style={{ fontWeight: 500 }}>{sub.email}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{sub.name || '—'}</td>
                  <td>
                    <span className={`badge badge-${sub.status === 'confirmed' ? 'active' : sub.status === 'pending_confirmation' ? 'pending' : 'inactive'}`}>
                      {sub.status === 'pending_confirmation' ? 'Pending' : sub.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{new Date(sub.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
