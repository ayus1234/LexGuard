'use client';

import React from 'react';
import { X, AlertTriangle, Trash2, ShieldCheck } from 'lucide-react';

interface PurgeSessionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PurgeSessionModal({ isOpen, onClose }: PurgeSessionModalProps) {
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
        aria-labelledby="purge-session-title"
        className="relative bg-white border border-[#FECACA] rounded-lg shadow-xl max-w-lg w-full p-6 space-y-4 z-10"
      >
        <div className="flex items-center justify-between pb-3 border-b border-[#FEE2E2]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center text-[#991B1B]">
              <Trash2 className="w-4 h-4" aria-hidden="true" />
            </div>
            <div>
              <h3 id="purge-session-title" className="text-sm font-bold text-[#0F172A]">
                Cryptographic Session Memory Purge
              </h3>
              <p className="text-[11px] font-mono text-[#DC2626]">Zero-Retention Security Architecture</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[#FEE2E2] text-[#64748B]"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>

        <div className="space-y-3.5">
          <div className="p-3 bg-[#FEF2F2] border border-[#FECACA] rounded space-y-2 text-xs">
            <div className="font-semibold text-[#991B1B] flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Warning: Irreversible Security Operation</span>
            </div>
            <p className="text-[#B45309] leading-relaxed text-[11px]">
              Session memory purge demonstrates LexGuard's zero-retention security architecture. In production,
              this action would cryptographically overwrite all ephemeral document data, vector embeddings, and
              active workspace state from in-memory storage.
            </p>
          </div>

          <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded space-y-2 text-xs">
            <div className="font-semibold text-[#0F172A]">Production Behavior</div>
            <ul className="space-y-1.5 text-[11px] text-[#475569] pl-4">
              <li className="flex items-start gap-2">
                <span className="text-[#DC2626] font-bold shrink-0">•</span>
                <span>All uploaded legal documents permanently deleted from RAM</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#DC2626] font-bold shrink-0">•</span>
                <span>PostgreSQL pgvector embeddings purged from tenant namespace</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#DC2626] font-bold shrink-0">•</span>
                <span>Active interrogation session history erased</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#DC2626] font-bold shrink-0">•</span>
                <span>Brief/checklist synthesis data wiped</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#DC2626] font-bold shrink-0">•</span>
                <span>Workspace reset to initial state</span>
              </li>
            </ul>
          </div>

          <div className="p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded text-xs space-y-2">
            <div className="font-semibold text-[#0F172A] flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-[#0284C7]" aria-hidden="true" />
              <span>Zero-Retention Compliance</span>
            </div>
            <p className="text-[#1E293B] leading-relaxed text-[11px]">
              This operation ensures attorney-client confidentiality by guaranteeing no legal document residue
              persists in system memory or vector databases. After purge, users would need to re-upload documents
              to continue analysis.
            </p>
          </div>

          <div className="flex items-start gap-2 p-2.5 bg-[#FFFBEB] border border-[#FDE68A] rounded text-[10px] text-[#92400E]">
            <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5 text-[#D97706]" aria-hidden="true" />
            <p className="leading-relaxed">
              <strong>Demo Environment:</strong> In this demonstration, no actual data exists to purge.
              Production deployments would enforce automatic purge on session disconnect per zero-retention policy.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-[#FEE2E2] flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors"
          >
            Understand Security Architecture
          </button>
        </div>
      </div>
    </div>
  );
}
