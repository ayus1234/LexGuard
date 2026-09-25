import React from 'react';
import { ShieldCheck, Lock } from 'lucide-react';

export const ComplianceBanner: React.FC = () => {
  return (
    <div className="bg-[#eff4ff] border-b border-[#cbdbf5] text-[11px] text-[#213145] px-4 py-1.5 flex flex-col md:flex-row items-center justify-between gap-2 select-none">
      <div className="flex items-center gap-2 max-w-4xl">
        <ShieldCheck className="w-3.5 h-3.5 text-[#006398] shrink-0" />
        <p className="leading-snug text-[#213145]">
          <span className="font-semibold text-[#0b1c30]">Educational Compliance Notice:</span>{' '}
          LexGuard provides document-grounded legal information and educational assistance. It does not provide professional legal advice. Consult a qualified attorney for legal matters.
        </p>
      </div>
      <div className="flex items-center gap-3 shrink-0 font-mono text-[10px] text-[#45464d]">
        <span className="inline-flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#006398]"></span>
          Strict Boundary Mode
        </span>
        <span className="hidden sm:inline-flex items-center gap-1">
          <Lock className="w-2.5 h-2.5 text-[#45464d]" />
          AES-256 Memory Encrypted
        </span>
        <span className="hidden lg:inline-flex items-center gap-1 text-[#059669]">
          • Zero-Retention In-Memory
        </span>
      </div>
    </div>
  );
};
