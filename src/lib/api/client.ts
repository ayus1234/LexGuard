/**
 * LexGuard Backend API Client
 * Clean, decoupled interface for interacting with the FastAPI document intelligence backend.
 */

import type { CorpusListResponse, CorpusStatsResponse } from '@/types';

export interface PageExtraction {
  page_number: number;
  text: string;
  character_start: number;
  character_end: number;
  word_count: number;
}

export interface SectionOutline {
  title: string;
  page_number: number;
  character_offset: number;
}

export interface DocumentMetadata {
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  sha256_hash: string;
  extraction_engine: string;
  processed_at: string;
}

export interface DocumentResponse {
  document_id: string;
  filename: string;
  file_type: 'pdf' | 'docx' | 'txt' | string;
  source_type: string;
  page_count: number;
  word_count: number;
  character_count: number;
  extracted_text: string;
  pages: PageExtraction[];
  sections: SectionOutline[];
  metadata: DocumentMetadata;
  created_at: string;
  processing_status: string;
}

export type ImportanceLevel = 'high' | 'medium' | 'standard';
export type ReviewLevel = 'review_recommended' | 'attention_warranted' | 'advisory_only';
export type ClauseCategory =
  | 'Liability'
  | 'Indemnification'
  | 'Intellectual Property'
  | 'Confidentiality'
  | 'Payment'
  | 'Termination'
  | 'Renewal'
  | 'Data Privacy'
  | 'Security'
  | 'Dispute Resolution'
  | 'Governing Law'
  | 'Service Levels'
  | 'Restrictions'
  | 'Other';

export interface Party {
  name: string;
  role: string;
}

export interface KeyInformation {
  category: string;
  label: string;
  value: string | null;
  source_reference: string | null;
}

export interface Clause {
  section: string | null;
  title: string;
  category: ClauseCategory;
  importance: ImportanceLevel;
  plain_language_summary: string;
  source_reference: string | null;
}

export interface AttentionArea {
  title: string;
  description: string;
  why_it_may_matter: string;
  source_reference: string | null;
  review_level: ReviewLevel;
}

export interface Citation {
  page: number | null;
  section: string | null;
  quoted_text: string;
  character_start: number | null;
  character_end: number | null;
  verified: boolean;
}

export interface DocumentAnalysis {
  document_summary: string;
  document_type: string;
  jurisdiction: string | null;
  parties: Party[];
  key_information: KeyInformation[];
  clauses: Clause[];
  attention_areas: AttentionArea[];
  citations: Citation[];
}

export interface AnalysisMetadata {
  model: string;
  processing_time_ms: number;
  character_count: number;
  prompt_tokens_estimated: number;
  citations_verified_count: number;
  citations_unverified_count: number;
  analyzed_at: string;
}

export interface DocumentAnalysisResponse {
  document_id: string;
  analysis: DocumentAnalysis;
  metadata: AnalysisMetadata;
}

export type GroundingStatus = 'grounded' | 'insufficient_evidence' | 'document_not_indexed';

export interface RetrievalResultItem {
  chunk_id: string;
  text: string;
  similarity_score: number;
  document_id: string;
  section: string | null;
  page_start: number;
  page_end: number;
  character_start: number;
  character_end: number;
}

export interface RetrievalResult {
  document_id: string;
  query: string;
  grounding_status: GroundingStatus;
  results: RetrievalResultItem[];
}

export interface DocumentIndexResponse {
  document_id: string;
  chunk_count: number;
  indexed: boolean;
  processing_time_ms: number;
}

export interface GroundedCitation {
  page: number | null;
  section: string | null;
  section_title?: string | null;
  quoted_text: string;
  chunk_id?: string | null;
  character_start?: number | null;
  character_end?: number | null;
  verified: boolean;
}

export interface RetrievedSourceItem {
  chunk_id: string;
  page: number | null;
  section: string | null;
  similarity: number;
}

export interface GroundedAnswerTelemetry {
  retrieval_ms: number;
  generation_ms: number;
  total_ms: number;
}

