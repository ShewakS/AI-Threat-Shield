import React, { useState } from 'react';
import {
  Link as LinkIcon, Trash2, AlertCircle, Loader2,
  ShieldCheck, ShieldAlert, AlertTriangle,
  Copy, Check, Clock, Globe, Info,
} from 'lucide-react';
import { api } from '../services/api';
import { useScans } from '../context/ScanContext';
import type { URLScanResult } from '../types';

const ProbBar: React.FC<{ label: string; value: number; color: string }> = ({ label, value, color }) => (
  <div>
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, fontWeight: 500, marginBottom: 5 }}>
      <span style={{ color }}>{label}</span>
      <span style={{ color: 'var(--c-text-main)' }}>{value}%</span>
    </div>
    <div className="prob-bar-track">
      <div className="prob-bar-fill" style={{ width: `${value}%`, background: color }} />
    </div>
  </div>
);

export const ScanURL: React.FC = () => {
  const { addScan } = useScans();
  const [url, setUrl]         = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const [result, setResult]   = useState<URLScanResult | null>(null);
  const [copied, setCopied]   = useState(false);

  const presets = [
    { label: 'Phishing: Fake Bank',   url: 'http://192.168.1.105/wellsfargo-verify-security-login/auth.php' },
    { label: 'Phishing: Fake MS Login', url: 'https://secure-login-microsoft-office365-verify.com' },
    { label: 'Benign: GitHub',        url: 'https://github.com/scikit-learn/scikit-learn' },
  ];

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) { setError('Please enter a URL to analyse.'); return; }
    setLoading(true); setError(null);
    try {
      const data = await api.scanURL(trimmed);
      setResult(data); addScan(data);
    } catch (err: any) {
      setError(err.message || 'URL inspection failed.');
    } finally {
      setLoading(false);
    }
  };

  const isPhishing = result?.predicted_class === 'Phishing';
  const isSpam     = result?.predicted_class === 'Spam';
  const isBenign   = result?.predicted_class === 'Ham';
  const label      = isBenign ? 'Benign' : result?.predicted_class ?? '';
  const badgeCls   = isPhishing ? 'badge-phishing' : isSpam ? 'badge-spam' : 'badge-benign';
  const Icon       = isPhishing ? ShieldAlert : isSpam ? AlertTriangle : ShieldCheck;
  const accentColor = isPhishing ? 'var(--c-phishing)' : isSpam ? 'var(--c-spam)' : 'var(--c-benign)';

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(
      `URL: ${result.text_preview}\nClassification: ${label} (${result.confidence}%)\nAdvice: ${result.security_advice.join(' | ')}`
    );
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>

      <div>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--c-text-main)', letterSpacing: '-0.02em' }}>Scan URL</h1>
        <p style={{ fontSize: 14, color: 'var(--c-text-muted)', marginTop: 4 }}>
          Inspect URL structure and heuristic indicators for phishing or malicious content.
        </p>
      </div>

      <div className="card" style={{ padding: '28px 30px' }}>
        <form onSubmit={handleScan}>
          {/* Presets */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
            <span style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>Examples:</span>
            {presets.map((p, i) => (
              <button key={i} type="button"
                onClick={() => { setUrl(p.url); setError(null); }}
                style={{
                  padding: '4px 10px', fontSize: 12, fontWeight: 500,
                  background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
                  borderRadius: 6, color: 'var(--c-text-muted)', cursor: 'pointer', transition: 'all .12s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--c-primary)'; e.currentTarget.style.color = 'var(--c-primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--c-border)'; e.currentTarget.style.color = 'var(--c-text-muted)'; }}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* URL input */}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Globe size={17} style={{ position: 'absolute', left: 14, color: 'var(--c-text-faint)', flexShrink: 0 }} />
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="e.g. https://secure-account-verification-portal.com/login"
              className="input-field mono"
              style={{ paddingLeft: 40, paddingRight: url ? 40 : 14 }}
            />
            {url && (
              <button type="button" onClick={() => { setUrl(''); setResult(null); setError(null); }}
                style={{ position: 'absolute', right: 12, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-text-muted)', display: 'flex' }}>
                <Trash2 size={15} />
              </button>
            )}
          </div>

          {error && <div className="alert-error" style={{ marginTop: 12 }}><AlertCircle size={15} /> {error}</div>}

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16, gap: 10, flexWrap: 'wrap' }}>
            <p style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>
              Inspects domain, HTTPS, entropy, suspicious keywords, and structural patterns.
            </p>
            <button className="btn-primary" type="submit" disabled={loading || !url.trim()}>
              {loading ? <><Loader2 size={15} className="animate-spin" /> Analysing…</> : <><LinkIcon size={14} /> Analyse URL</>}
            </button>
          </div>
        </form>
      </div>

      {/* Result */}
      {result && (
        <div className="card" style={{ overflow: 'hidden', borderLeft: `4px solid ${accentColor}` }}>
          {/* Verdict banner */}
          <div style={{ padding: '22px 28px', borderBottom: '1px solid var(--c-border)', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div className="icon-circle" style={{ background: isPhishing ? 'var(--c-phishing-lt)' : isSpam ? 'var(--c-spam-lt)' : 'var(--c-benign-lt)', color: accentColor }}>
                <Icon size={20} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span className={`badge ${badgeCls}`}>{label}</span>
                  <span style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>Risk: <strong>{result.threat_level}</strong></span>
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--c-text-main)' }}>
                  {isPhishing ? 'Malicious or Deceptive Phishing URL' : isSpam ? 'Suspicious or Promotional URL' : 'URL Appears Benign & Legitimate'}
                </h3>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: accentColor, lineHeight: 1 }}>{result.confidence}%</div>
                <div style={{ fontSize: 11, color: 'var(--c-text-muted)', marginTop: 3 }}>confidence</div>
              </div>
              <button onClick={handleCopy} style={{ padding: '7px 10px', background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8, cursor: 'pointer', color: 'var(--c-text-muted)', display: 'flex' }}>
                {copied ? <Check size={15} style={{ color: 'var(--c-benign)' }} /> : <Copy size={15} />}
              </button>
            </div>
          </div>

          <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 22 }}>
            <p style={{ fontSize: 13, color: 'var(--c-text-muted)', lineHeight: 1.65 }}>{result.threat_description}</p>

            {/* URL structural breakdown */}
            {result.url_details && (
              <div style={{ background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 10, padding: '18px 20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 14, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)' }}>
                  <Globe size={14} style={{ color: 'var(--c-primary)' }} /> URL Structural Analysis
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
                  {[
                    { k: 'Domain', v: result.url_details.domain || 'N/A' },
                    { k: 'Protocol', v: result.url_details.has_https ? '🔒 HTTPS' : '⚠ HTTP' },
                    { k: 'URL Length', v: `${result.url_details.url_length} chars` },
                    { k: 'Dots', v: result.url_details.dot_count },
                    { k: 'Hyphens', v: result.url_details.hyphen_count },
                    { k: 'IP Address', v: result.url_details.is_ip_address ? 'Yes (Suspicious)' : 'No' },
                  ].map(({ k, v }) => (
                    <div key={k} style={{ background: 'var(--c-bg-white)', border: '1px solid var(--c-border)', borderRadius: 8, padding: '10px 14px' }}>
                      <div style={{ fontSize: 11, color: 'var(--c-text-muted)', marginBottom: 4 }}>{k}</div>
                      <div className="mono" style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v}</div>
                    </div>
                  ))}
                </div>
                {result.url_details.suspicious_keywords_found?.length > 0 && (
                  <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--c-border)', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>Trigger keywords:</span>
                    {result.url_details.suspicious_keywords_found.map((kw, i) => (
                      <span key={i} className="badge mono" style={{ background: 'var(--c-phishing-lt)', color: 'var(--c-phishing)', border: '1px solid var(--c-phishing-b)', fontSize: 11 }}>{kw}</span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Probabilities */}
            <div style={{ background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 10, padding: '18px 20px' }}>
              <p style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', marginBottom: 14 }}>
                Class Probability Distribution
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <ProbBar label="Benign (Ham)" value={result.probabilities.Ham}      color="var(--c-benign)"   />
                <ProbBar label="Spam"         value={result.probabilities.Spam}     color="var(--c-spam)"     />
                <ProbBar label="Phishing"     value={result.probabilities.Phishing} color="var(--c-phishing)" />
              </div>
            </div>

            {/* Advice */}
            {result.security_advice?.length > 0 && (
              <div style={{ background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 10, padding: '16px 20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10, fontSize: 13, fontWeight: 600, color: 'var(--c-text-main)' }}>
                  <Info size={14} style={{ color: 'var(--c-primary)' }} /> Recommended Action
                </div>
                <ul style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 5 }}>
                  {result.security_advice.map((adv, i) => (
                    <li key={i} style={{ fontSize: 13, color: 'var(--c-text-muted)', lineHeight: 1.55 }}>{adv}</li>
                  ))}
                </ul>
              </div>
            )}

            <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--c-text-faint)', borderTop: '1px solid var(--c-border)', paddingTop: 14 }}>
              <Clock size={12} /> Inspection completed in {result.processing_time_ms} ms
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
