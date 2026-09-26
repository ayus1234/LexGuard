'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  suggestedInterrogations,
  initialQATurns,
  mockDocumentViewport,
} from '@/lib/mock-data/qa';
import { QATurn } from '@/types';
import { apiClient, DocumentAskResponse } from '@/lib/api/client';
import {
  ShieldCheck,
  Search,
  ArrowUp,
  FileText,
  AlertCircle,
  Copy,
  Pin,
  Check,
  RotateCcw,
  Sparkles,
  ExternalLink,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Lock,
  Download,
  AlertTriangle,
  ChevronRight,
  Loader2,
} from 'lucide-react';

const PAGE_CONTENT_MAP: Record<number, { section: string; text: string }> = {
  1: {
    section: 'Article 1.0: Definitions & Grant',
    text: `ARTICLE 1 — DEFINITIONS AND INTERPRETATION
1.1 Defined Terms. As used herein: "Customer Data" means all electronic data or information submitted by Customer to the SaaS Services. "SaaS Services" means the multi-tenant software-as-a-service platform identified in the Order Form.

ARTICLE 2 — PROVISION OF SERVICES
2.1 Access Rights. Vendor hereby grants Customer a non-exclusive, non-transferable right to access and use the SaaS Services during the Subscription Term solely for Customer's internal business operations.`,
  },
  4: {
    section: 'Article 3.0: Term & Renewal',
    text: `ARTICLE 3 — TERM AND AUTO-RENEWAL
3.1 Initial Term. This agreement shall commence on the Effective Date and continue for an initial term of three (3) years.

3.2 Renewal Mechanics. Thereafter, this agreement shall automatically renew for successive twelve (12) month periods unless either party provides written notice of non-renewal at least sixty (60) calendar days prior to the expiration of the current initial term. Notice of non-renewal must be delivered in accordance with Section 18.4.`,
  },
  6: {
    section: 'Article 4.0: Fees & Invoicing',
    text: `ARTICLE 4 — FEES AND PAYMENT TERMS
4.1 Invoicing and Payment. Customer shall pay all fees specified in applicable Order Forms within thirty (30) days from the invoice date.
4.2 Currency. Fees are quoted and payable in United States dollars.
4.3 Payment Obligations. Customer payment obligations are non-cancelable and fees paid are non-refundable except as expressly provided in Section 9.3. Quantities purchased cannot be decreased during the relevant Subscription Term. Any uncredited upfront annual fees ($240,000 commitment) remain non-refundable.`,
  },
  10: {
    section: 'Section 8.0: Risk Allocation',
    text: `ARTICLE 8 — LIMITATIONS OF REMEDIES AND DAMAGES

8.1 Consequential Damages Waiver.
NEITHER PARTY SHALL BE LIABLE TO THE OTHER FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF OR IN CONNECTION WITH THIS AGREEMENT.

8.2 Direct Damages. Subject to Section 8.3, each party shall remain responsible for direct damages demonstrated with reasonable certainty.

8.3 Aggregate Liability Ceiling.
IN NO EVENT SHALL EITHER PARTY'S AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT, WHETHER IN CONTRACT, TORT, OR UNDER ANY OTHER THEORY OF LIABILITY, EXCEED THE TOTAL AMOUNT OF FEES ACTUALLY PAID BY CUSTOMER HEREUNDER IN THE THREE (3) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY.

8.4 Exceptions to Ceiling. The limitations set forth in Section 8.3 shall not apply to: (i) Customer's payment obligations under Article 4; (ii) indemnification obligations under Article 11; or (iii) damages arising from gross negligence or willful misconduct.`,
  },
  11: {
    section: 'Article 9.0: Termination',
    text: `ARTICLE 9 — TERMINATION

9.1 Termination for Cause. Either party may terminate this agreement immediately upon written notice if the other party materially breaches any provision of this agreement and fails to cure such material breach within thirty (30) days after receipt of written notice.

9.2 Termination for Convenience. Either party may terminate this agreement or any Order Form for convenience without cause upon ninety (90) days prior written notice to the other party. In the event of customer termination for convenience, customer shall not be entitled to any refund of prepaid fees.

9.3 Effect of Termination for Breach. If this agreement is terminated by Customer for Vendor's uncured material breach pursuant to Section 9.1, Vendor shall refund to Customer any prepaid, unused fees covering the remainder of the Subscription Term.`,
  },
  14: {
    section: 'Article 11.0: Indemnification',
    text: `ARTICLE 11 — INDEMNIFICATION

11.1 Vendor Indemnification. Vendor shall defend, indemnify, and hold harmless Customer, its affiliates, and their respective officers, directors, and employees against any third-party claims alleging that the SaaS services infringe or misappropriate any patent, copyright, or trademark.

11.2 Customer Indemnification. Customer shall defend, indemnify, and hold harmless Vendor against any third-party claims alleging that Customer Data or customer use of the services violates applicable law or infringes third-party intellectual property rights.`,
  },
  15: {
    section: 'Article 12.0: Data Privacy & AI',
    text: `ARTICLE 12 — DATA PRIVACY AND SECURITY

12.1 Customer Data Ownership and AI Prohibitions. As between the parties, Customer retains all right, title, and interest in and to all Customer Data. Vendor shall not access, use, disclose, or process Customer Data except to provide the SaaS Services. Vendor explicitly covenants that Customer Data and Customer telemetry shall not be used, directly or indirectly, to train, tune, or improve artificial intelligence, machine learning, or large language models.

12.2 Security Safeguards. Vendor shall maintain administrative, physical, and technical safeguards designed to protect the security, confidentiality, and integrity of Customer Data (SOC 2 Type II compliant).`,
  },
  16: {
    section: 'Article 16.0: SLA & Uptime',
    text: `ARTICLE 16 — SERVICE LEVEL AGREEMENT & SLA REMEDIES

16.1 Service Availability. Vendor warrants that the SaaS Services will maintain an Uptime Percentage of at least 99.9% during each calendar month.

16.2 Service Credits and Chronic Breach. In the event uptime falls below 99.0%, Customer shall be entitled to a service credit equal to 25% of the monthly fee. In the event uptime falls below 95.0% in two consecutive calendar months, Customer may terminate this agreement for cause under Section 9.1.`,
  },
  17: {
    section: 'Article 18.0: Governing Law',
    text: `ARTICLE 18 — GENERAL PROVISIONS

18.1 Governing Law. This agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of law principles.

18.2 Venue and Dispute Resolution. The state and federal courts located in Wilmington, Delaware shall have exclusive jurisdiction over any dispute arising under this agreement.

18.4 Notice Formalities. Any notice required or permitted hereunder must be in writing and delivered by certified registered mail, return receipt requested, to the registered agent of the vendor at its Delaware headquarters. Email transmission does not constitute formal legal notice under this section.`,
  },
};

