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

import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.redirect import router as redirect_router
from app.api.v1.router import router as api_v1_router
from app.config import get_settings
from app.dependencies import close_redis, get_db, get_redis
from app.utils.logging import configure_logging

settings = get_settings()

# ── Logging Configuration ─────────────────────────────
configure_logging(env=settings.APP_ENV, debug=settings.APP_DEBUG)
logger = structlog.get_logger(__name__)
access_logger = structlog.get_logger("http.access")


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


# ── Security, Request ID & Observability Middleware ───
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    structlog.contextvars.clear_contextvars()

    # Generate/propagate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Get client IP and handle proxy forwarding securely
    from app.utils.client_ip import get_client_ip

    client_ip = get_client_ip(request)

    # Bind request variables to structured logging context
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        client_ip=client_ip,
        method=request.method,
        path=request.url.path,
    )

    path = request.url.path
    is_noise_route = path == "/metrics" or path.startswith("/health")

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        if not is_noise_route:
            # Track HTTP Metrics
            from app.utils.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method, path=path, status_code=str(status_code)
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, path=path).observe(
                duration_ms / 1000.0
            )

            # Log HTTP access details
            access_logger.info(
                "http_request_completed",
                status_code=status_code,
                duration_ms=round(duration_ms, 2),
            )

    # Attach request ID to response headers
    response.headers["X-Request-ID"] = request_id

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

    return response


# ── Exception Helpers ─────────────────────────────────
def get_error_code(status_code: int) -> str:
    from fastapi import status

    mapping = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_410_GONE: "GONE",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    }
    return mapping.get(status_code, "INTERNAL_SERVER_ERROR")


# ── Exception Handlers ────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())

    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": get_error_code(exc.status_code),
                "message": exc.detail,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())

    # Simplify/format validation error messages
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "invalid value")
        error_messages.append(f"{loc}: {msg}")

    message = "; ".join(error_messages) if error_messages else "Validation failed"

    logger.warning(
        "validation_error",
        errors=exc.errors(),
        message=message,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())

    logger.exception(
        "unhandled_exception",
        error=str(exc),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        },
    )


# ── Health Checks & Probes ─────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check(redis: Redis = Depends(get_redis)):
    """
    Health check endpoint for load balancers and monitoring.

    Returns status of all dependencies.
    """
    health = {"status": "healthy", "service": settings.APP_NAME}

    # Check Redis
    try:
        await redis.ping()
        health["redis"] = "connected"
    except Exception:
        health["redis"] = "disconnected"
        health["status"] = "degraded"

    return health


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness probe to check if the container is running."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/health/ready", tags=["Health"])
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Readiness probe to check if downstream services are reachable."""
    health = {"status": "healthy", "service": settings.APP_NAME}
    status_code = 200

    # Check database
    try:
        from sqlalchemy import text

        await db.execute(text("SELECT 1"))
        health["postgres"] = "connected"
        if db.bind is not None:
            health["postgres_dialect"] = db.bind.dialect.name
            health["postgres_driver"] = db.bind.dialect.driver
    except Exception as e:
        logger.error("readiness_check_postgres_failed", error=str(e))
        health["postgres"] = "disconnected"
        health["status"] = "degraded"
        status_code = 503

    # Check Redis
    try:
        await redis.ping()
        health["redis"] = "connected"
    except Exception as e:
        logger.error("readiness_check_redis_failed", error=str(e))
        health["redis"] = "disconnected"
        health["status"] = "degraded"
        status_code = 503

    return JSONResponse(status_code=status_code, content=health)


# ── Observability & Metrics ───────────────────────────
@app.get("/metrics", tags=["Observability"])
def metrics_endpoint():
    """Exposes Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── Register Routers ──────────────────────────────────
# API routes under /api/v1
app.include_router(api_v1_router)

# Redirect route at root level (MUST be last to avoid catching API routes)
app.include_router(redirect_router)
