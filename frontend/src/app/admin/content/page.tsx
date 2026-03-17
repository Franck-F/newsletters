'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getContentItems, createContentItem, deleteContentItem, ingestContent } from '@/lib/api';

export default function ContentPage() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', url: '', summary: '', source: '', tags: '' });
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);

  function getJwt() {
    const jwt = localStorage.getItem('jwt');
    if (!jwt) { router.push('/admin/login'); throw new Error('No JWT'); }
    return jwt;
  }

  async function load() {
    try {
      const data = await getContentItems(getJwt());
      setItems(data);
    } catch { router.push('/admin/login'); }
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function handleSync() {
    setSyncing(true);
    try {
      const res = await ingestContent(getJwt());
      alert(`Sync complete! Added ${res.items_added.rss} from RSS and ${res.items_added.gmail} from Gmail.`);
      await load();
    } catch (err: any) {
      alert(err.message);
    }
    setSyncing(false);
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await createContentItem(getJwt(), { ...form, tags: form.tags.split(',').map(t => t.trim()).filter(Boolean), type: 'manual' });
      setForm({ title: '', url: '', summary: '', source: '', tags: '' });
      setShowForm(false);
      await load();
    } catch (err: any) { alert(err.message); }
    setSaving(false);
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this content item?')) return;
    try { await deleteContentItem(getJwt(), id); await load(); } catch (err: any) { alert(err.message); }
  }

  if (loading) return <div style={{ color: 'var(--text-muted)' }}>Loading…</div>;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, margin: '0 0 4px' }}>Content Items</h1>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: 14 }}>{items.length} items collected</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button id="sync-content-btn" className="btn btn-secondary" onClick={handleSync} disabled={syncing}>
            {syncing ? '⌛ Syncing…' : '🔄 Sync Content'}
          </button>
          <button id="add-content-btn" className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : '➕ Add Item'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, margin: '0 0 16px' }}>Add Content Item</h2>
          <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div><label className="label">Title *</label><input className="input" value={form.title} onChange={e => setForm({...form, title: e.target.value})} required /></div>
            <div><label className="label">URL *</label><input className="input" type="url" value={form.url} onChange={e => setForm({...form, url: e.target.value})} required /></div>
            <div><label className="label">Source</label><input className="input" value={form.source} onChange={e => setForm({...form, source: e.target.value})} placeholder="e.g. TechCrunch" /></div>
            <div><label className="label">Tags (comma-separated)</label><input className="input" value={form.tags} onChange={e => setForm({...form, tags: e.target.value})} placeholder="ai, tech" /></div>
            <div style={{ gridColumn: '1 / -1' }}><label className="label">Summary</label><textarea className="input" style={{ minHeight: 80, resize: 'vertical' }} value={form.summary} onChange={e => setForm({...form, summary: e.target.value})} /></div>
            <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end' }}>
              <button id="save-content-btn" type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        {items.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>No content items yet. Add one above or connect a feed.</p>
        ) : (
          <table className="table">
            <thead>
              <tr><th>Title</th><th>Source</th><th>Type</th><th>Tags</th><th>Date</th><th></th></tr>
            </thead>
            <tbody>
              {items.map((item: any) => (
                <tr key={item.id}>
                  <td style={{ fontWeight: 500, maxWidth: 240 }}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text)', textDecoration: 'none' }}>{item.title}</a>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{item.source || '—'}</td>
                  <td><span className="badge" style={{ background: 'rgba(6,182,212,0.1)', color: 'var(--accent-2)' }}>{item.type}</span></td>
                  <td style={{ fontSize: 12, maxWidth: 180 }}>
                    {(item.tags || []).map((t: string) => (
                      <span key={t} style={{ marginRight: 4, padding: '1px 8px', background: 'var(--surface-2)', borderRadius: 999, color: 'var(--text-muted)' }}>{t}</span>
                    ))}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>{new Date(item.collected_at).toLocaleDateString()}</td>
                  <td>
                    <button id={`delete-${item.id}`} className="btn btn-danger" style={{ padding: '4px 10px', fontSize: 12 }} onClick={() => handleDelete(item.id)}>Delete</button>
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
