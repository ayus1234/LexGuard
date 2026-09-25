export interface DocumentMeta {
  id: string;
  title: string;
  subtitle?: string;
  category: string;
  jurisdiction: string;
  wordCount: number;
  pageCount: number;
  hash: string;
  uploadTime: string;
  standardPrecedent?: string;
  tags?: string[];
  status?: string;
  source?: string;
}

export interface OperationalParameter {
  id: string;
  title: string;
  value: string;
  description: string;
  citation: string;
  tag: string;
  tagColor?: 'blue' | 'amber' | 'emerald' | 'slate';
  iconType: 'parties' | 'term' | 'financial' | 'termination' | 'renewal' | 'jurisdiction';
}

export type RiskLevel = 'High Attention' | 'Medium' | 'Standard' | 'Favorable';

export interface Clause {
  id: string;
  section: string;
  name: string;
  category: string;
  riskLevel: RiskLevel;
  plainMeaning: string;
  originalText?: string;
  recommendation?: string;
  lineRange?: string;
  page?: number;
}

export interface AttentionArea {
  id: string;
  section: string;
  title: string;
  summary: string;
  whyItMatters: string;
  line: number;
  originalQuote?: string;
  severity: 'critical' | 'warning' | 'info';
}

export interface CitationInspectorData {
  section: string;
  title: string;
  documentName: string;
  page: number;
  totalPages: number;
  ocrConfidence: number;
  precedingText: string;
  highlightedText: string;
  followingText: string;
  matchHash: string;
  evaluation: {
    varianceText: string;
    cappedAt: string;
    description: string;
    suggestedFallback: string;
  };
}

export interface DocumentAnalysis {
  document: DocumentMeta;
  accuracyScore: number;
  executiveBrief: {
    summary: string;
    pricingEscalator: {
      headline: string;
      details: string;
    };
    ipScope: {
      headline: string;
      details: string;
    };
    arbitrationForum: {
      headline: string;
      details: string;
    };
    groundedSentencesCount: number;
  };
  equilibrium: {
    vendorTilt: number;
    baselineStandardPercent: number;
    heavyNegotiatePercent: number;
    recommendation: string;
    status: string;
  };
  operationalParameters: OperationalParameter[];
  clauses: Clause[];
  attentionAreas: AttentionArea[];
  activeCitation: CitationInspectorData;
}

export interface ClauseDiff {
  id: string;
  section: string;
  title: string;
  badgeText: string;
  badgeType: 'critical' | 'moderate' | 'low';
  baselineVersion: string;
  baselineLabel: string;
  baselineHtml: string;
  counterpartyVersion: string;
  counterpartyLabel: string;
  counterpartyHtml: string;
  riskCalculation: {
    title: string;
    capImpact?: string;
    subhead?: string;
    description: string;
    recommendation: string;
  };
  actions: {
    primaryText: string;
    secondaryText: string;
  };
}

export interface DeltaNavItem {
  id: string;
  section: string;
  title: string;
  summary: string;
  badgeText: string;
  severity: 'CRIT' | 'MED' | 'LOW';
  category: string;
}

export interface ComparisonResult {
  docA: {
    name: string;
    version: string;
    badge: string;
    description: string;
  };
  docB: {
    name: string;
    version: string;
    badge: string;
    description: string;
  };
  totalChanges: number;
  highRiskShifts: number;
  addedClauses: number;
  removedClauses: number;
  modifications: number;
  diffs: ClauseDiff[];
  deltaNav: DeltaNavItem[];
  engineInfo: {
    diffEngine: string;
    corpusBaseline: string;
    auditDigest: string;
  };
}

export interface QACarveOutItem {
  type: 'urgent' | 'standard';
  title: string;
  description: string;
}

export interface QAGroundingCitation {
  page: number;
  section: string;
  tag: string;
  quote: string;
  actionText: string;
}

export interface QATurn {
  id: string;
  speaker: 'user' | 'lexguard';
  authorName: string;
  timestamp: string;
  query?: string;
  badges?: string[];
  groundedText?: string;
  carveOutMatrix?: QACarveOutItem[];
  strategicConsideration?: string;
  groundingCitations?: QAGroundingCitation[];
  reviewRecommendedNotice?: {
    title: string;
    description: string;
    anchorLink?: string;
  };
  groundingLatency?: string;
  confidence?: string;
}

export interface ChecklistItem {
  id: string;
  sectionIndex: number;
  sectionTitle: string;
  title: string;
  citation: string;
  badgeText: string;
  badgeVariant: 'urgent' | 'medium' | 'high' | 'scheduled' | 'verified';
  completed: boolean;
}

export interface LawyerAgendaItem {
  id: string;
  priority: 'High' | 'Medium';
  category: string;
  agendaTopic: string;
  whyDiscuss: string;
  contractCitation: string;
  suggestedPhrasing: string;
  marketStandard: string;
}

export interface PublicLawDocument {
  id: string;
  title: string;
  code: string;
  jurisdiction: string;
  category: string;
  year: number;
  summary: string;
  precedentCount: number;
  status: string;
  relevance: string;
}
