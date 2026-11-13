import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Shield,
  LayoutDashboard,
  MessageSquare,
  Link as LinkIcon,
  History,
  X,
} from 'lucide-react';
import { useScans } from '../../context/ScanContext';

interface SidebarProps {
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onCloseMobile }) => {
  const { health } = useScans();
  const isHealthy = health?.status === 'healthy';

  const navItems = [
    { name: 'Dashboard',    path: '/',             icon: LayoutDashboard },
    { name: 'Scan Message', path: '/scan-message', icon: MessageSquare },
    { name: 'Scan URL',     path: '/scan-url',     icon: LinkIcon },
    { name: 'Scan History', path: '/history',      icon: History },
  ];

  const inner = (
    <div className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <Shield size={20} strokeWidth={2.2} />
        </div>
        <div>
          <div className="sidebar-brand-name">AI Threat Shield</div>
          <div className="sidebar-brand-sub">Intelligent Threat Detection</div>
        </div>

        {/* Mobile close */}
        <button
          onClick={onCloseMobile}
          style={{
            display: 'none',
            marginLeft: 'auto',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--c-text-muted)',
            padding: 4,
            borderRadius: 6,
          }}
          className="mobile-close"
          aria-label="Close menu"
        >
          <X size={18} />
        </button>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {navItems.map(({ name, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            onClick={onCloseMobile}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={17} strokeWidth={2} />
            <span>{name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer status */}
      <div className="sidebar-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 4 }}>
          <span
            className="status-dot"
            style={{ background: isHealthy ? 'var(--c-benign)' : 'var(--c-spam)' }}
          />
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-text-main)' }}>
            {isHealthy ? 'Backend Connected' : 'Connecting…'}
          </span>
        </div>
        <p style={{ fontSize: 11, color: 'var(--c-text-muted)' }}>ML-Powered Detection · XGBoost</p>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop */}
      <div style={{ display: 'none' }} className="desktop-sidebar-wrapper">
        {inner}
      </div>
      {/* Always show on md+ via CSS */}
      <div className="hidden md:block shrink-0">
        {inner}
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          style={{
            position: 'fixed', inset: 0, zIndex: 50,
            display: 'flex',
          }}
          className="md:hidden"
        >
          <div
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.35)' }}
            onClick={onCloseMobile}
          />
          <div style={{ position: 'relative', zIndex: 10, boxShadow: '4px 0 20px rgba(0,0,0,.15)' }}>
            {inner}
          </div>
        </div>
      )}
    </>
  );
};
