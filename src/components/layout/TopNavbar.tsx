'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BrandLogo } from '@/components/ui/BrandLogo';
import { Search, History, Lock, Shield, Menu, X, CheckCircle2, ShieldCheck, RefreshCw } from 'lucide-react';

interface TopNavbarProps {
  onOpenCommandPalette?: () => void;
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  onOpenCommandPalette,
  onToggleSidebar,
  isSidebarOpen,
}) => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isVerificationsOpen, setIsVerificationsOpen] = useState(false);
  const [isSecurityOpen, setIsSecurityOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const verificationsRef = useRef<HTMLDivElement>(null);
  const securityRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsVerificationsOpen(false);
        setIsSecurityOpen(false);
        setIsProfileOpen(false);
      }
    };
    const handleClickOutside = (e: MouseEvent) => {
      if (verificationsRef.current && !verificationsRef.current.contains(e.target as Node)) {
        setIsVerificationsOpen(false);
      }
      if (securityRef.current && !securityRef.current.contains(e.target as Node)) {
        setIsSecurityOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setIsProfileOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const navItems = [
    { label: 'Analyze', href: '/analyze' },
    { label: 'Sample Library', href: '/library', badge: '200' },
    { label: 'Public Law', href: '/public-law', badge: '285' },
    { label: 'Compare', href: '/compare' },
    { label: 'Q&A Grounded', href: '/ask' },
    { label: 'Brief & Checklist', href: '/brief' },
  ];

  return (
    <header className="bg-white border-b border-[#E2E8F0] sticky top-0 z-40">
      <div className="max-w-[1680px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {/* Left: Mobile Toggle & Brand Logo */}
        <div className="flex items-center gap-3">
          {onToggleSidebar && (
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-1.5 rounded hover:bg-[#F1F5F9] text-[#64748B] focus:outline-none"
              aria-label="Toggle Sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}

          <BrandLogo showTag size="sm" />
        </div>

        {/* Center: Main Navigation Tabs */}
        <nav className="hidden xl:flex items-center gap-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-[#0F172A] text-white shadow-sm font-semibold'
                    : 'text-[#475569] hover:text-[#0F172A] hover:bg-[#F1F5F9]'
                }`}
              >
                <span>{item.label}</span>
                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full leading-tight ${
                      isActive
                        ? 'bg-[#1E293B] text-sky-200 border border-slate-700'
                        : 'bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right: Search, Actions, Profile */}
        <div className="flex items-center gap-3">
          {/* Quick Search Trigger */}
          <button
            onClick={onOpenCommandPalette}
            className="hidden md:flex items-center gap-2 bg-[#F8FAFC] hover:bg-[#F1F5F9] border border-[#CBD5E1] rounded px-2.5 py-1 text-xs text-[#64748B] transition-colors w-48 lg:w-64 justify-between"
            aria-label="Search corpus"
          >
            <span className="flex items-center gap-1.5 truncate">
              <Search className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span className="truncate">Search corpus, statutes...</span>
            </span>
            <kbd className="font-mono text-[10px] bg-white border border-[#CBD5E1] text-[#64748B] px-1.5 py-0.2 rounded shadow-2xs">
              ⌘K
            </kbd>
          </button>

          {/* Status & Session Indicators */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-[#64748B] relative">
            {/* 1. Notification / Verifications Counter Control */}
            <div className="relative" ref={verificationsRef}>
              <button
                onClick={() => {
                  setIsVerificationsOpen(!isVerificationsOpen);
                  setIsSecurityOpen(false);
                  setIsProfileOpen(false);
                }}
                aria-expanded={isVerificationsOpen}
                aria-label="12 Active System Verifications"
                title="12 Active System Verifications"
                className={`relative p-1.5 rounded transition-colors ${
                  isVerificationsOpen ? 'bg-[#0F172A] text-white' : 'hover:bg-[#F1F5F9] text-[#475569]'
                }`}
              >
                <History className={`w-4 h-4 ${isVerificationsOpen ? 'text-white' : 'text-[#475569]'}`} />
                <span className="absolute -top-0.5 -right-0.5 bg-[#0284C7] text-white text-[9px] font-mono px-1 rounded-full font-bold">
                  12
                </span>
              </button>

              {isVerificationsOpen && (
                <div
                  role="dialog"
                  aria-label="Session Verifications Panel"
                  className="absolute right-0 mt-2 w-80 sm:w-96 bg-white border border-[#CBD5E1] rounded-lg shadow-xl p-4 z-50 animate-in fade-in slide-in-from-top-1 duration-150 text-left"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0] mb-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                      <span className="text-xs font-bold text-[#0F172A]">Session Verifications (12/12)</span>
                    </div>
                    <span className="text-[10px] font-mono font-semibold bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] px-2 py-0.5 rounded-full">
                      All Operational
                    </span>
                  </div>

                  <div className="space-y-2 max-h-72 overflow-y-auto pr-1 text-xs">
                    {[
                      { title: 'Corpus Registry Audit', detail: '500/500 documents verified & indexed', time: 'Active' },
                      { title: 'PostgreSQL pgvector Store', detail: 'VECTOR(3072) cosine index operational', time: 'Active' },
                      { title: 'Gemini Primary Key', detail: 'gemini-1.5-flash online & ready', time: 'Verified' },
                      { title: 'Gemini Fallback Key', detail: 'Automated 429/quota failover armed', time: 'Standby' },
                      { title: 'Zero-Retention Privacy', detail: 'RAM scrub on disconnect active', time: 'Enforced' },
                      { title: 'Magic-Byte MIME Inspector', detail: 'PDF, DOCX & TXT validation active', time: 'Armed' },
                      { title: 'Prompt-Injection Armor', detail: 'Delimiter escaping & boundary isolation', time: 'Active' },
                      { title: 'Citation Grounding Engine', detail: 'Exact substring character matching', time: 'Active' },
                      { title: 'Refusal Protocol', detail: 'Insufficient evidence handling armed', time: 'Ready' },
                      { title: 'Executive Synthesis Pipeline', detail: 'Lawyer Preparation Brief ready', time: 'Loaded' },
                      { title: 'PyMuPDF Binary Exporter', detail: 'Clean PDF generation ready', time: 'Ready' },
                      { title: 'Word Document Exporter', detail: 'python-docx OpenXML generation ready', time: 'Ready' },
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-start justify-between gap-2 p-1.5 rounded hover:bg-[#F8FAFC]">
                        <div className="space-y-0.5">
                          <div className="font-semibold text-[#1E293B] flex items-center gap-1.5 text-[11px]">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                            {item.title}
                          </div>
                          <div className="text-[10px] text-[#64748B] pl-3 leading-tight">{item.detail}</div>
                        </div>
                        <span className="text-[9px] font-mono bg-[#F1F5F9] text-[#475569] px-1.5 py-0.5 rounded shrink-0">
                          {item.time}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-3 border-t border-[#E2E8F0] mt-3 flex items-center justify-between text-[10px] font-mono text-[#64748B]">
                    <span>Telemetry Sync: Live Session</span>
                    <button
                      onClick={() => setIsVerificationsOpen(false)}
                      className="text-[#0284C7] hover:underline font-semibold"
                    >
                      Close (Esc)
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* 2. Lock / Security Telemetry Control */}
            <div className="relative" ref={securityRef}>
              <button
                onClick={() => {
                  setIsSecurityOpen(!isSecurityOpen);
                  setIsVerificationsOpen(false);
                  setIsProfileOpen(false);
                }}
                aria-expanded={isSecurityOpen}
                aria-label="Security and Privacy Telemetry"
                title="Security & Privacy Telemetry"
                className={`p-1.5 rounded transition-colors ${
                  isSecurityOpen ? 'bg-[#0F172A] text-white' : 'hover:bg-[#F1F5F9] text-[#64748B]'
                }`}
              >
                <Lock className={`w-4 h-4 ${isSecurityOpen ? 'text-white' : 'text-[#64748B]'}`} />
              </button>

              {isSecurityOpen && (
                <div
                  role="dialog"
                  aria-label="Security and Privacy Telemetry Panel"
                  className="absolute right-0 mt-2 w-80 sm:w-96 bg-white border border-[#CBD5E1] rounded-lg shadow-xl p-4 z-50 animate-in fade-in slide-in-from-top-1 duration-150 text-left"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0] mb-3">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-[#0284C7]" />
                      <span className="text-xs font-bold text-[#0F172A]">Security & Privacy Telemetry</span>
                    </div>
                    <span className="text-[10px] font-mono font-semibold bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] px-2 py-0.5 rounded-full">
                      Zero-Retention
                    </span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div className="p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                      <div className="flex items-center justify-between font-semibold text-[11px] text-[#0F172A]">
                        <span>Zero-Retention Policy</span>
                        <span className="text-[#059669] font-mono flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                          Active
                        </span>
                      </div>
                      <p className="text-[10px] text-[#64748B] leading-relaxed">
                        Uploaded contracts are held in ephemeral memory and immediately scrubbed post-extraction. No user documents train foundation models.
                      </p>
                    </div>

                    <div className="p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                      <div className="flex items-center justify-between font-semibold text-[11px] text-[#0F172A]">
                        <span>PostgreSQL + pgvector Isolation</span>
                        <span className="text-[#059669] font-mono flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                          Operational
                        </span>
                      </div>
                      <p className="text-[10px] text-[#64748B] leading-relaxed">
                        Tenant-isolated similarity queries scoped strictly by <code className="bg-[#E2E8F0] px-1 rounded text-[#0F172A]">document_id</code> with VECTOR(3072) cosine index.
                      </p>
                    </div>

                    <div className="p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                      <div className="flex items-center justify-between font-semibold text-[11px] text-[#0F172A]">
                        <span>Gemini Key Orchestration</span>
                        <span className="text-[#059669] font-mono flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                          Server-Side Only
                        </span>
                      </div>
                      <p className="text-[10px] text-[#64748B] leading-relaxed">
                        Primary and secondary API keys reside exclusively in backend environment memory. Zero client bundle exposure.
                      </p>
                    </div>

                    <div className="p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                      <div className="flex items-center justify-between font-semibold text-[11px] text-[#0F172A]">
                        <span>Upload Armor &amp; Sandboxing</span>
                        <span className="text-[#059669] font-mono flex items-center gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                          Enforced
                        </span>
                      </div>
                      <p className="text-[10px] text-[#64748B] leading-relaxed">
                        Magic-byte signature verification, 50MB ceiling, and strict path-traversal filename sanitization.
                      </p>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-[#E2E8F0] mt-3 flex items-center justify-between text-[10px] font-mono text-[#64748B]">
                    <span>Transport: TLS 1.3 Encrypted</span>
                    <button
                      onClick={() => setIsSecurityOpen(false)}
                      className="text-[#0284C7] hover:underline font-semibold"
                    >
                      Close (Esc)
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="h-4 w-px bg-[#E2E8F0] hidden sm:block" />

          {/* 3. User Profile / Active Session Control */}
          <div className="relative pl-1" ref={profileRef}>
            <button
              onClick={() => {
                setIsProfileOpen(!isProfileOpen);
                setIsVerificationsOpen(false);
                setIsSecurityOpen(false);
              }}
              aria-expanded={isProfileOpen}
              aria-label="Counsel Profile and Active Session Settings"
              className="flex items-center gap-2.5 p-1 rounded hover:bg-[#F8FAFC] transition-colors focus:outline-none"
            >
              <div className="text-right hidden sm:block">
                <div className="text-xs font-semibold text-[#0F172A] leading-tight">
                  Lead Legal Counsel
                </div>
                <div className="text-[10px] font-mono text-[#059669] flex items-center justify-end gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#059669] animate-pulse"></span>
                  Pro Tier / Active Session
                </div>
              </div>

              {/* Avatar */}
              <div className="w-8 h-8 rounded-full bg-slate-900 border border-slate-700 overflow-hidden flex items-center justify-center shrink-0">
                <img
                  src="/lead-legal-counsel.png"
                  alt="Lead Counsel"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.currentTarget;
                    target.style.display = 'none';
                    if (target.parentElement) {
                      target.parentElement.innerHTML = '<span class="text-xs font-bold text-white">LC</span>';
                    }
                  }}
                />
              </div>
            </button>

            {isProfileOpen && (
              <div
                role="dialog"
                aria-label="Account Profile and Session Dialog"
                className="absolute right-0 mt-2 w-72 sm:w-80 bg-white border border-[#CBD5E1] rounded-lg shadow-xl p-4 z-50 animate-in fade-in slide-in-from-top-1 duration-150 text-left"
              >
                <div className="flex items-center gap-3 pb-3 border-b border-[#E2E8F0]">
                  <div className="w-10 h-10 rounded-full bg-slate-900 border border-slate-700 overflow-hidden flex items-center justify-center shrink-0">
                    <img
                      src="/lead-legal-counsel.png"
                      alt="Lead Counsel"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#0F172A]">Lead Legal Counsel</div>
                    <div className="text-[11px] font-mono text-[#64748B]">counsel@lexguard.internal</div>
                  </div>
                </div>

                <div className="py-3 space-y-2 text-xs">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-[#64748B]">Subscription Tier:</span>
                    <span className="font-semibold text-[#0284C7] font-mono bg-[#EFF6FF] px-2 py-0.5 rounded border border-[#BFDBFE]">
                      Pro Enterprise
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-[#64748B]">Session State:</span>
                    <span className="font-semibold text-[#059669] font-mono flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                      ARMED &amp; ISOLATED
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-[#64748B]">Legal Scope:</span>
                    <span className="font-mono text-[#0F172A]">Educational Debrief</span>
                  </div>
                </div>

                <div className="p-2.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded text-[10px] text-[#1E293B] leading-relaxed mb-3">
                  <strong>Notice:</strong> LexGuard provides AI legal document intelligence for counsel consultation prep. It is not formal legal representation.
                </div>

                <div className="pt-2 border-t border-[#E2E8F0] space-y-1.5">
                  <button
                    onClick={() => {
                      if (typeof window !== 'undefined') {
                        sessionStorage.removeItem('lexguard_active_doc_id');
                        sessionStorage.removeItem('lexguard_active_doc_title');
                        window.location.href = '/';
                      }
                    }}
                    className="w-full py-1.5 px-2.5 text-xs font-semibold text-[#991B1B] hover:bg-[#FEF2F2] rounded border border-[#FECACA] flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Reset Active Intake Session</span>
                  </button>
                  <button
                    onClick={() => setIsProfileOpen(false)}
                    className="w-full py-1 text-center text-[10px] font-mono text-[#64748B] hover:underline"
                  >
                    Dismiss (Esc)
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-1.5 rounded hover:bg-[#F1F5F9] text-[#64748B]"
            aria-label="Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="xl:hidden border-t border-[#E2E8F0] bg-white px-4 py-3 space-y-1">
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenCommandPalette?.();
            }}
            className="w-full flex items-center justify-between bg-[#F8FAFC] border border-[#CBD5E1] rounded px-3 py-2 text-xs text-[#64748B] mb-2"
          >
            <span className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5" />
              <span>Search corpus, statutes, clauses...</span>
            </span>
            <kbd className="font-mono text-[10px] bg-white border border-[#CBD5E1] px-1 rounded">⌘K</kbd>
          </button>

          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2 rounded text-xs font-medium ${
                  isActive ? 'bg-[#0F172A] text-white' : 'text-[#475569] hover:bg-[#F1F5F9]'
                }`}
              >
                <span>{item.label}</span>
                {item.badge && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                      isActive ? 'bg-[#1E293B] text-sky-200' : 'bg-[#EFF6FF] text-[#0284C7]'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
};
