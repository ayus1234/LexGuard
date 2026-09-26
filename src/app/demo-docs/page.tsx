'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import type { CorpusDocument, CorpusStatsResponse } from '@/types';
import {
  Search,
  X,
  FolderOpen,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface CategoryItem {
  name: string;
  count: number;
  id: string;
}

export default function DemoDocsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('all');
  const [previewDoc, setPreviewDoc] = useState<CorpusDocument | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  // API data
  const [documents, setDocuments] = useState<CorpusDocument[]>([]);
  const [totalDocs, setTotalDocs] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<CorpusStatsResponse | null>(null);
  const [scopeCategories, setScopeCategories] = useState<CategoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch corpus stats on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await apiClient.getCorpusStats();
        setStats(statsData);
      } catch (err: any) {
        console.error('Failed to fetch corpus stats:', err);
        setError('Failed to load corpus statistics');
      }
    };
    fetchStats();
  }, []);

  // Fetch categories for demo documents
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiClient.getCorpusCategories('fictional_demo');
        const mappedCategories: CategoryItem[] = response.categories.map((cat) => ({
          name: cat.name,
          count: cat.count,
          id: cat.name.toLowerCase().replace(/\s+&\s+/g, '-').replace(/\s+/g, '-').replace(/[()]/g, ''),
        }));
        setScopeCategories([
          { name: 'All Demo Documents', count: response.total_documents, id: 'all' },
          ...mappedCategories
        ]);
      } catch (err: any) {
        console.error('Failed to fetch categories:', err);
        setScopeCategories([]);
      }
    };
    fetchCategories();
  }, []);

  // Fetch documents whenever filters change
  useEffect(() => {
    const fetchDocuments = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const categoryFilter = selectedCategory === 'all' ? null : 
                              scopeCategories.find(c => c.id === selectedCategory)?.name || null;
        const response = await apiClient.getCorpusDocuments({
          page: currentPage,
          page_size: itemsPerPage,
          doc_type: 'fictional_demo',
          category: categoryFilter,
          jurisdiction: selectedJurisdiction === 'all' ? null : selectedJurisdiction,
          search: searchQuery || null,
        });
        setDocuments(response.documents);
        setTotalDocs(response.total);
        setTotalPages(response.total_pages);
      } catch (err: any) {
        console.error('Failed to fetch corpus documents:', err);
        setError('Failed to load demo documents from corpus.');
        setDocuments([]);
        setTotalDocs(0);
        setTotalPages(0);
      } finally {
        setIsLoading(false);
      }
    };
    if (scopeCategories.length > 0 || selectedCategory === 'all') {
      fetchDocuments();
    }
  }, [currentPage, selectedCategory, selectedJurisdiction, searchQuery, scopeCategories]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, selectedJurisdiction]);

  const getVisiblePages = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        pages.push(i);
      }
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  const extractKeyClauses = (doc: CorpusDocument): string[] => {
    return [
      doc.citation,
      doc.summary.split('.')[0].substring(0, 60) + (doc.summary.split('.')[0].length > 60 ? '...' : ''),
    ].filter(Boolean);
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-[#0284C7] shrink-0" aria-hidden="true" />
          <span>
            <strong className="font-semibold text-[#0F172A]">Demo Document Vault</strong>{' '}
            <span className="font-mono text-[10px] bg-white border border-[#CBD5E1] px-1.5 py-0.2 rounded text-[#0284C7] font-semibold">
              v1.0 Sandbox
            </span>{' '}
            Executable legal agreements for live demonstration and end-to-end testing.
          </span>
        </div>
        <div className="text-[11px] font-mono text-[#059669] shrink-0 flex items-center gap-1 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
          Zero-Retention Testing Active
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-4">
          <div className="space-y-1">
            <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
              CORPUS REPOSITORY / 05 / Executable Contracts
            </div>
            <h1 className="text-3xl font-display font-bold text-[#0F172A] tracking-tight">
              Demo Document Library
            </h1>
            <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
              Complete legal agreements designed for live demonstration, testing, and system validation.
            </p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">{stats?.demo_documents_count || 15}</div>
              <div className="text-[11px] text-[#64748B]">Demo Docs</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">{scopeCategories.length - 1}</div>
              <div className="text-[11px] text-[#64748B]">Categories</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">100%</div>
              <div className="text-[11px] text-[#64748B]">Analyzable</div>
            </div>
            <div className="bg-white border border-[#CBD5E1] rounded-lg p-3 space-y-0.5">
              <div className="text-2xl font-display font-bold text-[#0F172A]">{stats?.total_count || 500}</div>
              <div className="text-[11px] text-[#64748B]">Total Corpus</div>
            </div>
          </div>
        </div>
        <div className="scaffold-card p-5 bg-[#0F172A] text-white border-0 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold tracking-wider text-sky-400 uppercase">
              DEMONSTRATION READY
            </span>
            <Sparkles className="w-4 h-4 text-sky-400" aria-hidden="true" />
          </div>
          <h3 className="text-base font-display font-bold">Live System Testing</h3>
          <div className="flex items-center justify-between text-xs font-mono py-1 border-y border-slate-700">
            <span className="text-slate-400">Corpus Status:</span>
            <span className="font-bold text-sky-300">Fully Executable</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            Complete contracts pre-validated for end-to-end demonstration workflows.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by keyword, title, citation..."
            className="w-full pl-10 pr-10 py-3 bg-white border border-[#CBD5E1] rounded-lg text-xs font-sans text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7]"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-[#94A3B8] hover:text-[#0F172A]">
              <X className="w-4 h-4" aria-hidden="true" />
            </button>
          )}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            {scopeCategories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name} ({cat.count})
              </option>
            ))}
          </select>
          <select
            value={selectedJurisdiction}
            onChange={(e) => setSelectedJurisdiction(e.target.value)}
            className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
          >
            <option value="all">Jurisdiction: All</option>
            {stats?.jurisdictions.map((jur) => (
              <option key={jur} value={jur}>{jur}</option>
            ))}
          </select>
          <select className="bg-white border border-[#CBD5E1] rounded px-3 py-2 text-[#0F172A]">
            <option>Language: English (US)</option>
          </select>
        </div>
        {scopeCategories.length > 0 && (
          <div className="flex items-center gap-1.5 overflow-x-auto py-1 text-xs">
            {scopeCategories.slice(0, 9).map((cat) => {
              const isActive = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-3 py-1.5 rounded-full font-medium whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                    isActive ? 'bg-[#0F172A] text-white shadow-2xs font-semibold' : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
                  }`}
                >
                  <span>{cat.name}</span>
                  <span className={`text-[10px] font-mono px-1 rounded-full ${isActive ? 'bg-slate-800 text-sky-300' : 'bg-white text-[#64748B]'}`}>
                    {cat.count}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {isLoading && (
        <div className="text-center py-12 text-[#64748B]">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#0284C7]"></div>
          <p className="mt-3 text-sm">Loading demo documents...</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {!isLoading && !error && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => (
            <div key={doc.id} className="scaffold-card p-5 space-y-4 border border-[#CBD5E1] hover:border-[#94A3B8] transition-all flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">{doc.category}</span>
                  <span className="px-2 py-0.5 rounded bg-[#F8FAFC] text-[#475569] border border-[#E2E8F0]">{doc.jurisdiction}</span>
                  <span className="px-2 py-0.5 rounded bg-[#F0FDF4] text-[#059669] border border-[#BBF7D0] text-[9px]">
                    DEMO
                  </span>
                </div>
                <div>
                  <h3 className="text-base font-display font-bold text-[#0F172A] leading-snug">{doc.title}</h3>
                  <p className="text-xs text-[#475569] mt-1 leading-relaxed line-clamp-3">{doc.summary}</p>
                </div>
                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-mono text-[#64748B] uppercase font-bold">Citation & Reference</div>
                  <div className="space-y-1">
                    {extractKeyClauses(doc).map((clause, idx) => (
                      <div key={idx} className="text-[11px] font-mono text-[#334155] bg-[#F8FAFC] border border-[#E2E8F0] px-2 py-0.5 rounded">
                        {clause}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="space-y-3 pt-3 border-t border-[#E2E8F0]">
                <div className="grid grid-cols-3 gap-2 text-center font-mono text-[10px] text-[#64748B]">
                  <div>
                    <div className="text-[#94A3B8]">Length</div>
                    <div className="font-semibold text-[#0F172A]">{doc.page_count} Pages</div>
                  </div>
                  <div>
                    <div className="text-[#94A3B8]">Density</div>
                    <div className="font-semibold text-[#0F172A]">{doc.word_count.toLocaleString()} w</div>
                  </div>
                  <div>
                    <div className="text-[#94A3B8]">ID</div>
                    <div className="font-semibold text-[#0F172A]">{doc.id.split('-')[0]}</div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={() => setPreviewDoc(doc)} className="py-1.5 px-3 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded transition-colors">
                    Preview
                  </button>
                  <button onClick={() => router.push('/analyze')} className="py-1.5 px-3 text-xs font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] rounded transition-colors">
                    Analyze
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!isLoading && !error && documents.length === 0 && (
        <div className="text-center py-12 text-[#64748B]">
          <p className="text-sm">No demo documents found matching your filters.</p>
          <p className="text-xs mt-2">Try adjusting your search or filter criteria.</p>
        </div>
      )}

      {!isLoading && !error && totalDocs > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#64748B] pt-2">
          <div className="font-mono text-[11px]">
            Showing {Math.min((currentPage - 1) * itemsPerPage + 1, totalDocs)}-{Math.min(currentPage * itemsPerPage, totalDocs)} of {totalDocs} demo documents
          </div>
          <div className="flex items-center gap-1 font-mono text-[11px]">
            <button onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1} className="p-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9] disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Previous page">
              <ChevronLeft className="w-4 h-4" />
            </button>
            {getVisiblePages().map((page, idx) =>
              typeof page === 'number' ? (
                <button key={idx} onClick={() => setCurrentPage(page)} className={`px-2.5 py-1 rounded ${currentPage === page ? 'bg-[#0F172A] text-white font-bold' : 'border border-[#CBD5E1] hover:bg-[#F1F5F9]'}`} aria-label={`Go to page ${page}`} aria-current={currentPage === page ? 'page' : undefined}>
                  {page}
                </button>
              ) : (
                <span key={idx} className="px-1">...</span>
              )
            )}
            <button onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="p-1 rounded border border-[#CBD5E1] hover:bg-[#F1F5F9] disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Next page">
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      )}

      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs" onClick={() => setPreviewDoc(null)} />
          <div role="dialog" aria-modal="true" aria-label="Document structure preview" className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-xl w-full p-6 space-y-4 z-10">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#0284C7] font-semibold">{previewDoc.category} • {previewDoc.jurisdiction}</span>
                <h3 className="text-lg font-display font-bold text-[#0F172A]">{previewDoc.title}</h3>
              </div>
              <button onClick={() => setPreviewDoc(null)} className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A]" aria-label="Close preview">
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>
            <div className="space-y-3 text-xs">
              <p className="text-[#334155] leading-relaxed">{previewDoc.summary}</p>
              <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-2 font-mono text-[11px]">
                <div className="text-[#64748B] font-bold uppercase">Document Metadata</div>
                <ul className="space-y-1 text-[#0F172A]">
                  <li>• ID: {previewDoc.id}</li>
                  <li>• Type: {previewDoc.doc_type.replace('_', ' ')}</li>
                  <li>• Pages: {previewDoc.page_count}</li>
                  <li>• Words: {previewDoc.word_count.toLocaleString()}</li>
                  <li className="text-[#0284C7]">• Citation: {previewDoc.citation}</li>
                </ul>
              </div>
            </div>
            <div className="pt-3 border-t border-[#E2E8F0] flex justify-end gap-2">
              <button onClick={() => setPreviewDoc(null)} className="px-4 py-2 text-xs text-[#64748B] hover:text-[#0F172A] rounded border border-[#CBD5E1]">
                Close Preview
              </button>
              <button onClick={() => { setPreviewDoc(null); router.push('/analyze'); }} className="px-4 py-2 text-xs font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B]">
                Preload Into Analyzer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