export interface CarveOutItem {
  type: 'urgent' | 'standard';
  title: string;
  description: string;
}

export interface ReviewNotice {
  title: string;
  description: string;
  anchor_link?: string | null;
}

export interface DocumentAskRequest {
  document_id: string;
  session_id?: string | null;
  question: string;
  top_k?: number;
}

export interface DocumentAskResponse {
  document_id: string;
  session_id?: string | null;
  question: string;
  answer: string;
  grounded: boolean;
  confidence: string;
  badges: string[];
  citations: GroundedCitation[];
  retrieved_sources: RetrievedSourceItem[];
  carve_out_matrix?: CarveOutItem[] | null;
  strategic_consideration?: string | null;
  review_recommended_notice?: ReviewNotice | null;
  model: string;
  telemetry: GroundedAnswerTelemetry;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

export class LexGuardApiClientError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', status: number = 500) {
    super(message);
    this.name = 'LexGuardApiClientError';
    this.code = code;
    this.status = status;
  }
}

// Determine API base URL with proper environment handling
// Production deployments should set NEXT_PUBLIC_API_BASE_URL explicitly
// Development allows localhost fallback
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 
  (typeof window !== 'undefined' && window.location?.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'http://127.0.0.1:8000');

// Log warning if production build without explicit configuration
if (process.env.NODE_ENV === 'production' && !process.env.NEXT_PUBLIC_API_BASE_URL) {
  console.warn(
    '[LexGuard] NEXT_PUBLIC_API_BASE_URL not set in production build. ' +
    'API requests may fail. Please configure this environment variable.'
  );
}

