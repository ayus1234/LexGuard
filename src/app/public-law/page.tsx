'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  publicLawJurisdictions,
  publicLawCategories,
  samplePublicLaws,
} from '@/lib/mock-data/public-law';
import { PublicLawDocument } from '@/types';
import {
  Scale,
  Search,
  X,
  BookOpen,
  ShieldCheck,
  ChevronRight,
  ExternalLink,
  SlidersHorizontal,
  Bookmark,
  Sparkles,
} from 'lucide-react';

export default function PublicLawPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('All Jurisdictions');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [activeStatuteModal, setActiveStatuteModal] = useState<PublicLawDocument | null>(null);

  const filteredLaws = samplePublicLaws.filter((law) => {
    const matchesSearch =
      law.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      law.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      law.summary.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesJurisdiction =
      selectedJurisdiction === 'All Jurisdictions' || law.jurisdiction === selectedJurisdiction;

    const matchesCategory =
      selectedCategory === 'All Categories' || law.category === selectedCategory;

    return matchesSearch && matchesJurisdiction && matchesCategory;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Header Banner */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-[#0284C7] shrink-0" aria-hidden="true" />
          <span>
            <strong className="font-semibold text-[#0F172A]">Public Statutory Corpus:</strong>{' '}
            285 Codified Federal, State, and Model Legal Frameworks for automated compliance benchmarking.
          </span>
        </div>
        <div className="text-[11px] font-mono text-[#059669] shrink-0 flex items-center gap-1 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
          Corpus Integrity: 100% Synchronized
        </div>
      </div>

      {/* 2. Page Title Area */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
            REGULATORY REPOSITORY / 04 / Public Law Index
          </div>
          <h1 className="text-3xl font-display font-bold text-[#0F172A] tracking-tight">
            Public Legal Document Library
          </h1>
          <p className="text-xs sm:text-sm text-[#475569] max-w-2xl leading-relaxed">
            Codified statutes, model corporate acts, uniform commercial codes, and regulatory frameworks used by LexGuard to benchmark private agreements against statutory floors.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 text-right">
            <div className="text-xs font-mono text-[#64748B]">Catalog Size</div>
            <div className="text-xl font-display font-bold text-[#0F172A]">285 Statutes</div>
          </div>
        </div>
      </div>

      {/* 3. Search & Filters */}
      <div className="space-y-3">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search public statutes, UCC sections, DGCL corporate law, or California codes (e.g. § 102(b)(7), UCC 2-719, non-compete)..."
            className="w-full pl-10 pr-10 py-3 bg-white border border-[#CBD5E1] rounded-lg text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] shadow-2xs"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-[#94A3B8] hover:text-[#0F172A]"
            >
              <X className="w-4 h-4" aria-hidden="true" />
            </button>
          )}
        </div>

        {/* Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <select
            value={selectedJurisdiction}
            onChange={(e) => setSelectedJurisdiction(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            {publicLawJurisdictions.map((j) => (
              <option key={j} value={j}>
                Jurisdiction: {j}
              </option>
            ))}
          </select>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            {publicLawCategories.map((c) => (
              <option key={c} value={c}>
                Category: {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 4. Statutes Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredLaws.map((law) => (
          <div
            key={law.id}
            className="scaffold-card p-5 space-y-4 border border-[#CBD5E1] hover:border-[#94A3B8] transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              {/* Badges */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                  {law.jurisdiction}
                </span>
                <span className="text-[10px] font-mono text-[#64748B]">Year: {law.year}</span>
              </div>

              {/* Title & Code */}
              <div>
                <div className="text-[11px] font-mono text-[#0284C7] font-semibold">{law.code}</div>
                <h3 className="text-base font-display font-bold text-[#0F172A] mt-0.5 leading-snug">
                  {law.title}
                </h3>
                <p className="text-xs text-[#475569] mt-2 leading-relaxed line-clamp-3">
                  {law.summary}
                </p>
              </div>

              {/* Relevance box */}
              <div className="p-2.5 rounded bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <div className="text-[10px] font-mono font-bold text-[#0F172A] uppercase">
                  Contract Analysis Role:
                </div>
                <p className="text-[11px] text-[#334155] leading-normal">{law.relevance}</p>
              </div>
            </div>

            {/* Bottom: Precedents & Action */}
            <div className="pt-3 border-t border-[#E2E8F0] flex items-center justify-between">
              <span className="text-[10px] font-mono text-[#64748B]">
                {law.precedentCount.toLocaleString()} Precedents Indexed
              </span>

              <button
                onClick={() => setActiveStatuteModal(law)}
                className="inline-flex items-center gap-1 text-xs text-[#0284C7] hover:underline font-medium"
              >
                <span>Inspect Statute</span>
                <ChevronRight className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Statute Inspection Modal */}
      {activeStatuteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs"
            onClick={() => setActiveStatuteModal(null)}
          />
          <div role="dialog" aria-modal="true" aria-label="Statute inspection detail" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-xl w-full p-6 space-y-4 z-10">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#0284C7] font-semibold">
                  {activeStatuteModal.jurisdiction} • {activeStatuteModal.category}
                </span>
                <h3 className="text-lg font-display font-bold text-[#0F172A]">
                  {activeStatuteModal.title}
                </h3>
                <div className="text-xs font-mono text-[#64748B]">{activeStatuteModal.code}</div>
              </div>
              <button
                onClick={() => setActiveStatuteModal(null)}
                className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A]"
                aria-label="Close statute detail"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                <div className="text-[10px] font-mono text-[#64748B] uppercase">Statutory Summary</div>
                <p className="text-[#334155] leading-relaxed">{activeStatuteModal.summary}</p>
              </div>

              <div className="p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded space-y-1">
                <div className="text-[10px] font-mono text-[#0284C7] uppercase font-semibold">
                  Benchmark Relevance
                </div>
                <p className="text-[#1E293B] leading-relaxed">{activeStatuteModal.relevance}</p>
              </div>
            </div>

            <div className="pt-3 border-t border-[#E2E8F0] flex justify-end gap-2">
              <button
                onClick={() => setActiveStatuteModal(null)}
                className="px-4 py-2 text-xs text-[#64748B] hover:text-[#0F172A] rounded border border-[#CBD5E1]"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setActiveStatuteModal(null);
                  router.push('/analyze');
                }}
                className="px-4 py-2 text-xs font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B]"
              >
                Cross-Reference Against Active Contract
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
