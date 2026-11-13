import React, { useState } from 'react';
import { 
  X, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  Copy, 
  Check, 
  Clock, 
  Globe
} from 'lucide-react';
import { useScans } from '../../context/ScanContext';
import type { URLScanResult } from '../../types';

export const ScanDetailModal: React.FC = () => {
  const { selectedScan, setSelectedScan } = useScans();
  const [copied, setCopied] = useState(false);

  if (!selectedScan) return null;

  const isPhishing = selectedScan.predicted_class === 'Phishing';
  const isSpam = selectedScan.predicted_class === 'Spam';
  const isBenign = selectedScan.predicted_class === 'Ham';

  const classificationLabel = isBenign ? 'Benign' : selectedScan.predicted_class;
  const badgeClass = isPhishing ? 'badge-phishing' : isSpam ? 'badge-spam' : 'badge-benign';
  const StatusIcon = isPhishing ? ShieldAlert : isSpam ? AlertTriangle : ShieldCheck;
  const accentColor = isPhishing ? 'var(--c-phishing)' : isSpam ? 'var(--c-spam)' : 'var(--c-benign)';

  const urlDetails = (selectedScan as URLScanResult).url_details;

  const handleCopy = () => {
    const text = `AI Threat Shield Evaluation Report:
Scan ID: ${selectedScan.id}
Classification: ${classificationLabel} (${selectedScan.confidence}% confidence)
Risk Level: ${selectedScan.threat_level}
Content Preview: ${selectedScan.text_preview}
Probabilities: Benign: ${selectedScan.probabilities.Ham}%, Spam: ${selectedScan.probabilities.Spam}%, Phishing: ${selectedScan.probabilities.Phishing}%
Key Indicators: ${selectedScan.top_indicators.join(', ')}
Security Advice: ${selectedScan.security_advice.join(' | ')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
      {/* Backdrop */}
      <div
        style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.45)', backdropFilter: 'blur(2px)' }}
        onClick={() => setSelectedScan(null)}
      />

      {/* Modal Dialog */}
      <div
        className="card"
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: 580,
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
          borderLeft: `4px solid ${accentColor}`
        }}
      >
        {/* Modal Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--c-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              className="icon-circle"
              style={{
                background: isPhishing ? 'var(--c-phishing-lt)' : isSpam ? 'var(--c-spam-lt)' : 'var(--c-benign-lt)',
                color: accentColor
              }}
            >
              <StatusIcon size={20} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                <span className={`badge ${badgeClass}`}>
                  {classificationLabel}
                </span>
                <span className="mono" style={{ fontSize: 11, color: 'var(--c-text-muted)' }}>
                  #{selectedScan.id}
                </span>
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--c-text-main)' }}>
                Evaluation Breakdown
              </h3>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={handleCopy}
              className="btn-secondary"
              style={{ padding: '6px 10px' }}
              title="Copy details"
            >
              {copied ? <Check size={14} style={{ color: 'var(--c-benign)' }} /> : <Copy size={14} />}
            </button>
            <button
              onClick={() => setSelectedScan(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--c-text-muted)', padding: 6, borderRadius: 6, display: 'flex' }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '22px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Content Preview */}
          <div>
            <label style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', display: 'block', marginBottom: 8 }}>
              Inspected Content
            </label>
            <div className="mono" style={{ padding: 12, background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8, fontSize: 12, color: 'var(--c-text-main)', wordBreak: 'break-all', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
              {selectedScan.text_preview}
            </div>
          </div>

          {/* Probabilities */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)' }}>
                Class Probabilities
              </span>
              <span className="mono" style={{ fontSize: 14, fontWeight: 800, color: accentColor }}>
                {selectedScan.confidence}% Confidence
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              <div style={{ padding: '10px 12px', background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8, textAlign: 'center' }}>
                <span style={{ fontSize: 11, color: 'var(--c-text-muted)', display: 'block' }}>Benign</span>
                <span className="mono" style={{ fontSize: 15, fontWeight: 700, color: 'var(--c-benign)', display: 'block', marginTop: 3 }}>
                  {selectedScan.probabilities.Ham}%
                </span>
              </div>
              <div style={{ padding: '10px 12px', background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8, textAlign: 'center' }}>
                <span style={{ fontSize: 11, color: 'var(--c-text-muted)', display: 'block' }}>Spam</span>
                <span className="mono" style={{ fontSize: 15, fontWeight: 700, color: 'var(--c-spam)', display: 'block', marginTop: 3 }}>
                  {selectedScan.probabilities.Spam}%
                </span>
              </div>
              <div style={{ padding: '10px 12px', background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8, textAlign: 'center' }}>
                <span style={{ fontSize: 11, color: 'var(--c-text-muted)', display: 'block' }}>Phishing</span>
                <span className="mono" style={{ fontSize: 15, fontWeight: 700, color: 'var(--c-phishing)', display: 'block', marginTop: 3 }}>
                  {selectedScan.probabilities.Phishing}%
                </span>
              </div>
            </div>
          </div>

          {/* URL Details if available */}
          {urlDetails && (
            <div style={{ padding: 14, background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', marginBottom: 10 }}>
                <Globe size={14} style={{ color: 'var(--c-primary)' }} />
                <span>URL Structural Analysis</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, fontSize: 12 }}>
                <div>
                  <span style={{ color: 'var(--c-text-muted)', display: 'block', fontSize: 11 }}>Domain:</span>
                  <span className="mono" style={{ fontWeight: 600, color: 'var(--c-text-main)' }}>
                    {urlDetails.domain || 'N/A'}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--c-text-muted)', display: 'block', fontSize: 11 }}>Protocol:</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-text-main)' }}>
                    {urlDetails.has_https ? '🔒 HTTPS Encrypted' : '⚠ HTTP (Unencrypted)'}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--c-text-muted)', display: 'block', fontSize: 11 }}>Length:</span>
                  <span className="mono" style={{ fontWeight: 600, color: 'var(--c-text-main)' }}>
                    {urlDetails.url_length} chars
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--c-text-muted)', display: 'block', fontSize: 11 }}>Dots / Hyphens:</span>
                  <span className="mono" style={{ fontWeight: 600, color: 'var(--c-text-main)' }}>
                    {urlDetails.dot_count} dots • {urlDetails.hyphen_count} hyphens
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Key Indicators */}
          {selectedScan.top_indicators && selectedScan.top_indicators.length > 0 && (
            <div>
              <label style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: 'var(--c-text-muted)', display: 'block', marginBottom: 8 }}>
                Top Extracted Indicators
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {selectedScan.top_indicators.map((ind, i) => (
                  <span
                    key={i}
                    className="badge badge-neutral mono"
                    style={{ fontSize: 11 }}
                  >
                    {ind}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Security Advice */}
          {selectedScan.security_advice && selectedScan.security_advice.length > 0 && (
            <div style={{ padding: 14, background: 'var(--c-bg-surface)', border: '1px solid var(--c-border)', borderRadius: 8 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-text-main)', display: 'block', marginBottom: 6 }}>
                Security Advice
              </label>
              <ul style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4, fontSize: 12, color: 'var(--c-text-muted)' }}>
                {selectedScan.security_advice.map((adv, idx) => (
                  <li key={idx} style={{ lineHeight: 1.5 }}>{adv}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Footer Metadata */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11, color: 'var(--c-text-muted)', paddingTop: 10, borderTop: '1px solid var(--c-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Clock size={12} />
              <span>Processed in {selectedScan.processing_time_ms} ms</span>
            </div>
            <span>{new Date(selectedScan.timestamp).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
