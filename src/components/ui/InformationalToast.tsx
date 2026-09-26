'use client';

import React from 'react';
import { Info, X } from 'lucide-react';

interface InformationalToastProps {
  message: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function InformationalToast({ message, isOpen, onClose }: InformationalToastProps) {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed bottom-4 right-4 max-w-md bg-white border border-[#CBD5E1] rounded-lg shadow-lg p-4 animate-slide-up z-50"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <Info className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
        <div className="text-xs text-[#334155] leading-relaxed flex-1">{message}</div>
        <button 
          onClick={onClose}
          className="p-0.5 hover:bg-[#F1F5F9] rounded"
          aria-label="Close notification"
        >
          <X className="w-4 h-4 text-[#64748B]" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