export const apiClient = {
  /**
   * Health check endpoint
   */
  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    const res = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!res.ok) {
      throw new LexGuardApiClientError('Health check failed', 'SERVICE_UNAVAILABLE', res.status);
    }

    return res.json();
  },

  /**
   * Uploads and parses a PDF, DOCX, or TXT legal document
   */
  async uploadDocument(file: File): Promise<DocumentResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData,
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard backend service. Please check your connection.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Response was not JSON
      }

      const message = errorData?.error?.message || `Server returned error (${res.status})`;
      const code = errorData?.error?.code || 'SERVER_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Analyzes an ingested document using the Gemini legal intelligence engine
   */
  async analyzeDocument(document: DocumentResponse): Promise<DocumentAnalysisResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ document }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard backend analysis service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Response was not JSON
      }

      const message = errorData?.error?.message || `Analysis failed (${res.status})`;
      const code = errorData?.error?.code || 'ANALYSIS_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Indexes a normalized legal document into the ChromaDB vector store
   */
  async indexDocument(document: DocumentResponse): Promise<DocumentIndexResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/index`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ document }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard vector indexing service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Indexing failed (${res.status})`;
      const code = errorData?.error?.code || 'INDEXING_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Performs semantic similarity retrieval over indexed document chunks
   */
  async searchDocument(
    documentId: string,
    query: string,
    topK: number = 5
  ): Promise<RetrievalResult> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/retrieval/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          query,
          top_k: topK,
        }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard retrieval service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Retrieval failed (${res.status})`;
      const code = errorData?.error?.code || 'RETRIEVAL_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Deletes document vector embeddings from ChromaDB / PostgreSQL
   */
  async deleteDocumentVectors(documentId: string): Promise<{ document_id: string; deleted: boolean }> {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/vectors`, {
      method: 'DELETE',
    });

    if (!res.ok) {
      throw new LexGuardApiClientError('Failed to delete document vectors', 'DELETE_ERROR', res.status);
    }

    return res.json();
  },

  /**
   * Performs grounded Q&A against the document vector embeddings using PostgreSQL pgvector + Gemini
   */
  async askDocument(
    documentId: string,
    question: string,
    topK: number = 5,
    sessionId?: string | null
  ): Promise<DocumentAskResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          question,
          top_k: topK,
          session_id: sessionId || null,
        }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard Q&A service. Please verify backend availability.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Q&A failed (${res.status})`;
      const code = errorData?.error?.code || 'QA_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Generates or retrieves a structured Lawyer Preparation Brief with verbatim citation grounding
   */
  async getLawyerBrief(
    documentId: string,
    document?: DocumentResponse | null,
    forceRegenerate: boolean = false
  ): Promise<LawyerBriefResponse> {
    let res: Response;
    try {
      res = await fetch(
        `${API_BASE_URL}/api/v1/documents/${documentId}/brief?force_regenerate=${forceRegenerate}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: JSON.stringify({
            document_id: documentId,
            document: document || null,
          }),
        }
      );
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard brief service. Please ensure the backend is running.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Brief generation failed (${res.status})`;
      const code = errorData?.error?.code || 'BRIEF_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Exports the Lawyer Preparation Brief as a high-fidelity PDF
   */
  async exportBriefPdf(
    documentId: string,
    brief?: LawyerBrief | null,
    document?: DocumentResponse | null
  ): Promise<Blob> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/brief/export/pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          brief: brief || null,
          document: document || null,
        }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard export service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      throw new LexGuardApiClientError(`PDF export failed (${res.status})`, 'EXPORT_ERROR', res.status);
    }

    const arrayBuf = await res.arrayBuffer();
    return new Blob([arrayBuf], { type: 'application/pdf' });
  },

  /**
   * Exports the Lawyer Preparation Brief as a formatted Microsoft Word document (.docx)
   */
  async exportBriefDocx(
    documentId: string,
    brief?: LawyerBrief | null,
    document?: DocumentResponse | null
  ): Promise<Blob> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/brief/export/docx`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          brief: brief || null,
          document: document || null,
        }),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard export service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      throw new LexGuardApiClientError(`DOCX export failed (${res.status})`, 'EXPORT_ERROR', res.status);
    }

    const arrayBuf = await res.arrayBuffer();
    return new Blob([arrayBuf], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
  },

  /**
   * Creates a cryptographically secure, time-limited share token for an executive dossier
   */
  async createShareDossier(request: CreateShareRequest): Promise<CreateShareResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/share/dossier`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(request),
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard share service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errData: ApiErrorResponse | null = null;
      try {
        errData = await res.json();
      } catch {
        // non-json
      }
      const message = errData?.error?.message || `Failed to create secure share link (${res.status})`;
      const code = errData?.error?.code || 'SHARE_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Retrieves a shared read-only dossier by token
   */
  async getSharedDossier(shareId: string): Promise<SharedDossierResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/share/dossier/${shareId}`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard share service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errData: ApiErrorResponse | null = null;
      try {
        errData = await res.json();
      } catch {
        // non-json
      }
      const message = errData?.error?.message || `Failed to load shared dossier (${res.status})`;
      const code = errData?.error?.code || 'SHARE_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Helper utility to trigger immediate client-side file download from a Blob
   */
  triggerDownload(blob: Blob, filename: string): void {
    if (typeof window === 'undefined') return;
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    link.style.display = 'none';
    document.body.appendChild(link);
    // Use setTimeout to ensure the link is in the DOM before clicking
    setTimeout(() => {
      link.click();
      // Delay cleanup to let the browser initiate the download
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 200);
    }, 0);
  },

  /**
   * Retrieves corpus documents with pagination and filtering
   */
  async getCorpusDocuments(params: {
    page?: number;
    page_size?: number;
    doc_type?: string | null;
    category?: string | null;
    jurisdiction?: string | null;
    search?: string | null;
  }): Promise<CorpusListResponse> {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params.doc_type) queryParams.append('doc_type', params.doc_type);
    if (params.category) queryParams.append('category', params.category);
    if (params.jurisdiction) queryParams.append('jurisdiction', params.jurisdiction);
    if (params.search) queryParams.append('search', params.search);

    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/corpus/documents?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard corpus service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Corpus retrieval failed (${res.status})`;
      const code = errorData?.error?.code || 'CORPUS_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Retrieves corpus statistics and available filter values
   */
  async getCorpusStats(): Promise<CorpusStatsResponse> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/corpus/stats`, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard corpus service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Corpus stats retrieval failed (${res.status})`;
      const code = errorData?.error?.code || 'CORPUS_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },

  /**
   * Retrieves category counts for a specific document type
   */
  async getCorpusCategories(docType?: string | null): Promise<{
    doc_type: string;
    total_documents: number;
    categories: Array<{name: string; count: number}>;
  }> {
    const queryParams = new URLSearchParams();
    if (docType) queryParams.append('doc_type', docType);

    let res: Response;
    try {
      const url = `${API_BASE_URL}/api/v1/corpus/categories${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      res = await fetch(url, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });
    } catch (networkErr: any) {
      throw new LexGuardApiClientError(
        'Unable to connect to LexGuard corpus service.',
        'NETWORK_ERROR',
        0
      );
    }

    if (!res.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await res.json();
      } catch {
        // Non-JSON response
      }

      const message = errorData?.error?.message || `Corpus categories retrieval failed (${res.status})`;
      const code = errorData?.error?.code || 'CORPUS_ERROR';
      throw new LexGuardApiClientError(message, code, res.status);
    }

    return res.json();
  },
};

