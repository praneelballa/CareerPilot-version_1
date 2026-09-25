from fastapi import APIRouter, Depends, status
from app.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns service availability, timestamp, and active environment."
)
async def check_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version="1.0.0"
    )