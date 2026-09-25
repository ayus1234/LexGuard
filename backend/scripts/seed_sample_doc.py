"""
Seed script to populate the sample document 'doc-saas-v42'
(Enterprise SaaS Master Services Agreement & SLA v4.2) into PostgreSQL + pgvector.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.schemas.document import DocumentResponse, PageExtraction, SectionOutline, DocumentMetadata
from app.services.retrieval_service import RetrievalService

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

async def seed():
    print("Seeding sample document 'doc-saas-v42' into PostgreSQL + pgvector...")
    
    # Locate exact character offsets in DOCUMENT_TEXT for precise page/section correlation
    def find_span(target: str) -> tuple[int, int]:
        idx = DOCUMENT_TEXT.find(target)
        if idx == -1:
            return (0, 0)
        return (idx, idx + len(target))

    art1_span = find_span("ARTICLE 1 — DEFINITIONS AND INTERPRETATION")
    art3_span = find_span("ARTICLE 3 — TERM AND AUTO-RENEWAL")
    art4_span = find_span("ARTICLE 4 — FEES AND PAYMENT TERMS")
    art8_span = find_span("ARTICLE 8 — LIMITATIONS OF REMEDIES AND DAMAGES")
    art9_span = find_span("ARTICLE 9 — TERMINATION")
    art11_span = find_span("ARTICLE 11 — INDEMNIFICATION")
    art12_span = find_span("ARTICLE 12 — DATA PRIVACY AND SECURITY")
    art16_span = find_span("ARTICLE 16 — SERVICE LEVEL AGREEMENT & SLA REMEDIES")
    art18_span = find_span("ARTICLE 18 — GENERAL PROVISIONS")

    pages = [
        PageExtraction(
            page_number=1,
            text=DOCUMENT_TEXT[art1_span[0]:art3_span[0]].strip(),
            character_start=art1_span[0],
            character_end=art3_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art1_span[0]:art3_span[0]].split())
        ),
        PageExtraction(
            page_number=4,
            text=DOCUMENT_TEXT[art3_span[0]:art4_span[0]].strip(),
            character_start=art3_span[0],
            character_end=art4_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art3_span[0]:art4_span[0]].split())
        ),
        PageExtraction(
            page_number=6,
            text=DOCUMENT_TEXT[art4_span[0]:art8_span[0]].strip(),
            character_start=art4_span[0],
            character_end=art8_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art4_span[0]:art8_span[0]].split())
        ),
        PageExtraction(
            page_number=10,
            text=DOCUMENT_TEXT[art8_span[0]:art9_span[0]].strip(),
            character_start=art8_span[0],
            character_end=art9_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art8_span[0]:art9_span[0]].split())
        ),
        PageExtraction(
            page_number=11,
            text=DOCUMENT_TEXT[art9_span[0]:art11_span[0]].strip(),
            character_start=art9_span[0],
            character_end=art11_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art9_span[0]:art11_span[0]].split())
        ),
        PageExtraction(
            page_number=14,
            text=DOCUMENT_TEXT[art11_span[0]:art12_span[0]].strip(),
            character_start=art11_span[0],
            character_end=art12_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art11_span[0]:art12_span[0]].split())
        ),
        PageExtraction(
            page_number=15,
            text=DOCUMENT_TEXT[art12_span[0]:art16_span[0]].strip(),
            character_start=art12_span[0],
            character_end=art16_span[0] - 1,
            word_count=len(DOCUMENT_TEXT[art12_span[0]:art16_span[0]].split())
        ),
        PageExtraction(
            page_number=16,
            text=DOCUMENT_TEXT[art16_span[0]:art18_span[0]].strip(),
            character_start=art16_span[0],
            character_end=art18_span[0] - 1,
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

    sec32 = find_span("3.2 Renewal Mechanics")
    sec43 = find_span("4.3 Payment Obligations")
    sec83 = find_span("8.3 Aggregate Liability Ceiling")
    sec92 = find_span("9.2 Termination for Convenience")
    sec112 = find_span("11.2 Customer Indemnification")
    sec121 = find_span("12.1 Customer Data Ownership and AI Prohibitions")
    sec162 = find_span("16.2 Service Credits and Chronic Breach")
    sec184 = find_span("18.4 Notice Formalities")

    sections = [
        SectionOutline(title="§ 3.2 Term and Auto-Renewal", page_number=4, character_offset=sec32[0]),
        SectionOutline(title="§ 4.3 Payment Obligations", page_number=6, character_offset=sec43[0]),
        SectionOutline(title="§ 8.3 Limitation of Liability", page_number=10, character_offset=sec83[0]),
        SectionOutline(title="§ 9.2 Termination for Convenience", page_number=11, character_offset=sec92[0]),
        SectionOutline(title="§ 11.2 Indemnification Obligations", page_number=14, character_offset=sec112[0]),
        SectionOutline(title="§ 12.1 Customer Data Ownership & AI", page_number=15, character_offset=sec121[0]),
        SectionOutline(title="§ 16.2 Uptime Commitment and SLA Remedies", page_number=16, character_offset=sec162[0]),
        SectionOutline(title="§ 18.4 Governing Law and Notice Formalities", page_number=17, character_offset=sec184[0]),
    ]

    doc = DocumentResponse(
        document_id="doc-saas-v42",
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
    )

    retrieval_service = RetrievalService()
    res = await retrieval_service.index_document(doc)
    print(f"Successfully seeded! Chunks indexed: {res.chunk_count}, time: {res.processing_time_ms}ms")

if __name__ == "__main__":
    asyncio.run(seed())
