import { ChecklistItem, LawyerAgendaItem } from '@/types';

export const initialChecklistItems: ChecklistItem[] = [
  {
    id: 'chk-1',
    sectionIndex: 1,
    sectionTitle: '1. Financial & Commitments',
    title: 'Confirm maximum 7% annual price escalator applicability after Year 1',
    citation: 'Section 4.2, Page 6 • Financial Impact: +$16,800/yr compound liability',
    badgeText: 'Urgent',
    badgeVariant: 'urgent',
    completed: false,
  },
  {
    id: 'chk-2',
    sectionIndex: 1,
    sectionTitle: '1. Financial & Commitments',
    title: 'Verify $240,000 upfront annual payment terms vs quarterly invoicing request',
    citation: 'Section 3.1, Page 4 • Treasury Working Capital Objective',
    badgeText: 'Medium',
    badgeVariant: 'medium',
    completed: false,
  },
  {
    id: 'chk-3',
    sectionIndex: 2,
    sectionTitle: '2. Liability & Indemnification',
    title: 'Negotiate 3-month liability cap back to 12-month standard market baseline',
    citation: 'Section 8.3, Page 10 • Current Market Standard: 12 Months',
    badgeText: 'High Attention',
    badgeVariant: 'high',
    completed: false,
  },
  {
    id: 'chk-4',
    sectionIndex: 2,
    sectionTitle: '2. Liability & Indemnification',
    title: 'Request reciprocal indemnification protection for vendor IP infringement claims',
    citation: 'Section 11.2, Page 14 • Current state: Unilateral customer indemnity',
    badgeText: 'High Attention',
    badgeVariant: 'high',
    completed: false,
  },
  {
    id: 'chk-5',
    sectionIndex: 3,
    sectionTitle: '3. Governance & Operations',
    title: 'Calendar 60-day written notice deadline for automatic 12-month renewal (Deadline: Sep 15, 2027)',
    citation: 'Section 2.2, Page 3 • Outlook & Jira Legal alerts created',
    badgeText: 'Scheduled',
    badgeVariant: 'scheduled',
    completed: true,
  },
  {
    id: 'chk-6',
    sectionIndex: 3,
    sectionTitle: '3. Governance & Operations',
    title: 'Confirm Delaware arbitration venue is acceptable to corporate risk committee',
    citation: 'Section 18.1, Page 22 • Risk Committee Sign-off on file (Doc ID #RC-998)',
    badgeText: 'Verified',
    badgeVariant: 'verified',
    completed: true,
  },
];

export const lawyerAgendaItems: LawyerAgendaItem[] = [
  {
    id: 'agenda-1',
    priority: 'High',
    category: 'Liability Ceiling Allocation',
    agendaTopic: 'Cap Reduction to 3 Months (~$60k) vs 12 Months ($240k)',
    whyDiscuss:
      'Vendor liability cap leaves company exposed to catastrophic service outage losses or data security breaches with negligible provider recourse.',
    contractCitation: 'Section 8.3, Page 10, Lines 412-430',
    suggestedPhrasing:
      '"Our standard procurement requirement mandates a 12-month trailing fee liability cap, plus a $1M carve-out for breach of confidentiality and security warranties."',
    marketStandard: '12 months trailing fees or 1.5x-2x Annual Contract Value (ACV).',
  },
  {
    id: 'agenda-2',
    priority: 'High',
    category: 'Indemnification Asymmetry',
    agendaTopic: 'Unilateral Customer Defense for Third-Party User Data Claims',
    whyDiscuss:
      'Customer indemnifies vendor against any claims arising from uploaded data, whereas vendor only provides narrow IP infringement defense with extensive exclusions.',
    contractCitation: 'Section 11.2, Page 14, Lines 510-535',
    suggestedPhrasing:
      '"Indemnification must be mutual. Vendor must defend and hold harmless customer from third-party claims arising from platform security failures or breach of applicable data protection laws."',
    marketStandard: 'Bilateral indemnification with mutual defense procedures.',
  },
  {
    id: 'agenda-3',
    priority: 'Medium',
    category: 'Commercial Escalation',
    agendaTopic: '7% Annual Compounding Price Escalator Without Termination Right',
    whyDiscuss:
      'Compounds over a 3-year term to an additional $53,000+ commitment with no right to exit if price hikes exceed internal budget ceilings.',
    contractCitation: 'Section 4.2, Page 6, Lines 183-201',
    suggestedPhrasing:
      '"Price adjustments shall not exceed CPI-U or 3% per year, and customer shall have the right to terminate within 30 days of notice without early termination penalty."',
    marketStandard: 'CPI-U tied, capped at 3-4% maximum per annum.',
  },
];
