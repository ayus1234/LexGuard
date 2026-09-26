'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { mockDocumentAnalysis } from '@/lib/mock-data/analysis';
import { Clause } from '@/types';
import {
  FileText,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  MessageSquareQuote,
  GitCompare,
  Download,
  AlertTriangle,
  CheckCircle2,
  Users,
  Calendar,
  DollarSign,
  Clock,
  RefreshCw,
  Scale,
  Sparkles,
  Copy,
  Check,
  X,
  FileCheck,
} from 'lucide-react';

export default function DocumentAnalysisPage() {
  const data = mockDocumentAnalysis;
  const [userContext, setUserContext] = useState<'founder' | 'procurement' | 'counsel'>('founder');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'high' | 'financial' | 'ip'>('all');
  const [activeClauseModal, setActiveClauseModal] = useState<Clause | null>(null);
  const [counterProposalCopied, setCounterProposalCopied] = useState(false);
  const [showCounterModal, setShowCounterModal] = useState(false);

  const filteredClauses = data.clauses.filter((clause) => {
    if (selectedFilter === 'high') return clause.riskLevel === 'High Attention';
    if (selectedFilter === 'financial') return clause.category === 'Financial';
    if (selectedFilter === 'ip') return clause.category === 'Intellectual Property';
    return true;
  });

  const getRiskBadge = (risk: Clause['riskLevel']) => {
    switch (risk) {
      case 'High Attention':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A] font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-[#D97706]"></span>
            High Attention
          </span>
        );
      case 'Medium':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]"></span>
            Medium
          </span>
        );
      case 'Standard':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#64748B]"></span>
            Standard
          </span>
        );
      case 'Favorable':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
            Favorable
          </span>
        );
    }
  };

  const getParamIcon = (type: string) => {
    switch (type) {
      case 'parties':
        return <Users className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      case 'term':
        return <Calendar className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      case 'financial':
        return <DollarSign className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      case 'termination':
        return <Clock className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      case 'renewal':
        return <RefreshCw className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      case 'jurisdiction':
        return <Scale className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
      default:
        return <FileText className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />;
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Top Educational Session Banner */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs text-[#1E293B] flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-[#0284C7] shrink-0" aria-hidden="true" />
          <span>
            <strong className="font-semibold text-[#0F172A]">AI-Powered Legal Assistance & Access:</strong>{' '}
            LexGuard makes complex legal documents understandable by identifying risk patterns and providing plain-English explanations.
            This educational tool improves your access to legal understanding but does not replace professional legal advice.
          </span>
        </div>
        <div className="font-mono text-[11px] text-[#64748B] shrink-0 flex items-center gap-2">
          <span>Session ID: #LG-9942-MSA</span>
          <span>•</span>
          <span className="text-[#059669] font-medium flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
            Synchronized
          </span>
        </div>
      </div>

      {/* 1.5 Dynamic Assistant Persona & User Context Switcher */}
      <div className="bg-white border border-[#CBD5E1] rounded-xl p-3 sm:p-4 shadow-2xs space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0F172A]">
              <Sparkles className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
              <span>Smart Context-Adaptive Assistant Logic</span>
              <span className="text-[10px] font-mono bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] px-2 py-0.5 rounded-full font-semibold">
                Dynamic Decision Engine Active
              </span>
            </div>
            <p className="text-[11px] text-[#64748B]">
              The assistant dynamically adjusts risk thresholds, plain-language translation, and negotiation tactics based on your active role.
            </p>
          </div>

          {/* Persona Tabs */}
          <div className="flex items-center gap-1.5 bg-[#F1F5F9] p-1 rounded-lg border border-[#E2E8F0]" role="tablist" aria-label="Assistant Persona Selection">
            <button
              onClick={() => setUserContext('founder')}
              role="tab"
              aria-selected={userContext === 'founder'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'founder'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              🚀 Founder / Non-Lawyer
            </button>
            <button
              onClick={() => setUserContext('procurement')}
              role="tab"
              aria-selected={userContext === 'procurement'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'procurement'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              💼 Procurement Director
            </button>
            <button
              onClick={() => setUserContext('counsel')}
              role="tab"
              aria-selected={userContext === 'counsel'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'counsel'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              ⚖️ In-House Legal Counsel
            </button>
          </div>
        </div>

        {/* Dynamic Contextual Guidance Banner */}
        <div className="p-3 rounded-lg border text-xs leading-relaxed transition-all">
          {userContext === 'founder' && (
            <div className="bg-[#FFFBEB] border border-[#FDE68A] text-[#92400E] p-2.5 rounded space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-xs">
                <span>🚀 Founder Decision Posture: Plain-English &amp; Cashflow Protection</span>
              </div>
              <p className="text-[11px] text-[#B45309]">
                The assistant translated 48 clauses into plain business terms. <strong>Key Action:</strong> Watch out for the automatic 12-month renewal lock-in in Section 4.2 and unilateral termination penalties. Consider proposing a 30-day mutual out clause before signing.
              </p>
            </div>
          )}
          {userContext === 'procurement' && (
            <div className="bg-[#EFF6FF] border border-[#BFDBFE] text-[#1E40AF] p-2.5 rounded space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-xs">
                <span>💼 Procurement Decision Posture: Commercial Balance &amp; SLA Enforcement</span>
              </div>
              <p className="text-[11px] text-[#1D4ED8]">
                Vendor Tilt is measured at <strong>68% vendor-favored</strong>. Vendor liability is capped at 1x monthly subscription fees ($5,000) while customer indemnity is uncapped. <strong>Key Action:</strong> Demand mutual liability caps tied to 12-month spend ($60,000) and add financial credits for downtime below 99.9%.
              </p>
            </div>
          )}
          {userContext === 'counsel' && (
            <div className="bg-[#F8FAFC] border border-[#CBD5E1] text-[#334155] p-2.5 rounded space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-xs">
                <span>⚖️ Legal Counsel Decision Posture: Statutory Benchmarking &amp; Redline Precision</span>
              </div>
              <p className="text-[11px] text-[#475569]">
                Benchmarked against Delaware General Corporation Law and UCC Article 2. <strong>Key Action:</strong> Review unilateral consequential damages carveout in Section 8.3 and non-solicitation restrictions in Section 11.4. Redline packet ready for outside counsel debrief.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 2. Document Title Bar & Main Actions */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-5">
        <div className="space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] rounded">
              B2B SOFTWARE LICENSE &amp; CLOUD SERVICES
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-[#F1F5F9] text-[#475569] border border-[#CBD5E1] rounded">
              Delaware Law • AAA Arbitration
            </span>
            <span className="text-[10px] font-mono text-[#64748B]">
              Cryptographic Fingerprint: {data.document.hash}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-display font-bold text-[#0F172A] tracking-tight">
            {data.document.title}
          </h1>

          <div className="text-xs text-[#64748B] flex flex-wrap items-center gap-x-3 gap-y-1 font-mono">
            <span>Source: {data.document.source}</span>
            <span>•</span>
            <span>16,820 words</span>
            <span>•</span>
            <span>28 Clauses Extracted</span>
            <span>•</span>
            <span className="text-[#059669]">Zero-Retention In-Memory Execution</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <Link
            href="/compare"
            className="px-3 py-1.5 text-xs font-medium text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded transition-colors flex items-center gap-1.5"
          >
            <GitCompare className="w-3.5 h-3.5 text-[#64748B]" aria-hidden="true" />
            <span>Compare with Standard</span>
          </Link>

          <Link
            href="/brief"
            className="px-3 py-1.5 text-xs font-medium text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded transition-colors flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-[#64748B]" aria-hidden="true" />
            <span>Export Lawyer Brief</span>
          </Link>

          <Link
            href="/ask"
            className="px-4 py-1.5 text-xs font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] rounded transition-colors flex items-center gap-1.5 shadow-xs"
          >
            <MessageSquareQuote className="w-3.5 h-3.5 text-sky-400" aria-hidden="true" />
            <span>Ask LexGuard Q&amp;A</span>
          </Link>
        </div>
      </div>

      {/* 3. Executive Intelligence Brief + Tone & Balance Assessment */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Left 2 Cols: Executive Intelligence Brief */}
        <div className="lg:col-span-2 scaffold-card p-5 sm:p-6 space-y-4 border border-[#CBD5E1] flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#0284C7] uppercase bg-[#EFF6FF] px-2 py-0.5 rounded border border-[#BFDBFE]">
                • SYNTHESIZED ANALYSIS
              </span>
              <span className="text-[11px] font-mono text-[#059669]">
                Accuracy Score: {data.accuracyScore}%
              </span>
            </div>

            <h2 className="text-lg font-display font-bold text-[#0F172A]">
              Executive Intelligence Brief
            </h2>

            <p className="text-xs text-[#334155] leading-relaxed">
              {data.executiveBrief.summary}
            </p>

            {/* 3 Key Parameter Callouts */}
            <div className="grid sm:grid-cols-3 gap-3 pt-2">
              <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded p-3 space-y-1">
                <div className="text-[10px] font-mono text-[#64748B]">Pricing Escalator</div>
                <div className="text-xs font-bold text-[#0F172A]">
                  {data.executiveBrief.pricingEscalator.headline}
                </div>
                <div className="text-[11px] text-[#64748B]">
                  {data.executiveBrief.pricingEscalator.details}
                </div>
              </div>

              <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded p-3 space-y-1">
                <div className="text-[10px] font-mono text-[#64748B]">IP Scope</div>
                <div className="text-xs font-bold text-[#0F172A]">
                  {data.executiveBrief.ipScope.headline}
                </div>
                <div className="text-[11px] text-[#64748B]">
                  {data.executiveBrief.ipScope.details}
                </div>
              </div>

              <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded p-3 space-y-1">
                <div className="text-[10px] font-mono text-[#64748B]">Arbitration Forum</div>
                <div className="text-xs font-bold text-[#0F172A]">
                  {data.executiveBrief.arbitrationForum.headline}
                </div>
                <div className="text-[11px] text-[#64748B]">
                  {data.executiveBrief.arbitrationForum.details}
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-[#E2E8F0] flex items-center justify-between text-[11px] font-mono text-[#64748B]">
            <span>Grounded in {data.executiveBrief.groundedSentencesCount} specific contractual sentences</span>
            <Link href="#citations" className="text-[#0284C7] hover:underline font-medium">
              View Citation Ledger →
            </Link>
          </div>
        </div>

        {/* Right Col: Tone & Balance Assessment */}
        <div className="scaffold-card p-5 sm:p-6 space-y-4 border border-[#CBD5E1] flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
                EQUILIBRIUM MATRIX
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]">
                {data.equilibrium.status}
              </span>
            </div>

            <h2 className="text-lg font-display font-bold text-[#0F172A]">
              Tone &amp; Balance Assessment
            </h2>

            <p className="text-[11px] text-[#64748B] leading-normal">
              Syntactic bias scoring calculated against 2,400+ negotiated B2B SaaS baselines in the LexGuard corpus.
            </p>

            {/* Circular Gauge */}
            <div className="flex flex-col items-center justify-center py-2">
              <div className="relative w-32 h-32 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  {/* Background Circle */}
                  <path
                    className="text-[#E2E8F0]"
                    strokeWidth="3.5"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  {/* Progress Circle (Vendor Tilt 68%) */}
                  <path
                    className="text-[#DC2626]"
                    strokeDasharray="68, 100"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>

                <div className="absolute flex flex-col items-center text-center">
                  <span className="text-2xl font-display font-bold text-[#0F172A]">
                    {data.equilibrium.vendorTilt}%
                  </span>
                  <span className="text-[9px] font-mono uppercase tracking-wider text-[#991B1B] font-semibold">
                    Vendor Tilt
                  </span>
                </div>
              </div>

              {/* Legend */}
              <div className="flex items-center gap-4 text-[10px] font-mono mt-3">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#CBD5E1]"></span>
                  <span>{data.equilibrium.baselineStandardPercent}% Baseline Standard</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-[#DC2626]"></span>
                  <span>{data.equilibrium.heavyNegotiatePercent}% Redline Negotiate</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded bg-[#FEF2F2] border border-[#FCA5A5] text-[11px] text-[#991B1B] leading-tight">
            {data.equilibrium.recommendation}
          </div>
        </div>
      </div>

      {/* 4. Extracted Operational Parameters (6 Key Anchors) */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-display font-bold text-[#0F172A]">
            Extracted Operational Parameters
          </h2>
          <span className="text-[11px] font-mono text-[#64748B]">
            Deterministic Parser v2.8 • 6 Key Anchors
          </span>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {data.operationalParameters.map((param) => (
            <div
              key={param.id}
              className="scaffold-card p-4 space-y-2 border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
                  {param.title}
                </div>
                {getParamIcon(param.iconType)}
              </div>

              <div className="text-sm font-display font-bold text-[#0F172A]">{param.value}</div>

              <p className="text-[11px] text-[#475569] leading-snug line-clamp-2">
                {param.description}
              </p>

              <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between text-[10px] font-mono">
                <span className="text-[#64748B]">{param.citation}</span>
                <span className="px-1.5 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                  {param.tag}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Clause Intelligence Engine Table */}
      <div className="space-y-3 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-display font-bold text-[#0F172A]">
              Clause Intelligence Engine
            </h2>
            <p className="text-xs text-[#64748B]">
              Cross-indexed against standard institutional playbook guidelines
            </p>
          </div>

          {/* Filter Pills */}
          <div role="group" aria-label="Filter clauses" className="flex items-center gap-1.5">
            <button
              onClick={() => setSelectedFilter('all')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                selectedFilter === 'all'
                  ? 'bg-[#0F172A] text-white'
                  : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
              }`}
            >
              All Clauses ({data.clauses.length})
            </button>
            <button
              onClick={() => setSelectedFilter('high')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                selectedFilter === 'high'
                  ? 'bg-[#0F172A] text-white'
                  : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
              }`}
            >
              High Attention (2)
            </button>
            <button
              onClick={() => setSelectedFilter('financial')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                selectedFilter === 'financial'
                  ? 'bg-[#0F172A] text-white'
                  : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
              }`}
            >
              Financial (1)
            </button>
            <button
              onClick={() => setSelectedFilter('ip')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                selectedFilter === 'ip'
                  ? 'bg-[#0F172A] text-white'
                  : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
              }`}
            >
              IP (1)
            </button>
          </div>
        </div>

        {/* Table Container */}
        <div className="scaffold-card overflow-x-auto border border-[#CBD5E1]">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[11px] font-mono text-[#64748B] uppercase">
                <th className="py-2.5 px-4 font-semibold">Clause Name &amp; Section</th>
                <th className="py-2.5 px-4 font-semibold">Category</th>
                <th className="py-2.5 px-4 font-semibold">Risk / Importance</th>
                <th className="py-2.5 px-4 font-semibold">Plain Meaning &amp; Contractual Impact</th>
                <th className="py-2.5 px-4 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {filteredClauses.map((clause) => (
                <tr key={clause.id} className="hover:bg-[#F8FAFC] transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-[#0F172A]">{clause.section}</div>
                    <div className="text-[11px] text-[#475569]">{clause.name}</div>
                    <div className="text-[10px] font-mono text-[#94A3B8]">{clause.lineRange}</div>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-[#475569]">
                    {clause.category}
                  </td>
                  <td className="py-3 px-4">{getRiskBadge(clause.riskLevel)}</td>
                  <td className="py-3 px-4 text-[#334155] leading-relaxed max-w-md">
                    {clause.plainMeaning}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setActiveClauseModal(clause)}
                      className="inline-flex items-center gap-1 text-xs text-[#0284C7] hover:underline font-medium"
                    >
                      <span>Review Details</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. Review Recommended: High-Negotiation Focus Areas (3 Items Flagged) */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base font-display font-bold text-[#0F172A]">
              Review Recommended: High-Negotiation Focus Areas
            </span>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] font-semibold">
            {data.attentionAreas.length} Items Flagged
          </span>
        </div>

        <p className="text-xs text-[#64748B]">
          Document sections exhibiting high variance from benchmark peer MSAs. Flagged for internal discussion with your legal representative.
        </p>

        <div className="grid md:grid-cols-3 gap-4 pt-1">
          {data.attentionAreas.map((area) => (
            <div
              key={area.id}
              className="scaffold-card p-4 space-y-3 border border-[#CBD5E1] border-t-2 border-t-[#DC2626] flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="text-[11px] font-mono font-bold text-[#DC2626] flex items-center justify-between">
                  <span>{area.section}</span>
                  <AlertTriangle className="w-3.5 h-3.5 text-[#DC2626]" />
                </div>

                <div className="text-xs font-display font-bold text-[#0F172A] leading-snug">
                  {area.title}
                </div>

                <p className="text-[11px] text-[#475569] leading-relaxed">{area.summary}</p>

                {/* Why It Matters */}
                <div className="p-2.5 rounded bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                  <div className="text-[10px] font-mono font-bold text-[#0F172A] uppercase">
                    Why It Matters:
                  </div>
                  <p className="text-[11px] text-[#334155] leading-normal">{area.whyItMatters}</p>
                </div>
              </div>

              <div className="pt-2 border-t border-[#F1F5F9] flex items-center justify-between text-[11px] font-mono">
                <Link
                  href="#citations"
                  className="text-[#0284C7] hover:underline font-medium flex items-center gap-1"
                >
                  <span>Read Original Clause</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
                <span className="text-[#94A3B8]">Line {area.line}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 7. Document Source Citation Inspector */}
      <div id="citations" className="space-y-3 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-base font-display font-bold text-[#0F172A]">
              Document Source Citation Inspector
            </h2>
            <p className="text-xs text-[#64748B]">
              Ground-truth excerpt verified via cryptographic parser index
            </p>
          </div>

          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
            Active Inspector: {data.activeCitation.section} ({data.activeCitation.title})
          </span>
        </div>

        {/* 2-Pane Box */}
        <div className="scaffold-card overflow-hidden border border-[#CBD5E1]">
          <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-[#E2E8F0]">
            {/* Left: Original Excerpt */}
            <div className="p-5 space-y-3 bg-[#F8FAFC]">
              <div className="flex items-center justify-between text-[11px] font-mono text-[#64748B] pb-2 border-b border-[#E2E8F0]">
                <span>
                  {data.activeCitation.documentName} • Page {data.activeCitation.page} of{' '}
                  {data.activeCitation.totalPages}
                </span>
                <span className="text-[#059669]">
                  OCR Confidence: {data.activeCitation.ocrConfidence}%
                </span>
              </div>

              <div className="space-y-2 font-mono text-xs leading-relaxed text-[#475569]">
                <p className="opacity-70">{data.activeCitation.precedingText}</p>

                {/* Highlighted Clause in Sky Well */}
                <div className="p-3 rounded border border-[#0284C7] bg-[#EFF6FF] text-[#0F172A] font-semibold whitespace-pre-line shadow-2xs">
                  {data.activeCitation.highlightedText}
                </div>

                <p className="opacity-70">{data.activeCitation.followingText}</p>
              </div>
            </div>

            {/* Right: LexGuard Evaluation */}
            <div className="p-5 space-y-4 bg-white flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
                    LEXGUARD EVALUATION
                  </span>
                  <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]">
                    {data.activeCitation.evaluation.varianceText}
                  </span>
                </div>

                <h3 className="text-base font-display font-bold text-[#0F172A]">
                  {data.activeCitation.evaluation.cappedAt}
                </h3>

                <p className="text-xs text-[#475569] leading-relaxed">
                  {data.activeCitation.evaluation.description}
                </p>

                {/* Suggested Negotiation Fallback */}
                <div className="p-3 rounded bg-[#F8FAFC] border border-[#CBD5E1] space-y-1.5">
                  <div className="text-[10px] font-mono font-bold text-[#0F172A] uppercase">
                    Suggested Negotiation Fallback:
                  </div>
                  <p className="text-xs font-mono text-[#0284C7] leading-relaxed">
                    &ldquo;{data.activeCitation.evaluation.suggestedFallback}&rdquo;
                  </p>
                </div>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => setShowCounterModal(true)}
                  className="w-full py-2.5 px-4 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors flex items-center justify-center gap-2"
                >
                  <Sparkles className="w-4 h-4 text-sky-400" />
                  <span>Draft Counter-Proposal</span>
                </button>
              </div>
            </div>
          </div>

          {/* Citation Box Footer */}
          <div className="p-3 bg-[#F1F5F9] border-t border-[#E2E8F0] flex items-center justify-between text-[11px] font-mono text-[#64748B]">
            <span>Match anchored at {data.activeCitation.matchHash}</span>
            <button
              onClick={() => alert('Opening full OCR document layer view...')}
              className="text-[#0284C7] hover:underline font-medium"
            >
              Expand Original PDF →
            </button>
          </div>
        </div>
      </div>

      {/* Clause Detail Modal */}
      {activeClauseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs"
            onClick={() => setActiveClauseModal(null)}
          />
          <div role="dialog" aria-modal="true" aria-label="Clause detail inspector" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-xl w-full p-6 space-y-4 z-10">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#0284C7] font-semibold">
                  {activeClauseModal.category}
                </span>
                <h3 className="text-lg font-display font-bold text-[#0F172A]">
                  {activeClauseModal.section}: {activeClauseModal.name}
                </h3>
              </div>
              <button
                onClick={() => setActiveClauseModal(null)}
                className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A]"
                aria-label="Close clause inspector"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1">
                <div className="text-[10px] font-mono text-[#64748B] uppercase">Plain Impact</div>
                <p className="text-[#334155] leading-relaxed">{activeClauseModal.plainMeaning}</p>
              </div>

              {activeClauseModal.recommendation && (
                <div className="p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded space-y-1">
                  <div className="text-[10px] font-mono text-[#0284C7] uppercase font-semibold">
                    Counsel Guidance
                  </div>
                  <p className="text-[#1E293B] leading-relaxed">
                    {activeClauseModal.recommendation}
                  </p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#E2E8F0] flex justify-end gap-2">
              <button
                onClick={() => setActiveClauseModal(null)}
                className="px-4 py-2 text-xs font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B]"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Counter Proposal Draft Modal */}
      {showCounterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs"
            onClick={() => setShowCounterModal(false)}
          />
          <div role="dialog" aria-modal="true" aria-label="Counter-proposal draft" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-xl w-full p-6 space-y-4 z-10">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#059669] font-semibold flex items-center gap-1">
                  <FileCheck className="w-3.5 h-3.5" aria-hidden="true" />
                  Pre-Structured Counter-Proposal Draft
                </span>
                <h3 className="text-lg font-display font-bold text-[#0F172A]">
                  Section 8.3: Limitation of Liability Redline
                </h3>
              </div>
              <button
                onClick={() => setShowCounterModal(false)}
                className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A]"
                aria-label="Close counter-proposal"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <div className="p-4 bg-[#F8FAFC] border border-[#CBD5E1] rounded text-xs font-mono text-[#0F172A] leading-relaxed space-y-2">
              <p>
                &ldquo;IN NO EVENT SHALL EITHER PARTY&apos;S MAXIMUM AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT EXCEED THE TOTAL FEES PAID OR PAYABLE BY CUSTOMER IN THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY; PROVIDED HOWEVER, THAT A SEPARATE SUPER-CAP OF ONE MILLION DOLLARS ($1,000,000) SHALL APPLY EXCLUSIVELY TO BREACHES OF DATA PRIVACY OR SECURITY OBLIGATIONS UNDER SECTION 12.&rdquo;
              </p>
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] font-mono text-[#64748B]">
                Aligned with ABA &amp; NVCA Standard Terms
              </span>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(
                    'IN NO EVENT SHALL EITHER PARTY\'S MAXIMUM AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT EXCEED THE TOTAL FEES PAID OR PAYABLE BY CUSTOMER IN THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY; PROVIDED HOWEVER, THAT A SEPARATE SUPER-CAP OF ONE MILLION DOLLARS ($1,000,000) SHALL APPLY EXCLUSIVELY TO BREACHES OF DATA PRIVACY OR SECURITY OBLIGATIONS UNDER SECTION 12.'
                  );
                  setCounterProposalCopied(true);
                  setTimeout(() => setCounterProposalCopied(false), 2000);
                }}
                className="px-4 py-2 text-xs font-semibold bg-[#0F172A] text-white hover:bg-[#1E293B] rounded flex items-center gap-1.5 transition-colors"
              >
                {counterProposalCopied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                    <span>Copied to Clipboard</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Copy Proposal Text</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
