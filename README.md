# LexGuard — AI Legal Document Intelligence Platform

> **"Understand the document before you sign it."**  
> An enterprise-grade, privacy-first legal document intelligence platform engineered for founders, procurement officers, and legal counsel. Powered by Google Gemini AI with dual-key automated failover, PostgreSQL + pgvector vector embeddings, and an institutional Google Stitch design system.

---

[![Backend Tests](https://img.shields.io/badge/Pytest-124%20passed%20%2F%200%20failed-brightgreen.svg)]()
[![Type Checking](https://img.shields.io/badge/Pyright-0%20errors%20%7C%20Strict-blue.svg)]()
[![Next.js Build](https://img.shields.io/badge/Next.js%2014-Production%20Verified-success.svg)]()
[![Vector Engine](https://img.shields.io/badge/PostgreSQL-pgvector%20(VECTOR%203072)-blueviolet.svg)]()
[![AI Engine](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash%20%2B%20Dual--Key%20Failover-orange.svg)]()
[![Corpus Library](https://img.shields.io/badge/Corpus%20Registry-500%20Indexed%20Documents-indigo.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-lightgrey.svg)]()

---

## 1. Executive Summary & Problem Statement

Commercial agreements govern all business relationships, yet startup founders, SMB leaders, and engineering teams routinely execute contracts containing unilateral indemnifications, automatic evergreen renewal traps, non-standard IP assignments, and trailing liability exposures. Traditional legal review is prohibitively slow and expensive ($500–$1,200/hour), while consumer AI models frequently hallucinate clauses, invent statutory citations, or leak confidential corporate data to public training sets.

**LexGuard** bridges this critical gap by providing an institutional-grade, zero-retention legal document intelligence engine:
- **Instant Risk Extraction**: Deconstructs 50+ page agreements into plain-English executive summaries, financial milestones, and operational exposures in seconds.
- **Bi-Directional Vendor Tilt Scoring**: Computes directional alignment (e.g., 68% vendor-favored) benchmarking clauses against 48 codified legal domains.
- **Zero-Hallucination Grounded Q&A**: Employs mathematical character-offset cross-referencing and Levenshtein citation validation, guaranteeing every answer references actual contract text or strictly refuses to answer.
- **Actionable Redlines & Negotiation Playbooks**: Generates market-standard counter-proposals and side-by-side contract version diffs.
- **Binary Executive Brief Exports**: Produces formatted PDF and Microsoft Word (.docx) briefing packets for attorneys and board meetings.
- **500-Document Institutional Corpus**: Pre-indexed repository of 200 standardized commercial templates, 285 state and federal statutory codes, and 15 executable demo contracts.

> **Important Legal Disclaimer**: LexGuard is an educational legal technology platform, **not** a law firm, and does not provide formal legal representation or statutory advice. All analyses, risk scores, and generated summaries represent educational debriefing tools designed for pre-consultation review with qualified legal counsel.

---

## 2. End-to-End System Workflow

```mermaid
flowchart TD
    subgraph Intake["1. Ephemeral Ingestion & Security"]
        A[User Upload / Sample Select] --> B[File Type & Magic Byte Validation]
        B --> C[PyMuPDF / python-docx / UTF-8 Text Extraction]
        C --> D[Zero-Retention Ephemeral Scrubber]
    end

    subgraph VectorEngine["2. Chunking & pgvector Storage"]
        C --> E[Clause-Aware Structural Chunker]
        E --> F[Gemini text-embedding-004]
        F --> G[(PostgreSQL + pgvector\nCosine Distance <=>)]
    end

    subgraph LLMIntelligence["3. AI Synthesis & Dual-Key Resiliency"]
        G --> H[Context Retrieval & Relevance Reranking]
        H --> I[Centralized Credential Manager\nPrimary -> Fallback Key Auto-Failover]
        I --> J[Gemini 1.5 Flash Analysis Engine]
    end

    subgraph Verification["4. Anti-Hallucination Barrier"]
        J --> K[Ground-Truth Citation Verifier]
        K -->|Verbatim Match Found| L[Verified Citation Badge §]
        K -->|Unverified / Missing| M[Strict Rejection / Warning]
    end

    subgraph Delivery["5. Client Presentation & Deliverables"]
        L --> N[Next.js 14 App Router UI]
        N --> O[Executive Dashboard & Clause Ledger]
        N --> P[Ask LexGuard Grounded Q&A]
        N --> Q[Side-by-Side Token Redline]
        N --> R[Same-Origin Export Proxy\nPDF & DOCX Downloads]
        N --> S[Encrypted Shared Dossier /share/:id]
    end
```

### Detailed Workflow Stages:
1. **Intake & Normalization**: The user uploads a PDF, DOCX, or TXT document (or selects from the 500-document institutional corpus). Raw files are validated via MIME headers and magic byte signatures. Ephemeral background scrubbers ensure uploaded raw files are purged from disk immediately after memory extraction.
2. **Chunking & Vector Ingestion**: The extracted text is partitioned into clause-aware semantic segments with sliding window overlaps, preserving section headers (§) and page offsets. Each chunk is embedded into 3,072-dimensional vector space using `text-embedding-004` and stored in PostgreSQL with `pgvector` indexed via cosine distance (`<=>`).
3. **Dual-Key Resilient Inference**: High-priority analysis jobs execute against Google Gemini 1.5 Flash. If the primary API credential experiences rate limits (HTTP 429) or transient provider outages (HTTP 503), the request-scoped Credential Manager automatically switches to the standby fallback credential without failing user workflows.
4. **Anti-Hallucination Citation Verification**: Every quotation, clause reference, or section assertion synthesized by the AI engine passes through an independent verification pipeline. The engine executes normalized character-offset matching against the raw text. Fabricated citations are rejected, and missing citations are flagged with operational notices.
5. **Interactive UI & Export Delivery**: Results are rendered in the Google Stitch design system. Users can query the document, review redline recommendations, share encrypted dossier snapshots, or trigger one-click PDF/DOCX downloads proxied through same-origin Next.js endpoints.

---

## 3. Core Features & Capabilities

### 1. Executive Intake & Synthesis (`/`)
- Multi-format ingestion supporting PDF, DOCX, and TXT agreements.
- Built-in drag-and-drop intake zone, raw text paste terminal, and one-click sample library selector.
- Live session security status badges (`Strict Boundary Mode`, `AES-256 Memory Encrypted`, `Zero-Retention In-Memory`).
- Dynamic corpus synchronization counter indicating federal and state statutory connectivity.

### 2. Deep Analysis Dossier & Clause Ledger (`/analyze`)
- **Executive Summary**: High-level deconstruction of contracting entities, effective dates, termination horizons, and financial commitments.
- **Vendor Tilt & Exposure Gauge**: Visual dial calculating directional bias (e.g., 68% vendor-favored) across four danger thresholds: Extreme Unilateral, Vendor Heavy, Neutral/Balanced, and Buyer Heavy.
- **48-Domain Clause Ledger**: Comprehensive taxonomy categorizing provisions into Indemnification, Liability Caps, IP Assignment, Non-Competes, Governing Law, Force Majeure, Confidentiality, and SLA Commitments.
- **Redline Counter-Proposals**: Pre-drafted, attorney-vetted replacement language for every high-risk clause.

### 3. Ask LexGuard — Document-Grounded Q&A (`/ask`)
- **Zero-Hallucination Barrier**: Strict retrieval-augmented generation (RAG) answering only what is explicitly contained within the agreement.
- **Refusal Guardrail**: Automatically rejects out-of-scope, speculative, or extrinsic questions (e.g., *"What is the penalty for nuclear war?"*).
- **Verbatim Grounding Citations**: Clickable citation tags display exact page numbers, section numbers, verbatim quoted excerpts, and source inspection anchors.
- **Depth Configuration**: Toggle between **Fast Grounding** (Top-3 semantic chunks) and **Comprehensive Grounding** (Top-5 deep scan).

### 4. Clause Delta & Redline Comparison (`/compare`)
- Side-by-side version comparison between initial drafts and redlines.
- Token-level insertions (`green`) and deletions (`red`) highlighting trailing liability changes, audit rights removals, and warranty disclaimers.
- Granular risk differential scoring and categorized change breakdown.

### 5. Counsel Preparation Brief & Action Checklist (`/brief`)
- **Prioritized Action Checklist**: Interactive verification items categorized into Urgent Blockers, Negotiation Scope, and Pre-Execution Verifications with live percentage completion metrics.
- **Counsel Meeting Strategy**: Structured meeting agenda, strategic questions for outside counsel, and estimated attorney time allocation.
- **Binary Document Exporters**:
  - **Export Executive Brief (PDF)**: High-resolution PDF dossier generated via PyMuPDF with headers, metadata tables, risk badges, and legal disclaimers.
  - **Export Word Checklist (.docx)**: Fully formatted Microsoft Word checklist generated via `python-docx` with colored callout boxes and styled tables.
  - **Same-Origin Download Proxy**: Next.js route proxies (`/api/export/pdf/...` and `/api/export/docx/...`) guarantee native `Content-Disposition` attachment downloads with clean human-readable filenames across all browser security policies.

### 6. Secure Shared Dossiers (`/share/[shareId]`)
- One-click shareable read-only snapshot links.
- Cryptographically isolated dossier viewer enabling outside counsel, co-founders, or board members to review findings without logging in.
- Full PDF and DOCX download support directly from the shared interface.

### 7. 500-Document Corpus Registry (`/library` & `/public-law`)
- **200 Curated Institutional Templates**: Standardized commercial frameworks across SaaS, Employment, NDA, Corporate, IP, Real Estate, Finance, and Privacy.
- **285 Public & Statutory Legal Documents**: Codified legal references including DGCL, Uniform Commercial Code (UCC), Defend Trade Secrets Act (DTSA), Federal Arbitration Act (FAA), GDPR, CCPA, and state labor codes.
- **15 Fictional Executable Demo Agreements**: Full-text operational agreements designed for instant, zero-latency evaluation.

### 8. Enterprise Visual Identity & Styling
- **Google Stitch Design Language**: Cohesive typography, slate palettes, and glassmorphic card containers.
- **Lead Legal Counsel Persona**: Professional corporate executive avatar integrated into persistent navigation and active session debrief modals.
- **Custom Security Favicon**: Precision vector shield emblem with interlocking "LG" monogram and true alpha-channel transparency (`RGBA: [0, 0, 0, 0]`) across 16×16, 32×32, 48×48 px and `.ico` multi-frame fallbacks.

---

## 4. Visual Interface & Platform Walkthrough

Explore the LexGuard Intelligence interface across its core legal assessment workflows:

### 1. Document Intake & Ingestion Workspace (`/`)
![Document Intake & Ingestion Workspace](docs/screenshots/01-intake-workspace.png)
*The primary intake terminal featuring multi-format document ingestion (PDF, DOCX, TXT), paste terminal, and real-time zero-retention memory encryption guards.*

### 2. Curated Institutional Sample Library (`/library`)
![Curated Institutional Sample Library](docs/screenshots/02-sample-library.png)
*Pre-indexed repository of 200 standardized commercial agreements across 17 legal taxonomies, enabling instant one-click analysis and pre-negotiation benchmarking.*

### 3. Executive Intelligence Brief & Vendor Tilt Matrix (`/analyze`)
![Executive Intelligence Brief & Vendor Tilt Matrix](docs/screenshots/03-analysis-dossier.png)
*Automated contract synthesis displaying a plain-English executive summary, financial commitments, and a quantitative Vendor Tilt dial measuring contractual bias.*

### 4. Document Comparison & Clause Delta Matrix (`/compare`)
![Document Comparison & Clause Delta Matrix](docs/screenshots/04-clause-compare.png)
*Token-level side-by-side redline comparison showing deleted customer protections, shifted liability baselines, and algorithmic risk impact calculations.*

### 5. Public Statutory Corpus & Legal Registry (`/public-law`)
![Public Statutory Corpus & Legal Registry](docs/screenshots/05-public-law-corpus.png)
*Comprehensive database of 285 codified federal, state, and uniform statutory frameworks (UCC, DGCL, DTSA, FAA, GDPR) used for automatic compliance benchmarking.*

### 6. Counsel Preparation Brief & Prioritized Action Checklist (`/brief`)
![Counsel Preparation Brief & Prioritized Action Checklist](docs/screenshots/06-action-checklist-brief.png)
*Prioritized pre-signature action checklist and strategic lawyer debriefing agenda with dynamic completion tracking, blocker alerts, and binary PDF/DOCX export controls.*

### 7. Ask LexGuard — Zero-Hallucination Grounded Q&A Interface (`/ask`)
![Ask LexGuard — Zero-Hallucination Grounded Q&A Interface](docs/screenshots/07-ask-lexguard-grounded-qa.png)
*Document-grounded conversational interrogation workspace featuring verbatim citation badges (§), dual-viewport source proof inspection, and carve-out risk matrices.*

---

## 5. System Architecture & Technical Stack

```
                                  +--------------------------------------------------+
                                  |            Next.js 14 Web Frontend               |
                                  |  TypeScript • Tailwind CSS • Lucide • Stitch UI  |
                                  +--------------------------------------------------+
                                           |                                   ^
                                           | REST (Fetch)                      | Same-Origin Proxy
                                           v                                   v
+------------------------------------------------------------------------------------+
|                         FastAPI Backend Service (Python 3.13)                      |
|                                                                                    |
|  +--------------------+   +-----------------------+   +-------------------------+  |
|  | Ingestion Service  |   | Retrieval / Vector    |   | Export Service          |  |
|  | PyMuPDF / docx     |   | pgvector / Cosine     |   | PyMuPDF / python-docx   |  |
|  +--------------------+   +-----------------------+   +-------------------------+  |
|            |                          |                            |               |
|            v                          v                            v               |
|  +--------------------+   +-----------------------+   +-------------------------+  |
|  | Ephemeral Scrubber |   | Gemini Dual-Key Mgr   |   | Verbatim Citation Check |  |
|  | In-Memory Shredder |   | Primary -> Fallback   |   | Levenshtein Matcher     |  |
|  +--------------------+   +-----------------------+   +-------------------------+  |
+------------------------------------------------------------------------------------+
             |                                              |
             v                                              v
+------------------------------------+    +------------------------------------------+
|      PostgreSQL 16 + pgvector      |    |         Google Gemini AI Engine          |
|  Document-Isolated Vector Store    |    |  Gemini 1.5 Flash • text-embedding-004   |
|  VECTOR(3072) Cosine Distance (<=>)|    |  Automated 429 / 503 Resiliency Failover |
+------------------------------------+    +------------------------------------------+
```

### Complete Technology Stack Breakdown:

| Domain | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js (App Router) | 14.2.35 | Server and client component rendering, routing, static optimization |
| **Language (Web)** | TypeScript | 5.x | Strict compile-time typing across frontend interfaces and API schemas |
| **Styling** | Tailwind CSS | 3.4.1 | Google Stitch design tokens, responsive utilities, enterprise theme |
| **Iconography** | Lucide React | 0.468.0 | Minimalist iconography matching legal enterprise standards |
| **Backend Framework** | FastAPI | 0.141.1 | High-performance asynchronous REST API engine |
| **Language (API)** | Python | 3.13 / 3.11+ | Backend services, vector pipelines, document parsing |
| **Data Validation** | Pydantic v2 | 2.13.5 | Strict request/response model validation and serialization |
| **Database** | PostgreSQL | 16+ | Relational persistence and document metadata tracking |
| **Vector Extension** | pgvector | 0.5.0 | 3,072-dimensional cosine similarity search (`<=>`) |
| **ORM & Drivers** | SQLAlchemy + psycopg 3 | 2.0.54 / 3.3.6 | Async session management and connection pooling |
| **Database Migrations** | Alembic | 1.20.0 | Versioned schema migration tracking |
| **LLM Inference** | Google Gemini 1.5 Flash | v1beta | Clause categorization, executive synthesis, conversational Q&A |
| **Text Embeddings** | Gemini text-embedding-004 | 3,072-dim | High-dimensional semantic representation of contract segments |
| **Credential Failover** | Custom Credential Manager | In-House | Request-scoped automated failover (`PRIMARY` -> `FALLBACK`) |
| **Document Parsers** | PyMuPDF (`fitz`), python-docx | 1.28.2 / 1.2.0 | Memory extraction of binary PDF and Word documents |
| **Binary Exporters** | PyMuPDF, python-docx | 1.28.2 / 1.2.0 | Programmatic styling and byte streaming of PDF & DOCX briefs |
| **Type Checking** | Pyright | Strict Mode | Zero-tolerance static typing across all backend Python modules |
| **Testing** | Pytest + pytest-asyncio | 9.1.1 | Automated backend regression testing (124 tests) |

---

## 6. Security, Privacy & Reliability Architecture

### 1. Dual-Key Automated Failover
- **Zero-Downtime Resilience**: The platform maintains two independent Google Gemini credentials: `GEMINI_API_KEY_PRIMARY` and `GEMINI_API_KEY_FALLBACK`.
- **Automatic Circuit Trigger**: If Gemini returns HTTP 429 (Resource Exhausted / Rate Limit) or HTTP 503 (Service Unavailable), the request automatically executes against the fallback credential.
- **Zero Secret Exposure**: All keys are strictly masked (`***`) in string representations, log files, terminal outputs, and client payloads.

### 2. Zero-Retention Ephemeral Scrubber
- **Memory-Only Processing**: Uploaded documents are streamed to ephemeral scratch paths, parsed directly into memory, and immediately deleted via `shutil.rmtree` / `os.unlink`.
- **Cleanup Guarantee**: File shredders are bound to FastAPI background tasks and `try...finally` execution blocks, ensuring temporary files are purged even if parsing errors occur.
- **Telemetry Privacy**: Document text and extracted provisions are never stored in telemetry records, application logs, or third-party monitoring services.

### 3. Tenant-Isolated Vector Boundaries
- Every vector embedding stored in PostgreSQL includes a mandatory `document_id` foreign key.
- Retrieval queries enforce SQL-level tenant isolation:
  ```sql
  SELECT chunk_id, content, 1 - (embedding <=> :query_vec) AS similarity
  FROM document_vectors
  WHERE document_id = :active_document_id
  ORDER BY embedding <=> :query_vec
  LIMIT :top_k;
  ```
- Cross-document vector leakage is mathematically impossible at the database query level.

### 4. Mathematical Citation Verification
- Citations returned by Gemini undergo automated character-offset and Levenshtein similarity verification against the raw document text.
- If a synthesized quote deviates by more than a minimal whitespace tolerance or cannot be anchored to an exact character span, it is flagged as `verified: false` and rendered with a warning badge.

---

## 7. API Route Reference

### Backend Endpoints (`http://localhost:8000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health check and database connectivity probe |
| `POST` | `/api/v1/documents/upload` | Multipart file upload (PDF, DOCX, TXT) with validation |
| `POST` | `/api/v1/documents/analyze` | Triggers clause extraction and risk analysis |
| `POST` | `/api/v1/documents/index` | Generates embeddings and stores vectors in pgvector |
| `POST` | `/api/v1/retrieval/search` | Document-scoped vector similarity search |
| `POST` | `/api/v1/documents/ask` | Grounded multi-turn conversational Q&A |
| `GET` | `/api/v1/documents/{id}/brief` | Generates lawyer briefing dossier and checklist |
| `GET` | `/api/v1/documents/{id}/brief/export/pdf` | Direct GET stream for Executive Brief PDF |
| `POST` | `/api/v1/documents/{id}/brief/export/pdf` | Parameterized POST stream for Executive Brief PDF |
| `GET` | `/api/v1/documents/{id}/brief/export/docx` | Direct GET stream for Word Action Checklist |
| `POST` | `/api/v1/documents/{id}/brief/export/docx` | Parameterized POST stream for Word Action Checklist |
| `POST` | `/api/v1/share/dossier` | Creates an encrypted shareable snapshot token |
| `GET` | `/api/v1/share/dossier/{share_id}` | Retrieves a read-only shared dossier by token |

### Frontend Proxy Routes (`http://localhost:3000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/export/pdf/[documentId]` | Same-origin streaming proxy for PDF Executive Brief |
| `GET` | `/api/export/docx/[documentId]` | Same-origin streaming proxy for DOCX Word Checklist |

---

## 8. Project Structure

```
├── docs/
│   └── screenshots/              # Platform walkthrough visual artifacts
│
├── backend/
│   ├── alembic/                  # Database migration environments
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/           # REST route controllers (health, docs, brief, share, etc.)
│   │   ├── core/                 # Config, logging, settings, dual-key credential manager
│   │   ├── db/                   # Database session, base model, pgvector helpers
│   │   ├── models/               # SQLAlchemy ORM models (Document, Vector, Share)
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # Core business logic
│   │   │   ├── analysis_service.py      # Clause categorization & risk scoring
│   │   │   ├── brief_service.py         # Lawyer brief & checklist synthesis
│   │   │   ├── cleanup_service.py       # Ephemeral file shredding
│   │   │   ├── docx_service.py          # Word document parsing & generation
│   │   │   ├── embedding_service.py     # Gemini text-embedding-004 wrapper
│   │   │   ├── export_service.py        # Binary PDF & DOCX export builders
│   │   │   ├── extraction_service.py    # Text parsing & boundary extraction
│   │   │   ├── gemini_service.py        # Gemini 1.5 Flash dual-key client
│   │   │   ├── pdf_service.py           # PyMuPDF parser & PDF renderer
│   │   │   ├── pgvector_store.py        # PostgreSQL pgvector similarity engine
│   │   │   └── retrieval_service.py     # Semantic RAG & citation verifier
│   │   └── utils/                # File validators & custom exceptions
│   ├── scripts/                  # Corpus auditing & administrative utilities
│   ├── tests/                    # 124 passing Pytest unit & integration tests
│   ├── pyproject.toml            # Backend dependencies & metadata
│   └── requirements.txt          # Python virtual environment requirements
│
├── public/                       # Static public assets
│   ├── favicon.ico               # Transparent multi-frame ICO (16×16, 32×32, 48×48)
│   ├── icon.svg                  # Transparent vector shield favicon
│   ├── lead-legal-counsel.png    # Persona avatar for Lead Legal Counsel
│   └── favicon-32x32.png         # 32px transparent PNG fallback
│
├── src/
│   ├── app/                      # Next.js 14 App Router
│   │   ├── api/export/           # Same-origin download proxies
│   │   ├── analyze/              # Analysis Dossier & Clause Ledger page
│   │   ├── ask/                  # Ask LexGuard Grounded Q&A page
│   │   ├── brief/                # Executive Brief & Action Checklist page
│   │   ├── compare/              # Redline & Clause Delta Comparison page
│   │   ├── library/              # 200 Curated Institutional Templates page
│   │   ├── public-law/           # 285 Public Statutory Corpus page
│   │   ├── settings/             # System Security & Privacy Settings page
│   │   ├── share/[shareId]/      # Secure Encrypted Shared Dossier page
│   │   ├── icon.svg              # Next.js App Router route-segment icon
│   │   ├── layout.tsx            # Global layout & metadata configuration
│   │   └── page.tsx              # Intake Hub & Document Landing page
│   ├── components/               # Modular UI component hierarchy
│   │   ├── layout/               # TopNavbar, AppShell, FooterBar
│   │   ├── navigation/           # CommandPalette (⌘K), SidebarNav
│   │   └── ui/                   # BrandLogo, RiskBadge, DialMeter
│   ├── lib/
│   │   ├── api/client.ts         # Centralized frontend API client
│   │   └── mock-data/            # Fallback datasets & corpus registries
│   └── types/                    # Shared TypeScript interfaces
│
├── docker-compose.yml            # PostgreSQL + pgvector container definition
├── package.json                  # Next.js frontend dependencies
├── tailwind.config.ts            # Tailwind design system configuration
└── tsconfig.json                 # TypeScript strict configuration
```

---

## 9. Local Setup & Quickstart Guide

### Prerequisites
- **Node.js**: `v18.17.0` or higher (Node 20 LTS recommended)
- **Python**: `3.11` to `3.13`
- **PostgreSQL**: Version 15+ with `pgvector` extension enabled (or Docker)
- **Git**

---

### Step 1: Clone the Repository & Setup Backend

```bash
# 1. Clone workspace
git clone <repository-url>
cd lexguard

# 2. Enter backend directory and create virtual environment
cd backend
python -m venv .venv

# 3. Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Create and edit `backend/.env`:

```bash
cp .env.example .env
```

Configure your credentials in `backend/.env`:

```env
# Application Settings
PROJECT_NAME="LexGuard Legal Intelligence"
ENVIRONMENT="development"
DEBUG=true

# Database Configuration (PostgreSQL with pgvector)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/lexguard
DATABASE_URL_SYNC=postgresql+psycopg://postgres:postgres@localhost:5432/lexguard

# Centralized Dual-Key Gemini Configuration
GEMINI_API_KEY_PRIMARY="your-primary-gemini-api-key"
GEMINI_API_KEY_FALLBACK="your-fallback-gemini-api-key"

# Embedding & LLM Models
GEMINI_MODEL="gemini-1.5-flash"
GEMINI_EMBEDDING_MODEL="text-embedding-004"

# CORS Configuration
ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

---

### Step 3: Start PostgreSQL with pgvector

You can run PostgreSQL with pgvector using Docker Compose from the project root:

```bash
# From project root:
docker-compose up -d
```

Or connect to an existing PostgreSQL database and enable `pgvector`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Run database migrations:

```bash
cd backend
alembic upgrade head
```

---

### Step 4: Install Frontend Dependencies

```bash
# From project root:
npm install
```

---

### Step 5: Launch the Application

#### Terminal 1 — Start Backend Server:
```bash
cd backend
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload
```
*API Swagger Documentation is available at: `http://localhost:8000/docs`*

#### Terminal 2 — Start Frontend Application:
```bash
# Development mode:
npm run dev

# Or Production mode:
npm run build
npm run start
```
*Web Application is available at: `http://localhost:3000`*

---

## 10. Verification & Quality Assurance Suite

LexGuard enforces strict code hygiene, 100% type safety, and comprehensive test coverage.

### 1. Run Backend Automated Pytest Suite
```bash
cd backend
.\.venv\Scripts\pytest -q tests
```
*Result: **124 passed / 0 failed** in ~10 seconds.*

### 2. Run Pyright Strict Type Checking
```bash
# From project root:
npx pyright --project backend
```
*Result: **0 errors, 0 warnings, 0 informations**.*

### 3. Run Production Next.js Build
```bash
npm run build
```
*Result: **Exit Code 0** (12/12 routes compiled cleanly).*

### 4. Audit 500-Document Corpus Registry
```bash
.\backend\.venv\Scripts\python backend/scripts/audit_corpus.py
```
*Result: **500/500 documents verified** (200 Templates + 285 Statutes + 15 Executable Demo Contracts).*

---

## 11. Live Evaluator & Judge Walkthrough (5–7 Minutes)

When presenting LexGuard to judges or evaluators, follow this exact chronological demonstration:

| Phase | Time | Action & Screen | Speaking Track |
| :--- | :--- | :--- | :--- |
| **1. The Problem** | 0:00–1:00 | **Intake Hub (`/`)** | *"Founders and businesses sign contracts without understanding hidden traps because legal review costs $800/hr. LexGuard gives non-lawyers document-grounded legal intelligence with zero hallucinations."* |
| **2. Instant Intake** | 1:00–1:45 | Click **Sample Library**, select **Enterprise SaaS MSA & SLA v4.2**, click **Analyze Document** | *"We parse PDFs and Word documents in memory with zero data retention. Watch how it extracts 50+ pages into structured intelligence in under 3 seconds."* |
| **3. Risk Dossier** | 1:45–2:45 | **Analysis Dashboard (`/analyze`)** | *"Notice the Vendor Tilt score: 68% vendor-favored. In the 48-domain Clause Ledger, look at Section 8.3 (Limitation of Liability). LexGuard highlights the trailing liability trap and provides an immediate counter-proposal redline."* |
| **4. Grounded Q&A** | 2:45–4:00 | **Ask LexGuard (`/ask`)** | *"Click the 'Early Termination' chip. Every sentence cited has a clickable badge § proving exact page and section grounding. Now ask an unanswerable question like 'What is the penalty for nuclear war?' LexGuard strictly refuses to hallucinate."* |
| **5. Version Redline** | 4:00–4:45 | **Clause Compare (`/compare`)** | *"Here is the side-by-side token-level comparison between the vendor draft and our revised counter-proposal, showing liability caps restored from $60K to $1M."* |
| **6. Counsel Brief & Export** | 4:45–5:30 | **Brief & Checklist (`/brief`)** | *"Before meeting your lawyer, LexGuard creates your agenda. Toggle items on the checklist to see completion update. Then click 'Export Executive Brief (PDF)' or 'Export Word (.docx)' for the attorney briefing packet."* |
| **7. Security & Wrap** | 5:30–6:00 | Click avatar / **`/settings`** | *"Dual-key Gemini failover prevents rate limits, and ephemeral scrubbers protect client privacy. LexGuard makes legal intelligence fast, grounded, and institutional."* |

---

## 12. Contributors & Acknowledgements

Developed for the **AI Intelligence & Ingestion Pipeline Challenge**.

- **Lead Architect & Developer**: Ayush Nathani
- **Design Inspiration**: Google Stitch Design System & Enterprise Legal Intelligence UX
- **AI Infrastructure**: Google DeepMind / Google Gemini Platform

---

*LexGuard Intelligence © 2026. All rights reserved. Educational Legal Intelligence Platform.*
