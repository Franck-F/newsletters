'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { unsubscribe } from '@/lib/api';
import { Suspense } from 'react';

function UnsubscribeContent() {
  const params = useSearchParams();
  const token = params.get('token');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  async function handleUnsubscribe() {
    if (!token) {
      setStatus('error');
      setMessage('No unsubscribe token found.');
      return;
    }
    setStatus('loading');
    try {
      await unsubscribe(token);
      setStatus('success');
      setMessage("You've been unsubscribed. Sorry to see you go!");
    } catch (err: any) {
      setStatus('error');
      setMessage(err.message || 'This link is invalid or expired.');
    }
  }

  return (
    <main style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, background: 'var(--bg)' }}>
      <div className="card" style={{ maxWidth: 440, width: '100%', textAlign: 'center' }}>
        {status === 'success' ? (
          <>
            <div style={{ fontSize: 48, marginBottom: 16 }}>👋</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px' }}>Unsubscribed</h1>
            <p style={{ color: 'var(--text-muted)', margin: '0 0 24px' }}>{message}</p>
            <a href="/" className="btn btn-secondary">Go back home</a>
          </>
        ) : (
          <>
            <div style={{ fontSize: 48, marginBottom: 16 }}>😢</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px' }}>Leaving already?</h1>
            <p style={{ color: 'var(--text-muted)', margin: '0 0 24px' }}>Click below to unsubscribe. You won&#39;t receive any more emails from us.</p>
            {status === 'error' && <p style={{ color: 'var(--danger)', marginBottom: 16, fontSize: 13 }}>{message}</p>}
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <a href="/" className="btn btn-secondary">Never mind</a>
              <button id="unsubscribe-btn" className="btn btn-danger" onClick={handleUnsubscribe} disabled={status === 'loading'}>
                {status === 'loading' ? 'Unsubscribing…' : 'Unsubscribe'}
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}

export default function UnsubscribePage() {
  return (
    <Suspense>
      <UnsubscribeContent />
    </Suspense>
  );
}
