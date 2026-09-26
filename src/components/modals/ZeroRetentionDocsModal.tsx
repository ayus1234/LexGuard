'use client';

import React from 'react';
import { X, Shield, Lock, Eye, Server, CheckCircle2 } from 'lucide-react';

interface ZeroRetentionDocsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ZeroRetentionDocsModal({ isOpen, onClose }: ZeroRetentionDocsModalProps) {
  if (!isOpen) return null;

  // Handle escape key press
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="docs-modal-title"
        className="relative bg-white border border-[#CBD5E1] rounded-lg shadow-modal max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 space-y-5 z-10"
      >
        {/* Header */}
        <div className="flex items-start justify-between sticky top-0 bg-white pb-3 border-b border-[#E2E8F0]">
          <div className="flex items-center gap-2.5">
            <Shield className="w-5 h-5 text-[#0284C7]" aria-hidden="true" />
            <h2 id="docs-modal-title" className="text-lg font-display font-bold text-[#0F172A]">
              Zero-Retention Privacy & Custom Template Ingestion
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-[#94A3B8] hover:text-[#0F172A] hover:bg-[#F1F5F9] transition-colors"
            aria-label="Close documentation"
          >
            <X className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-5 text-sm text-[#334155] leading-relaxed">
          {/* Overview */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold text-[#0F172A]">Privacy-First Document Processing</h3>
            <p>
              LexGuard is engineered with a <strong>zero-retention ephemeral principle</strong> to ensure
              corporate users' sensitive contract text is never stored on server disks or transmitted to
              third-party AI training datasets.
            </p>
          </div>

          {/* Key Features Grid */}
          <div className="grid md:grid-cols-2 gap-3">
            <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg space-y-2">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
                <h4 className="font-semibold text-[#0F172A] text-xs uppercase tracking-wide">Memory-Only Processing</h4>
              </div>
              <p className="text-xs text-[#475569]">
                Documents are streamed to ephemeral scratch paths, parsed directly into memory, and immediately
                deleted via automated cleanup routines.
              </p>
            </div>

            <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg space-y-2">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
                <h4 className="font-semibold text-[#0F172A] text-xs uppercase tracking-wide">Cleanup Guarantee</h4>
              </div>
              <p className="text-xs text-[#475569]">
                File shredders are bound to background tasks and try-finally blocks, ensuring temporary files
                are purged even if parsing errors occur.
              </p>
            </div>

            <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg space-y-2">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
                <h4 className="font-semibold text-[#0F172A] text-xs uppercase tracking-wide">Telemetry Privacy</h4>
              </div>
              <p className="text-xs text-[#475569]">
                Document text and extracted provisions are never stored in telemetry records, application logs,
                or third-party monitoring services.
              </p>
            </div>

            <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg space-y-2">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
                <h4 className="font-semibold text-[#0F172A] text-xs uppercase tracking-wide">Tenant Isolation</h4>
              </div>
              <p className="text-xs text-[#475569]">
                Contract embeddings remain cryptographically isolated by document ID, preventing cross-document
                vector leakage at the database query level.
              </p>
            </div>
          </div>

          {/* Custom Template Ingestion */}
          <div className="space-y-3 p-4 bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg">
            <h3 className="text-base font-semibold text-[#0F172A]">Custom Template Batch Ingestion</h3>
            <p>
              Enterprise users can bulk import proprietary standard forms to train zero-retention private
              benchmarks. Model weights remain <strong>fully client-isolated</strong> and{' '}
              <strong>strictly ephemeral</strong> within your active session.
            </p>
            <div className="space-y-2 text-xs">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
                <span>
                  <strong>Supported Format:</strong> ZIP archives containing PDF, DOCX, or TXT files
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
                <span>
                  <strong>Size Limit:</strong> 100MB per batch upload
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
                <span>
                  <strong>Session Scope:</strong> Custom benchmarks remain active only during your current session
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
                <span>
                  <strong>Automatic Cleanup:</strong> All ingested templates are automatically purged when your session ends
                </span>
              </div>
            </div>
          </div>

          {/* Security Architecture */}
          <div className="space-y-2">
            <h3 className="text-base font-semibold text-[#0F172A]">Security Architecture</h3>
            <div className="space-y-2 text-xs font-mono bg-[#F8FAFC] border border-[#E2E8F0] rounded p-3">
              <div className="text-[#64748B]">Document Processing Flow:</div>
              <div className="pl-3 space-y-1 text-[#0F172A]">
                <div>1. Upload → File validation (magic bytes)</div>
                <div>2. Stream to ephemeral memory buffer</div>
                <div>3. Extract text & generate embeddings</div>
                <div>4. <span className="text-[#DC2626] font-semibold">Immediate file deletion</span> (os.unlink)</div>
                <div>5. Process in isolated vector space</div>
                <div>6. Session end → <span className="text-[#DC2626] font-semibold">Full cleanup</span></div>
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div className="p-4 bg-[#F8FAFC] border border-[#CBD5E1] rounded space-y-2">
            <p className="text-xs text-[#475569]">
              <strong className="text-[#0F172A]">Note:</strong> LexGuard never retains raw contract text
              on persistent storage, never transmits documents to public AI training datasets, and never
              shares your analysis data across tenant boundaries. All processing happens in secure,
              session-scoped memory that is automatically wiped upon completion.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-[#E2E8F0] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B] transition-colors"
          >
            Close Documentation
          </button>
        </div>
      </div>
    </div>
  );
}
