from datetime import datetime, timezone
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Operational status")
    environment: str = Field(description="Runtime environment")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(default="1.0.0")