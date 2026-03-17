'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getNewsletters, generateNewsletter } from '@/lib/api';
import Link from 'next/link';

export default function NewslettersPage() {
  const router = useRouter();
  const [newsletters, setNewsletters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  function getJwt() {
    const jwt = localStorage.getItem('jwt');
    if (!jwt) { router.push('/admin/login'); throw new Error('No JWT'); }
    return jwt;
  }

  async function load() {
    try {
      const data = await getNewsletters(getJwt());
      setNewsletters(data);
    } catch { router.push('/admin/login'); }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const result = await generateNewsletter(getJwt(), { max_items: 5 });
      await load();
      router.push(`/admin/newsletters/${result.newsletter_id}`);
    } catch (err: any) {
      alert(err.message || 'Generation failed. Make sure your Gemini API key is configured.');
    }
    setGenerating(false);
  }

  if (loading) return <div style={{ color: 'var(--text-muted)' }}>Loading…</div>;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 4px' }}>Newsletters</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: 14 }}>{newsletters.length} total</p>
        </div>
        <button id="generate-btn" className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
          {generating ? '⏳ Generating…' : '✨ Generate New'}
        </button>
      </div>

      <div className="card">
        {newsletters.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>No newsletters yet. Click &quot;Generate New&quot; to create your first one.</p>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Title</th><th>Status</th><th>Created</th><th>Sent</th><th></th></tr>
            </thead>
            <tbody>
              {newsletters.map((nl: any) => (
                <tr key={nl.id}>
                  <td style={{ fontWeight: 500 }}>{nl.title}</td>
                  <td><span className={`badge badge-${nl.status}`}>{nl.status}</span></td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{new Date(nl.created_at).toLocaleDateString()}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{nl.sent_at ? new Date(nl.sent_at).toLocaleDateString() : '—'}</td>
                  <td>
                    <Link id={`view-nl-${nl.id}`} href={`/admin/newsletters/${nl.id}`} className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: 12 }}>Edit / Send</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
