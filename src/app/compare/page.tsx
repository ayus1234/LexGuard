'use client';

import React, { useState } from 'react';
import { mockComparisonResult } from '@/lib/mock-data/comparison';
import {
  GitCompare,
  Download,
  Lock,
  Unlock,
  AlertTriangle,
  CheckCircle2,
  FileText,
  SlidersHorizontal,
  ChevronRight,
  ShieldAlert,
  ArrowRight,
  Info,
  Check,
  X,
  FileCheck,
  Sparkles,
} from 'lucide-react';

export default function CompareRedliningPage() {
  const data = mockComparisonResult;
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLocked, setIsLocked] = useState(true);
  const [granularity, setGranularity] = useState<'token' | 'char'>('token');
  const [activeDiffId, setActiveDiffId] = useState('diff-8-3');
  const [decisionFeedback, setDecisionFeedback] = useState<string | null>(null);

  const categories = [
    { id: 'all', label: 'All Differences', count: 34 },
    { id: 'liability', label: 'Liability & Caps', count: 4 },
    { id: 'termination', label: 'Termination & Rollover', count: 6 },
    { id: 'ip', label: 'Data Ownership & IP', count: 5 },
    { id: 'financial', label: 'Financial & Escalators', count: 3 },
    { id: 'dispute', label: 'Dispute Resolution', count: 2 },
  ];

  const handleAction = (clause: string, action: string) => {
    setDecisionFeedback(`Recorded decision for ${clause}: "${action}". Staged for counsel brief.`);
    setTimeout(() => setDecisionFeedback(null), 3500);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Header Banner */}
      <div className="bg-[#FFFBEB] border border-[#FCD34D] border-l-4 border-l-[#D97706] rounded-r-lg p-3 text-xs text-[#92400E] flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-[#D97706] shrink-0" />
          <span>
            <strong className="font-semibold text-[#0F172A]">Institutional Redline &amp; Statutory Risk Intelligence:</strong>{' '}
            Automated word-level token reconciliation active. Output reflects automated algorithmic discrepancy analysis and does not constitute formal legal counsel.
          </span>
        </div>
        <div className="text-[11px] font-mono text-[#0284C7] shrink-0 flex items-center gap-1 font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]"></span>
          SHA-256 Validated Matching
        </div>
      </div>

      {/* Decision feedback alert toast */}
      {decisionFeedback && (
        <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded-lg text-xs font-mono text-[#065F46] flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#059669]" />
            <span>{decisionFeedback}</span>
          </div>
          <button onClick={() => setDecisionFeedback(null)} className="hover:text-black">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 2. Page Title Area */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
            COMPARISON MODE: Doc A vs. Doc B (Reconciliation Complete)
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-[#0F172A] tracking-tight">
            Document Comparison &amp; Clause Delta Matrix
          </h1>
          <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
            Automated word-level redlining, deleted customer protections, added vendor obligations, and shifted risk baselines.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setGranularity(granularity === 'token' ? 'char' : 'token')}
            className="px-3 py-1.5 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded flex items-center gap-1.5"
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-[#64748B]" />
            <span>Granularity: {granularity === 'token' ? 'Token-Level' : 'Character-Level'}</span>
          </button>

          <button
            onClick={() => alert('Exporting redline comparison summary (.docx)...')}
            className="px-4 py-1.5 text-xs font-semibold text-white bg-[#0284C7] hover:bg-[#0369A1] rounded flex items-center gap-1.5 transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Redline PDF (.docx)</span>
          </button>
        </div>
      </div>

      {/* 3. 5 Delta Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-1">
          <div className="text-[10px] font-mono text-[#64748B] uppercase font-bold">TOTAL CHANGES</div>
          <div className="text-2xl font-display font-bold text-[#0F172A]">{data.totalChanges}</div>
          <div className="text-[10px] font-mono text-[#64748B]">Deltas</div>
        </div>

        <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-1">
          <div className="text-[10px] font-mono text-[#DC2626] uppercase font-bold flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-[#DC2626]" />
            HIGH RISK SHIFTS
          </div>
          <div className="text-2xl font-display font-bold text-[#DC2626]">{data.highRiskShifts}</div>
          <div className="text-[10px] font-mono text-[#991B1B]">Unfavorable</div>
        </div>

        <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-1">
          <div className="text-[10px] font-mono text-[#059669] uppercase font-bold">ADDED CLAUSES</div>
          <div className="text-2xl font-display font-bold text-[#059669]">+{data.addedClauses}</div>
          <div className="text-[10px] font-mono text-[#065F46]">New Sections</div>
        </div>

        <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-1">
          <div className="text-[10px] font-mono text-[#DC2626] uppercase font-bold">REMOVED CLAUSES</div>
          <div className="text-2xl font-display font-bold text-[#DC2626]">{data.removedClauses}</div>
          <div className="text-[10px] font-mono text-[#991B1B]">Omitted</div>
        </div>

        <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-1 col-span-2 sm:col-span-1">
          <div className="text-[10px] font-mono text-[#D97706] uppercase font-bold">MODIFICATIONS</div>
          <div className="text-2xl font-display font-bold text-[#D97706]">{data.modifications}</div>
          <div className="text-[10px] font-mono text-[#92400E]">Adjustments</div>
        </div>
      </div>

      {/* 4. Document Selector Bar with Synchronized Lock */}
      <div className="scaffold-card p-4 border border-[#CBD5E1] bg-white flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Document A */}
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold text-[#0284C7] uppercase">
              DOCUMENT A • BASELINE
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1]">
              {data.docA.version}
            </span>
          </div>
          <div className="text-xs font-display font-bold text-[#0F172A] truncate">
            {data.docA.name}
          </div>
          <div className="text-[11px] text-[#64748B]">{data.docA.description}</div>
        </div>

        {/* Lock Button */}
        <div className="flex items-center justify-center shrink-0 py-1 md:py-0">
          <button
            onClick={() => setIsLocked(!isLocked)}
            className={`px-3 py-1.5 text-xs font-mono rounded border flex items-center gap-1.5 transition-colors ${
              isLocked
                ? 'bg-[#EFF6FF] border-[#BFDBFE] text-[#0284C7]'
                : 'bg-white border-[#CBD5E1] text-[#64748B]'
            }`}
          >
            {isLocked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
            <span>Synchronized Lock</span>
          </button>
        </div>

        {/* Document B */}
        <div className="flex-1 space-y-1 md:text-right">
          <div className="flex items-center md:justify-end gap-2">
            <span className="text-[10px] font-mono font-bold text-[#D97706] uppercase">
              DOCUMENT B • COUNTERPARTY
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
              {data.docB.version}
            </span>
          </div>
          <div className="text-xs font-display font-bold text-[#0F172A] truncate">
            {data.docB.name}
          </div>
          <div className="text-[11px] text-[#64748B]">{data.docB.description}</div>
        </div>
      </div>

      {/* 5. Difference Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-1 text-xs">
        {categories.map((cat) => {
          const isActive = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-full font-medium whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                isActive
                  ? 'bg-[#0F172A] text-white shadow-2xs font-semibold'
                  : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
              }`}
            >
              <span>{cat.label}</span>
              <span
                className={`text-[10px] font-mono px-1 rounded-full ${
                  isActive ? 'bg-slate-800 text-sky-300' : 'bg-white text-[#64748B]'
                }`}
              >
                {cat.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* 6. Comparison Content Area (Clause Diffs + Right Sidebar) */}
      <div className="grid lg:grid-cols-12 gap-5 items-start">
        {/* Left 8 Cols: Clause Diffs */}
        <div className="lg:col-span-8 space-y-5">
          {data.diffs.map((diff) => (
            <div
              key={diff.id}
              id={diff.id}
              className={`scaffold-card border rounded-lg overflow-hidden transition-all ${
                activeDiffId === diff.id ? 'border-[#0284C7] ring-1 ring-[#0284C7]' : 'border-[#CBD5E1]'
              }`}
            >
              {/* Diff Header */}
              <div className="border-b border-[#E2E8F0] bg-[#F8FAFC] px-4 py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-[#0F172A] bg-white border border-[#CBD5E1] px-2 py-0.5 rounded">
                    {diff.section}
                  </span>
                  <h3 className="text-xs font-display font-bold text-[#0F172A]">{diff.title}</h3>
                </div>

                <span
                  className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${
                    diff.badgeType === 'critical'
                      ? 'bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]'
                      : 'bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]'
                  }`}
                >
                  {diff.badgeText}
                </span>
              </div>

              {/* Side-by-Side Comparison Wells */}
              <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[#E2E8F0] p-4 text-xs font-mono leading-relaxed">
                {/* Baseline Box */}
                <div className="space-y-2 pr-0 md:pr-3 pb-3 md:pb-0">
                  <div className="flex items-center justify-between text-[10px] text-[#64748B] pb-1 border-b border-[#F1F5F9]">
                    <span className="font-bold text-[#0F172A]">{diff.baselineVersion}</span>
                    <span className="text-[#0284C7]">{diff.baselineLabel}</span>
                  </div>
                  <div
                    dangerouslySetInnerHTML={{ __html: diff.baselineHtml }}
                    className="text-[#334155]"
                  />
                </div>

                {/* Counterparty Redline Box */}
                <div className="space-y-2 pl-0 md:pl-3 pt-3 md:pt-0">
                  <div className="flex items-center justify-between text-[10px] text-[#64748B] pb-1 border-b border-[#F1F5F9]">
                    <span className="font-bold text-[#0F172A]">{diff.counterpartyVersion}</span>
                    <span className="text-[#D97706]">{diff.counterpartyLabel}</span>
                  </div>
                  <div
                    dangerouslySetInnerHTML={{ __html: diff.counterpartyHtml }}
                    className="text-[#334155]"
                  />
                </div>
              </div>

              {/* Algorithmic Risk Impact Calculation Callout */}
              <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0] space-y-2.5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] font-mono">
                  <span className="font-bold text-[#0F172A]">{diff.riskCalculation.title}</span>
                  <span className="text-[#DC2626] font-semibold">
                    {diff.riskCalculation.capImpact}
                  </span>
                </div>

                <div className="text-xs space-y-1">
                  <div className="font-semibold text-[#0F172A]">
                    {diff.riskCalculation.subhead}:{' '}
                    <span className="font-normal text-[#475569]">
                      {diff.riskCalculation.description}
                    </span>
                  </div>
                  <p className="text-[11px] font-mono text-[#0284C7]">
                    {diff.riskCalculation.recommendation}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="pt-2 flex flex-wrap items-center justify-end gap-2">
                  <button
                    onClick={() => handleAction(diff.section, diff.actions.primaryText)}
                    className="px-3 py-1.5 text-xs font-semibold bg-white border border-[#CBD5E1] text-[#0F172A] hover:bg-[#F1F5F9] rounded transition-colors"
                  >
                    {diff.actions.primaryText}
                  </button>
                  <button
                    onClick={() => handleAction(diff.section, diff.actions.secondaryText)}
                    className="px-3 py-1.5 text-xs font-semibold bg-[#0F172A] text-white hover:bg-[#1E293B] rounded transition-colors"
                  >
                    {diff.actions.secondaryText}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Right 4 Cols: Delta Navigator & Execution Desk */}
        <div className="lg:col-span-4 space-y-4">
          {/* Delta Navigator */}
          <div className="scaffold-card border border-[#CBD5E1] p-4 space-y-3 bg-white">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-2">
              <h3 className="text-xs font-display font-bold text-[#0F172A]">Delta Navigator</h3>
              <span className="text-[10px] font-mono text-[#64748B]">4 of 34 Visible</span>
            </div>

            <div className="space-y-1.5">
              {data.deltaNav.map((nav) => (
                <button
                  key={nav.id}
                  onClick={() => {
                    setActiveDiffId(nav.id);
                    const el = document.getElementById(nav.id);
                    if (el) el.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className={`w-full p-2 rounded text-left flex items-start justify-between gap-2 transition-colors ${
                    activeDiffId === nav.id
                      ? 'bg-[#EFF6FF] border border-[#BFDBFE]'
                      : 'hover:bg-[#F8FAFC] border border-transparent'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`text-[9px] font-mono px-1 rounded font-bold ${
                          nav.severity === 'CRIT'
                            ? 'bg-red-100 text-red-700'
                            : nav.severity === 'MED'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {nav.severity}
                      </span>
                      <span className="text-xs font-bold text-[#0F172A]">{nav.section}</span>
                    </div>
                    <div className="text-[11px] text-[#64748B] line-clamp-1">{nav.summary}</div>
                  </div>

                  <span className="text-[10px] font-mono text-[#DC2626] font-semibold shrink-0">
                    {nav.badgeText}
                  </span>
                </button>
              ))}
            </div>

            <div className="pt-2 border-t border-[#E2E8F0] text-center">
              <button
                onClick={() => alert('Loading remaining 29 structural differences...')}
                className="text-[11px] font-mono text-[#0284C7] hover:underline"
              >
                View Remaining 29 Structural Differences →
              </button>
            </div>
          </div>

          {/* Redline Execution Desk */}
          <div className="scaffold-card border border-[#CBD5E1] p-4 space-y-3 bg-white">
            <h3 className="text-xs font-display font-bold text-[#0F172A] flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#0284C7]" />
              <span>Redline Execution Desk</span>
            </h3>

            <div className="space-y-2">
              <button
                onClick={() => alert('Compiling comprehensive counsel redline summary...')}
                className="w-full py-2 px-3 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors text-center"
              >
                Generate Counsel Redline Summary
              </button>

              <button
                onClick={() => alert('Exporting Word Track Changes redline file (.docx)...')}
                className="w-full py-2 px-3 text-xs font-semibold bg-white border border-[#CBD5E1] text-[#0F172A] hover:bg-[#F1F5F9] rounded transition-colors text-center"
              >
                Export Redline PDF (Word Track Changes)
              </button>

              <button
                onClick={() => alert('Flagged all 4 non-standard provisions for review.')}
                className="w-full py-2 px-3 text-xs font-semibold bg-white border border-[#CBD5E1] text-[#0F172A] hover:bg-[#F1F5F9] rounded transition-colors text-center"
              >
                Accept All Standard / Flag Non-Standard
              </button>
            </div>

            <div className="pt-2 border-t border-[#E2E8F0] space-y-1 font-mono text-[10px] text-[#64748B]">
              <div className="flex justify-between">
                <span>Diff Parser Engine:</span>
                <span className="font-semibold text-[#0F172A]">{data.engineInfo.diffEngine}</span>
              </div>
              <div className="flex justify-between">
                <span>Corpus Baseline:</span>
                <span className="text-[#0F172A]">{data.engineInfo.corpusBaseline}</span>
              </div>
              <div className="flex justify-between">
                <span>Audit Digest Hash:</span>
                <span className="text-[#0284C7]">{data.engineInfo.auditDigest}</span>
              </div>
            </div>
          </div>

          {/* Negotiation Strategy Note */}
          <div className="scaffold-card p-3.5 bg-[#EFF6FF] border border-[#BFDBFE] space-y-1 text-xs">
            <div className="font-semibold text-[#0F172A] flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5 text-[#0284C7]" />
              <span>Negotiation Strategy Note</span>
            </div>
            <p className="text-[#334155] leading-relaxed text-[11px]">
              Vendor usually compromises quickly on § 8.3 (Liability) when countered with a 12-month standard paired with a reciprocal cap on customer indemnity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
