'use client';

import React from 'react';
import { X, FileText, Lock, Eye } from 'lucide-react';

interface ExpandPdfModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentTitle: string;
  pageCount?: number;
  ocrConfidence?: number;
}

export default function ExpandPdfModal({
  isOpen,
  onClose,
  documentTitle,
  pageCount = 18,
  ocrConfidence = 99.4,
}: ExpandPdfModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-label="Close modal backdrop"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="expand-pdf-title"
        className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-xl max-w-lg w-full p-6 space-y-4 z-10"
      >
        <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#EFF6FF] border border-[#BFDBFE] flex items-center justify-center text-[#0284C7]">
              <Eye className="w-4 h-4" aria-hidden="true" />
            </div>
            <div>
              <h3 id="expand-pdf-title" className="text-sm font-bold text-[#0F172A]">
                Full PDF Document Viewer
              </h3>
              <p className="text-[11px] font-mono text-[#64748B]">Expanded Viewport Feature</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[#F1F5F9] text-[#64748B]"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div className="space-y-3.5">
          <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-2 text-xs">
            <div className="font-semibold text-[#0F172A] flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-[#0284C7]" aria-hidden="true" />
              <span>Document Metadata</span>
            </div>
            <div className="space-y-1 font-mono text-[11px] text-[#475569] pl-5">
              <div className="flex justify-between">
                <span>Document:</span>
                <span className="text-[#0F172A] font-semibold truncate max-w-[280px]" title={documentTitle}>
                  {documentTitle}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Total Pages:</span>
                <span className="text-[#0F172A] font-semibold">{pageCount} pages</span>
              </div>
              <div className="flex justify-between">
                <span>OCR Quality:</span>
                <span className="text-[#059669] font-semibold">{ocrConfidence}% confidence</span>
              </div>
              <div className="flex justify-between">
                <span>Format:</span>
                <span className="text-[#0F172A] font-semibold">PDF (Searchable)</span>
              </div>
            </div>
          </div>

          <div className="p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded text-xs space-y-2">
            <div className="font-semibold text-[#0F172A]">Feature Demonstration</div>
            <p className="text-[#1E293B] leading-relaxed text-[11px]">
              The full PDF viewport feature demonstrates an expanded document viewer with synchronized highlighting,
              page navigation, and zoom controls. In production deployment, this would render the complete PDF
              document with cryptographic integrity verification and support for clause-level citation jumping.
            </p>
          </div>

          <div className="flex items-start gap-2 p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded text-[10px] text-[#64748B]">
            <Lock className="w-3 h-3 shrink-0 mt-0.5 text-[#059669]" aria-hidden="true" />
            <p className="leading-relaxed">
              All document viewing occurs in zero-retention in-memory sandbox. No PDF data is persisted to disk
              or transmitted beyond your active browser session.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-[#E2E8F0] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors"
          >
            Understand
          </button>
        </div>
      </div>
    </div>
  );
}
