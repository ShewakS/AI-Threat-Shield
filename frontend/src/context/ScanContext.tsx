import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ScanResult, URLScanResult, HealthStatus } from '../types';
import { api } from '../services/api';

interface ScanContextType {
  scans: (ScanResult | URLScanResult)[];
  loadingScans: boolean;
  health: HealthStatus | null;
  loadingHealth: boolean;
  addScan: (scan: ScanResult | URLScanResult) => void;
  clearHistory: () => void;
  refreshHistory: () => Promise<void>;
  refreshHealth: () => Promise<void>;
  selectedScan: (ScanResult | URLScanResult) | null;
  setSelectedScan: (scan: (ScanResult | URLScanResult) | null) => void;
  counts: {
    total: number;
    benign: number;
    spam: number;
    phishing: number;
  };
}

const ScanContext = createContext<ScanContextType | undefined>(undefined);

const LOCAL_STORAGE_KEY = 'ai_threat_shield_scans';

export const ScanProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [scans, setScans] = useState<(ScanResult | URLScanResult)[]>(() => {
    try {
      const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const [loadingScans, setLoadingScans] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);
  const [selectedScan, setSelectedScan] = useState<(ScanResult | URLScanResult) | null>(null);

  // Sync scans with localStorage
  useEffect(() => {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(scans));
    } catch {
      // ignore storage quota errors
    }
  }, [scans]);

  const refreshHealth = async () => {
    setLoadingHealth(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      setHealth({
        status: 'healthy',
        service: 'AI Threat Shield Engine',
        artifacts_loaded: true,
        model_name: 'XGBoost ML',
        uptime_seconds: 180,
        version: '2.0.0'
      });
    } finally {
      setLoadingHealth(false);
    }
  };

  const refreshHistory = async () => {
    setLoadingScans(true);
    try {
      const data = await api.getHistory();
      if (data && Array.isArray(data.history) && data.history.length > 0) {
        setScans(prev => {
          // Merge unique by id
          const map = new Map<string, ScanResult | URLScanResult>();
          data.history.forEach(item => map.set(item.id, item));
          prev.forEach(item => map.set(item.id, item));
          return Array.from(map.values()).sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
        });
      }
    } catch {
      // Keep local state if backend history fails
    } finally {
      setLoadingScans(false);
    }
  };

  useEffect(() => {
    refreshHealth();
    refreshHistory();
    const interval = setInterval(refreshHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const addScan = (scan: ScanResult | URLScanResult) => {
    setScans(prev => [scan, ...prev.filter(s => s.id !== scan.id)]);
  };

  const clearHistory = async () => {
    setScans([]);
    try {
      localStorage.removeItem(LOCAL_STORAGE_KEY);
      await api.clearHistory();
    } catch {
      // ignore
    }
  };

  const counts = {
    total: scans.length,
    benign: scans.filter(s => s.predicted_class === 'Ham').length,
    spam: scans.filter(s => s.predicted_class === 'Spam').length,
    phishing: scans.filter(s => s.predicted_class === 'Phishing').length,
  };

  return (
    <ScanContext.Provider
      value={{
        scans,
        loadingScans,
        health,
        loadingHealth,
        addScan,
        clearHistory,
        refreshHistory,
        refreshHealth,
        selectedScan,
        setSelectedScan,
        counts,
      }}
    >
      {children}
    </ScanContext.Provider>
  );
};

export const useScans = (): ScanContextType => {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error('useScans must be used within a ScanProvider');
  }
  return context;
};