export interface BriefSourceCitation {
  page: number | null;
  section: string | null;
  quoted_text: string;
  character_start: number | null;
  character_end: number | null;
  verified: boolean;
}

export interface KeyInformationItem {
  category: string;
  label: string;
  value: string | null;
  source_reference: string | null;
  page: number | null;
  section: string | null;
  verified: boolean;
}

export interface AttentionAreaItem {
  id: string;
  title: string;
  category: string;
  description: string;
  why_it_matters: string;
  review_level: 'review_recommended' | 'attention_warranted' | 'advisory_only';
  source_reference: string | null;
  page: number | null;
  section: string | null;
  verified: boolean;
}

export interface NegotiationPointItem {
  id: string;
  title: string;
  category: string;
  current_provision: string;
  discussion_point: string;
  suggested_compromise: string | null;
  market_baseline: string | null;
  source_reference: string | null;
  page: number | null;
  section: string | null;
  verified: boolean;
}

export interface CounselQuestionItem {
  id: string;
  priority: 'High' | 'Medium' | 'Standard';
  category: string;
  agenda_topic: string;
  why_discuss: string;
  suggested_phrasing: string | null;
  contract_citation: string | null;
  market_standard: string | null;
  page: number | null;
  section: string | null;
  verified: boolean;
}

export interface BriefChecklistItem {
  id: string;
  section_index: number;
  section_title: string;
  title: string;
  citation: string;
  badge_text: string;
  badge_variant: 'urgent' | 'high' | 'medium' | 'scheduled' | 'verified';
  completed: boolean;
  page: number | null;
  section: string | null;
}

export interface ImportantClauseItem {
  section: string | null;
  title: string;
  category: string;
  summary: string;
  source_reference: string | null;
  page: number | null;
  verified: boolean;
}

export interface LawyerBrief {
  document_id: string;
  document_title: string;
  document_type: string;
  jurisdiction: string | null;
  generated_at: string;
  executive_summary: string;
  key_information: KeyInformationItem[];
  attention_areas: AttentionAreaItem[];
  negotiation_points: NegotiationPointItem[];
  counsel_questions: CounselQuestionItem[];
  checklist: BriefChecklistItem[];
  important_clauses: ImportantClauseItem[];
  citations: BriefSourceCitation[];
  disclaimer: string;
  model: string;
  citations_verified_count: number;
  citations_unverified_count: number;
  processing_time_ms: number;
}

export interface LawyerBriefResponse {
  document_id: string;
  brief: LawyerBrief;
}

export interface CreateShareRequest {
  document_id: string;
  title?: string | null;
  brief: LawyerBrief;
  ttl_hours?: number;
}

export interface CreateShareResponse {
  share_id: string;
  expires_at: string;
  share_url: string;
  title: string;
  is_localhost: boolean;
}

export interface SharedDossierResponse {
  share_id: string;
  document_id: string;
  title: string;
  created_at: string;
  expires_at: string;
  brief: LawyerBrief;
  disclaimer: string;
}

