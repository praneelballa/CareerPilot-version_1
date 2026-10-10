from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import (
    health, resume, jobs, matching, intelligence, company, applications, gmail
)
from app.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
logger = setup_logging(debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing CareerPilotAI Runtime...")
    yield
    logger.info("Shutting down CareerPilotAI Runtime...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred in the intelligence pipeline.", "path": request.url.path}
    )

app.include_router(health.router, tags=["Health"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(resume.router, prefix=f"{settings.API_V1_STR}/resume", tags=["Resume Intelligence"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["Job Discovery"])
app.include_router(matching.router, prefix=f"{settings.API_V1_STR}/matching", tags=["Matching Engine"])
app.include_router(intelligence.router, prefix=f"{settings.API_V1_STR}/intelligence", tags=["Application Intelligence"])
app.include_router(company.router, prefix=f"{settings.API_V1_STR}/company", tags=["Company Research"])
app.include_router(applications.router, prefix=f"{settings.API_V1_STR}/applications", tags=["Application Packaging"])
app.include_router(gmail.router, prefix=f"{settings.API_V1_STR}/gmail", tags=["Gmail Automation"])


@app.get("/", include_in_schema=False)
async def root_redirect():
    return {"service": settings.PROJECT_NAME, "docs": f"{settings.API_V1_STR}/docs", "health": "/health"}