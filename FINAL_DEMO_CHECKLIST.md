# LexGuard — Final Hackathon Demo Checklist & Runbook

This document serves as the operational guide for conducting live, flawless 5–10 minute hackathon presentations and judge evaluations of the **LexGuard AI Legal Document Intelligence Platform**.

---

## 1. System Operational Status

| Component | Status | Verification Detail |
| :--- | :--- | :--- |
| **Backend Service** | `ONLINE` | FastAPI running on `http://127.0.0.1:8000` (Health: `status: ok`) |
| **Frontend Application** | `ONLINE` | Next.js 14 App Router on `http://localhost:3000` (0 build errors) |
| **PostgreSQL + pgvector** | `READY` | Document-scoped tenant isolation, VECTOR(3072) embeddings, cosine distance |
| **Gemini AI Engine** | `READY` | Gemini 1.5 Flash active with automated fallback failover |
| **Primary Credential** | `CONFIGURED` | Masked in telemetry; tested with automated failover handling |
| **Fallback Credential** | `CONFIGURED` | Standby credential activated automatically on HTTP 429/503 |
| **RAG / Grounded Q&A** | `VERIFIED` | Document-scoped semantic search with strict refusal on unstated facts |
| **Citation Verification** | `VERIFIED` | Exact character offset matching; rejects fabricated quotes |
| **PDF & DOCX Export** | `VERIFIED` | PyMuPDF & python-docx binary generation with persistent educational disclaimers |
| **500-Document Corpus** | `VERIFIED` | 200 Templates + 285 Public Statutes + 15 Fictional Demo Docs (100% Integrity) |

---

## 2. Pre-Demo Checklist (5 Minutes Before Judging)

Complete these checks prior to sharing your screen or inviting evaluators:

- [ ] **Docker / PostgreSQL**: Ensure database container is running:
  ```powershell
  docker ps
  ```
- [ ] **Backend Service Running**:
  ```powershell
  cd backend
  .\.venv\Scripts\python -m uvicorn app.main:app --port 8000
  ```
  Verify via `http://localhost:8000/api/health` returns `{"status":"ok"}`.
- [ ] **Frontend Production/Dev Server Running**:
  ```powershell
  npm run dev   # or npm run start
  ```
- [ ] **Browser Clean State**:
  - Open Chrome/Edge in full screen at 1440×900 or 1920×1080 resolution.
  - Navigate to `http://localhost:3000`.
  - Open DevTools Console (F12) once to verify **0 console errors**, then close DevTools for clean presentation.
- [ ] **Verify Audio & Screen Share**:
  - Maximize browser window.
  - Confirm compliance banner and fixed left navigation rail are properly visible.

---

## 3. Recommended 5–7 Minute Judge Demonstration Flow

Follow this exact chronological script:

### Step 1: The Problem & Intake Workspace (`/` — 1 Minute)
- **What to say**: *"Founders and businesses sign contracts without understanding hidden traps because legal review costs $800/hr. LexGuard is an institutional legal intelligence engine that synthesizes obligations and flags risks with mathematical citation grounding."*
- **Action**:
  - Show the clean Google Stitch UI with the compliance banner.
  - Point out the **500 Corpus References Indexed** telemetry chip.
  - Click the **Sample Library** tab and select **Enterprise SaaS Master Services Agreement & SLA v4.2** to simulate zero-friction legal intake.

### Step 2: Comprehensive Analysis Dashboard (`/analyze` — 1.5 Minutes)
- **What to say**: *"Within milliseconds, LexGuard extracts all operational parameters and determines directional alignment. Here, the contract exhibits a 68% Vendor-favored tilt."*
- **Action**:
  - Highlight the **Executive Intelligence Summary** and the **Vendor Tilt Gauge**.
  - Show the **Extracted Operational Parameters** (Parties, 3-Year Term, Non-refundable $240k fee).
  - Scroll to **Clause Intelligence Table**. Click the **High Attention (2)** filter.
  - Click **Review Details** on **Section 8.3 (Limitation of Liability)**. Show verbatim raw contract text, character offset matching, and the instant counter-proposal recommendation. Close modal.

### Step 3: Ask LexGuard Grounded Q&A (`/ask` — 1.5 Minutes)
- **What to say**: *"General AI models hallucinate in legal contexts. LexGuard uses deterministic vector grounding with anti-hallucination guardrails."*
- **Action**:
  - Click the suggested chip: **Early Termination**.
  - Review the synthesized answer: point out the verified badge referencing **Section 3.2** and **Section 9.2**.
  - Now demonstrate safety: Type an unanswerable question: *"What is the penalty for nuclear war?"*
  - Show LexGuard's strict refusal: *"Insufficient evidence in document to answer this query without speculation."*

### Step 4: Redlining & Comparison (`/compare` — 1 Minute)
- **What to say**: *"When the counterparty returns revisions, LexGuard performs token-level delta analysis."*
- **Action**:
  - Point out the 5 delta metric cards (34 total modifications, 4 high-risk deviations).
  - Show the side-by-side redline diff: trailing liability cap slashed from 12 months down to 3 months (flagged in red/green).
  - Click **Draft Counter-Proposal** to demonstrate immediate negotiation defense.

### Step 5: Counsel Brief & Binary Export (`/brief` — 1 Minute)
- **What to say**: *"LexGuard does not replace your attorney—it empowers you to work with them efficiently."*
- **Action**:
  - Show the **Action Checklist**. Check off 1 item; watch the progress ring advance from 33% to 50%.
  - Switch to **Tab 2: Lawyer Preparation Brief** to show the 3 structured agenda items for counsel.
  - Click **Export Executive Brief (PDF)** or **Export DOCX** to trigger instant binary report generation.

### Step 6: Vault & Privacy Wrap-Up (`/library` & `/settings` — 30 Seconds)
- **Action**:
  - Briefly click `/library` (show 200 Curated Institutional Templates) and `/public-law` (show 285 Codified Statutes).
  - Click `/settings`: show **Zero-Data-Retention** ephemeral RAM scrubbing and the immutable SHA-256 session audit trail.

---

## 4. Emergency Backup & Resilience Plan

| Scenario | Immediate Action |
| :--- | :--- |
| **Gemini Primary Key Rate Limited (HTTP 429)** | System automatically engages `GEMINI_API_KEY_FALLBACK` with zero interruption to the user. No manual intervention required. |
| **Gemini Service Unavailable (HTTP 503)** | System catches transient failure, engages secondary credential, and returns clean structured guidance. |
| **PostgreSQL Disconnects** | The application returns clear structured status codes; restart PostgreSQL container via `docker start lexguard-db`. |
| **Browser Accidental Refresh (F5)** | All screens load instant default states (`doc-saas-v42`) without blanking or crashing. |
| **Network Slowness / API Latency** | Use the preloaded quick-pick demo documents (`Enterprise SaaS MSA v4.2`), which are cached in memory for instant responses. |
