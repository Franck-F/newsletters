'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const navItems = [
  { href: '/admin', label: 'Dashboard', icon: '📊' },
  { href: '/admin/content', label: 'Content', icon: '📰' },
  { href: '/admin/newsletters', label: 'Newsletters', icon: '✉️' },
  { href: '/admin/subscribers', label: 'Subscribers', icon: '👥' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    localStorage.removeItem('jwt');
    router.push('/admin/login');
  }

  if (pathname === '/admin/login') return <>{children}</>;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside className="sidebar">
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text)', marginBottom: 4 }}>📬 Newsletter</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Admin Dashboard</div>
        </div>
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`sidebar-link ${pathname === item.href ? 'active' : ''}`}
          >
            <span>{item.icon}</span> {item.label}
          </Link>
        ))}
        <div style={{ marginTop: 'auto', paddingTop: 16 }}>
          <button id="logout-btn" className="btn btn-secondary" style={{ width: '100%', fontSize: 13 }} onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto', background: 'var(--bg)' }}>
        {children}
      </main>
    </div>
  );
}
