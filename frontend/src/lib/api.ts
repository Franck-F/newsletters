const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ---- Auth ----

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
}

// ---- Subscribers ----

export async function subscribe(email: string, name?: string) {
  const res = await fetch(`${API_BASE}/api/v1/public/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Subscription failed');
  }
  return res.json();
}

export async function confirmSubscription(token: string) {
  const res = await fetch(`${API_BASE}/api/v1/public/confirm-subscription?token=${token}`);
  if (!res.ok) throw new Error('Confirmation failed');
  return res.json();
}

export async function unsubscribe(token: string) {
  const res = await fetch(`${API_BASE}/api/v1/public/unsubscribe?token=${token}`, { method: 'POST' });
  if (!res.ok) throw new Error('Unsubscribe failed');
  return res.json();
}

export async function getSubscribers(jwt: string) {
  const res = await fetch(`${API_BASE}/api/v1/subscribers`, {
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to fetch subscribers');
  return res.json();
}

// ---- Content Items ----

export async function ingestContent(jwt: string) {
  const res = await fetch(`${API_BASE}/api/v1/content-items/ingest`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to trigger ingestion');
  return res.json();
}

export async function getContentItems(jwt: string, params?: Record<string, string>) {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  const res = await fetch(`${API_BASE}/api/v1/content-items${query}`, {
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to fetch content items');
  return res.json();
}

export async function createContentItem(jwt: string, data: object) {
  const res = await fetch(`${API_BASE}/api/v1/content-items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${jwt}` },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create content item');
  return res.json();
}

export async function deleteContentItem(jwt: string, id: number) {
  const res = await fetch(`${API_BASE}/api/v1/content-items/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to delete content item');
}

// ---- Newsletters ----

export async function getNewsletters(jwt: string) {
  const res = await fetch(`${API_BASE}/api/v1/newsletters`, {
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to fetch newsletters');
  return res.json();
}

export async function getNewsletter(jwt: string, id: number) {
  const res = await fetch(`${API_BASE}/api/v1/newsletters/${id}`, {
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) throw new Error('Failed to fetch newsletter');
  return res.json();
}

export async function generateNewsletter(jwt: string, options?: object) {
  const res = await fetch(`${API_BASE}/api/v1/newsletters/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${jwt}` },
    body: JSON.stringify(options || { max_items: 5 }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Generation failed');
  }
  return res.json();
}

export async function updateNewsletter(jwt: string, id: number, data: object) {
  const res = await fetch(`${API_BASE}/api/v1/newsletters/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${jwt}` },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update newsletter');
  return res.json();
}

export async function sendNewsletter(jwt: string, id: number) {
  const res = await fetch(`${API_BASE}/api/v1/newsletters/${id}/send`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${jwt}` },
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Send failed');
  }
  return res.json();
}
