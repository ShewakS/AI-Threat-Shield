import type {
  ScanResult,
  URLScanResult,
  BatchScanResult,
  ModelInfo,
  PresetSample,
  HealthStatus
} from '../types';

const API_BASE = '/api';

export const api = {
  async scanText(text: string, source: string = 'auto'): Promise<ScanResult> {
    const res = await fetch(`${API_BASE}/scan/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Scan request failed' }));
      throw new Error(err.detail || `Server error (${res.status})`);
    }
    return res.json();
  },

  async scanURL(url: string): Promise<URLScanResult> {
    const res = await fetch(`${API_BASE}/scan/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'URL scan request failed' }));
      throw new Error(err.detail || `Server error (${res.status})`);
    }
    return res.json();
  },

  async scanBatch(items: string[]): Promise<BatchScanResult> {
    const res = await fetch(`${API_BASE}/scan/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Batch scan request failed' }));
      throw new Error(err.detail || `Server error (${res.status})`);
    }
    return res.json();
  },

  async uploadBatchFile(file: File): Promise<BatchScanResult> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/scan/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'File upload scan failed' }));
      throw new Error(err.detail || `Server error (${res.status})`);
    }
    return res.json();
  },

  async getModelInfo(): Promise<ModelInfo> {
    const res = await fetch(`${API_BASE}/analytics/model`);
    if (!res.ok) throw new Error('Failed to load model details');
    return res.json();
  },

  async getPresets(): Promise<PresetSample[]> {
    const res = await fetch(`${API_BASE}/analytics/presets`);
    if (!res.ok) throw new Error('Failed to load presets');
    return res.json();
  },

  async getHistory(): Promise<{ total_scans: number; breakdown: Record<string, number>; history: ScanResult[] }> {
    const res = await fetch(`${API_BASE}/analytics/history`);
    if (!res.ok) throw new Error('Failed to load history');
    return res.json();
  },

  async clearHistory(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/analytics/history`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to clear history');
    return res.json();
  },

  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to load system health');
    return res.json();
  }
};
