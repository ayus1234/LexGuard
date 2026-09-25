'use client';

import React, { useState } from 'react';
import { ComplianceBanner } from './ComplianceBanner';
import { TopNavbar } from './TopNavbar';
import { Sidebar } from './Sidebar';
import { FooterBar } from './FooterBar';
import { CommandPalette } from '../navigation/CommandPalette';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-[#F8F9FF] text-[#0B1C30] overflow-hidden">
      {/* 0. Accessible Skip Navigation Link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-[#0284C7] focus:text-white focus:rounded focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white font-medium text-xs"
      >
        Skip to main content
      </a>

      {/* 1. Persistent Topmost Compliance Banner */}
      <ComplianceBanner />

      {/* 2. Top Navigation Bar */}
      <TopNavbar
        onOpenCommandPalette={() => setCommandPaletteOpen(true)}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        isSidebarOpen={sidebarOpen}
      />

      {/* 3. Main Tri-Panel Layout: Intact Fixed Sidebar + Scrollable Central Content */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main id="main-content" className="flex-1 min-h-0 overflow-y-auto flex flex-col bg-[#F8F9FF]" tabIndex={-1}>
          <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* 4. Persistent Bottom Telemetry Bar */}
      <FooterBar />

      {/* 5. Global Command Palette Modal */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />
    </div>
  );
};
