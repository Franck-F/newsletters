'use client';

import { useState } from 'react';
import { subscribe } from '@/lib/api';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');
    try {
      await subscribe(email, name);
      setStatus('success');
      setMessage('Check your inbox to confirm your subscription!');
    } catch (err: any) {
      setStatus('error');
      setMessage(err.message || 'Something went wrong. Try again.');
    }
  }

  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', background: 'var(--bg)', position: 'relative', overflow: 'hidden' }}>
      {/* Background glow */}
      <div style={{ position: 'absolute', top: '-150px', left: '50%', transform: 'translateX(-50%)', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(124,58,237,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '-100px', right: '-100px', width: '400px', height: '400px', background: 'radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ maxWidth: '520px', width: '100%', textAlign: 'center', position: 'relative', zIndex: 1 }}>
        {/* Badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', background: 'rgba(124,58,237,0.1)', border: '1px solid rgba(124,58,237,0.3)', borderRadius: 999, fontSize: 13, color: 'rgba(167,139,250,0.9)', marginBottom: 28, fontWeight: 500 }}>
          <span>✨</span> Weekly curated insights
        </div>

        <h1 style={{ fontSize: 52, fontWeight: 800, lineHeight: 1.1, margin: '0 0 16px', background: 'linear-gradient(135deg, #e2e8f0 30%, rgba(167,139,250,0.8))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Stay ahead of<br />the curve
        </h1>

        <p style={{ fontSize: 17, color: 'var(--text-muted)', margin: '0 0 40px', lineHeight: 1.6 }}>
          Get the best articles, tools, and ideas delivered straight to your inbox every week — curated and summarised by AI.
        </p>

        {status === 'success' ? (
          <div style={{ padding: '24px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 12, color: '#6ee7b7' }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>🎉</div>
            <p style={{ margin: 0, fontWeight: 600 }}>{message}</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <input
              id="name-input"
              type="text"
              placeholder="Your name (optional)"
              value={name}
              onChange={e => setName(e.target.value)}
              className="input"
              style={{ textAlign: 'center' }}
            />
            <input
              id="email-input"
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="input"
              style={{ textAlign: 'center' }}
            />
            {status === 'error' && (
              <p style={{ color: 'var(--danger)', margin: 0, fontSize: 13 }}>{message}</p>
            )}
            <button id="subscribe-btn" type="submit" className="btn btn-primary" disabled={status === 'loading'} style={{ padding: '14px 28px', fontSize: 16 }}>
              {status === 'loading' ? 'Subscribing…' : 'Subscribe for free →'}
            </button>
          </form>
        )}

        <p style={{ marginTop: 20, fontSize: 12, color: 'var(--text-muted)' }}>
          No spam. Unsubscribe anytime. 100% free.
        </p>

        {/* Mini feature pills */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 48, flexWrap: 'wrap' }}>
          {['AI-curated content', 'Weekly digest', 'One-click unsubscribe'].map(f => (
            <span key={f} style={{ padding: '6px 14px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 999, fontSize: 12, color: 'var(--text-muted)' }}>{f}</span>
          ))}
        </div>
      </div>
    </main>
  );
}
