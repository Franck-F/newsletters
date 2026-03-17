'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { confirmSubscription } from '@/lib/api';
import { Suspense } from 'react';

function ConfirmContent() {
  const params = useSearchParams();
  const token = params.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No confirmation token found.');
      return;
    }
    confirmSubscription(token)
      .then(() => {
        setStatus('success');
        setMessage("You're confirmed! Welcome aboard 🎉");
      })
      .catch((err: any) => {
        setStatus('error');
        setMessage(err.message || 'This link is invalid or expired.');
      });
  }, [token]);

  return (
    <main style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, background: 'var(--bg)' }}>
      <div className="card" style={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
        {status === 'loading' && (
          <>
            <div style={{ fontSize: 40, marginBottom: 16 }}>⏳</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px' }}>Confirming your subscription…</h1>
            <p style={{ color: 'var(--text-muted)', margin: 0 }}>Just a moment please.</p>
          </>
        )}
        {status === 'success' && (
          <>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🎉</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px' }}>You&#39;re in!</h1>
            <p style={{ color: 'var(--text-muted)', margin: '0 0 24px' }}>{message}</p>
            <a href="/" className="btn btn-primary">Back to home</a>
          </>
        )}
        {status === 'error' && (
          <>
            <div style={{ fontSize: 48, marginBottom: 16 }}>❌</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px' }}>Oops!</h1>
            <p style={{ color: 'var(--text-muted)', margin: '0 0 24px' }}>{message}</p>
            <a href="/" className="btn btn-secondary">Go back</a>
          </>
        )}
      </div>
    </main>
  );
}

export default function ConfirmPage() {
  return (
    <Suspense>
      <ConfirmContent />
    </Suspense>
  );
}
