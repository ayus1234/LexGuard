import { ComparisonResult } from '@/types';

export const mockComparisonResult: ComparisonResult = {
  docA: {
    name: 'Enterprise SaaS Master Services Agreement',
    version: 'v4.1 GOLD',
    badge: 'Baseline',
    description: 'Standard Customer Paper (Executed Q2 Baseline)',
  },
  docB: {
    name: 'Enterprise SaaS Master Services Agreement',
    version: 'v4.2 MARKUP',
    badge: 'Counterparty',
    description: 'Vendor Redline Received Nov 24, 2024',
  },
  totalChanges: 34,
  highRiskShifts: 4,
  addedClauses: 3,
  removedClauses: 2,
  modifications: 29,
  diffs: [
    {
      id: 'diff-8-3',
      section: '§ 8.3',
      title: 'Limitation of Liability Cap & Reciprocal Indemnity',
      badgeText: 'High Risk Shift',
      badgeType: 'critical',
      baselineVersion: 'Baseline Paper (v4.1)',
      baselineLabel: 'Customer Standard',
      baselineHtml:
        'Except for indemnification liabilities under Section 11, in no event shall either party\'s aggregate liability arising out of or related to this Agreement exceed the total fees paid or payable by Customer under the applicable Order Form in the preceding <span class="bg-red-100 text-red-700 line-through px-1 rounded">twelve (12) months</span> giving rise to such claim.',
      counterpartyVersion: 'Vendor Redline (v4.2)',
      counterpartyLabel: 'Counterparty Draft',
      counterpartyHtml:
        'Except for indemnification liabilities under Section 11, in no event shall either party\'s aggregate liability arising out of or related to this Agreement exceed the total fees <span class="bg-emerald-100 text-emerald-800 underline px-1 rounded font-medium">actually paid</span> by Customer under the applicable Order Form in the preceding <span class="bg-emerald-100 text-emerald-800 underline px-1 rounded font-medium">three (3) months</span> giving rise to such claim.',
      riskCalculation: {
        title: 'ALGORITHMIC RISK IMPACT CALCULATION',
        capImpact: 'Cap Impact: -$180,000 USD (75% Reduction)',
        subhead: 'High-Impact Risk Shift',
        description:
          'Vendor reduced maximum damages recovery ceiling from standard 12-month trailing billing ($240,000 ARR baseline) to 3 months ($60,000). Also struck "or payable", effectively shielding vendor from liability if breaches occur during transition or invoice disputes.',
        recommendation:
          'Recommendation: Reject change; reinstate 12-month trailing standard with $500k super-cap.',
      },
      actions: {
        primaryText: 'Draft Counter-Proposal',
        secondaryText: 'Reject Markup',
      },
    },
    {
      id: 'diff-12-1',
      section: '§ 12.1',
      title: 'Proprietary Rights, Derived Telemetry & Model Training',
      badgeText: 'IP Shift',
      badgeType: 'critical',
      baselineVersion: 'Baseline Paper (v4.1)',
      baselineLabel: 'Customer Standard',
      baselineHtml:
        'Customer retains exclusive ownership, title, and all intellectual property rights in and to all Customer Data and all derived analytical models generated from execution of the Services.',
      counterpartyVersion: 'Vendor Redline (v4.2)',
      counterpartyLabel: 'Counterparty Draft',
      counterpartyHtml:
        'Customer retains exclusive ownership over Customer Data. <span class="bg-emerald-100 text-emerald-800 underline px-1 rounded font-medium">Vendor shall exclusively own all aggregated telemetry, metadata, anonymized workflow artifacts, and derived algorithmic enhancements developed by or on behalf of Vendor during the Term.</span>',
      riskCalculation: {
        title: 'SUBTLE INTELLECTUAL PROPERTY TRANSFER',
        capImpact: 'Model Extraction Risk',
        subhead: 'IP Ownership Carveout',
        description:
          'Vendor is claiming unencumbered proprietary title over "derived algorithmic enhancements." In multi-tenant generative systems, this grants vendor the legal right to fine-tune shared commercial models using customer organizational logic and workflow data patterns.',
        recommendation:
          'Recommendation: Insert explicit carveout barring commercial AI fine-tuning or retention of customer prompt/output logic.',
      },
      actions: {
        primaryText: 'Insert Model Protective Rider',
        secondaryText: 'Strike Sentence',
      },
    },
    {
      id: 'diff-3-2',
      section: '§ 3.2',
      title: 'Renewal Notification Window & Formal Dispatch Rules',
      badgeText: 'Moderate Risk',
      badgeType: 'moderate',
      baselineVersion: 'Baseline Paper (v4.1)',
      baselineLabel: 'Customer Standard',
      baselineHtml:
        'Either party may terminate this Agreement without cause upon <span class="bg-red-100 text-red-700 line-through px-1 rounded">thirty (30) days</span> prior written notice prior to the end of the then-current Term.',
      counterpartyVersion: 'Vendor Redline (v4.2)',
      counterpartyLabel: 'Counterparty Draft',
      counterpartyHtml:
        'Either party may terminate this Agreement without cause upon <span class="bg-emerald-100 text-emerald-800 underline px-1 rounded font-medium">sixty (60) days</span> prior written notice <span class="bg-emerald-100 text-emerald-800 underline px-1 rounded font-medium">delivered via certified registered mail with tracking proof</span> prior to the end of the then-current Term.',
      riskCalculation: {
        title: 'NOTICE WINDOW NARROWED & FORMALITIES INTRODUCED',
        capImpact: 'Rollover Trapping Mechanism',
        subhead: 'Procedural Friction',
        description:
          'Doubles the advance notice deadline from 30 to 60 days and disallows standard email termination. Creates administrative hazard of involuntary multi-year auto-renewals if certified postal delivery is delayed.',
        recommendation:
          'Recommendation: Compromise on 45 days, but mandate that formal corporate email dispatch satisfies notice.',
      },
      actions: {
        primaryText: 'Accept 45d / Email Only',
        secondaryText: 'Reject Modification',
      },
    },
  ],
  deltaNav: [
    {
      id: 'diff-8-3',
      section: '§ 8.3',
      title: 'Liability Cap',
      summary: 'Trailing 12 mos down to 3 m...',
      badgeText: '75% Reduction',
      severity: 'CRIT',
      category: 'Liability & Caps',
    },
    {
      id: 'diff-12-1',
      section: '§ 12.1',
      title: 'Telemetry & IP',
      summary: 'Algorithmic derivative owne...',
      badgeText: 'Model Transfer',
      severity: 'CRIT',
      category: 'Data Ownership & IP',
    },
    {
      id: 'diff-3-2',
      section: '§ 3.2',
      title: 'Renewal Notice',
      summary: '30d to 60d certified mail disp...',
      badgeText: 'Notice Rollover',
      severity: 'MED',
      category: 'Termination & Rollover',
    },
    {
      id: 'diff-4-2',
      section: '§ 4.2',
      title: 'Fee Escalator',
      summary: 'Unilateral annual price increa...',
      badgeText: '+7% Floor',
      severity: 'LOW',
      category: 'Financial & Escalators',
    },
    {
      id: 'diff-18-1',
      section: '§ 18.1',
      title: 'Dispute Venue',
      summary: 'Delaware sole-arbitrator man...',
      badgeText: 'DE Arb',
      severity: 'LOW',
      category: 'Dispute Resolution',
    },
  ],
  engineInfo: {
    diffEngine: 'Myers-Delta Lexical v2.4',
    corpusBaseline: 'Delaware General Corp § 102',
    auditDigest: '0x9F4B...C401',
  },
};
