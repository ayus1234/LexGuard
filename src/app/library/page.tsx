'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { sampleCategories, sampleDocuments, SampleDocumentItem } from '@/lib/mock-data/library';
import {
  Search,
  X,
  FileText,
  Zap,
  CheckCircle2,
  FolderOpen,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Eye,
  SlidersHorizontal,
  CloudUpload,
} from 'lucide-react';

export default function SampleLibraryPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('all');
  const [previewDoc, setPreviewDoc] = useState<SampleDocumentItem | null>(null);

  const filteredDocs = sampleDocuments.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.keyClauses.some((c) => c.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory =
      selectedCategory === 'all' ||
      (selectedCategory === 'tech' && doc.category.includes('Technology')) ||
      (selectedCategory === 'hr' && doc.category.includes('Employment')) ||
      (selectedCategory === 'nda' && doc.category.includes('NDA')) ||
      (selectedCategory === 'corp' && doc.category.includes('Corporate')) ||
      (selectedCategory === 'real-estate' && doc.category.includes('Property')) ||
      (selectedCategory === 'finance' && doc.category.includes('Finance')) ||
      (selectedCategory === 'privacy' && doc.category.includes('Privacy'));

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Header Vault Banner */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-[#0284C7] shrink-0" aria-hidden="true" />
          <span>
            <strong className="font-semibold text-[#0F172A]">Curated Institutional Vault</strong>{' '}
            <span className="font-mono text-[10px] bg-white border border-[#CBD5E1] px-1.5 py-0.2 rounded text-[#0284C7] font-semibold">
              v24.4 Calibrated
            </span>{' '}
            Standardized statutory templates pre-indexed for zero-latency retrieval and semantic parsing.
          </span>
        </div>
        <div className="text-[11px] font-mono text-[#059669] shrink-0 flex items-center gap-1 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
          Zero-Retention Ingestion Guard Active
        </div>
      </div>

      {/* 2. Page Title & Direct Preload Card */}
      <div className="grid lg:grid-cols-3 gap-6 items-start">
        {/* Left 2 Cols: Title & Stats */}
        <div className="lg:col-span-2 space-y-4">
          <div className="space-y-1">
            <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
              CORPUS REPOSITORY / 03 / Public Taxonomy
            </div>
            <h1 className="text-3xl font-display font-bold text-[#0F172A] tracking-tight">
              Sample Legal Document Library
            </h1>
            <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
              Access 200 standardized legal templates for instant analysis. This curated library democratizes legal document intelligence,
              providing everyone—from startups to small businesses—with the same analytical foundation used by corporate legal departments.
            </p>
          </div>

          {/* 4 Benchmark Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">200</div>
              <div className="text-[11px] text-[#64748B]">Standard Templates</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">17</div>
              <div className="text-[11px] text-[#64748B]">Legal Taxonomies</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">50+</div>
              <div className="text-[11px] text-[#64748B]">US &amp; Int&apos;l Venues</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">2024</div>
              <div className="text-[11px] text-[#64748B]">Market Standards</div>
            </div>
          </div>
        </div>

        {/* Right Col: Fast Ingestion Card */}
        <div className="scaffold-card p-5 bg-[#0F172A] text-white border-0 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold tracking-wider text-sky-400 uppercase">
              FAST INGESTION ENGINE
            </span>
            <Zap className="w-4 h-4 text-sky-400" aria-hidden="true" />
          </div>

          <h3 className="text-base font-display font-bold">Direct Preload</h3>

          <div className="flex items-center justify-between text-xs font-mono py-1 border-y border-slate-700">
            <span className="text-slate-400">Corpus Pre-Parsed Weights:</span>
            <span className="font-bold text-sky-300">1.4 GB / In-Memory</span>
          </div>

          <p className="text-[11px] text-slate-300 leading-relaxed">
            Selecting any template bypasses OCR intake, providing instant clause-level risk mapping &amp; benchmark cross-examination.
          </p>

          <div className="pt-2 flex items-center justify-between text-[10px] font-mono">
            <div className="flex items-center gap-1">
              <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                DE
              </span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                NY
              </span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                CA
              </span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-sky-400">
                +47
              </span>
            </div>
            <span className="text-emerald-400 font-semibold">All Venues Validated</span>
          </div>
        </div>
      </div>

      {/* 3. Search Bar & Filter Controls */}
      <div className="space-y-3">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by keyword, clause type, statutory requirement, or title (e.g., non-solicitation, Delaware SaaS MSA, mutual NDA)..."
            className="w-full pl-10 pr-10 py-3 bg-white border border-[#CBD5E1] rounded-lg text-xs font-sans text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] shadow-2xs"
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

        {/* Filter Dropdowns Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-xs">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            <option value="all">Category: All Categories</option>
            <option value="tech">Technology &amp; SaaS (34)</option>
            <option value="hr">Employment &amp; HR (28)</option>
            <option value="nda">NDA &amp; Confidentiality (22)</option>
            <option value="corp">Business &amp; Corporate (31)</option>
          </select>

          <select className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]">
            <option>Document Type: All Structure Types</option>
            <option>Master Agreement</option>
            <option>Addendum &amp; Rider</option>
            <option>Unilateral Policy</option>
          </select>

          <select
            value={selectedJurisdiction}
            onChange={(e) => setSelectedJurisdiction(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            <option value="all">Jurisdiction: All (50+)</option>
            <option value="de">Delaware Law</option>
            <option value="ca">California Law</option>
            <option value="ny">New York Law</option>
            <option value="tx">Texas Law</option>
          </select>

          <select className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]">
            <option>Standard: All Curated Provenance</option>
            <option>NVCA Venture Standard</option>
            <option>ABA Labor Standard</option>
            <option>CREI Model</option>
          </select>

          <select className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]">
            <option>Language: English (US)</option>
            <option>English (UK)</option>
          </select>
        </div>

        {/* Category Navigation Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 text-xs">
          {sampleCategories.map((cat) => {
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
                <span>{cat.name}</span>
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
      </div>

      {/* 4. Document Cards Grid (3 Columns) */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredDocs.map((doc) => (
          <div
            key={doc.id}
            className="scaffold-card p-5 space-y-4 border border-[#CBD5E1] hover:border-[#94A3B8] transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              {/* Badges */}
              <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                <span className="px-2 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                  {doc.category}
                </span>
                <span className="px-2 py-0.5 rounded bg-[#F8FAFC] text-[#475569] border border-[#E2E8F0]">
                  {doc.jurisdiction}
                </span>
              </div>

              {/* Title & Description */}
              <div>
                <h3 className="text-base font-display font-bold text-[#0F172A] leading-snug">
                  {doc.title}
                </h3>
                <p className="text-xs text-[#475569] mt-1 leading-relaxed line-clamp-3">
                  {doc.description}
                </p>
              </div>

              {/* Standard Key Clauses */}
              <div className="space-y-1.5 pt-1">
                <div className="text-[10px] font-mono text-[#64748B] uppercase font-bold">
                  Standard Key Clauses
                </div>
                <div className="space-y-1">
                  {doc.keyClauses.map((clause, idx) => (
                    <div
                      key={idx}
                      className="text-[11px] font-mono text-[#334155] bg-[#F8FAFC] border border-[#E2E8F0] px-2 py-0.5 rounded"
                    >
                      {clause}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom: Specs & Action Buttons */}
            <div className="space-y-3 pt-3 border-t border-[#E2E8F0]">
              <div className="grid grid-cols-3 gap-2 text-center font-mono text-[10px] text-[#64748B]">
                <div>
                  <div className="text-[#94A3B8]">Length</div>
                  <div className="font-semibold text-[#0F172A]">{doc.pages} Pages</div>
                </div>
                <div>
                  <div className="text-[#94A3B8]">Density</div>
                  <div className="font-semibold text-[#0F172A]">
                    {doc.wordCount.toLocaleString()} w
                  </div>
                </div>
                <div>
                  <div className="text-[#94A3B8]">Standard</div>
                  <div className="font-semibold text-[#0F172A]">{doc.standard}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setPreviewDoc(doc)}
                  className="py-1.5 px-3 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded transition-colors text-center"
                >
                  Preview Structure
                </button>
                <button
                  onClick={() => router.push('/analyze')}
                  className="py-1.5 px-3 text-xs font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] rounded transition-colors text-center"
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 5. Custom Template Batch Intake Banner */}
      <div className="scaffold-card p-5 border border-[#CBD5E1] bg-[#F8FAFC] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <CloudUpload className="w-5 h-5 text-[#0284C7] shrink-0 mt-0.5" />
          <div className="space-y-0.5 text-xs">
            <h4 className="font-semibold text-[#0F172A]">Need custom template ingestion?</h4>
            <p className="text-[#475569] leading-relaxed">
              Bulk import your enterprise standard forms to train zero-retention private benchmarks.
              Model weights remain fully client-isolated and strictly ephemeral within your active session.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => alert('Viewing zero-retention documentation...')}
            className="px-3 py-1.5 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded"
          >
            Documentation
          </button>
          <button
            onClick={() => alert('Initiating secure encrypted zip intake...')}
            className="px-3 py-1.5 text-xs font-semibold text-white bg-[#0284C7] hover:bg-[#0369A1] rounded"
          >
            Batch Intake (.zip)
          </button>
        </div>
      </div>

      {/* 6. Pagination Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#64748B] pt-2">
        <div className="font-mono text-[11px]">
          Showing 1-{filteredDocs.length} of 200 verified templates
        </div>

        <div className="flex items-center gap-1 font-mono text-[11px]">
          <button className="p-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9] disabled:opacity-50">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button className="px-2.5 py-1 rounded bg-[#0F172A] text-white font-bold">1</button>
          <button className="px-2.5 py-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9]">2</button>
          <button className="px-2.5 py-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9]">3</button>
          <span>...</span>
          <button className="px-2.5 py-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9]">34</button>
          <button className="p-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9]">
            <ChevronRight className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </div>

      {/* Structure Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs"
            onClick={() => setPreviewDoc(null)}
          />
          <div role="dialog" aria-modal="true" aria-label="Document structure preview" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-xl w-full p-6 space-y-4 z-10">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#0284C7] font-semibold">
                  {previewDoc.category} • {previewDoc.jurisdiction}
                </span>
                <h3 className="text-lg font-display font-bold text-[#0F172A]">
                  {previewDoc.title}
                </h3>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A]"
                aria-label="Close preview"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <p className="text-[#334155] leading-relaxed">{previewDoc.description}</p>

              <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-2 font-mono text-[11px]">
                <div className="text-[#64748B] font-bold uppercase">Template Structure</div>
                <ul className="space-y-1 text-[#0F172A]">
                  <li>• Preamble &amp; Definitions Hierarchy</li>
                  <li>• Core Operational Covenants &amp; Term ({previewDoc.pages} Pages)</li>
                  {previewDoc.keyClauses.map((c, i) => (
                    <li key={i} className="text-[#0284C7]">
                      • Key Risk Target: {c}
                    </li>
                  ))}
                  <li>• General Miscellaneous, Governing Law &amp; Execution Block</li>
                </ul>
              </div>
            </div>

            <div className="pt-3 border-t border-[#E2E8F0] flex justify-end gap-2">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-4 py-2 text-xs text-[#64748B] hover:text-[#0F172A] rounded border border-[#CBD5E1]"
              >
                Close Preview
              </button>
              <button
                onClick={() => {
                  setPreviewDoc(null);
                  router.push('/analyze');
                }}
                className="px-4 py-2 text-xs font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B]"
              >
                Preload Into Analyzer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
