'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Upload,
  FileText,
  FolderKanban,
  Scale,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Zap,
  Sparkles,
  Layers,
  Search,
  BookOpen,
} from 'lucide-react';

export default function IntakeWorkspacePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'upload' | 'paste' | 'library' | 'public'>('upload');
  const [dragOver, setDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [pastedText, setPastedText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSimulatedUpload = (fileName: string) => {
    setUploadedFile(fileName);
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      router.push('/analyze');
    }, 1000);
  };

  const handlePreload = (docType: string) => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      router.push('/analyze');
    }, 600);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. Header Banner & Title */}
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
        <div className="space-y-2 max-w-3xl">
          <div className="inline-flex items-center gap-2">
            <span className="text-[11px] font-mono font-semibold tracking-wider text-[#0284C7] bg-[#EFF6FF] border border-[#BFDBFE] px-2 py-0.5 rounded-full uppercase">
              • NEXT-GEN AI LEGAL INTELLIGENCE
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-display font-bold text-[#0F172A] tracking-tight leading-tight">
            Understand the document before you sign it.
          </h1>

          <p className="text-sm sm:text-base text-[#475569] leading-relaxed">
            LexGuard helps you understand complex legal agreements, uncover ambiguous or one-sided
            clauses, query document-grounded facts, and prepare focused questions for your legal counsel.
          </p>
        </div>

        {/* Engine Status & System Pills */}
        <div className="flex flex-col items-start lg:items-end gap-2 shrink-0">
          <div className="text-[11px] font-mono text-[#64748B] flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
            Engine V4.2.1 • Operational Grounding Active
          </div>

          <div className="flex flex-wrap lg:flex-col items-start lg:items-end gap-1.5 font-mono text-[11px] text-[#334155]">
            <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded shadow-2xs">
              500 Corpus References •
            </span>
            <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded shadow-2xs">
              Gemini Legal Engine •
            </span>
            <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded shadow-2xs text-[#059669]">
              Zero-Retention Security
            </span>
          </div>
        </div>
      </div>

      {/* 2. Primary Intake Card with Multi-Modal Ingestion Tabs */}
      <div className="scaffold-card overflow-hidden shadow-xs border border-[#CBD5E1]">
        {/* Tab Navigation */}
        <div className="border-b border-[#E2E8F0] bg-[#F8FAFC] px-4 pt-3 flex flex-wrap items-center justify-between gap-2">
          <div role="tablist" aria-label="Document intake method" className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-3.5 py-2 text-xs font-semibold rounded-t border-b-2 flex items-center gap-2 transition-colors ${
                activeTab === 'upload'
                  ? 'border-[#0284C7] bg-white text-[#0F172A] shadow-2xs'
                  : 'border-transparent text-[#64748B] hover:text-[#0F172A]'
              }`}
              role="tab"
              aria-selected={activeTab === 'upload'}
              id="tab-upload"
              aria-controls="tabpanel-upload"
            >
              <Upload className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Upload File</span>
            </button>

            <button
              onClick={() => setActiveTab('paste')}
              className={`px-3.5 py-2 text-xs font-semibold rounded-t border-b-2 flex items-center gap-2 transition-colors ${
                activeTab === 'paste'
                  ? 'border-[#0284C7] bg-white text-[#0F172A] shadow-2xs'
                  : 'border-transparent text-[#64748B] hover:text-[#0F172A]'
              }`}
              role="tab"
              aria-selected={activeTab === 'paste'}
              id="tab-paste"
              aria-controls="tabpanel-paste"
            >
              <FileText className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Paste Text</span>
            </button>

            <button
              onClick={() => setActiveTab('library')}
              className={`px-3.5 py-2 text-xs font-semibold rounded-t border-b-2 flex items-center gap-2 transition-colors ${
                activeTab === 'library'
                  ? 'border-[#0284C7] bg-white text-[#0F172A] shadow-2xs'
                  : 'border-transparent text-[#64748B] hover:text-[#0F172A]'
              }`}
              role="tab"
              aria-selected={activeTab === 'library'}
              id="tab-library"
              aria-controls="tabpanel-library"
            >
              <FolderKanban className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Sample Library</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                200
              </span>
            </button>

            <button
              onClick={() => setActiveTab('public')}
              className={`px-3.5 py-2 text-xs font-semibold rounded-t border-b-2 flex items-center gap-2 transition-colors ${
                activeTab === 'public'
                  ? 'border-[#0284C7] bg-white text-[#0F172A] shadow-2xs'
                  : 'border-transparent text-[#64748B] hover:text-[#0F172A]'
              }`}
              role="tab"
              aria-selected={activeTab === 'public'}
              id="tab-public"
              aria-controls="tabpanel-public"
            >
              <Scale className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Public Legal Document</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                285
              </span>
            </button>
          </div>

          <div className="text-[11px] font-mono text-[#64748B] pb-2 sm:pb-0">
            Buffer: In-Memory {uploadedFile ? '14.8 MB' : '0 MB'}
          </div>
        </div>

        {/* Tab Body */}
        <div className="p-6 sm:p-8 space-y-6">
          {/* TAB 1: Upload File */}
          {activeTab === 'upload' && (
            <div
              role="tabpanel"
              id="tabpanel-upload"
              aria-labelledby="tab-upload"
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                if (e.dataTransfer.files?.[0]) {
                  handleSimulatedUpload(e.dataTransfer.files[0].name);
                }
              }}
              className={`border-2 border-dashed rounded-lg p-8 sm:p-12 text-center transition-colors ${
                dragOver
                  ? 'border-[#0284C7] bg-[#EFF6FF]'
                  : 'border-[#CBD5E1] hover:border-[#94A3B8] bg-[#F8FAFC]'
              }`}
            >
              <div className="w-12 h-12 rounded-lg bg-white border border-[#CBD5E1] shadow-xs flex items-center justify-center mx-auto text-[#0284C7] mb-4">
                <Upload className="w-6 h-6" aria-hidden="true" />
              </div>

              <div className="space-y-2 max-w-lg mx-auto">
                <h3 className="text-base sm:text-lg font-semibold text-[#0F172A]">
                  Drop your legal agreement here or{' '}
                  <label className="text-[#0284C7] hover:underline cursor-pointer">
                    Browse files
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.docx,.txt"
                      aria-label="Upload a legal document (PDF, DOCX, or TXT)"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleSimulatedUpload(e.target.files[0].name);
                        }
                      }}
                    />
                  </label>
                </h3>
                <p className="text-xs text-[#64748B] leading-normal">
                  High-resolution optical extraction supports scanned executed agreements, drafts,
                  and multi-party covenants.
                </p>
              </div>

              {/* Supported Format Pills */}
              <div className="flex items-center justify-center gap-2 pt-6 font-mono text-[10px] text-[#475569]">
                <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded">PDF</span>
                <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded">DOCX</span>
                <span className="bg-white border border-[#CBD5E1] px-2.5 py-1 rounded">TXT</span>
                <span className="bg-[#EFF6FF] border border-[#BFDBFE] text-[#0284C7] px-2.5 py-1 rounded font-semibold">
                  Up to 50MB
                </span>
              </div>

              {isProcessing && (
                <div className="mt-6 inline-flex items-center gap-2 text-xs font-mono text-[#0284C7] bg-white px-3 py-1.5 rounded border border-[#BFDBFE] animate-pulse">
                  <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                  Parsing cryptographic document fingerprint in zero-retention memory...
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Paste Text */}
          {activeTab === 'paste' && (
            <div role="tabpanel" id="tabpanel-paste" aria-labelledby="tab-paste" className="space-y-4">
              <label htmlFor="paste-contract-text" className="sr-only">Paste contract text</label>
              <textarea
                id="paste-contract-text"
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Paste contract provisions, clauses, master services agreements, or covenants here for immediate structured risk extraction and plain-English synthesis..."
                rows={8}
                className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-4 text-xs font-mono text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] focus:ring-1 focus:ring-[#0284C7]"
              />

              <div className="flex items-center justify-between">
                <div className="text-[11px] font-mono text-[#64748B]">
                  {pastedText.split(/\s+/).filter(Boolean).length} words • {pastedText.length} characters
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPastedText('')}
                    className="px-3 py-1.5 text-xs text-[#64748B] hover:text-[#0F172A] rounded border border-[#CBD5E1]"
                  >
                    Clear
                  </button>
                  <button
                    onClick={() => handleSimulatedUpload('Pasted_Agreement_Dossier.txt')}
                    disabled={!pastedText.trim()}
                    className="px-4 py-1.5 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors disabled:opacity-50"
                  >
                    Execute Synthesized Analysis
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Sample Library Quick Pick */}
          {activeTab === 'library' && (
            <div role="tabpanel" id="tabpanel-library" aria-labelledby="tab-library" className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#64748B]">Select a verified template from the 200-document corpus:</span>
                <Link href="/library" className="text-[#0284C7] hover:underline font-medium">
                  View all 200 documents →
                </Link>
              </div>

              <div className="grid sm:grid-cols-3 gap-3">
                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    Enterprise SaaS MSA &amp; SLA v4.2
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">18 pgs • Delaware Law • Cloud Provisioning</div>
                </button>

                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    Commercial Real Estate Triple-Net (NNN)
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">24 pgs • Texas Statutory • CREI Model</div>
                </button>

                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    Mutual Confidentiality (NDA)
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">6 pgs • California Law • Trade Secrets</div>
                </button>
              </div>
            </div>
          )}

          {/* TAB 4: Public Legal Document Quick Pick */}
          {activeTab === 'public' && (
            <div role="tabpanel" id="tabpanel-public" aria-labelledby="tab-public" className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#64748B]">Select a codified statute from the 285-document public law catalog:</span>
                <Link href="/public-law" className="text-[#0284C7] hover:underline font-medium">
                  Explore full 285 statutes →
                </Link>
              </div>

              <div className="grid sm:grid-cols-3 gap-3">
                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    Delaware General Corp Law § 102(b)(7)
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">8 Del. C. § 102 • Officer Exculpation</div>
                </button>

                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    UCC § 2-719 Remedy Limitations
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">Federal UCC • Consequential Damages</div>
                </button>

                <button
                  onClick={() => router.push('/analyze')}
                  className="p-3 rounded border border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#0284C7] cursor-pointer group transition-colors text-left w-full"
                >
                  <div className="text-xs font-semibold text-[#0F172A] group-hover:text-[#0284C7]">
                    California Bus. &amp; Prof. § 16600
                  </div>
                  <div className="text-[11px] text-[#64748B] mt-1">Cal. SB 699 • Non-Compete Invalidation</div>
                </button>
              </div>
            </div>
          )}

          {/* One-Click Pre-Loaders (Stitch screen) */}
          <div className="pt-2 border-t border-[#E2E8F0] flex flex-wrap items-center gap-3 text-xs">
            <span className="font-mono text-[11px] font-bold text-[#475569] uppercase flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-[#0284C7]" aria-hidden="true" />
              One-Click Pre-Loaders:
            </span>

            <button
              onClick={() => handlePreload('msa')}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#0F172A] font-medium border border-[#CBD5E1] transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]"></span>
              MSA Tech SaaS (18 pgs)
            </button>

            <button
              onClick={() => handlePreload('lease')}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#0F172A] font-medium border border-[#CBD5E1] transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]"></span>
              Commercial Lease (24 pgs)
            </button>

            <button
              onClick={() => handlePreload('nda')}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#0F172A] font-medium border border-[#CBD5E1] transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]"></span>
              Mutual NDA (6 pgs)
            </button>
          </div>

          {/* Session Confidentiality Guaranteed banner */}
          <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg p-3.5 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
            <div className="text-xs space-y-0.5">
              <div className="font-semibold text-[#0F172A]">Session Confidentiality Guaranteed</div>
              <p className="text-[#334155] leading-relaxed text-[11px]">
                Documents are parsed in-memory using zero-data-retention sandboxes and are strictly
                never added to public training data or shared libraries. Cryptographic hashes expire
                automatically when your session closes.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Document Intelligence Matrix (Verification Pipeline) */}
      <div className="space-y-4 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="text-[11px] font-mono font-bold tracking-wider text-[#0284C7] uppercase">
              Verification Pipeline
            </div>
            <h2 className="text-xl font-display font-bold text-[#0F172A]">
              Document Intelligence Matrix
            </h2>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <button
              onClick={() => setActiveTab('paste')}
              className="text-[#0284C7] hover:underline font-medium"
            >
              → Jump to Paste Text Mode
            </button>
            <span className="text-[#CBD5E1]">•</span>
            <Link href="/library" className="text-[#475569] hover:text-[#0F172A] font-medium">
              Explore 500 Curated Legal Docs
            </Link>
          </div>
        </div>

        {/* 5 Cards Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Card 1: Plain-English Synthesis */}
          <div className="scaffold-card p-5 space-y-3 flex flex-col justify-between border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors">
            <div className="space-y-2">
              <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center font-mono text-xs font-bold">
                01
              </div>
              <h3 className="text-base font-display font-bold text-[#0F172A]">
                Plain-English Synthesis
              </h3>
              <p className="text-xs text-[#475569] leading-relaxed">
                Translates dense, multisyllabic legalese into lucid, digestible operational summaries.
                Details obligations, financial milestones, and automatic renewal traps.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F5F9]">
              <span className="text-[10px] font-mono text-[#0284C7] bg-[#EFF6FF] px-2 py-0.5 rounded-full border border-[#BFDBFE]">
                • Deterministic Grounding
              </span>
            </div>
          </div>

          {/* Card 2: Clause Intelligence */}
          <div className="scaffold-card p-5 space-y-3 flex flex-col justify-between border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors">
            <div className="space-y-2">
              <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center font-mono text-xs font-bold">
                02
              </div>
              <h3 className="text-base font-display font-bold text-[#0F172A]">
                Clause Intelligence
              </h3>
              <p className="text-xs text-[#475569] leading-relaxed">
                Automated taxonomy tags indemnities, governing law, IP assignments, and non-solicitation
                covenants, benchmarking each against market-standard baselines.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F5F9]">
              <span className="text-[10px] font-mono text-[#0F172A] bg-[#F1F5F9] px-2 py-0.5 rounded-full border border-[#CBD5E1]">
                • 48 Standard Legal Taxonomies
              </span>
            </div>
          </div>

          {/* Card 3: Attention Areas & Flags */}
          <div className="scaffold-card p-5 space-y-3 flex flex-col justify-between border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors">
            <div className="space-y-2">
              <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center font-mono text-xs font-bold">
                03
              </div>
              <h3 className="text-base font-display font-bold text-[#0F172A]">
                Attention Areas &amp; Flags
              </h3>
              <p className="text-xs text-[#475569] leading-relaxed">
                Pinpoints ambiguous phrases, unilateral termination triggers, and uncapped exposure
                liabilities without formulating definitive legal conclusions.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F5F9]">
              <span className="text-[10px] font-mono text-[#D97706] bg-[#FEF3C7] px-2 py-0.5 rounded-full border border-[#FCD34D]">
                • Descriptive Risk Scoring
              </span>
            </div>
          </div>

          {/* Card 4: Comparison & Redlining (STAGE 04) */}
          <div className="scaffold-card p-5 space-y-3 flex flex-col justify-between border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center font-mono text-xs font-bold">
                  04
                </div>
                <span className="text-[10px] font-mono text-[#64748B] bg-[#F1F5F9] px-2 py-0.5 rounded">
                  STAGE 04
                </span>
              </div>
              <h3 className="text-base font-display font-bold text-[#0F172A]">
                Comparison &amp; Redlining
              </h3>
              <p className="text-xs text-[#475569] leading-relaxed">
                Side-by-side diffing highlights added warranties, struck-through safeguards, and
                stealthy alterations between negotiated revisions.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F5F9]">
              <span className="text-[10px] font-mono text-[#059669] bg-[#ECFDF5] px-2 py-0.5 rounded-full border border-[#A7F3D0]">
                • Inline Word-Level Differencing
              </span>
            </div>
          </div>

          {/* Card 5: Counsel Preparation Brief & Checklist (STAGE 05) */}
          <div className="scaffold-card p-5 space-y-3 flex flex-col justify-between border border-[#CBD5E1] hover:border-[#94A3B8] transition-colors md:col-span-2">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="w-7 h-7 rounded bg-[#EFF6FF] text-[#0284C7] flex items-center justify-center font-mono text-xs font-bold">
                  05
                </div>
                <div className="flex items-center gap-1.5 font-mono text-[10px]">
                  <span className="bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] px-2 py-0.5 rounded">
                    PDF / Word Export
                  </span>
                  <span className="bg-[#F1F5F9] text-[#64748B] px-2 py-0.5 rounded">STAGE 05</span>
                </div>
              </div>
              <h3 className="text-base font-display font-bold text-[#0F172A]">
                Counsel Preparation Brief &amp; Checklist
              </h3>
              <p className="text-xs text-[#475569] leading-relaxed">
                Generates a structured, prioritized executive debrief with concrete questions ready for
                your attorney consultation. Saves hours of billable legal fees by arming you with precise
                page-line citations, conflicting provisions, and suggested compromise phrasing.
              </p>
            </div>
            <div className="pt-2 border-t border-[#F1F5F9] flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-mono text-[#059669] bg-[#ECFDF5] px-2 py-0.5 rounded-full border border-[#A7F3D0]">
                ✓ 100% Document-grounded questions with exact page references
              </span>
              <span className="text-[10px] font-mono text-[#475569] bg-[#F1F5F9] px-2 py-0.5 rounded-full border border-[#CBD5E1]">
                Pre-Formatted Consultation Agenda Included
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Live Inspection Telemetry (Institutional Benchmark Engine) */}
      <div className="scaffold-card p-6 border border-[#CBD5E1] bg-white">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="text-[11px] font-mono font-bold tracking-wider text-[#0284C7] uppercase">
              Live Inspection Telemetry
            </div>
            <h3 className="text-lg font-display font-bold text-[#0F172A]">
              Institutional Benchmark Engine
            </h3>
            <p className="text-xs text-[#475569] leading-relaxed">
              Cross-checks agreement parameters against federal statutes, state consumer protection acts,
              and standard commercial conventions.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-xs">
              <div>
                <span className="text-[#64748B]">Indexed Case Precedents: </span>
                <span className="font-semibold text-[#0F172A]">1,420,000+</span>
              </div>
              <div>
                <span className="text-[#64748B]">Average Parse Latency: </span>
                <span className="font-semibold text-[#0284C7]">1.84s / 20pgs</span>
              </div>
            </div>
          </div>

          {/* 3 Metric Blocks */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full lg:w-auto shrink-0">
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <Scale className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
                <span className="text-xs font-mono font-bold text-[#0F172A]">99.8%</span>
              </div>
              <div className="text-xs font-semibold text-[#0F172A]">Statutory Consistency</div>
              <div className="text-[10px] text-[#64748B]">Verified against 285 Public Laws</div>
            </div>

            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <ShieldCheck className="w-4 h-4 text-[#059669]" aria-hidden="true" />
                <span className="text-xs font-mono font-bold text-[#0F172A]">AES-256</span>
              </div>
              <div className="text-xs font-semibold text-[#0F172A]">Transient Storage</div>
              <div className="text-[10px] text-[#64748B]">Ephemeral RAM wipe on disconnect</div>
            </div>

            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <Layers className="w-4 h-4 text-[#D97706]" aria-hidden="true" />
                <span className="text-xs font-mono font-bold text-[#0F172A]">1M Context</span>
              </div>
              <div className="text-xs font-semibold text-[#0F172A]">Long-Context Parser</div>
              <div className="text-[10px] text-[#64748B]">Full book-length master pacts</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
