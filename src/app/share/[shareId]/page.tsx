'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  apiClient,
  SharedDossierResponse,
  LawyerBrief,
} from '@/lib/api/client';
import { BrandLogo } from '@/components/ui/BrandLogo';
import {
  FileText,
  ShieldCheck,
  AlertTriangle,
  Download,
  Calendar,
  CheckCircle2,
  Clock,
  ExternalLink,
  ChevronRight,
  Loader2,
  Lock,
  ArrowLeft,
  CheckSquare,
  Scale,
} from 'lucide-react';

export default function SharedDossierPage() {
  const params = useParams();
  const shareId = Array.isArray(params?.shareId) ? params.shareId[0] : (params?.shareId as string);

  const [loading, setLoading] = useState<boolean>(true);
  const [dossier, setDossier] = useState<SharedDossierResponse | null>(null);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);
  const [isExportingPdf, setIsExportingPdf] = useState<boolean>(false);
  const [isExportingDocx, setIsExportingDocx] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'brief' | 'checklist'>('brief');

  useEffect(() => {
    if (!shareId) return;

    const fetchDossier = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getSharedDossier(shareId);
        setDossier(data);
      } catch (err: any) {
        setError({
          code: err?.code || 'UNAVAILABLE',
          message: err?.message || 'Unable to load shared legal dossier.',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDossier();
  }, [shareId]);

  const handleExportPdf = async () => {
    if (!dossier) return;
    setIsExportingPdf(true);
    try {
      const downloadUrl = `/api/export/pdf/${encodeURIComponent(dossier.document_id)}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'LexGuard_Executive_Brief.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(`PDF Export: ${err?.message || 'Unable to download PDF'}`);
    } finally {
      setTimeout(() => setIsExportingPdf(false), 2000);
    }
  };

  const handleExportDocx = async () => {
    if (!dossier) return;
    setIsExportingDocx(true);
    try {
      const downloadUrl = `/api/export/docx/${encodeURIComponent(dossier.document_id)}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'LexGuard_Word_Checklist.docx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err: any) {
      alert(`DOCX Export: ${err?.message || 'Unable to download DOCX'}`);
    } finally {
      setTimeout(() => setIsExportingDocx(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-6 space-y-4">
        <BrandLogo showTag size="md" />
        <div className="flex items-center gap-2 text-xs font-mono text-[#0284C7] bg-white border border-[#CBD5E1] px-4 py-2 rounded shadow-2xs">
          <Loader2 className="w-4 h-4 animate-spin text-[#0284C7]" />
          <span>Verifying cryptographic share token &amp; loading dossier...</span>
        </div>
      </div>
    );
  }

  if (error || !dossier) {
    const isExpired = error?.code === 'SHARE_EXPIRED';
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-6">
        <div className="max-w-md w-full bg-white border border-[#CBD5E1] rounded-lg shadow-md p-6 space-y-4 text-center">
          <div className="w-12 h-12 rounded-full bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center mx-auto text-[#991B1B]">
            <AlertTriangle className="w-6 h-6" />
          </div>

          <div className="space-y-1">
            <h2 className="text-base font-bold text-[#0F172A]">
              {isExpired ? 'Shared Dossier Link Expired' : 'Shared Dossier Unavailable'}
            </h2>
            <p className="text-xs text-[#64748B] leading-relaxed">
              {error?.message ||
                'This shared legal dossier link was not found or has expired under zero-retention policy.'}
            </p>
          </div>

          <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded text-[11px] font-mono text-[#475569] text-left space-y-1">
            <div className="flex justify-between">
              <span>Token Ref:</span>
              <span className="truncate max-w-[180px]">{shareId}</span>
            </div>
            <div className="flex justify-between">
              <span>Status:</span>
              <span className="text-[#991B1B] font-semibold">{error?.code || '404 NOT FOUND'}</span>
            </div>
            <div className="flex justify-between">
              <span>Privacy Policy:</span>
              <span>Zero-Retention Auto-Purge</span>
            </div>
          </div>

          <Link
            href="/"
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-[#0F172A] hover:bg-[#1E293B] text-white text-xs font-semibold rounded transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to LexGuard Intake Workspace</span>
          </Link>
        </div>
      </div>
    );
  }

  const brief: LawyerBrief = dossier.brief;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      {/* Top Read-Only Bar */}
      <header className="bg-white border-b border-[#E2E8F0] sticky top-0 z-40">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <BrandLogo showTag size="sm" />
            <span className="hidden sm:inline-flex items-center gap-1.5 text-[10px] font-mono font-semibold bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] px-2 py-0.5 rounded-full">
              <Lock className="w-3 h-3" />
              Shared Read-Only Dossier
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportPdf}
              disabled={isExportingPdf}
              className="px-3 py-1.5 text-xs font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] disabled:opacity-60 rounded flex items-center gap-1.5 transition-colors shadow-2xs"
            >
              {isExportingPdf ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span className="hidden sm:inline">Export Executive Brief (PDF)</span>
              <span className="sm:hidden">PDF</span>
            </button>

            <button
              onClick={handleExportDocx}
              disabled={isExportingDocx}
              className="px-3 py-1.5 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] disabled:opacity-60 rounded flex items-center gap-1.5 transition-colors"
            >
              {isExportingDocx ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-[#0284C7]" />
              ) : (
                <FileText className="w-3.5 h-3.5 text-[#64748B]" />
              )}
              <span className="hidden sm:inline">Export Word Checklist (.docx)</span>
              <span className="sm:hidden">Word</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Document Dossier Header */}
        <div className="scaffold-card p-5 sm:p-6 bg-white border border-[#CBD5E1] space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#E2E8F0] pb-3">
            <div className="flex items-center gap-2 text-[10px] font-mono text-[#64748B]">
              <span className="font-bold text-[#0284C7] uppercase">
                • SHARE TOKEN: {dossier.share_id.substring(0, 16)}...
              </span>
              <span>•</span>
              <span>EXPIRES: {new Date(dossier.expires_at).toLocaleDateString()}</span>
            </div>
            <span className="text-[10px] font-mono bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] px-2 py-0.5 rounded-full font-semibold">
              Verified Dossier
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-display font-bold text-[#0F172A] tracking-tight">
            {brief.document_title || dossier.title}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-xs text-[#64748B]">
            <span className="flex items-center gap-1">
              <FileText className="w-3.5 h-3.5 text-[#0284C7]" />
              Format: {brief.document_type}
            </span>
            {brief.jurisdiction && (
              <span className="flex items-center gap-1">
                <Scale className="w-3.5 h-3.5 text-[#0284C7]" />
                Jurisdiction: {brief.jurisdiction}
              </span>
            )}
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#059669]" />
              {brief.citations_verified_count} Citations Verified
            </span>
          </div>

          <p className="text-xs text-[#475569] leading-relaxed pt-1">
            {brief.executive_summary}
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-2">
          <button
            onClick={() => setActiveTab('brief')}
            className={`px-3 py-1.5 text-xs font-semibold rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'brief'
                ? 'bg-[#0F172A] text-white shadow-xs'
                : 'text-[#475569] hover:bg-[#F1F5F9]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Executive Brief &amp; Attention Areas</span>
          </button>
          <button
            onClick={() => setActiveTab('checklist')}
            className={`px-3 py-1.5 text-xs font-semibold rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'checklist'
                ? 'bg-[#0F172A] text-white shadow-xs'
                : 'text-[#475569] hover:bg-[#F1F5F9]'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5" />
            <span>Pre-Execution Checklist ({brief.checklist.length})</span>
          </button>
        </div>

        {/* Tab 1: Brief Details */}
        {activeTab === 'brief' && (
          <div className="space-y-6">
            {/* Attention Areas */}
            <div className="scaffold-card p-5 bg-white border border-[#CBD5E1] space-y-4">
              <h2 className="text-sm font-bold text-[#0F172A] flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[#D97706]" />
                <span>Critical Attention Areas ({brief.attention_areas.length})</span>
              </h2>

              <div className="grid md:grid-cols-2 gap-3">
                {brief.attention_areas.map((att, i) => (
                  <div key={i} className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#0F172A]">{att.title}</span>
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-semibold ${
                          att.review_level === 'review_recommended'
                            ? 'bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]'
                            : 'bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]'
                        }`}
                      >
                        {att.review_level === 'review_recommended' ? 'URGENT' : 'ATTENTION'}
                      </span>
                    </div>
                    <p className="text-[#475569] text-[11px] leading-relaxed">{att.description}</p>
                    <div className="pt-1 text-[10px] text-[#0284C7] font-mono flex items-center justify-between">
                      <span>Citation: {att.source_reference || 'Contract Body'}</span>
                      {att.verified && <span className="text-[#059669] font-bold">✓ Verified</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Information */}
            <div className="scaffold-card p-5 bg-white border border-[#CBD5E1] space-y-4">
              <h2 className="text-sm font-bold text-[#0F172A]">Key Commercial &amp; Legal Terms</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                {brief.key_information.map((item, i) => (
                  <div key={i} className="p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded text-xs space-y-0.5">
                    <div className="text-[10px] text-[#64748B] font-mono">{item.label}</div>
                    <div className="font-semibold text-[#0F172A] truncate" title={item.value || 'Not Stated'}>
                      {item.value || 'Not Stated'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Checklist */}
        {activeTab === 'checklist' && (
          <div className="scaffold-card p-5 bg-white border border-[#CBD5E1] space-y-4">
            <h2 className="text-sm font-bold text-[#0F172A] flex items-center gap-2">
              <CheckSquare className="w-4 h-4 text-[#0284C7]" />
              <span>Pre-Execution Verification Checklist</span>
            </h2>

            <div className="space-y-2">
              {brief.checklist.map((chk, i) => (
                <div
                  key={i}
                  className="flex items-start justify-between gap-3 p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded text-xs"
                >
                  <div className="space-y-1">
                    <div className="font-semibold text-[#0F172A] flex items-center gap-2">
                      <span className="w-4 h-4 rounded border border-[#CBD5E1] bg-white flex items-center justify-center text-[10px] font-bold text-[#0284C7]">
                        {i + 1}
                      </span>
                      <span>{chk.title}</span>
                    </div>
                    <div className="text-[10px] text-[#64748B] pl-6 font-mono">
                      Ref: {chk.citation}
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] font-semibold shrink-0">
                    {chk.badge_text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legal Disclaimer */}
        <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg p-4 flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-[#0284C7] shrink-0 mt-0.5" />
          <div className="text-xs space-y-0.5">
            <div className="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0284C7]">
              MANDATORY EDUCATIONAL &amp; NON-LEGAL ADVICE DISCLAIMER
            </div>
            <p className="text-[#334155] leading-relaxed text-[11px]">
              {dossier.disclaimer || brief.disclaimer}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
