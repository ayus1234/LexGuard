'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FileText,
  FolderKanban,
  Scale,
  GitCompare,
  MessageSquareQuote,
  CheckSquare,
  ShieldCheck,
  Sliders,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();

  const mainNav = [
    {
      label: 'Analyze Dossier',
      href: '/analyze',
      icon: FileText,
      hasArrow: true,
    },
    {
      label: 'Sample Library',
      href: '/library',
      icon: FolderKanban,
      badge: '200',
    },
    {
      label: 'Public Law Corpus',
      href: '/public-law',
      icon: Scale,
      badge: '285',
    },
    {
      label: 'Demo Document Library',
      href: '/demo-docs',
      icon: Sparkles,
      badge: '15',
    },
    {
      label: 'Clause Compare',
      href: '/compare',
      icon: GitCompare,
      hasArrow: true,
    },
    {
      label: 'Document Q&A Grounded',
      href: '/ask',
      icon: MessageSquareQuote,
      hasArrow: true,
    },
    {
      label: 'Brief & Checklist',
      href: '/brief',
      icon: CheckSquare,
      hasArrow: true,
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/40 z-30 lg:hidden backdrop-blur-xs transition-opacity"
        />
      )}

      <aside
        aria-label="Sidebar Navigation"
        className={`w-64 shrink-0 bg-[#FFFFFF] border-r border-[#E2E8F0] flex flex-col justify-between p-3.5 transition-transform duration-200 z-30 h-full overflow-y-auto select-none ${
          isOpen
            ? 'fixed inset-y-0 left-0 translate-x-0 shadow-lg'
            : 'fixed inset-y-0 left-0 -translate-x-full lg:static lg:translate-x-0'
        }`}
      >
        <div className="space-y-5">
          {/* Section: Inspection Hub */}
          <div>
            <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase px-2 mb-2">
              Inspection Hub
            </div>
            <nav aria-label="Inspection Hub Navigation" className="space-y-1">
              {mainNav.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onClose}
                    className={`flex items-center justify-between px-2.5 py-2 rounded text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-[#0F172A] text-white shadow-xs font-semibold'
                        : 'text-[#334155] hover:bg-[#F1F5F9] hover:text-[#0F172A]'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-[#64748B]'}`}
                        aria-hidden="true"
                      />
                      <span>{item.label}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                          isActive
                            ? 'bg-[#1E293B] text-sky-200'
                            : 'bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}

                    {item.hasArrow && !item.badge && (
                      <ChevronRight
                        className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-[#94A3B8]'}`}
                        aria-hidden="true"
                      />
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Section: Verification Engine */}
          <div className="pt-3 border-t border-[#E2E8F0]">
            <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase px-2 mb-2">
              Verification Engine
            </div>

            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded p-2.5 space-y-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-semibold text-[#1E293B]">Corpus Integrity</span>
                <span className="font-mono font-bold text-[#0284C7]">100%</span>
              </div>
              <div className="w-full bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden" role="progressbar" aria-valuenow={100} aria-valuemin={0} aria-valuemax={100} aria-label="Corpus integrity 100%">
                <div className="bg-[#0284C7] h-full w-full rounded-full"></div>
              </div>
              <p className="text-[10px] text-[#64748B] leading-tight">
                Federal & State codified standards synchronized
              </p>
            </div>
          </div>

          {/* Section: Active Session Guard */}
          <div className="pt-3 border-t border-[#E2E8F0] space-y-2">
            <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase px-2">
              Active Session Guard
            </div>

            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded p-2.5 space-y-1.5 text-[10px] font-mono">
              <div className="flex items-center justify-between">
                <span className="text-[#64748B]">Zero-Retention:</span>
                <span className="text-[#059669] font-bold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
                  ARMED
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#64748B]">RAM Scrub:</span>
                <span className="text-[#0F172A]">On Disconnect</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#64748B]">Memory Digest:</span>
                <span className="text-[#0284C7] truncate max-w-[100px]">0x82f4...d901</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Utility Links */}
        <div className="pt-4 border-t border-[#E2E8F0] space-y-1 mt-4">
          <Link
            href="/settings#audit"
            className="flex items-center gap-2 px-2.5 py-2 text-xs font-medium text-[#475569] hover:text-[#0F172A] hover:bg-[#F1F5F9] rounded transition-colors"
          >
            <ShieldCheck className="w-4 h-4 text-[#64748B]" aria-hidden="true" />
            <span>Audit Trail Log</span>
          </Link>
          <Link
            href="/settings"
            className={`flex items-center gap-2 px-2.5 py-2 text-xs font-medium rounded transition-colors ${
              pathname === '/settings'
                ? 'bg-[#0F172A] text-white'
                : 'text-[#475569] hover:text-[#0F172A] hover:bg-[#F1F5F9]'
            }`}
          >
            <Sliders className="w-4 h-4 text-[#64748B]" aria-hidden="true" />
            <span>Engine Preferences</span>
          </Link>
        </div>
      </aside>
    </>
  );
};
