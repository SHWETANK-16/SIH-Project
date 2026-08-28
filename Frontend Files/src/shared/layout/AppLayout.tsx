import { Bell, ChevronLeft, ChevronRight, LogOut, Menu, Search, Settings, ShieldCheck, UserRound } from 'lucide-react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { APP_CONFIG } from '../../app/config';
import { useAuthContext } from '../../app/providers';
import { LogoMark } from '../components/LogoMark';
import { PageTransition } from '../components/PageTransition';

const navigation = [
  ['Dashboard', '/dashboard', '▦'],
  ['Transactions', '/transactions', '↔'],
  ['Investigations', '/investigations/INV-2026-041', '◎'],
  ['Entities', '/entities/ENT-102', '◌'],
  ['Alerts', '/alerts', '⚠'],
  ['Reports', '/reports', '▤'],
] as const;

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, signOut } = useAuthContext();
  const navigate = useNavigate();
  const closeMobile = () => setMobileOpen(false);

  function logout() { signOut(); navigate('/login'); }

  return <div className={`app-shell ${collapsed ? 'sidebar-collapsed' : ''}`}>
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`} aria-label="Main navigation">
      <div className="sidebar-top"><LogoMark compact={collapsed} /><button className="icon-button collapse-control" onClick={() => setCollapsed((value) => !value)} aria-label="Toggle sidebar">{collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}</button></div>
      {!collapsed && <p className="sidebar-project">{APP_CONFIG.projectName}</p>}
      <nav className="nav-list">{navigation.map(([label, path, icon]) => <NavLink key={label} to={path} onClick={closeMobile} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}><span className="nav-icon">{icon}</span><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-bottom">
        <button className="nav-link plain-button"><Settings size={17} /><span>Settings</span></button>
        <div className="user-card"><div className="avatar">{user?.initials ?? 'IO'}</div>{!collapsed && <div><strong>{user?.name ?? 'Investigator'}</strong><small>{user?.role ?? 'Officer'}</small></div>}</div>
        <button className="nav-link plain-button logout" onClick={logout}><LogOut size={17} /><span>Logout</span></button>
      </div>
    </aside>
    {mobileOpen && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={closeMobile} />}
    <section className="app-content">
      <header className="topbar"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div className="topbar-search"><Search size={16} /><input aria-label="Global search" placeholder="Search cases, entities, transactions..." /></div><div className="topbar-actions"><button className="icon-button" aria-label="Notifications"><Bell size={18} /><i /></button><div className="system-status"><ShieldCheck size={15} /> <span>System secure</span></div><button className="avatar profile-button" aria-label="Open user profile"><UserRound size={16} /></button></div></header>
      <PageTransition><Outlet /></PageTransition>
    </section>
  </div>;
}
