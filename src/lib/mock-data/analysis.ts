import { DocumentAnalysis } from '@/types';

export const mockDocumentAnalysis: DocumentAnalysis = {
  document: {
    id: 'doc-saas-v42',
    title: 'Enterprise SaaS Master Services Agreement & SLA v4.2',
    subtitle: 'B2B SOFTWARE LICENSE & CLOUD SERVICES • Delaware Law • AAA Arbitration',
    category: 'Technology & SaaS',
    jurisdiction: 'Delaware Law',
    wordCount: 16820,
    pageCount: 24,
    hash: '0x82f4...d901',
    uploadTime: 'Today, 11:42 AM',
    standardPrecedent: 'NVCA Tech',
    source: 'Client Upload (Today, 11:42 AM)',
    tags: ['B2B SOFTWARE LICENSE & CLOUD SERVICES', 'Delaware Law • AAA Arbitration'],
    status: 'In-Memory Synchronized',
  },
  accuracyScore: 99.4,
  executiveBrief: {
    summary:
      'This contract governs an enterprise multi-tenant cloud provision between Apex Cloud Solutions LLC (Vendor) and Horizon Health Tech Inc. (Customer). The structure features a fixed 36-month initial term at $240,000 annually with automatic 12-month extension rollovers. Crucially, the agreement demonstrates an aggressive provider bias within liability and IP provisions: Vendor exposure is curtailed to trailing 3 months of fees, while Customer indemnity obligations remain uncapped across third-party claims.',
    pricingEscalator: {
      headline: '+7% Annual Maximum',
      details: 'Requires 30 days prior notice',
    },
    ipScope: {
      headline: 'Asymmetric Artifacts',
      details: 'Customer owns inputs; Vendor owns derived models',
    },
    arbitrationForum: {
      headline: 'Delaware AAA',
      details: 'Mandatory single arbitrator, Dover',
    },
    groundedSentencesCount: 48,
  },
  equilibrium: {
    vendorTilt: 68,
    baselineStandardPercent: 68,
    heavyNegotiatePercent: 32,
    recommendation: 'Recommendation: Focus counsel time on Section 8.3 & 11.2 first.',
    status: 'Imbalance Detected',
  },
  operationalParameters: [
    {
      id: 'param-parties',
      title: 'IDENTIFIED PARTIES',
      value: 'Apex Cloud & Horizon Health',
      description: 'Apex Cloud Solutions LLC (Delaware LLC, Vendor) & Horizon Health Tech Inc. (Customer).',
      citation: 'Preamble, p. 1',
      tag: 'Bilateral Signature',
      tagColor: 'blue',
      iconType: 'parties',
    },
    {
      id: 'param-term',
      title: 'TERM & DURATION',
      value: '36-Month Initial Term',
      description: 'Nov 15, 2024 to Nov 14, 2027. Effective date aligns with tenant sandbox provisioning date.',
      citation: 'Section 3.1, p. 4',
      tag: '782 Days Remaining',
      tagColor: 'blue',
      iconType: 'term',
    },
    {
      id: 'param-financial',
      title: 'FINANCIAL AMOUNTS',
      value: '$240,000 / Year Commitment',
      description: 'Annual upfront billing ($20,000/mo equivalent). Subject to 7% annual compounding escalator cap.',
      citation: 'Section 4.1 & Sched B',
      tag: '+7% Escalation Active',
      tagColor: 'amber',
      iconType: 'financial',
    },
    {
      id: 'param-termination',
      title: 'TERMINATION MECHANISMS',
      value: '90d Convenience / 30d Cure',
      description: '90 days prior written notice required for mutual convenience; 30-day cure window for material breaches.',
      citation: 'Section 9.2, p. 11',
      tag: 'Standard Cure Window',
      tagColor: 'slate',
      iconType: 'termination',
    },
    {
      id: 'param-renewal',
      title: 'RENEWAL MECHANICS',
      value: 'Automatic 12-Month Rollover',
      description: 'Renews automatically for subsequent 1-year terms unless opt-out notice is transmitted 60 days prior to anniversary.',
      citation: 'Section 3.2, p. 4',
      tag: '60-Day Deadband',
      tagColor: 'amber',
      iconType: 'renewal',
    },
    {
      id: 'param-jurisdiction',
      title: 'JURISDICTION & VENUE',
      value: 'Delaware Courts & AAA',
      description: 'Dover, Delaware legal venue with mandatory single-arbitrator commercial AAA arbitration. Waiver of jury trial.',
      citation: 'Section 18.1, p. 19',
      tag: 'Exclusive Venue',
      tagColor: 'blue',
      iconType: 'jurisdiction',
    },
  ],
  clauses: [
    {
      id: 'cl-8-3',
      section: 'Section 8.3',
      name: 'Limitation of Liability',
      category: 'Liability',
      riskLevel: 'High Attention',
      plainMeaning:
        'Vendor liability is capped at aggregate fees paid in trailing 3 months (~$60k), whereas Customer liability remains completely uncapped on IP and confidentiality breaches.',
      lineRange: 'Line 412-430',
      page: 10,
      recommendation: 'Reject 3-month cap; replace with standard 12-month trailing baseline and reciprocal cap.',
    },
    {
      id: 'cl-4-2',
      section: 'Section 4.2',
      name: 'Unilateral Price Adjustments',
      category: 'Financial',
      riskLevel: 'Medium',
      plainMeaning:
        'Vendor may modify subscription pricing upon 30 days written notice following Year 1, constrained only by the 7% annual escalator cap without Customer right of pre-termination.',
      lineRange: 'Line 183-201',
      page: 6,
      recommendation: 'Require mutual agreement for increases above 3% or permit termination without penalty.',
    },
    {
      id: 'cl-12-1',
      section: 'Section 12.1',
      name: 'Data Ownership & Derived IP',
      category: 'Intellectual Property',
      riskLevel: 'High Attention',
      plainMeaning:
        'Customer retains ownership of raw tenant inputs, but Vendor claims exclusive perpetual title over all aggregated telemetry, metadata models, and derived algorithmic enhancements.',
      lineRange: 'Line 560-582',
      page: 14,
      recommendation: 'Carve out customer workflow models and prohibit commercial model training on tenant data.',
    },
    {
      id: 'cl-14-5',
      section: 'Section 14.5',
      name: 'Non-Solicitation of Personnel',
      category: 'Restriction',
      riskLevel: 'Standard',
      plainMeaning:
        '2-year reciprocal prohibition against soliciting or hiring any technical or sales personnel who contributed directly to service performance.',
      lineRange: 'Line 640-652',
      page: 16,
      recommendation: 'Standard covenant. Ensure general job postings are explicitly excepted.',
    },
    {
      id: 'cl-16-2',
      section: 'Section 16.2',
      name: 'Service Level Credits',
      category: 'Obligation',
      riskLevel: 'Favorable',
      plainMeaning:
        'Robust 99.9% uptime baseline with tiered credits (up to 30% monthly fee offset for downtime exceeding 4 hours). Applied automatically to subsequent invoicing.',
      lineRange: 'Line 88-110',
      page: 21,
      recommendation: 'Market favorable terms. Verify auto-credit mechanism is monitored by IT ops.',
    },
  ],
  attentionAreas: [
    {
      id: 'att-11-2',
      section: 'SECTION 11.2',
      title: 'Asymmetric Indemnification Obligations',
      summary:
        'Customer must fully indemnify Vendor against all third-party claims arising from uploaded data or end-user workflow usage, while Vendor indemnification is strictly limited to direct IP infringement.',
      whyItMatters:
        'Disproportionate risk transfer. Under Delaware law, indemnification without reciprocal defense burdens Horizon Health Tech with defense fees.',
      line: 510,
      severity: 'critical',
    },
    {
      id: 'att-5-4',
      section: 'SECTION 5.4',
      title: 'Short Dispute Window for Invoicing',
      summary:
        'Customer is granted a narrow 15 calendar day objection timeframe after receipt of invoice. Failure to object in writing waives all future disputation rights.',
      whyItMatters:
        'Standard enterprise billing approval cycles typically take 30 to 45 days. 15 days creates an operational trap causing invoice forfeiture.',
      line: 245,
      severity: 'warning',
    },
    {
      id: 'att-3-2',
      section: 'SECTION 3.2',
      title: 'Automatic Term Extension Deadline',
      summary:
        'Mandatory automatic 1-year contract extension triggered if termination notice is not formally received exactly 60 calendar days prior to expiration.',
      whyItMatters:
        'Missed calendar tracking commits the organization to an additional $240,000+ commitment with no opt-out until Nov 2028.',
      line: 142,
      severity: 'warning',
    },
  ],
  activeCitation: {
    section: 'Section 8.3',
    title: 'Limitation of Liability',
    documentName: 'Master_Services_Agreement_v4.2.pdf',
    page: 10,
    totalPages: 24,
    ocrConfidence: 99.8,
    precedingText:
      '8.2 Disclaimer. EXCEPT AS EXPRESSLY PROVIDED HEREIN, NEITHER PARTY MAKES ANY WARRANTIES OF ANY KIND...',
    highlightedText:
      '§ 8.3 LIMITATION OF LIABILITY.\n"IN NO EVENT SHALL APEX CLOUD SOLUTIONS LLC, ITS AFFILIATES, OR THEIR LICENSORS BE LIABLE TO HORIZON HEALTH TECH FOR ANY INDIRECT, PUNITIVE, SPECIAL, OR CONSEQUENTIAL DAMAGES. APEX\'S MAXIMUM AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT UNDER ALL CLAIMS SHALL BE STRICTLY LIMITED TO THE TOTAL FEES ACTUALLY PAID BY CUSTOMER TO VENDOR IN THE THREE (3) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY."',
    followingText:
      '8.4 Exclusions. The limitations set forth in Section 8.3 shall not apply to Customer\'s payment obligations or Customer\'s indemnification obligations under Section 11.',
    matchHash: 'sha256:7bc89d...1m4',
    evaluation: {
      varianceText: 'Variance: +42% vs Market',
      cappedAt: 'Capped at 3-Month Fees',
      description:
        'Standard enterprise software liability caps typically span 12 months of paid fees (or 2x annual contract value for health and sensitive workloads). A 3-month cap ($60,000) severely underinsures Horizon against platform outages or data destruction.',
      suggestedFallback:
        'Replace "three (3) months" with "twelve (12) months", and add a $1,000,000 super-cap for data privacy breaches (Section 12.4).',
    },
  },
};
