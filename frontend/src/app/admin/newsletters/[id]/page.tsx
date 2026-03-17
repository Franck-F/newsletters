'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { getNewsletter, updateNewsletter, sendNewsletter } from '@/lib/api';

export default function NewsletterEditorPage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);
  const [newsletter, setNewsletter] = useState<any>(null);
  const [title, setTitle] = useState('');
  const [htmlBody, setHtmlBody] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [showSendConfirm, setShowSendConfirm] = useState(false);

  function getJwt() {
    const jwt = localStorage.getItem('jwt');
    if (!jwt) { router.push('/admin/login'); throw new Error('No JWT'); }
    return jwt;
  }

  useEffect(() => {
    getNewsletter(getJwt(), id)
      .then(data => {
        setNewsletter(data);
        setTitle(data.title);
        setHtmlBody(data.html_body || '');
        setLoading(false);
      })
      .catch(() => router.push('/admin/login'));
  }, [id]);

  async function handleSave() {
    setSaving(true);
    try { await updateNewsletter(getJwt(), id, { title, html_body: htmlBody }); alert('Saved!'); }
    catch (err: any) { alert(err.message); }
    setSaving(false);
  }

  async function handleSend() {
    setSending(true);
    try {
      await sendNewsletter(getJwt(), id);
      setNewsletter({ ...newsletter, status: 'sent' });
      setShowSendConfirm(false);
      alert('Newsletter sent successfully via Brevo!');
    } catch (err: any) { alert(err.message); }
    setSending(false);
  }

  if (loading) return <div style={{ color: 'var(--text-muted)' }}>Loading…</div>;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <button id="back-btn" className="btn btn-secondary" style={{ fontSize: 12, padding: '4px 12px', marginBottom: 12 }} onClick={() => router.back()}>← Back</button>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>Edit Newsletter</h1>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <span className={`badge badge-${newsletter?.status}`}>{newsletter?.status}</span>
          <button id="save-btn" className="btn btn-secondary" onClick={handleSave} disabled={saving}>{saving ? 'Saving…' : 'Save Draft'}</button>
          {newsletter?.status !== 'sent' && (
            <button id="send-btn" className="btn btn-primary" onClick={() => setShowSendConfirm(true)}>✉️ Send</button>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Editor */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card">
            <label className="label">Subject / Title</label>
            <input className="input" value={title} onChange={e => setTitle(e.target.value)} />
          </div>
          <div className="card" style={{ flex: 1 }}>
            <label className="label">HTML Body</label>
            <textarea
              id="html-editor"
              className="input"
              value={htmlBody}
              onChange={e => setHtmlBody(e.target.value)}
              style={{ minHeight: 400, fontFamily: 'monospace', fontSize: 12, resize: 'vertical' }}
            />
          </div>
        </div>

        {/* Live Preview */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', fontSize: 12, color: 'var(--text-muted)', fontWeight: 600 }}>PREVIEW</div>
          <iframe
            id="preview-iframe"
            srcDoc={htmlBody}
            style={{ width: '100%', height: '520px', border: 'none', background: 'white' }}
            title="Newsletter Preview"
          />
        </div>
      </div>

      {/* Send Confirmation Modal */}
      {showSendConfirm && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ maxWidth: 400, width: '90%', textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🚀</div>
            <h2 style={{ margin: '0 0 8px', fontSize: 20 }}>Send to all subscribers?</h2>
            <p style={{ color: 'var(--text-muted)', margin: '0 0 24px', fontSize: 14 }}>This will immediately send the newsletter to all confirmed subscribers via Brevo. This action cannot be undone.</p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button id="cancel-send-btn" className="btn btn-secondary" onClick={() => setShowSendConfirm(false)}>Cancel</button>
              <button id="confirm-send-btn" className="btn btn-primary" onClick={handleSend} disabled={sending}>{sending ? 'Sending…' : 'Yes, Send!'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