const PERSONA_QUESTIONS = {
  founder: [
    { id: 'f1', category: 'Renewal Trap', question: 'What is the exact deadline to prevent automatic 12-month lock-in?' },
    { id: 'f2', category: 'Cashflow Risk', question: 'What happens if our company needs to terminate early due to runway constraints?' },
    { id: 'f3', category: 'Personal Liability', question: 'Are founders or individual officers exposed to personal indemnity?' },
    { id: 'f4', category: 'Data Control', question: 'Can the vendor withhold or lock access to our customer records?' },
  ],
  procurement: [
    { id: 'p1', category: 'Liability Ratio', question: 'What is the aggregate liability cap relative to our annual contract value ($240k)?' },
    { id: 'p2', category: 'SLA Remedies', question: 'What financial service credits do we receive if monthly uptime drops below 99.9%?' },
    { id: 'p3', category: 'Price Protection', question: 'Are price increases capped upon renewal or can the vendor increase fees unilaterally?' },
    { id: 'p4', category: 'Invoice Dispute', question: 'Can we withhold disputed fees without service suspension or late penalty interest?' },
  ],
  counsel: [
    { id: 'c1', category: 'Risk Allocation', question: 'Does the consequential damages waiver mutualize or exclude third-party IP indemnification?' },
    { id: 'c2', category: 'Delaware Law', question: 'How does Delaware governing law interact with Section 8.3 aggregate damages ceiling?' },
    { id: 'c3', category: 'Breach Notice', question: 'What are the exact cure periods and notice requirements under Section 9.1 for material breach?' },
    { id: 'c4', category: 'AI & Data IP', question: 'Does Section 12.1 adequately prohibit training proprietary ML/LLM models on customer data?' },
  ],
};

