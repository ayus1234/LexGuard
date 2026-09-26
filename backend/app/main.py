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
    """
    from app.services.retrieval_service import retrieval_service
    from app.core.corpus import get_corpus_document_by_id
    
    demo_doc_id = "doc-saas-v42"
    
    # Check if already indexed
    if retrieval_service.is_document_indexed(demo_doc_id):
        logger.info(f"Demo document {demo_doc_id} already indexed in vector store")
        return
    
    logger.info(f"Demo document {demo_doc_id} not found in vector store, indexing now...")
    
    # Get the demo document from corpus
    demo_doc = get_corpus_document_by_id(demo_doc_id)
    if not demo_doc:
        logger.warning(f"Demo document {demo_doc_id} not found in corpus registry")
        return
    
    # Index the document
    result = await retrieval_service.index_document(demo_doc)
    logger.info(f"Demo document {demo_doc_id} indexed successfully: {result.chunk_count} chunks, {result.processing_time_ms}ms")


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
