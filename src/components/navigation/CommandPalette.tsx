'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  FileText,
  Scale,
  GitCompare,
  MessageSquareQuote,
  CheckSquare,
  Zap,
  ArrowRight,
  X,
  BookOpen,
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Open handled outside or toggled
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const quickActions = [
    {
      title: 'Analyze Dossier',
      description: 'Open full document intelligence dashboard',
      icon: FileText,
      href: '/analyze',
      category: 'Workspace',
    },
    {
      title: 'Sample Legal Document Library',
      description: 'Browse 200 standardized contracts and covenants',
      icon: BookOpen,
      href: '/library',
      category: 'Corpus',
    },
    {
      title: 'Public Law Corpus',
      description: 'Search 285 federal, Delaware, CA & UCC statutes',
      icon: Scale,
      href: '/public-law',
      category: 'Corpus',
    },
    {
      title: 'Clause Compare & Redlining',
      description: 'Side-by-side token differencing and risk shifts',
      icon: GitCompare,
      href: '/compare',
      category: 'Tools',
    },
    {
      title: 'Document-Grounded Q&A',
      description: 'Interrogate active contract with zero hallucination',
      icon: MessageSquareQuote,
      href: '/ask',
      category: 'Tools',
    },
    {
      title: 'Counsel Preparation Brief & Checklist',
      description: 'Prioritized lawyer agenda and pre-signature checklist',
      icon: CheckSquare,
      href: '/brief',
      category: 'Tools',
    },
    {
      title: 'Pre-Load: Enterprise SaaS MSA (18 pgs)',
      description: 'Instant zero-OCR preload for tech services contract',
      icon: Zap,
      href: '/analyze',
      category: 'Quick Preloaders',
    },
  ];

  const filtered = query.trim()
    ? quickActions.filter(
        (a) =>
          a.title.toLowerCase().includes(query.toLowerCase()) ||
          a.description.toLowerCase().includes(query.toLowerCase()) ||
          a.category.toLowerCase().includes(query.toLowerCase())
      )
    : quickActions;

  const handleSelect = (href: string) => {
    router.push(href);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div role="dialog" aria-modal="true" aria-label="Command Palette" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal w-full max-w-2xl overflow-hidden z-10">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
          <Search className="w-4 h-4 text-[#64748B] shrink-0" aria-hidden="true" />
          <label htmlFor="command-palette-search" className="sr-only">Search commands, corpus, statutes, or clauses</label>
          <input
            id="command-palette-search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands, corpus, statutes, or clauses (e.g. § 8.3, MSA, Delaware)..."
            className="w-full bg-transparent px-3 py-3.5 text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none"
            autoFocus
          />
          <button
            onClick={onClose}
            className="p-1 text-[#94A3B8] hover:text-[#0F172A] rounded focus:outline-none focus:ring-2 focus:ring-[#0284C7]"
            aria-label="Close command palette"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        {/* Results List */}
        <div role="listbox" aria-label="Search results" className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-xs text-[#64748B]">
              No results found for &ldquo;{query}&rdquo;.
            </div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleSelect(item.href)}
                  className="w-full flex items-center justify-between p-2.5 rounded hover:bg-[#F1F5F9] text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#0F172A] flex items-center gap-2">
                        <span>{item.title}</span>
                        <span className="text-[10px] font-mono font-normal text-[#64748B] bg-[#E2E8F0] px-1.5 py-0.2 rounded">
                          {item.category}
                        </span>
                      </div>
                      <div className="text-[11px] text-[#64748B] line-clamp-1">
                        {item.description}
                      </div>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-[#94A3B8] group-hover:text-[#0284C7] group-hover:translate-x-0.5 transition-all shrink-0" aria-hidden="true" />
                </button>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="border-t border-[#E2E8F0] px-4 py-2 bg-[#F8FAFC] flex items-center justify-between text-[11px] text-[#64748B] font-mono">
          <span>Navigation &amp; Execution Shortcuts</span>
          <div className="flex items-center gap-3">
            <span>[ESC] to close</span>
            <span>[↵] to execute</span>
          </div>
        </div>
      </div>
    </div>
  );
};
