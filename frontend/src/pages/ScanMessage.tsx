import React, { useState } from 'react';
import {
  Send, Trash2, AlertCircle, Loader2,
  ShieldCheck, ShieldAlert, AlertTriangle,
  Copy, Check, Clock, Info,
} from 'lucide-react';
import { api } from '../services/api';
import { useScans } from '../context/ScanContext';
import type { ScanResult } from '../types';

/* ── reusable prob bar ── */
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

export const ScanMessage: React.FC = () => {
  const { addScan } = useScans();
  const [messageType, setMessageType] = useState<'auto' | 'sms' | 'email'>('auto');
  const [content, setContent]         = useState('');
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState<string | null>(null);
  const [result, setResult]           = useState<ScanResult | null>(null);
  const [copied, setCopied]           = useState(false);

  const presets = [
    { label: 'Phishing: Bank Alert',  type: 'email' as const, text: 'URGENT SECURITY ALERT: Your Wells Fargo account was locked due to suspicious activity. Verify credentials at https://wellsfargo-verify-login.com/auth within 24 h or your account will be permanently closed.' },
    { label: 'Spam: Lottery Prize',   type: 'sms'   as const, text: 'CONGRATULATIONS! You won $1,000,000 in the 2026 International Mobile Draw! Text CLAIM to 88442 or visit http://freeprizes.xyz now.' },
    { label: 'Benign: Team Meeting',  type: 'email' as const, text: 'Hi Team, let us meet tomorrow at 10:00 AM in Conference Room B for our sprint retrospective. Please update your Jira tickets beforehand. Thanks, Sarah.' },
  ];

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) { setError('Message content is required.'); return; }
    setLoading(true); setError(null);
    try {
      const data = await api.scanText(trimmed, messageType);
      setResult(data); addScan(data);
    } catch (err: any) {
      setError(err.message || 'Analysis request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(
      `Classification: ${result.predicted_class} (${result.confidence}%)\nAdvice: ${result.security_advice.join(' | ')}`
    );
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };

  const isPhishing = result?.predicted_class === 'Phishing';
  const isSpam     = result?.predicted_class === 'Spam';
  const isBenign   = result?.predicted_class === 'Ham';
  const label      = isBenign ? 'Benign' : result?.predicted_class ?? '';
  const badgeCls   = isPhishing ? 'badge-phishing' : isSpam ? 'badge-spam' : 'badge-benign';
  const Icon       = isPhishing ? ShieldAlert : isSpam ? AlertTriangle : ShieldCheck;
  const accentColor = isPhishing ? 'var(--c-phishing)' : isSpam ? 'var(--c-spam)' : 'var(--c-benign)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>

      {/* Page heading */}
      <div>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--c-text-main)', letterSpacing: '-0.02em' }}>Scan Message</h1>
        <p style={{ fontSize: 14, color: 'var(--c-text-muted)', marginTop: 4 }}>
          Analyse SMS messages, emails, and suspicious text for spam or phishing.
        </p>
      </div>

      {/* Input card */}
      <div className="card" style={{ padding: '28px 30px' }}>
        <form onSubmit={handleScan}>

          {/* Controls row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 18 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--c-text-body)' }}>Type:</label>
              <select
                value={messageType}
                onChange={e => setMessageType(e.target.value as any)}
                style={{
                  padding: '5px 10px', fontSize: 13, fontWeight: 500,
                  background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
                  borderRadius: 7, color: 'var(--c-text-main)', outline: 'none', cursor: 'pointer',
                }}
              >
                <option value="auto">Auto-detect</option>
                <option value="sms">SMS</option>
                <option value="email">Email</option>
              </select>
            </div>

            {/* Presets */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>Try an example:</span>
              {presets.map((p, i) => (
                <button
                  key={i} type="button"
                  onClick={() => { setContent(p.text); setMessageType(p.type); setError(null); }}
                  style={{
                    padding: '4px 10px', fontSize: 12, fontWeight: 500,
                    background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)',
                    borderRadius: 6, color: 'var(--c-text-muted)', cursor: 'pointer',
                    transition: 'all .12s',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--c-primary)';
                    e.currentTarget.style.color = 'var(--c-primary)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--c-border)';
                    e.currentTarget.style.color = 'var(--c-text-muted)';
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Textarea */}
          <textarea
            className="textarea-field"
            rows={6}
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Paste your message or email content here…"
          />

          {/* Error */}
          {error && (
            <div className="alert-error" style={{ marginTop: 12 }}>
              <AlertCircle size={15} /> {error}
            </div>
          )}

          {/* Action bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16, flexWrap: 'wrap', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 12, color: 'var(--c-text-muted)' }}>
              <span>{content.length} chars</span>
              <span style={{ color: 'var(--c-border)' }}>·</span>
              <span>{content.trim() ? content.trim().split(/\s+/).length : 0} words</span>
              {content && (
                <button type="button" onClick={() => { setContent(''); setResult(null); setError(null); }}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-text-muted)', display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
                  <Trash2 size={13} /> Clear
                </button>
              )}
            </div>
            <button className="btn-primary" type="submit" disabled={loading || !content.trim()}>
              {loading ? <><Loader2 size={15} className="animate-spin" /> Analysing…</> : <><Send size={14} /> Analyse Message</>}
            </button>
          </div>
        </form>
      </div>

      {/* Result card */}
      {result && (
        <div
          className="card"
          style={{ overflow: 'hidden', borderLeft: `4px solid ${accentColor}` }}
        >
          {/* Verdict banner */}
          <div style={{ padding: '22px 28px', borderBottom: '1px solid var(--c-border)', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div className="icon-circle" style={{
                background: isPhishing ? 'var(--c-phishing-lt)' : isSpam ? 'var(--c-spam-lt)' : 'var(--c-benign-lt)',
                color: accentColor,
              }}>
                <Icon size={20} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span className={`badge ${badgeCls}`}>{label}</span>
                  <span style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>Risk: <strong>{result.threat_level}</strong></span>
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--c-text-main)' }}>
                  {isPhishing ? 'Critical Phishing & Credential Theft Risk'
                    : isSpam ? 'Spam or Promotional Content Detected'
                    : 'Message Appears Legitimate & Safe'}
                </h3>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: accentColor, lineHeight: 1 }}>{result.confidence}%</div>
                <div style={{ fontSize: 11, color: 'var(--c-text-muted)', marginTop: 3 }}>confidence</div>
              </div>
              <button
                onClick={handleCopy}
                style={{
                  padding: '7px 10px', background: 'var(--c-bg-surface)',
                  border: '1px solid var(--c-border)', borderRadius: 8,
                  cursor: 'pointer', color: 'var(--c-text-muted)', display: 'flex',
                }}
              >
                {copied ? <Check size={15} style={{ color: 'var(--c-benign)' }} /> : <Copy size={15} />}
              </button>
            </div>
          </div>

          {/* Body */}
          <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 22 }}>
            {/* Description */}
            <p style={{ fontSize: 13, color: 'var(--c-text-muted)', lineHeight: 1.65 }}>{result.threat_description}</p>

            {/* Probability bars */}
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

            {/* Signals */}
            {result.top_indicators?.length > 0 && (
              <div>
                <p style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', marginBottom: 10 }}>
                  Top Signals Extracted
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {result.top_indicators.map((ind, i) => (
                    <span key={i} className="badge badge-neutral mono" style={{ fontSize: 11 }}>{ind}</span>
                  ))}
                </div>
              </div>
            )}

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

            {/* Latency */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--c-text-faint)', borderTop: '1px solid var(--c-border)', paddingTop: 14 }}>
              <Clock size={12} /> Inference completed in {result.processing_time_ms} ms
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
