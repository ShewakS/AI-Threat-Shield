import React from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, RefreshCw } from 'lucide-react';
import { useScans } from '../../context/ScanContext';

interface HeaderProps {
  onOpenMobile: () => void;
}

const PAGE_META: Record<string, { title: string; description: string }> = {
  '/':             { title: 'Dashboard',     description: 'Overview of threat detection activity and quick scan actions.' },
  '/scan-message': { title: 'Scan Message',  description: 'Analyse SMS messages, emails, and suspicious text with ML.' },
  '/scan-url':     { title: 'Scan URL',      description: 'Inspect URL structure and indicators for potential phishing threats.' },
  '/history':      { title: 'Scan History',  description: 'Complete record of all processed threat evaluations.' },
};

export const Header: React.FC<HeaderProps> = ({ onOpenMobile }) => {
  const { pathname } = useLocation();
  const { health, loadingHealth, refreshHealth } = useScans();
  const isHealthy = health?.status === 'healthy';
  const { title, description } = PAGE_META[pathname] ?? { title: 'AI Threat Shield', description: '' };

  return (
    <header className="page-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* Mobile hamburger */}
        <button
          onClick={onOpenMobile}
          className="md:hidden"
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--c-text-muted)', padding: '6px 8px', borderRadius: 6,
          }}
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <div className="header-title">{title}</div>
          {description && <div className="header-sub">{description}</div>}
        </div>
      </div>

      {/* Engine status pill */}
      <div
        style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '6px 12px',
          background: 'var(--c-bg-surface)',
          border: '1px solid var(--c-border)',
          borderRadius: 8,
          fontSize: 13,
        }}
      >
        <span
          className="status-dot"
          style={{ background: isHealthy ? 'var(--c-benign)' : 'var(--c-spam)' }}
        />
        <span style={{ fontWeight: 500, color: 'var(--c-text-main)' }}>
          {health?.model_name ?? 'XGBoost'}
        </span>
        <span style={{ color: 'var(--c-text-muted)' }}>
          ({isHealthy ? 'Online' : 'Connecting'})
        </span>
        <button
          onClick={() => refreshHealth()}
          disabled={loadingHealth}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--c-text-muted)', padding: 2, borderRadius: 4, display: 'flex',
          }}
          title="Refresh health"
        >
          <RefreshCw size={12} className={loadingHealth ? 'animate-spin' : ''} />
        </button>
      </div>
    </header>
  );
};
