"""
FastAPI Application Entry Point
─────────────────────────────────
The main application factory.

ARCHITECTURE:
- Lifespan context manager for startup/shutdown
- CORS middleware for frontend
- API versioning via router prefix
- Redirect endpoint mounted at root (not under /api/v1)
- Health check for monitoring
- Structured logging
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.v1.router import router as api_v1_router
from app.api.v1.redirect import router as redirect_router
from app.dependencies import get_redis, close_redis

settings = get_settings()

# ── Logging Configuration ─────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Application Lifespan ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown lifecycle management.
    
    Startup:
    - Verify Redis connectivity
    - Log configuration info
    
    Shutdown:
    - Close Redis connection pool
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} ({settings.APP_ENV})")
    logger.info(f"📡 Base URL: {settings.BASE_URL}")

    # Verify Redis
    try:
        redis = await get_redis()
        pong = await redis.ping()
        logger.info(f"✅ Redis connected: {pong}")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed (operating in degraded mode): {e}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_redis()


# ── Create Application ────────────────────────────────
app = FastAPI(
    title="Scalable URL Shortener",
    description=(
        "A production-grade URL shortening service with analytics, "
        "rate limiting, JWT authentication, and Redis caching."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler.
    
    WHY?
    - Never expose internal errors to clients
    - Log stack trace for debugging
    - Return consistent error format
    """
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Health Check ───────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns status of all dependencies.
    """
    health = {"status": "healthy", "service": settings.APP_NAME}

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        health["redis"] = "connected"
    except Exception:
        health["redis"] = "disconnected"
        health["status"] = "degraded"

    return health


# ── Register Routers ──────────────────────────────────
# API routes under /api/v1
app.include_router(api_v1_router)

# Redirect route at root level (MUST be last to avoid catching API routes)
app.include_router(redirect_router)
