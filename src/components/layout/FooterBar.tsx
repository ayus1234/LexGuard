import React from 'react';
import Link from 'next/link';

export const FooterBar: React.FC = () => {
  return (
    <footer className="bg-white border-t border-[#E2E8F0] px-4 sm:px-6 py-2.5 text-[11px] text-[#64748B] flex flex-col md:flex-row items-center justify-between gap-3 shrink-0">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px]">
        <span className="flex items-center gap-1.5 text-[#0F172A] font-medium">
          <span className="w-2 h-2 rounded-full bg-[#059669]"></span>
          Gemini 1.5 Pro Legal Engine: Online
        </span>
        <span className="flex items-center gap-1 text-[#475569]">
          • Session Security: Zero-Retention In-Memory
        </span>
        <span className="hidden sm:flex items-center gap-1 text-[#475569]">
          • 500 Corpus References Indexed
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs font-medium text-[#475569]">
        <Link href="/settings#terms" className="hover:text-[#0F172A] transition-colors">
          Terms
        </Link>
        <Link href="/settings#privacy" className="hover:text-[#0F172A] transition-colors">
          Privacy Guarantee
        </Link>
        <Link href="/settings#docs" className="hover:text-[#0F172A] transition-colors">
          Documentation
        </Link>
      </div>
    </footer>
  );
};
