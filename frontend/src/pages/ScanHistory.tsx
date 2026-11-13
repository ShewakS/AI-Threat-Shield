import React, { useState } from 'react';
import { 
  Search, 
  Trash2, 
  Eye, 
  Inbox,
  Download
} from 'lucide-react';
import { useScans } from '../context/ScanContext';

export const ScanHistory: React.FC = () => {
  const { scans, clearHistory, setSelectedScan } = useScans();
  const [filterClass, setFilterClass] = useState<'All' | 'Ham' | 'Spam' | 'Phishing'>('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [confirmClear, setConfirmClear] = useState(false);

  const filteredScans = scans.filter((scan) => {
    // Class filter
    if (filterClass !== 'All' && scan.predicted_class !== filterClass) {
      return false;
    }
    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const previewMatch = scan.text_preview.toLowerCase().includes(q);
      const idMatch = scan.id.toLowerCase().includes(q);
      const classMatch = scan.predicted_class.toLowerCase().includes(q);
      return previewMatch || idMatch || classMatch;
    }
    return true;
  });

  const handleExportCSV = () => {
    if (scans.length === 0) return;
    const headers = ['ID', 'Timestamp', 'Classification', 'Confidence', 'Threat Level', 'Preview'];
    const rows = scans.map(s => [
      s.id,
      s.timestamp,
      s.predicted_class === 'Ham' ? 'Benign' : s.predicted_class,
      `${s.confidence}%`,
      s.threat_level,
      `"${s.text_preview.replace(/"/g, '""')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `threat_shield_scan_history_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1040 }}>
      {/* Page Heading */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--c-text-main)', letterSpacing: '-0.02em' }}>
            Scan History
          </h1>
          <p style={{ fontSize: 14, color: 'var(--c-text-muted)', marginTop: 4 }}>
            Review all previous text, message, and URL threat evaluations.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {scans.length > 0 && (
            <button
              onClick={handleExportCSV}
              className="btn-secondary"
            >
              <Download size={14} />
              <span>Export CSV</span>
            </button>
          )}

          {scans.length > 0 && (
            confirmClear ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 8px', background: 'var(--c-phishing-lt)', borderRadius: 8, border: '1px solid var(--c-phishing-b)' }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-phishing)' }}>Confirm clear?</span>
                <button
                  onClick={() => {
                    clearHistory();
                    setConfirmClear(false);
                  }}
                  style={{
                    padding: '3px 8px', background: 'var(--c-phishing)', color: '#fff', border: 'none', borderRadius: 4, fontSize: 11, fontWeight: 600, cursor: 'pointer'
                  }}
                >
                  Yes
                </button>
                <button
                  onClick={() => setConfirmClear(false)}
                  style={{
                    padding: '3px 8px', background: '#fff', color: 'var(--c-text-muted)', border: '1px solid var(--c-border)', borderRadius: 4, fontSize: 11, cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setConfirmClear(true)}
                className="btn-secondary"
                style={{ color: 'var(--c-phishing)', borderColor: 'var(--c-border)' }}
              >
                <Trash2 size={14} />
                <span>Clear History</span>
              </button>
            )
          )}
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
        {/* Class Filter Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'var(--c-bg-surface)', padding: 4, borderRadius: 8, border: '1px solid var(--c-border)', overflowX: 'auto' }}>
          {(['All', 'Ham', 'Spam', 'Phishing'] as const).map((tab) => {
            const label = tab === 'Ham' ? 'Benign' : tab;
            const count = tab === 'All' 
              ? scans.length 
              : scans.filter(s => s.predicted_class === tab).length;
            const isActive = filterClass === tab;

            return (
              <button
                key={tab}
                onClick={() => setFilterClass(tab)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '5px 12px',
                  borderRadius: 6,
                  border: 'none',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: isActive ? 'var(--c-primary)' : 'transparent',
                  color: isActive ? '#fff' : 'var(--c-text-muted)',
                  transition: 'all .14s'
                }}
              >
                <span>{label}</span>
                <span
                  style={{
                    fontSize: 10,
                    padding: '1px 6px',
                    borderRadius: 10,
                    background: isActive ? 'rgba(255,255,255,0.25)' : 'var(--c-border)',
                    color: isActive ? '#fff' : 'var(--c-text-muted)'
                  }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', minWidth: 260 }}>
          <Search size={15} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--c-text-faint)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scans by text or ID..."
            className="input-field"
            style={{ paddingLeft: 34, height: 38, fontSize: 13 }}
          />
        </div>
      </div>

      {/* Scans Table */}
      <div className="card" style={{ overflow: 'hidden' }}>
        {filteredScans.length === 0 ? (
          <div style={{ padding: '52px 24px', textAlign: 'center' }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: 'var(--c-bg-surface)',
                border: '1px solid var(--c-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 12px',
                color: 'var(--c-text-faint)'
              }}
            >
              <Inbox size={22} />
            </div>
            <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-text-main)', marginBottom: 4 }}>
              No matching scans found
            </h3>
            <p style={{ fontSize: 13, color: 'var(--c-text-muted)' }}>
              {scans.length === 0
                ? 'Your scan history is empty. Try running a scan on the message or URL page.'
                : 'Try adjusting your search query or class filter.'}
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 90 }}>ID</th>
                  <th>Input Preview</th>
                  <th style={{ width: 100 }}>Type</th>
                  <th style={{ width: 130 }}>Classification</th>
                  <th style={{ width: 110 }}>Confidence</th>
                  <th style={{ width: 160 }}>Date</th>
                  <th style={{ width: 90, textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredScans.map((scan) => {
                  const isBenign = scan.predicted_class === 'Ham';
                  const isSpam = scan.predicted_class === 'Spam';
                  const isPhishing = scan.predicted_class === 'Phishing';

                  const badgeClass = isPhishing
                    ? 'badge-phishing'
                    : isSpam
                    ? 'badge-spam'
                    : 'badge-benign';

                  const label = isBenign ? 'Benign' : scan.predicted_class;
                  const isUrl = scan.text_preview.startsWith('http') || scan.text_preview.includes('www.');
                  const typeLabel = isUrl ? 'URL' : 'Message';

                  return (
                    <tr key={scan.id}>
                      <td className="mono" style={{ fontSize: 12, color: 'var(--c-text-muted)' }}>
                        #{scan.id}
                      </td>
                      <td className="truncate-cell mono" style={{ fontSize: 12 }}>
                        {scan.text_preview}
                      </td>
                      <td>
                        <span className="badge badge-neutral" style={{ fontSize: 11 }}>
                          {typeLabel}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${badgeClass}`}>
                          {label}
                        </span>
                      </td>
                      <td className="mono" style={{ fontSize: 13, fontWeight: 700, color: 'var(--c-text-main)' }}>
                        {scan.confidence}%
                      </td>
                      <td style={{ fontSize: 12, color: 'var(--c-text-muted)', whiteSpace: 'nowrap' }}>
                        {new Date(scan.timestamp).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          onClick={() => setSelectedScan(scan)}
                          className="btn-ghost"
                          style={{ fontSize: 12 }}
                        >
                          <Eye size={13} />
                          <span>View</span>
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
