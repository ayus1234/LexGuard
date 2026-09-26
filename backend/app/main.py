import sys
import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if sys.platform == "win32":
    # On Windows, psycopg 3 async driver requires SelectorEventLoop
    set_policy = getattr(asyncio, "set_event_loop_policy", None)
    selector_policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if callable(set_policy) and selector_policy is not None:
        set_policy(selector_policy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from app.core.config import settings
    from app.core.logging import logger
    from app.utils.file_validation import LexGuardException
    from app.api.routes import health, documents, analysis, retrieval, brief, share, corpus
    from app.db.session import close_database, check_database_health
else:
    try:
        from backend.app.core.config import settings
        from backend.app.core.logging import logger
        from backend.app.utils.file_validation import LexGuardException
        from backend.app.api.routes import health, documents, analysis, retrieval, brief, share, corpus
        from backend.app.db.session import close_database, check_database_health
    except ImportError:
        from app.core.config import settings
        from app.core.logging import logger
        from app.utils.file_validation import LexGuardException
        from app.api.routes import health, documents, analysis, retrieval, brief, share, corpus
        from app.db.session import close_database, check_database_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure demo document is indexed
    logger.info("Application startup: checking demo document indexing...")
    try:
        await _ensure_demo_document_indexed()
        logger.info("Demo document check complete")
    except Exception as e:
        logger.warning(f"Demo document indexing check failed (non-fatal): {str(e)}")
    
    yield
    
    # Shutdown
    await close_database()


async def _ensure_demo_document_indexed():
    """
    Idempotent check to ensure the primary demo document (doc-saas-v42) is indexed.
    Only indexes if not already present in the vector store.
    Creates the document structure directly since it's the primary demo document.
    """
    from app.services.retrieval_service import retrieval_service
    from app.schemas.document import DocumentResponse, PageExtraction, SectionOutline, DocumentMetadata
    from datetime import datetime, timezone
    
    demo_doc_id = "doc-saas-v42"
    
    # Check if already indexed
    if retrieval_service.is_document_indexed(demo_doc_id):
        logger.info(f"Demo document {demo_doc_id} already indexed in vector store")
        return
    
    logger.info(f"Demo document {demo_doc_id} not found in vector store, indexing now...")
    
    # Create the demo document structure directly
    # This is the primary demo document text from the seed script
    DOCUMENT_TEXT = """ARTICLE 1 — DEFINITIONS AND INTERPRETATION
1.1 Defined Terms. As used herein: "Customer Data" means all electronic data or information submitted by Customer to the SaaS Services. "SaaS Services" means the multi-tenant software-as-a-service platform identified in the Order Form.

ARTICLE 2 — PROVISION OF SERVICES
2.1 Access Rights. Vendor hereby grants Customer a non-exclusive, non-transferable right to access and use the SaaS Services during the Subscription Term solely for Customer's internal business operations.

ARTICLE 3 — TERM AND AUTO-RENEWAL
3.1 Initial Term. This agreement shall commence on the Effective Date and continue for an initial term of three (3) years.
3.2 Renewal Mechanics. Thereafter, this agreement shall automatically renew for successive twelve (12) month periods unless either party provides written notice of non-renewal at least sixty (60) calendar days prior to the expiration of the current initial term. Notice of non-renewal must be delivered in accordance with Section 18.4.

ARTICLE 4 — FEES AND PAYMENT TERMS
4.1 Invoicing and Payment. Customer shall pay all fees specified in applicable Order Forms within thirty (30) days from the invoice date.
4.2 Currency. Fees are quoted and payable in United States dollars.
4.3 Payment Obligations. Customer payment obligations are non-cancelable and fees paid are non-refundable except as expressly provided in Section 9.3. Quantities purchased cannot be decreased during the relevant Subscription Term. Any uncredited upfront annual fees ($240,000 commitment) remain non-refundable.

ARTICLE 8 — LIMITATIONS OF REMEDIES AND DAMAGES
8.1 Consequential Damages Waiver. NEITHER PARTY SHALL BE LIABLE TO THE OTHER FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF OR IN CONNECTION WITH THIS AGREEMENT.
8.2 Direct Damages. Subject to Section 8.3, each party shall remain responsible for direct damages demonstrated with reasonable certainty.
8.3 Aggregate Liability Ceiling. IN NO EVENT SHALL EITHER PARTY'S AGGREGATE LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT, WHETHER IN CONTRACT, TORT, OR UNDER ANY OTHER THEORY OF LIABILITY, EXCEED THE TOTAL AMOUNT OF FEES ACTUALLY PAID BY CUSTOMER HEREUNDER IN THE THREE (3) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO LIABILITY.
8.4 Exceptions to Ceiling. The limitations set forth in Section 8.3 shall not apply to: (i) Customer's payment obligations under Article 4; (ii) indemnification obligations under Article 11; or (iii) damages arising from gross negligence or willful misconduct.

ARTICLE 9 — TERMINATION
9.1 Termination for Cause. Either party may terminate this agreement immediately upon written notice if the other party materially breaches any provision of this agreement and fails to cure such material breach within thirty (30) days after receipt of written notice.
9.2 Termination for Convenience. Either party may terminate this agreement or any Order Form for convenience without cause upon ninety (90) days prior written notice to the other party. In the event of customer termination for convenience, customer shall not be entitled to any refund of prepaid fees.
9.3 Effect of Termination for Breach. If this agreement is terminated by Customer for Vendor's uncured material breach pursuant to Section 9.1, Vendor shall refund to Customer any prepaid, unused fees covering the remainder of the Subscription Term.

ARTICLE 11 — INDEMNIFICATION
11.1 Vendor Indemnification. Vendor shall defend, indemnify, and hold harmless Customer, its affiliates, and their respective officers, directors, and employees against any third-party claims alleging that the SaaS services infringe or misappropriate any patent, copyright, or trademark.
11.2 Customer Indemnification. Customer shall defend, indemnify, and hold harmless Vendor against any third-party claims alleging that Customer Data or customer use of the services violates applicable law or infringes third-party intellectual property rights.

ARTICLE 12 — DATA PRIVACY AND SECURITY
12.1 Customer Data Ownership and AI Prohibitions. As between the parties, Customer retains all right, title, and interest in and to all Customer Data. Vendor shall not access, use, disclose, or process Customer Data except to provide the SaaS Services. Vendor explicitly covenants that Customer Data and Customer telemetry shall not be used, directly or indirectly, to train, tune, or improve artificial intelligence, machine learning, or large language models.
12.2 Security Safeguards. Vendor shall maintain administrative, physical, and technical safeguards designed to protect the security, confidentiality, and integrity of Customer Data (SOC 2 Type II compliant).

ARTICLE 16 — SERVICE LEVEL AGREEMENT & SLA REMEDIES
16.1 Service Availability. Vendor warrants that the SaaS Services will maintain an Uptime Percentage of at least 99.9% during each calendar month.
16.2 Service Credits and Chronic Breach. In the event uptime falls below 99.0%, Customer shall be entitled to a service credit equal to 25% of the monthly fee. In the event uptime falls below 95.0% in two consecutive calendar months, Customer may terminate this agreement for cause under Section 9.1.

ARTICLE 18 — GENERAL PROVISIONS
18.1 Governing Law. This agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of law principles.
18.2 Venue and Dispute Resolution. The state and federal courts located in Wilmington, Delaware shall have exclusive jurisdiction over any dispute arising under this agreement.
18.4 Notice Formalities. Any notice required or permitted hereunder must be in writing and delivered by certified registered mail, return receipt requested, to the registered agent of the vendor at its Delaware headquarters. Email transmission does not constitute formal legal notice under this section.
"""
    
    # Create page extractions
    def find_span(target: str) -> tuple:
        idx = DOCUMENT_TEXT.find(target)
        if idx == -1:
            return (0, 0)
        return (idx, idx + len(target))
    
    art1_span = find_span("ARTICLE 1 — DEFINITIONS")
    art3_span = find_span("ARTICLE 3 — TERM")
    art4_span = find_span("ARTICLE 4 — FEES")
    art8_span = find_span("ARTICLE 8 — LIMITATIONS")
    art9_span = find_span("ARTICLE 9 — TERMINATION")
    art11_span = find_span("ARTICLE 11 — INDEMNIFICATION")
    art12_span = find_span("ARTICLE 12 — DATA PRIVACY")
    art16_span = find_span("ARTICLE 16 — SERVICE LEVEL")
    art18_span = find_span("ARTICLE 18 — GENERAL")
    
    pages = [
        PageExtraction(
            page_number=1,
            text=DOCUMENT_TEXT[art1_span[0]:art3_span[0]].strip(),
            character_start=art1_span[0],
            character_end=art3_span[0],
            word_count=len(DOCUMENT_TEXT[art1_span[0]:art3_span[0]].split())
        ),
        PageExtraction(
            page_number=4,
            text=DOCUMENT_TEXT[art3_span[0]:art4_span[0]].strip(),
            character_start=art3_span[0],
            character_end=art4_span[0],
            word_count=len(DOCUMENT_TEXT[art3_span[0]:art4_span[0]].split())
        ),
        PageExtraction(
            page_number=6,
            text=DOCUMENT_TEXT[art4_span[0]:art8_span[0]].strip(),
            character_start=art4_span[0],
            character_end=art8_span[0],
            word_count=len(DOCUMENT_TEXT[art4_span[0]:art8_span[0]].split())
        ),
        PageExtraction(
            page_number=10,
            text=DOCUMENT_TEXT[art8_span[0]:art9_span[0]].strip(),
            character_start=art8_span[0],
            character_end=art9_span[0],
            word_count=len(DOCUMENT_TEXT[art8_span[0]:art9_span[0]].split())
        ),
        PageExtraction(
            page_number=11,
            text=DOCUMENT_TEXT[art9_span[0]:art11_span[0]].strip(),
            character_start=art9_span[0],
            character_end=art11_span[0],
            word_count=len(DOCUMENT_TEXT[art9_span[0]:art11_span[0]].split())
        ),
        PageExtraction(
            page_number=14,
            text=DOCUMENT_TEXT[art11_span[0]:art12_span[0]].strip(),
            character_start=art11_span[0],
            character_end=art12_span[0],
            word_count=len(DOCUMENT_TEXT[art11_span[0]:art12_span[0]].split())
        ),
        PageExtraction(
            page_number=15,
            text=DOCUMENT_TEXT[art12_span[0]:art16_span[0]].strip(),
            character_start=art12_span[0],
            character_end=art16_span[0],
            word_count=len(DOCUMENT_TEXT[art12_span[0]:art16_span[0]].split())
        ),
        PageExtraction(
            page_number=16,
            text=DOCUMENT_TEXT[art16_span[0]:art18_span[0]].strip(),
            character_start=art16_span[0],
            character_end=art18_span[0],
            word_count=len(DOCUMENT_TEXT[art16_span[0]:art18_span[0]].split())
        ),
        PageExtraction(
            page_number=17,
            text=DOCUMENT_TEXT[art18_span[0]:].strip(),
            character_start=art18_span[0],
            character_end=len(DOCUMENT_TEXT),
            word_count=len(DOCUMENT_TEXT[art18_span[0]:].split())
        ),
    ]
    
    sections = [
        SectionOutline(title="§ 3.2 Term and Auto-Renewal", page_number=4, character_offset=art3_span[0]),
        SectionOutline(title="§ 4.3 Payment Obligations", page_number=6, character_offset=art4_span[0]),
        SectionOutline(title="§ 8.3 Limitation of Liability", page_number=10, character_offset=art8_span[0]),
        SectionOutline(title="§ 9.2 Termination for Convenience", page_number=11, character_offset=art9_span[0]),
        SectionOutline(title="§ 11.2 Indemnification Obligations", page_number=14, character_offset=art11_span[0]),
        SectionOutline(title="§ 12.1 Customer Data Ownership & AI", page_number=15, character_offset=art12_span[0]),
        SectionOutline(title="§ 16.2 Uptime Commitment and SLA Remedies", page_number=16, character_offset=art16_span[0]),
        SectionOutline(title="§ 18.4 Governing Law and Notice Formalities", page_number=17, character_offset=art18_span[0]),
    ]
    
    demo_doc = DocumentResponse(
        document_id=demo_doc_id,
        filename="Enterprise_SaaS_Master_Services_Agreement_v4.2.pdf",
        file_type="pdf",
        source_type="sample",
        page_count=18,
        word_count=len(DOCUMENT_TEXT.split()),
        character_count=len(DOCUMENT_TEXT),
        extracted_text=DOCUMENT_TEXT,
        pages=pages,
        sections=sections,
        metadata=DocumentMetadata(
            original_filename="Enterprise_SaaS_Master_Services_Agreement_v4.2.pdf",
            file_size_bytes=len(DOCUMENT_TEXT.encode("utf-8")),
            mime_type="application/pdf",
            sha256_hash="0x82f4d901a4e8c1b2f7e6d5c4b3a29180",
            extraction_engine="LexGuard PDF Optical Parser v4.2",
            processed_at=datetime.now(timezone.utc),
        ),
        processing_status="completed",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    
    # Index the document
    try:
        result = await retrieval_service.index_document(demo_doc)
        logger.info(f"Demo document {demo_doc_id} indexed successfully: {result.chunk_count} chunks, {result.processing_time_ms}ms")
    except Exception as e:
        logger.error(f"Failed to index demo document {demo_doc_id}: {str(e)}")
        raise


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="LexGuard Legal Document Intelligence & Ingestion API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS for Next.js frontend communication
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    # Domain Exception Handler
    @application.exception_handler(LexGuardException)
    async def lexguard_exception_handler(request: Request, exc: LexGuardException):
        logger.warning(f"Handled application exception: code={exc.code}, status={exc.status_code}, msg={exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )

    # Fallback Exception Handler
    @application.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception during request {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred while processing the request.",
                }
            },
        )

    # Route registrations
    application.include_router(health.router, prefix="/api")
    application.include_router(documents.router, prefix=settings.API_V1_PREFIX)
    application.include_router(analysis.router, prefix=settings.API_V1_PREFIX)
    application.include_router(retrieval.router, prefix=settings.API_V1_PREFIX)
    application.include_router(brief.router, prefix=settings.API_V1_PREFIX)
    application.include_router(share.router, prefix=settings.API_V1_PREFIX)
    application.include_router(corpus.router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()

if __name__ == "__main__":
    import uvicorn

    loop_arg = "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto"
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, loop=loop_arg)
