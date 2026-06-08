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
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.redirect import router as redirect_router
from app.api.v1.router import router as api_v1_router
from app.config import get_settings
from app.dependencies import close_redis, get_redis

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


# ── Security & Request ID Middleware ──────────────────
@app.middleware("http")
async def security_and_request_id_middleware(request: Request, call_next):
    # Generate/propagate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

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
        f"HTTP exception: status_code={exc.status_code} detail={exc.detail} request_id={request_id}"
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

    logger.warning(f"Validation error: {exc.errors()} request_id={request_id}")

    # Simplify/format validation error messages
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "invalid value")
        error_messages.append(f"{loc}: {msg}")

    message = "; ".join(error_messages) if error_messages else "Validation failed"

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

    logger.exception(f"Unhandled exception: {exc} request_id={request_id}")

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
