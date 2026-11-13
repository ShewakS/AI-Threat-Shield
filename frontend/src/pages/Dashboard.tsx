import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  MessageSquare,
  Link as LinkIcon,
  ArrowRight,
  Eye,
  Inbox,
} from 'lucide-react';
import { useScans } from '../context/ScanContext';

/* ── helper ── */
const StatCard: React.FC<{
  variant: 'total' | 'benign' | 'spam' | 'phish';
  label: string;
  value: number;
  sub: string;
  icon: React.ReactNode;
}> = ({ variant, label, value, sub, icon }) => {
  const iconBg: Record<string, string> = {
    total:  '#F1F5F9',
    benign: 'var(--c-benign-lt)',
    spam:   'var(--c-spam-lt)',
    phish:  'var(--c-phishing-lt)',
  };
  const valColor: Record<string, string> = {
    total:  'var(--c-text-main)',
    benign: 'var(--c-benign)',
    spam:   'var(--c-spam)',
    phish:  'var(--c-phishing)',
  };

  return (
    <div className={`stat-card stat-card--${variant}`}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', marginBottom: 12 }}>
            {label}
          </p>
          <p style={{ fontSize: 30, fontWeight: 800, color: valColor[variant], lineHeight: 1, letterSpacing: '-0.03em' }}>
            {value}
          </p>
          <p style={{ fontSize: 12, color: 'var(--c-text-muted)', marginTop: 6 }}>{sub}</p>
        </div>
        <div
          className="icon-circle"
          style={{ background: iconBg[variant], color: valColor[variant] }}
        >
          {icon}
        </div>
      </div>
    </div>
  );
};

/* ── main ── */
export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { scans, counts, setSelectedScan } = useScans();
  const latestScans = scans.slice(0, 5);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* ── Hero banner ── */}
      <div className="card" style={{ padding: '28px 32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--c-text-main)', letterSpacing: '-0.03em' }}>
            AI Threat Shield
          </h1>
          <span className="badge badge-teal" style={{ fontSize: 11 }}>Threat Detection System</span>
        </div>
        <p style={{ fontSize: 14, color: 'var(--c-text-muted)', maxWidth: 520 }}>
          Detect suspicious messages and URLs in real time using a trained XGBoost machine-learning classifier.
        </p>
      </div>

      {/* ── Stat cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 16 }}>
        <StatCard variant="total"  label="Total Scans"       value={counts.total}    sub="Evaluations performed"    icon={<ShieldCheck   size={18} />} />
        <StatCard variant="benign" label="Benign Detected"   value={counts.benign}   sub="Legitimate & safe"        icon={<CheckCircle2  size={18} />} />
        <StatCard variant="spam"   label="Spam Detected"     value={counts.spam}     sub="Unsolicited commercial"   icon={<AlertTriangle size={18} />} />
        <StatCard variant="phish"  label="Phishing Detected" value={counts.phishing} sub="High-risk deceptive"      icon={<ShieldAlert   size={18} />} />
      </div>

      {/* ── Quick scan ── */}
      <div className="card" style={{ padding: '28px 32px' }}>
        <h2 className="section-title" style={{ marginBottom: 18 }}>What would you like to scan?</h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
          {/* Card: message */}
          <div
            style={{
              padding: '24px', borderRadius: 12,
              background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
              display: 'flex', flexDirection: 'column', gap: 12,
              transition: 'border-color .15s',
            }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--c-border-hover)')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--c-border)')}
          >
            <div className="icon-circle" style={{ background: 'var(--c-primary-lt)', color: 'var(--c-primary)' }}>
              <MessageSquare size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--c-text-main)', marginBottom: 5 }}>Scan a Message</h3>
              <p style={{ fontSize: 13, color: 'var(--c-text-muted)', lineHeight: 1.55 }}>
                Check SMS messages, emails, and suspicious text for spam or phishing.
              </p>
            </div>
            <button className="btn-primary" style={{ alignSelf: 'flex-start', marginTop: 4 }} onClick={() => navigate('/scan-message')}>
              Analyse Message <ArrowRight size={14} />
            </button>
          </div>

          {/* Card: URL */}
          <div
            style={{
              padding: '24px', borderRadius: 12,
              background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
              display: 'flex', flexDirection: 'column', gap: 12,
              transition: 'border-color .15s',
            }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--c-border-hover)')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--c-border)')}
          >
            <div className="icon-circle" style={{ background: 'var(--c-primary-lt)', color: 'var(--c-primary)' }}>
              <LinkIcon size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--c-text-main)', marginBottom: 5 }}>Scan a URL</h3>
              <p style={{ fontSize: 13, color: 'var(--c-text-muted)', lineHeight: 1.55 }}>
                Analyse URL structure and heuristic indicators for potential threats.
              </p>
            </div>
            <button className="btn-primary" style={{ alignSelf: 'flex-start', marginTop: 4 }} onClick={() => navigate('/scan-url')}>
              Analyse URL <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* ── Recent activity ── */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--c-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 className="section-title">Recent Activity</h2>
            <p className="section-sub">Latest threat evaluations processed by the engine</p>
          </div>
          {scans.length > 0 && (
            <button className="btn-ghost" onClick={() => navigate('/history')}>
              View All <ArrowRight size={13} />
            </button>
          )}
        </div>

        {latestScans.length === 0 ? (
          /* empty state */
          <div style={{ padding: '52px 24px', textAlign: 'center' }}>
            <div style={{
              width: 52, height: 52, borderRadius: '50%',
              background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 14px', color: 'var(--c-text-faint)',
            }}>
              <Inbox size={22} />
            </div>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-text-main)', marginBottom: 6 }}>
              No scans yet
            </h3>
            <p style={{ fontSize: 13, color: 'var(--c-text-muted)', marginBottom: 18, maxWidth: 340, margin: '0 auto 18px' }}>
              Get started by analysing a message or a URL using the quick scan actions above.
            </p>
            <button className="btn-primary" onClick={() => navigate('/scan-message')}>
              Scan Your First Message <ArrowRight size={14} />
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Input Preview</th>
                  <th>Type</th>
                  <th>Classification</th>
                  <th>Date</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {latestScans.map(scan => {
                  const isBenign   = scan.predicted_class === 'Ham';
                  const isSpam     = scan.predicted_class === 'Spam';
                  const isPhishing = scan.predicted_class === 'Phishing';
                  const badgeCls   = isPhishing ? 'badge-phishing' : isSpam ? 'badge-spam' : 'badge-benign';
                  const label      = isBenign ? 'Benign' : scan.predicted_class;
                  const isUrl      = scan.text_preview.startsWith('http') || scan.text_preview.includes('www.');

                  return (
                    <tr key={scan.id}>
                      <td className="truncate-cell mono" style={{ fontSize: 12 }}>
                        {scan.text_preview}
                      </td>
                      <td>
                        <span className="badge badge-neutral" style={{ fontSize: 11 }}>
                          {isUrl ? 'URL' : 'Message'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${badgeCls}`}>{label}</span>
                      </td>
                      <td style={{ fontSize: 12, color: 'var(--c-text-muted)', whiteSpace: 'nowrap' }}>
                        {new Date(scan.timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button className="btn-ghost" style={{ fontSize: 12 }} onClick={() => setSelectedScan(scan)}>
                          <Eye size={13} /> View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
