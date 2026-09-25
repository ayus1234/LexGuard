import { QATurn } from '@/types';

export const suggestedInterrogations = [
  {
    id: 'q1',
    category: 'Early Termination',
    question: 'What happens if we terminate early for convenience?',
  },
  {
    id: 'q2',
    category: 'Model Training',
    question: 'Is customer data used to train AI models or telemetry?',
  },
  {
    id: 'q3',
    category: 'Liability Analysis',
    question: 'What is the maximum aggregate liability cap and carve-outs?',
    active: true,
  },
  {
    id: 'q4',
    category: 'SLA Breach',
    question: 'What are our remedies if uptime drops below 99.0%?',
  },
];

export const initialQATurns: QATurn[] = [
  {
    id: 'turn-1-user',
    speaker: 'user',
    authorName: 'Lead Legal Counsel',
    timestamp: '10:41:18 AM EST',
    query: 'What is the maximum aggregate liability exposure for our company under this agreement, and are there carve-outs?',
  },
  {
    id: 'turn-1-lexguard',
    speaker: 'lexguard',
    authorName: 'LexGuard Legal Engine',
    timestamp: '10:41:19 AM EST',
    badges: ['§ 8.3 & § 11.2 Verified', '• 100% Grounded in Agreement Clauses'],
    groundedText:
      'Under Section 8.3, the aggregate liability of both parties is capped at the total fees actually paid in the three (3) months immediately preceding the event giving rise to liability. Based on your documented $20,000 monthly commitment, this strictly limits direct monetary exposure to approximately $60,000.',
    carveOutMatrix: [
      {
        type: 'urgent',
        title: 'Indemnification (§ 11.2)',
        description: 'Third-party intellectual property infringement claims are entirely uncapped.',
      },
      {
        type: 'standard',
        title: 'Standard Exclusions',
        description: 'Gross negligence and willful misconduct are exempt from any monetary ceiling.',
      },
    ],
    strategicConsideration:
      'Capping customer remedies at 3 months disproportionately favors the vendor in high-impact outage or data loss scenarios. Consider presenting the negotiation redline indicated in the source drawer.',
    groundingCitations: [
      {
        page: 10,
        section: '§ 8.3',
        tag: 'Active Anchor',
        quote:
          '"Limitation of Liability: ...shall be strictly limited to the total fees actually paid in the three (3) months immediately..."',
        actionText: 'Highlighted in Viewer →',
      },
      {
        page: 14,
        section: '§ 11.2',
        tag: 'Indemnity Ref',
        quote:
          '"Indemnification Obligations: Customer shall defend, indemnify and hold harmless vendor from claims alleging..."',
        actionText: 'Inspect Source ↗',
      },
    ],
    groundingLatency: '182ms',
    confidence: '99.8%',
  },
  {
    id: 'turn-2-user',
    speaker: 'user',
    authorName: 'Lead Legal Counsel',
    timestamp: '10:44:02 AM EST',
    query: 'Does the agreement automatically renew, and what is the deadline to opt out?',
  },
  {
    id: 'turn-2-lexguard',
    speaker: 'lexguard',
    authorName: 'LexGuard Legal Engine',
    timestamp: '10:44:03 AM EST',
    badges: ['§ 3.2 & § 18.4 Verified', '• Zero Hallucination Verified'],
    groundedText:
      'Yes. Under Section 3.2, this agreement automatically rolls over for successive 12-month periods unless written notice of non-renewal is received at least sixty (60) calendar days prior to the expiration of the current initial term (November 14, 2027).',
    reviewRecommendedNotice: {
      title: 'Review Recommended: Delivery Formalities',
      description:
        'The 60-day notice cannot be satisfied solely via email. Section 18.4 requires physical transmission via certified registered mail to the vendor\'s Delaware headquarters with return receipt requested.',
      anchorLink: 'Page 4, Lines 142-158 • Section 3.2 (Renewal Mechanics) →',
    },
    groundingLatency: '164ms',
    confidence: '99.9%',
  },
];

export const mockDocumentViewport = {
  documentTitle: 'Master_Services_Agreement_v4.2.pdf',
  page: 10,
  totalPages: 18,
  ocrAccuracy: 99.8,
  sectionName: 'Section 8.0: Risk Allocation',
  articleText: `ARTICLE 8 — LIMITATIONS OF REMEDIES AND DAMAGES

8.1 Consequential Damages Waiver.
NEITHER PARTY SHALL BE LIABLE TO THE OTHER FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES...

8.2 Direct Damages. Subject to Section 8.3, each party shall remain responsible for direct damages demonstrated with reasonable certainty...

[VECTOR TARGET § 8.3 — MATCHES QUERY 1]     OFFSET: 0X482A
"8.3 Aggregate Liability Ceiling. IN NO EVENT SHALL EITHER PARTY'S AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT, WHETHER IN CONTRACT, TORT, OR UNDER ANY OTHER THEORY OF LIABILITY, EXCEED THE TOTAL AMOUNT OF FEES ACTUALLY PAID BY CUSTOMER HEREUNDER IN THE THREE (3) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY."

8.4 Exceptions to Ceiling. The limitations set forth in Section 8.3 shall not apply to: (i) Customer's payment obligations under Article 4; (ii) indemnification obligations under Article 11; or (iii) damages arising from gross negligence or willful misconduct.`,
  sha256Digest: 'SHA-256 Digest Verified • Block #14,921 • Immutable',
  suggestedStrategy: {
    counselPrep:
      'Ask vendor to match mutual 12-month fee cap ($240,000) and insert a reciprocal "super-cap" for confidentiality breaches ($500,000).',
  },
  relatedAnchors: [
    { section: '§ 3.2 Term and Auto-Renewal', page: 4 },
    { section: '§ 8.3 Limitation of Liability', page: 10, active: true },
    { section: '§ 11.2 IP Indemnification Procedures', page: 14 },
    { section: '§ 18.4 Notice Formalities (Delaware)', page: 17 },
  ],
};
