import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ScanProvider } from './context/ScanContext';
import { Layout } from './components/Layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { ScanMessage } from './pages/ScanMessage';
import { ScanURL } from './pages/ScanURL';
import { ScanHistory } from './pages/ScanHistory';

export const App: React.FC = () => {
  return (
    <ScanProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="scan-message" element={<ScanMessage />} />
            <Route path="scan-url" element={<ScanURL />} />
            <Route path="history" element={<ScanHistory />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ScanProvider>
  );
};

export default App;
