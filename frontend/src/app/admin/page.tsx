'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getNewsletters, getContentItems, getSubscribers } from '@/lib/api';
import Link from 'next/link';

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState({ newsletters: 0, content: 0, subscribers: 0 });
  const [recentNewsletters, setRecentNewsletters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const jwt = localStorage.getItem('jwt');
    if (!jwt) { router.push('/admin/login'); return; }
    Promise.all([
      getNewsletters(jwt),
      getContentItems(jwt),
      getSubscribers(jwt),
    ]).then(([nl, ct, subs]) => {
      setStats({ newsletters: nl.length, content: ct.length, subscribers: subs.length });
      setRecentNewsletters(nl.slice(0, 5));
      setLoading(false);
    }).catch(() => { router.push('/admin/login'); });
  }, [router]);

  if (loading) return <div style={{ color: 'var(--text-muted)' }}>Loading…</div>;

  const statCards = [
    { label: 'Newsletters', value: stats.newsletters, icon: '✉️', color: 'var(--accent)' },
    { label: 'Content Items', value: stats.content, icon: '📰', color: 'var(--accent-2)' },
    { label: 'Subscribers', value: stats.subscribers, icon: '👥', color: '#10b981' },
  ];

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 8px' }}>Dashboard</h1>
      <p style={{ color: 'var(--text-muted)', margin: '0 0 32px', fontSize: 14 }}>Welcome back. Here&#39;s what&#39;s happening.</p>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 40 }}>
        {statCards.map(s => (
          <div key={s.label} className="card" style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ fontSize: 32, width: 56, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', background: `${s.color}18`, borderRadius: 12 }}>{s.icon}</div>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700 }}>{s.value}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 40 }}>
        <Link id="action-generate" href="/admin/newsletters" className="btn btn-primary">✨ Generate Newsletter</Link>
        <Link id="action-add-content" href="/admin/content" className="btn btn-secondary">➕ Add Content</Link>
      </div>

      {/* Recent newsletters */}
      <div className="card">
        <h2 style={{ fontSize: 16, fontWeight: 600, margin: '0 0 16px' }}>Recent Newsletters</h2>
        {recentNewsletters.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>No newsletters yet. Generate your first one above.</p>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Title</th><th>Status</th><th>Created</th><th></th></tr>
            </thead>
            <tbody>
              {recentNewsletters.map((nl: any) => (
                <tr key={nl.id}>
                  <td style={{ fontWeight: 500 }}>{nl.title}</td>
                  <td><span className={`badge badge-${nl.status}`}>{nl.status}</span></td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{new Date(nl.created_at).toLocaleDateString()}</td>
                  <td><Link href={`/admin/newsletters/${nl.id}`} style={{ color: 'var(--accent)', fontSize: 13, fontWeight: 500 }}>View →</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
