import React from 'react';
import Link from 'next/link';

interface BrandLogoProps {
  showTag?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const BrandLogo: React.FC<BrandLogoProps> = ({ showTag = false, className = '', size = 'md' }) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
  };

  return (
    <Link href="/" className={`inline-flex items-center gap-2.5 group ${className}`}>
      {/* Brand Icon */}
      <div
        className={`${iconSizes[size]} bg-[#0F172A] rounded-lg flex items-center justify-center p-1.5 shadow-sm relative shrink-0 transition-transform group-hover:scale-105`}
      >
        <svg viewBox="0 0 32 32" fill="none" className="w-full h-full">
          {/* Top line */}
          <rect x="5" y="7" width="22" height="3" rx="1.5" fill="#38BDF8" />
          {/* Middle line */}
          <rect x="5" y="14" width="16" height="3" rx="1.5" fill="#38BDF8" />
          {/* Bottom line */}
          <rect x="5" y="21" width="11" height="3" rx="1.5" fill="#38BDF8" />
          {/* Circular plus badge */}
          <circle cx="23" cy="20" r="5.5" fill="#0284C7" />
          <path
            d="M23 17.5V22.5M20.5 20H25.5"
            stroke="#FFFFFF"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </div>

      {/* Brand Text */}
      <div className="flex items-center gap-2">
        <span className={`${textSizes[size]} font-display font-bold tracking-tight text-[#0F172A]`}>
          Lex<span className="text-[#0284C7]">Guard</span>
        </span>

        {showTag && (
          <span className="text-[10px] font-mono font-semibold tracking-wider px-1.5 py-0.5 rounded bg-[#E2E8F0] text-[#475569] uppercase border border-[#CBD5E1]">
            Intelligence
          </span>
        )}
      </div>
    </Link>
  );
};
