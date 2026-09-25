from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import health
from app.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
logger = setup_logging(debug=settings.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing CareerPilotAI Backend Infrastructure...")
    yield
    logger.info("Shutting down CareerPilotAI Backend Infrastructure...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (CORS) Configuration
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Structured Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception intercepted at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected internal server error occurred.",
            "path": request.url.path
        }
    )

# Direct Router Mounting
app.include_router(health.router, tags=["Health"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])

@app.get("/", include_in_schema=False)
async def root_redirect():
    return {
        "service": settings.PROJECT_NAME,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health"
    }