import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { ScanDetailModal } from '../Modals/ScanDetailModal';

export const Layout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--c-bg-page)' }}>
      {/* Desktop Sidebar */}
      <Sidebar mobileOpen={mobileOpen} onCloseMobile={() => setMobileOpen(false)} />

      {/* Right column: header + page content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Header onOpenMobile={() => setMobileOpen(true)} />

        <main style={{ flex: 1, padding: '28px 32px', maxWidth: 1160, width: '100%' }}>
          <Outlet />
        </main>
      </div>

      <ScanDetailModal />
    </div>
  );
};
