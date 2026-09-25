export interface SampleDocumentItem {
  id: string;
  title: string;
  category: string;
  jurisdiction: string;
  description: string;
  keyClauses: string[];
  pages: number;
  wordCount: number;
  standard: string;
}

export const sampleCategories = [
  { name: 'All Templates', count: 200, id: 'all' },
  { name: 'Technology & SaaS', count: 34, id: 'tech' },
  { name: 'Employment & HR', count: 28, id: 'hr' },
  { name: 'NDA & Confidentiality', count: 22, id: 'nda' },
  { name: 'Business & Corporate', count: 31, id: 'corp' },
  { name: 'Intellectual Property', count: 19, id: 'ip' },
  { name: 'Property & Real Estate', count: 26, id: 'real-estate' },
  { name: 'Finance & Lending', count: 24, id: 'finance' },
  { name: 'Privacy & Data', count: 16, id: 'privacy' },
];

export const sampleDocuments: SampleDocumentItem[] = [
  {
    id: 'doc-saas-v42',
    title: 'Enterprise SaaS Master Services Agreement & SLA v4.2',
    category: 'Technology & SaaS',
    jurisdiction: 'Delaware Law',
    description:
      'Multi-tenant cloud provisioning agreement with tiered uptime SLA credits, mutual IP indemnification, and liability caps.',
    keyClauses: ['§ 8.3 Limitation of Liability', '§ 12.1 Data Ownership', '§ 16.2 Service Credits'],
    pages: 18,
    wordCount: 14820,
    standard: 'NVCA Tech',
  },
  {
    id: 'doc-nda-bilateral',
    title: 'Mutual Confidentiality & Proprietary Rights Agreement',
    category: 'NDA & Confidentiality',
    jurisdiction: 'California Law',
    description:
      'Bilateral non-disclosure pact including trade secrets carveouts, standard 3-year survival, and residuals protection.',
    keyClauses: ['§ 3.2 Residuals Defense', '§ 5.1 Cal. Non-Compete Carveout'],
    pages: 6,
    wordCount: 3450,
    standard: 'SV Standard',
  },
  {
    id: 'doc-exec-employment',
    title: 'Executive Employment Agreement & IP Assignment',
    category: 'Employment & HR',
    jurisdiction: 'New York Law',
    description:
      'C-suite compensation structure, double-trigger change-of-control vesting, severance gates, and non-solicitation covenants.',
    keyClauses: [
      '§ 4.2 Change-of-Control Vesting',
      '§ 7.1 Invention Assignment',
      '§ 11.3 Severance Trigger',
    ],
    pages: 14,
    wordCount: 9120,
    standard: 'ABA Labor',
  },
  {
    id: 'doc-cre-nnn',
    title: 'Commercial Real Estate Triple-Net (NNN) Lease',
    category: 'Property & Real Estate',
    jurisdiction: 'Texas Statutory',
    description:
      'Standard tenant obligations for operating expenses, structural repairs, default remedies, and CASP certifications.',
    keyClauses: [
      '§ 5.4 Operating Pass-Throughs',
      '§ 14.1 CASP Compliance',
      '§ 22.8 Estoppel Certificate',
    ],
    pages: 24,
    wordCount: 18200,
    standard: 'CREI Model',
  },
  {
    id: 'doc-series-a-term',
    title: 'Series A Preferred Stock Investment Term Sheet',
    category: 'Finance & Lending',
    jurisdiction: 'Delaware Court of Chancery',
    description:
      '1x non-participating liquidation preference, protective provisions, board seat allocation, and pay-to-play structure.',
    keyClauses: [
      '§ 2.1 1x Liquidation Pref',
      '§ 3.5 Protective Voting Rights',
      '§ 6.2 Pay-to-Play Structure',
    ],
    pages: 12,
    wordCount: 7800,
    standard: 'NVCA Standard',
  },
  {
    id: 'doc-dpa-gdpr',
    title: 'API License & Data Processing Agreement (GDPR / CCPA)',
    category: 'Privacy & Data',
    jurisdiction: 'Multi-Jurisdictional EU/US',
    description:
      'Standard processor obligations, sub-processor notification timeline, security measures, and standard contractual clauses.',
    keyClauses: [
      '§ 4.1 Subprocessor 30d Notice',
      '§ 7.2 48h Breach Reporting',
      '§ 10.3 Schrems II Transfers',
    ],
    pages: 16,
    wordCount: 11350,
    standard: 'EU SCC Std',
  },
];