export default function DocumentQAPage() {
  const [userContext, setUserContext] = useState<'founder' | 'procurement' | 'counsel'>('counsel');
  const [turns, setTurns] = useState<QATurn[]>(initialQATurns);
  const [inputText, setInputText] = useState('');
  const [citationDepth, setCitationDepth] = useState<'comprehensive' | 'executive'>('comprehensive');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeSuggested, setActiveSuggested] = useState('q3');
  const [activePage, setActivePage] = useState(10);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [activeDocId, setActiveDocId] = useState<string>('doc-saas-v42');
  const [activeDocTitle, setActiveDocTitle] = useState<string>('Enterprise SaaS Master Services Agreement & SLA v4.2');
  const [pageCount, setPageCount] = useState<number>(18);
  const [highlightedQuote, setHighlightedQuote] = useState<string | null>(null);
  const [sessionId] = useState<string>(() => `session-${Date.now()}`);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedDocId = sessionStorage.getItem('lexguard_active_doc_id');
      const storedDocTitle = sessionStorage.getItem('lexguard_active_doc_title');
      const storedPageCount = sessionStorage.getItem('lexguard_active_page_count');
      if (storedDocId) setActiveDocId(storedDocId);
      if (storedDocTitle) setActiveDocTitle(storedDocTitle);
      if (storedPageCount) setPageCount(parseInt(storedPageCount, 10) || 18);
    }
  }, []);

  const handleExecuteQuery = async () => {
    const questionText = inputText.trim();
    if (!questionText || isLoading) return;

    const roleName = userContext === 'founder'
      ? 'Founder / Non-Lawyer'
      : userContext === 'procurement'
      ? 'Procurement Director'
      : 'Lead Legal Counsel';

    const newQuery: QATurn = {
      id: `turn-${Date.now()}-user`,
      speaker: 'user',
      authorName: roleName,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      query: questionText,
    };

    setTurns((prev) => [...prev, newQuery]);
    setInputText('');
    setIsLoading(true);

    const topK = citationDepth === 'comprehensive' ? 5 : 3;

    try {
      const response: DocumentAskResponse = await apiClient.askDocument(
        activeDocId,
        questionText,
        topK,
        sessionId
      );

      const newResponse: QATurn = {
        id: `turn-${Date.now()}-lexguard`,
        speaker: 'lexguard',
        authorName: 'LexGuard Legal Engine',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        badges: response.badges && response.badges.length > 0
          ? response.badges
          : response.grounded
            ? ['§ Grounded in Agreement Clauses', '• Zero Hallucination Verified']
            : ['• Insufficient Evidence in Document'],
        groundedText: response.answer,
        carveOutMatrix: response.carve_out_matrix
          ? response.carve_out_matrix.map((c) => ({
              type: c.type,
              title: c.title,
              description: c.description,
            }))
          : undefined,
        strategicConsideration: response.strategic_consideration || undefined,
        reviewRecommendedNotice: response.review_recommended_notice
          ? {
              title: response.review_recommended_notice.title,
              description: response.review_recommended_notice.description,
              anchorLink: response.review_recommended_notice.anchor_link || undefined,
            }
          : undefined,
        groundingCitations: response.citations && response.citations.length > 0
          ? response.citations.map((c) => ({
              page: c.page || 1,
              section: c.section ? `§ ${c.section}` : 'General',
              tag: c.verified ? 'Verified Grounding' : 'Unverified Evidence ⚠',
              quote: c.quoted_text,
              actionText: c.verified ? 'Inspect Source ↗' : 'Verify Quote ↗',
            }))
          : undefined,
        groundingLatency: `${response.telemetry.total_ms}ms`,
        confidence: response.confidence,
      };

      setTurns((prev) => [...prev, newResponse]);

      // If citations were returned, focus the first cited page and highlight quote
      if (response.citations && response.citations.length > 0) {
        const firstCitation = response.citations[0];
        if (firstCitation.page) {
          setActivePage(firstCitation.page);
        }
        if (firstCitation.quoted_text) {
          setHighlightedQuote(firstCitation.quoted_text);
        }
      }
    } catch (err: any) {
      const errorResponse: QATurn = {
        id: `turn-${Date.now()}-error`,
        speaker: 'lexguard',
        authorName: 'LexGuard Legal Engine',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        badges: ['Operational Notice'],
        groundedText: `Unable to complete legal grounding: ${err.message || 'Service unavailable'}. Please verify backend connection and try again.`,
        confidence: '0%',
        groundingLatency: '0ms',
      };
      setTurns((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedClick = (id: string, question: string) => {
    setActiveSuggested(id);
    setInputText(question);
  };

  const currentPageData = PAGE_CONTENT_MAP[activePage] || {
    section: mockDocumentViewport.sectionName,
    text: mockDocumentViewport.articleText,
  };

  const renderHighlightedArticleText = (text: string, quote: string | null) => {
    if (!quote || !quote.trim()) {
      return text;
    }

    const cleanQuote = quote.trim();
    const lowerText = text.toLowerCase();
    const lowerQuote = cleanQuote.toLowerCase();
    const index = lowerText.indexOf(lowerQuote);

    if (index === -1) {
      const shortPrefix = cleanQuote.slice(0, 35).toLowerCase();
      const prefixIndex = lowerText.indexOf(shortPrefix);
      if (prefixIndex === -1) return text;

      const before = text.slice(0, prefixIndex);
      const matched = text.slice(prefixIndex, prefixIndex + Math.min(cleanQuote.length, text.length - prefixIndex));
      const after = text.slice(prefixIndex + matched.length);
      return (
        <>
          {before}
          <mark className="bg-[#FEF08A] text-[#0F172A] font-semibold px-1 py-0.5 rounded border border-[#FDE047]">
            {matched}
          </mark>
          {after}
        </>
      );
    }

    const before = text.slice(0, index);
    const matched = text.slice(index, index + cleanQuote.length);
    const after = text.slice(index + cleanQuote.length);

    return (
      <>
        {before}
        <mark className="bg-[#FEF08A] text-[#0F172A] font-semibold px-1 py-0.5 rounded border border-[#FDE047]">
          {matched}
        </mark>
        {after}
      </>
    );
  };

  return (
    <div className="space-y-5 pb-12">
      {/* 1. Document Target Bar */}
      <div className="scaffold-card p-4 border border-[#CBD5E1] bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
            <h1 className="text-base font-display font-bold text-[#0F172A]">
              {activeDocTitle}
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-x-3 text-[11px] font-mono text-[#64748B]">
            <span>{pageCount} pages • 14,820 words</span>
            <span>•</span>
            <span>Grounding: SHA-256 (0x82f4...d901)</span>
            <span>•</span>
            <span className="text-[#0284C7]">Vector Anchor: PostgreSQL pgvector</span>
            <span className="bg-[#EFF6FF] text-[#0284C7] px-1.5 py-0.2 rounded border border-[#BFDBFE]">
              Deterministic Mode
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[11px] font-mono px-2 py-1 rounded bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] flex items-center gap-1 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
            Zero-Hallucination Barrier Active
          </span>

          <button
            onClick={() => alert('Exporting Q&A Analysis Memo (.pdf)...')}
            className="px-3 py-1 text-xs font-semibold text-[#0F172A] bg-white border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-[#64748B]" aria-hidden="true" />
            <span>Export Memo</span>
          </button>
        </div>
      </div>

      {/* 2. Educational Compliance Notice */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs text-[#1E293B] flex items-start gap-2">
        <AlertCircle className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" aria-hidden="true" />
        <p className="leading-snug">
          <strong className="font-semibold text-[#0F172A]">Educational Assistance Only:</strong>{' '}
          LexGuard synthesizes verbatim factual content parsed directly from the verified document memory store. It does not compute formal legal counsel or statutory advice. Confirm strategic determinations with qualified counsel.
        </p>
      </div>

      {/* 3. Smart Context-Adaptive Assistant Persona & Corpus Interrogations */}
      <div className="space-y-3 bg-white border border-[#CBD5E1] rounded-xl p-3 sm:p-4 shadow-2xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0F172A]">
              <Sparkles className="w-4 h-4 text-[#0284C7]" aria-hidden="true" />
              <span>Smart Context-Adaptive Assistant Logic</span>
              <span className="text-[10px] font-mono bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] px-2 py-0.5 rounded-full font-semibold">
                Dynamic Q&amp;A Lens Active
              </span>
            </div>
            <p className="text-[11px] text-[#64748B]">
              Select your persona lens to query the document through role-specific risk frameworks and interrogation playbooks.
            </p>
          </div>

          {/* Persona Selection Tabs */}
          <div className="flex items-center gap-1.5 bg-[#F1F5F9] p-1 rounded-lg border border-[#E2E8F0]" role="tablist" aria-label="Assistant Persona Selection">
            <button
              onClick={() => {
                setUserContext('founder');
                setActiveSuggested('f1');
                setInputText(PERSONA_QUESTIONS.founder[0].question);
              }}
              role="tab"
              aria-selected={userContext === 'founder'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'founder'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              🚀 Founder / Non-Lawyer
            </button>
            <button
              onClick={() => {
                setUserContext('procurement');
                setActiveSuggested('p1');
                setInputText(PERSONA_QUESTIONS.procurement[0].question);
              }}
              role="tab"
              aria-selected={userContext === 'procurement'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'procurement'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              💼 Procurement Director
            </button>
            <button
              onClick={() => {
                setUserContext('counsel');
                setActiveSuggested('c1');
                setInputText(PERSONA_QUESTIONS.counsel[0].question);
              }}
              role="tab"
              aria-selected={userContext === 'counsel'}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                userContext === 'counsel'
                  ? 'bg-white text-[#0F172A] shadow-xs font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              ⚖️ In-House Legal Counsel
            </button>
          </div>
        </div>

        {/* Dynamic Context Guidance Banner */}
        <div className="p-2.5 rounded border text-xs leading-relaxed">
          {userContext === 'founder' && (
            <div className="bg-[#FFFBEB] border border-[#FDE68A] text-[#92400E] p-2 rounded flex items-center justify-between">
              <span><strong>🚀 Founder Lens:</strong> Focusing on personal liability risk, hidden auto-renewals, and non-refundable runway commitments.</span>
              <span className="text-[10px] font-mono text-[#B45309]">Plain-English Synthesis</span>
            </div>
          )}
          {userContext === 'procurement' && (
            <div className="bg-[#EFF6FF] border border-[#BFDBFE] text-[#1E40AF] p-2 rounded flex items-center justify-between">
              <span><strong>💼 Procurement Lens:</strong> Focusing on liability caps ($5k vs $240k spend), financial SLA uptime credits, and price escalators.</span>
              <span className="text-[10px] font-mono text-[#1D4ED8]">Vendor Tilt: 68%</span>
            </div>
          )}
          {userContext === 'counsel' && (
            <div className="bg-[#F8FAFC] border border-[#CBD5E1] text-[#334155] p-2 rounded flex items-center justify-between">
              <span><strong>⚖️ Legal Counsel Lens:</strong> Focusing on Delaware governing law, mutual consequential damages carve-outs, and AI training covenants.</span>
              <span className="text-[10px] font-mono text-[#475569]">Delaware UCC Grounded</span>
            </div>
          )}
        </div>

        {/* Dynamic Role-Specific Suggested Interrogations */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-[11px] font-mono text-[#64748B]">
            <span className="uppercase font-bold tracking-wider">Suggested Interrogations ({userContext.toUpperCase()} Lens)</span>
            <span>4 contextual hotspots</span>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {PERSONA_QUESTIONS[userContext].map((item) => {
              const isSelected = activeSuggested === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSuggestedClick(item.id, item.question)}
                  aria-label={`Select suggested question: ${item.question}`}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    isSelected
                      ? 'border-[#0284C7] bg-[#EFF6FF] shadow-2xs ring-1 ring-[#0284C7]'
                      : 'border-[#CBD5E1] bg-white hover:border-[#94A3B8] hover:bg-[#F8FAFC]'
                  }`}
                >
                  <div className="text-[10px] font-mono font-bold uppercase text-[#0284C7]">
                    {item.category}
                  </div>
                  <div className="text-xs font-semibold text-[#0F172A] mt-1 leading-snug">
                    {item.question}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 4. Main Q&A Workspace (2/3 Conversation Area + 1/3 Document Viewport) */}
      <div className="grid lg:grid-cols-12 gap-5 items-start">
        {/* Left 8 Cols: Conversation Area */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-4">
          <div className="scaffold-card border border-[#CBD5E1] overflow-hidden flex flex-col">
            {/* Thread Header */}
            <div className="border-b border-[#E2E8F0] bg-[#F8FAFC] px-4 py-2.5 flex items-center justify-between">
              <div className="text-xs font-semibold text-[#0F172A] flex items-center gap-2">
                <span>Active Interrogation Session</span>
                <span className="text-[10px] font-mono text-[#64748B] bg-[#E2E8F0] px-1.5 py-0.2 rounded">
                  {Math.floor(turns.length / 2)} Turns Grounded
                </span>
              </div>

              <button
                onClick={() => setTurns(initialQATurns)}
                className="text-[11px] font-mono text-[#64748B] hover:text-[#0F172A] flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset Context</span>
              </button>
            </div>

            {/* Conversation Messages */}
            <div className="p-4 sm:p-6 space-y-6 max-h-[640px] overflow-y-auto">
              {turns.map((turn) => {
                if (turn.speaker === 'user') {
                  return (
                    <div key={turn.id} className="space-y-1.5">
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-6 h-6 rounded bg-[#0F172A] text-white flex items-center justify-center font-mono text-[10px] font-bold">
                          LC
                        </div>
                        <span className="font-semibold text-[#0F172A]">{turn.authorName}</span>
                        <span className="text-[10px] font-mono text-[#94A3B8]">
                          {turn.timestamp}
                        </span>
                      </div>
                      <div className="pl-8 text-xs sm:text-sm font-semibold text-[#0F172A] leading-relaxed">
                        {turn.query}
                      </div>
                    </div>
                  );
                }

                // LexGuard Response
                return (
                  <div
                    key={turn.id}
                    className="space-y-3.5 pl-8 border-l-2 border-[#0284C7] ml-3"
                  >
                    {/* Header Badges */}
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-display font-bold text-[#0F172A] flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-[#0284C7]" aria-hidden="true" />
                        Grounded Answer
                      </span>
                      {turn.badges?.map((badge, i) => (
                        <span
                          key={i}
                          className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]"
                        >
                          {badge}
                        </span>
                      ))}
                    </div>

                    {/* Grounded Text */}
                    <div className="text-xs sm:text-sm text-[#334155] leading-relaxed">
                      {turn.groundedText}
                    </div>

                    {/* Carve-out Matrix if present */}
                    {turn.carveOutMatrix && (
                      <div className="p-3 rounded bg-[#F8FAFC] border border-[#CBD5E1] space-y-2">
                        <div className="text-[10px] font-mono font-bold text-[#0F172A] uppercase">
                          SECTION 8.4 CARVE-OUT MATRIX:
                        </div>
                        <div className="space-y-1 text-xs">
                          {turn.carveOutMatrix.map((item, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                              <span className="text-[#DC2626] font-bold shrink-0">!</span>
                              <div>
                                <span className="font-semibold text-[#0F172A]">{item.title}: </span>
                                <span className="text-[#475569]">{item.description}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Strategic Consideration callout */}
                    {turn.strategicConsideration && (
                      <div className="p-3 rounded bg-[#EFF6FF] border border-[#BFDBFE] text-xs space-y-1">
                        <div className="font-semibold text-[#0F172A] flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-[#0284C7]" aria-hidden="true" />
                          <span>Potential Strategic Consideration</span>
                        </div>
                        <p className="text-[#334155] leading-relaxed text-[11px]">
                          {turn.strategicConsideration}
                        </p>
                      </div>
                    )}

                    {/* Review Recommended Notice banner */}
                    {turn.reviewRecommendedNotice && (
                      <div className="p-3 rounded bg-[#FEF3C7] border border-[#FCD34D] text-xs space-y-1.5">
                        <div className="font-semibold text-[#92400E] flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-[#D97706]" aria-hidden="true" />
                          <span>{turn.reviewRecommendedNotice.title}</span>
                        </div>
                        <p className="text-[#92400E] text-[11px] leading-relaxed">
                          {turn.reviewRecommendedNotice.description}
                        </p>
                        {turn.reviewRecommendedNotice.anchorLink && (
                          <div
                            onClick={() => {
                              if (turn.reviewRecommendedNotice?.anchorLink?.includes('Page 4')) {
                                setActivePage(4);
                              } else if (turn.reviewRecommendedNotice?.anchorLink?.includes('Page 11')) {
                                setActivePage(11);
                              }
                            }}
                            className="pt-1 font-mono text-[10px] text-[#0284C7] hover:underline cursor-pointer"
                          >
                            {turn.reviewRecommendedNotice.anchorLink}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Grounding Citations */}
                    {turn.groundingCitations && (
                      <div className="space-y-2 pt-1">
                        <div className="text-[10px] font-mono font-bold text-[#64748B] uppercase">
                          PRIMARY GROUNDING CITATIONS (ACTIVE INFERENCES)
                        </div>
                        <div className="grid sm:grid-cols-2 gap-2">
                          {turn.groundingCitations.map((c, i) => (
                            <div
                              key={i}
                              onClick={() => {
                                setActivePage(c.page);
                                setHighlightedQuote(c.quote);
                              }}
                              className="p-2.5 rounded bg-white border border-[#CBD5E1] space-y-1 text-xs cursor-pointer hover:border-[#0284C7] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <div className="flex items-center justify-between font-mono text-[10px]">
                                <span className="font-bold text-[#0F172A]">
                                  Page {c.page} • {c.section}
                                </span>
                                <span className={`px-1.5 py-0.2 rounded font-semibold ${
                                  c.tag.includes('Unverified')
                                    ? 'bg-[#FEE2E2] text-[#DC2626] border border-[#FECACA]'
                                    : 'bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]'
                                }`}>
                                  {c.tag}
                                </span>
                              </div>
                              <p className="text-[11px] text-[#475569] italic line-clamp-2">
                                {c.quote}
                              </p>
                              <div className="text-[10px] font-mono text-[#0284C7] hover:underline pt-0.5 flex items-center gap-1">
                                <span>{c.actionText}</span>
                                <ExternalLink className="w-2.5 h-2.5" aria-hidden="true" />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action Bar */}
                    <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-[#64748B] border-t border-[#F1F5F9]">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(turn.groundedText || '');
                            setCopiedId(turn.id);
                            setTimeout(() => setCopiedId(null), 2000);
                          }}
                          className="hover:text-[#0F172A] flex items-center gap-1"
                        >
                          {copiedId === turn.id ? (
                            <>
                              <Check className="w-3 h-3 text-[#059669]" aria-hidden="true" />
                              <span>Copied Finding</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" aria-hidden="true" />
                              <span>Copy Finding</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => alert('Pinned to Lawyer Summary Brief (/brief)')}
                          className="hover:text-[#0F172A] flex items-center gap-1"
                        >
                          <Pin className="w-3 h-3" />
                          <span>Pin to Summary Brief</span>
                        </button>
                      </div>

                      <div className="text-[10px]">
                        Grounding Latency: {turn.groundingLatency} • Confidence: {turn.confidence}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Dynamic Loading State */}
              {isLoading && (
                <div className="space-y-3.5 pl-8 border-l-2 border-[#0284C7] ml-3 animate-pulse">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 text-[#0284C7] animate-spin" aria-hidden="true" />
                    <span className="text-xs font-display font-bold text-[#0F172A]">
                      LexGuard Grounded Retrieval &amp; Verification...
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                      PostgreSQL pgvector Query
                    </span>
                  </div>
                  <div className="text-xs text-[#64748B] leading-relaxed">
                    Searching document embeddings, executing isolated tenant vector similarity search, and verifying verbatim citation quotes against retrieved chunks...
                  </div>
                </div>
              )}
            </div>

            {/* Input Bar Area */}
            <div className="border-t border-[#E2E8F0] p-4 bg-[#F8FAFC] space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <span className="font-mono text-[11px] text-[#059669] flex items-center gap-1 font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#059669]"></span>
                  Strict Document Grounding (Zero-Hallucination ON)
                </span>

                <div className="flex items-center gap-1 text-[11px] font-mono">
                  <span className="text-[#64748B]">Citation Depth:</span>
                  <button
                    onClick={() => setCitationDepth('comprehensive')}
                    className={`px-2 py-0.5 rounded ${
                      citationDepth === 'comprehensive'
                        ? 'bg-[#0F172A] text-white font-bold'
                        : 'bg-white border border-[#CBD5E1] text-[#64748B]'
                    }`}
                  >
                    Comprehensive
                  </button>
                  <button
                    onClick={() => setCitationDepth('executive')}
                    className={`px-2 py-0.5 rounded ${
                      citationDepth === 'executive'
                        ? 'bg-[#0F172A] text-white font-bold'
                        : 'bg-white border border-[#CBD5E1] text-[#64748B]'
                    }`}
                  >
                    Executive Brief
                  </button>
                </div>
              </div>

              {/* Text Input */}
              <div className="relative">
                <Search className="w-4 h-4 text-[#64748B] absolute left-3.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleExecuteQuery();
                  }}
                  aria-label="Ask a contract question grounded strictly in document text"
                  placeholder="Ask any question grounded strictly in the text of this contract..."
                  className="w-full pl-10 pr-24 py-3 bg-white border border-[#CBD5E1] rounded-lg text-xs font-sans text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#0284C7] focus:ring-offset-1 focus:border-[#0284C7] shadow-2xs"
                />
                <button
                  onClick={handleExecuteQuery}
                  disabled={!inputText.trim() || isLoading}
                  aria-label="Execute document interrogation query"
                  className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded flex items-center gap-1.5 transition-colors disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-[#0284C7]"
                >
                  <span>{isLoading ? 'Querying...' : 'Execute'}</span>
                  <ArrowUp className="w-3.5 h-3.5" aria-hidden="true" />
                </button>
              </div>

              <div className="text-[10px] font-mono text-[#64748B] flex items-center justify-between">
                <span>Target Vector Scope: PostgreSQL Scoped Document Id ({activeDocId})</span>
                <span>Press ↵ to analyze • Shift+↵ for multi-line query</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right 4 Cols: Evidence & Source Grounding Viewport */}
        <div className="lg:col-span-5 xl:col-span-4 space-y-4">
          <div className="scaffold-card border border-[#CBD5E1] p-4 space-y-3.5 bg-white">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-2.5">
              <div>
                <h3 className="text-sm font-display font-bold text-[#0F172A]">
                  Evidence &amp; Source Grounding
                </h3>
                <div className="text-[10px] font-mono text-[#64748B]">
                  Live Document Viewport • Page {activePage}
                </div>
              </div>

              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE]">
                OCR: {mockDocumentViewport.ocrAccuracy}%
              </span>
            </div>

            {/* Document Viewer Box */}
            <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-lg p-3 space-y-2 font-mono text-[11px]">
              {/* Controls */}
              <div className="flex items-center justify-between text-[#64748B] pb-1.5 border-b border-[#E2E8F0]">
                <span>
                  P. {activePage} / {pageCount}
                </span>
                <span className="text-[10px]">{currentPageData.section}</span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setZoomLevel(Math.max(80, zoomLevel - 10))}
                    className="p-0.5 hover:text-[#0F172A]"
                  >
                    <ZoomOut className="w-3 h-3" />
                  </button>
                  <span className="text-[9px]">{zoomLevel}%</span>
                  <button
                    onClick={() => setZoomLevel(Math.min(130, zoomLevel + 10))}
                    className="p-0.5 hover:text-[#0F172A]"
                  >
                    <ZoomIn className="w-3 h-3" />
                  </button>
                </div>
              </div>

              {/* Verbatim Document Article Text with highlight */}
              <div
                style={{ fontSize: `${(11 * zoomLevel) / 100}px` }}
                className="leading-relaxed text-[#334155] whitespace-pre-line max-h-64 overflow-y-auto pr-1"
              >
                {renderHighlightedArticleText(currentPageData.text, highlightedQuote)}
              </div>

              <div className="pt-2 border-t border-[#E2E8F0] text-[9px] text-[#059669] font-mono flex items-center justify-between">
                <span>{mockDocumentViewport.sha256Digest}</span>
                <Lock className="w-3 h-3 text-[#64748B]" aria-hidden="true" />
              </div>
            </div>

            {/* Suggested Legal Strategy (Counsel Prep) */}
            <div className="scaffold-card p-3 bg-[#EFF6FF] border border-[#BFDBFE] space-y-2">
              <div className="text-[10px] font-mono font-bold uppercase text-[#0284C7] flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-[#0284C7]" aria-hidden="true" />
                Suggested Legal Strategy (Counsel Prep)
              </div>

              <p className="text-xs text-[#1E293B] leading-relaxed">
                {mockDocumentViewport.suggestedStrategy.counselPrep}
              </p>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <button
                  onClick={() => alert('Inserted proposed 12-month redline into comparison desk (/compare)')}
                  className="py-1 px-2 text-[10px] font-mono font-semibold bg-[#0F172A] text-white rounded hover:bg-[#1E293B] text-center"
                >
                  Insert Proposed Redline
                </button>
                <button
                  onClick={() => alert('Opening 2,400 SaaS precedent benchmark ledger...')}
                  className="py-1 px-2 text-[10px] font-mono font-semibold bg-white border border-[#CBD5E1] text-[#0F172A] rounded hover:bg-[#F1F5F9] text-center"
                >
                  Compare Market Baseline
                </button>
              </div>
            </div>

            {/* Related Document Anchors */}
            <div className="space-y-1.5 pt-1">
              <div className="text-[10px] font-mono font-bold text-[#64748B] uppercase">
                RELATED DOCUMENT ANCHORS
              </div>
              <div className="space-y-1">
                {mockDocumentViewport.relatedAnchors.map((anchor, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setActivePage(anchor.page);
                      setHighlightedQuote(null);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-left font-mono text-[11px] transition-colors ${
                      activePage === anchor.page
                        ? 'bg-[#EFF6FF] text-[#0284C7] border border-[#BFDBFE] font-bold'
                        : 'bg-[#F8FAFC] text-[#334155] hover:bg-[#F1F5F9] border border-[#E2E8F0]'
                    }`}
                  >
                    <span>{anchor.section}</span>
                    <span className="text-[10px] text-[#94A3B8]">Page {anchor.page}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
