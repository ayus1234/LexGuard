import { PublicLawDocument } from '@/types';

export const publicLawJurisdictions = [
  'All Jurisdictions',
  'Federal (US Code)',
  'Delaware (DGCL)',
  'California (Civil Code)',
  'New York (NY LLC & UCC)',
  'Texas (TBOC)',
  'European Union (EU)',
];

export const publicLawCategories = [
  'All Categories',
  'Corporate Governance & Formation',
  'Commercial Code & Contracts (UCC)',
  'Intellectual Property & Trade Secrets',
  'Labor & Employment Standards',
  'Privacy & Data Protection',
  'Dispute Resolution & Arbitration',
];

export const samplePublicLaws: PublicLawDocument[] = [
  {
    id: 'law-dgcl-102',
    title: 'Delaware General Corporation Law § 102(b)(7)',
    code: '8 Del. C. § 102(b)(7)',
    jurisdiction: 'Delaware (DGCL)',
    category: 'Corporate Governance & Formation',
    year: 2024,
    summary:
      'Exculpation of directors and officers from personal liability for monetary damages resulting from breaches of the fiduciary duty of care.',
    precedentCount: 14200,
    status: 'Codified Baseline Validated',
    relevance: 'Standard benchmark for corporate charter indemnification analysis.',
  },
  {
    id: 'law-ucc-2719',
    title: 'Uniform Commercial Code § 2-719: Limitation of Remedy',
    code: 'UCC § 2-719',
    jurisdiction: 'Federal (US Code)',
    category: 'Commercial Code & Contracts (UCC)',
    year: 2023,
    summary:
      'Contractual modification or limitation of remedy in commercial sales, governing failure of essential purpose and consequential damages exclusion.',
    precedentCount: 38400,
    status: 'Codified Baseline Validated',
    relevance: 'Critical baseline for evaluating enforceability of trailing fee liability caps.',
  },
  {
    id: 'law-cal-16600',
    title: 'California Business & Professions Code § 16600 & SB 699',
    code: 'Cal. Bus. & Prof. § 16600',
    jurisdiction: 'California (Civil Code)',
    category: 'Labor & Employment Standards',
    year: 2024,
    summary:
      'Voiding of non-compete agreements regardless of where or when signed; civil penalties for employers seeking to enforce out-of-state restraints.',
    precedentCount: 9800,
    status: 'Codified Baseline Validated',
    relevance: 'Used to flag non-enforceable non-compete covenants in California employee agreements.',
  },
  {
    id: 'law-dtsa-1836',
    title: 'Defend Trade Secrets Act (DTSA) 18 U.S.C. § 1836',
    code: '18 U.S.C. § 1836',
    jurisdiction: 'Federal (US Code)',
    category: 'Intellectual Property & Trade Secrets',
    year: 2022,
    summary:
      'Federal private cause of action for trade secret misappropriation, civil seizure provisions, and mandatory whistleblower immunity notices.',
    precedentCount: 12600,
    status: 'Codified Baseline Validated',
    relevance: 'Benchmark for trade secrets and confidential information carve-outs.',
  },
  {
    id: 'law-faa-title9',
    title: 'Federal Arbitration Act (FAA) 9 U.S.C. § 1 et seq.',
    code: '9 U.S.C. § 1-16',
    jurisdiction: 'Federal (US Code)',
    category: 'Dispute Resolution & Arbitration',
    year: 2023,
    summary:
      'Preemption standards for commercial arbitration clauses, enforceability of class action waivers, and judicial confirmation standards.',
    precedentCount: 45000,
    status: 'Codified Baseline Validated',
    relevance: 'Validates arbitration enforceability and venue selection.',
  },
  {
    id: 'law-gdpr-art28',
    title: 'EU General Data Protection Regulation (GDPR) Article 28',
    code: 'Regulation (EU) 2016/679 Art. 28',
    jurisdiction: 'European Union (EU)',
    category: 'Privacy & Data Protection',
    year: 2024,
    summary:
      'Mandatory processor terms, sub-processor authorization requirements, audit rights, and standard contractual transfer obligations.',
    precedentCount: 22100,
    status: 'Codified Baseline Validated',
    relevance: 'Primary benchmark for data processing agreements and cross-border clauses.',
  },
];
