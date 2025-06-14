"""Main FastAPI application for the Agentic SRE backend.
This file initializes the FastAPI app, sets up middleware,
defines exception handlers, and includes the API routers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logging import setup_logging, get_logger
from app.core.exceptions import AgenticSREException

# Import the new routers we have created
from app.api.routes import chat as chat_router
from app.api.websockets import event_handlers as websocket_router

# --- Initial Setup ---
# Configure logging as early as possible
setup_logging(settings)
logger = get_logger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# --- Middleware Configuration ---
# Add CORS middleware to allow requests from our frontend
if settings.CORS_ORIGINS:
    # Manually parse the comma-separated string into a list of origins
    allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Use the parsed list
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("CORS_ORIGINS is not set. No CORS middleware will be applied.")

# --- Exception Handlers ---
@app.exception_handler(AgenticSREException)
async def custom_agentic_exception_handler(request: Request, exc: AgenticSREException):
    """Handles all custom exceptions and returns structured JSON."""

    logger.error(
        "Custom exception caught: %s", exc.error_code, extra={"error_details": exc.details, "path": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )

# --- API Routers ---
# Connect route modules to the main application
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(websocket_router.router, tags=["WebSocket"])


# --- Root and Health Check Endpoints ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm the API is running."""

    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""

    return {"status": "ok"}
