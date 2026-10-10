from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobSearchFilter(BaseModel):
    role: str = Field(..., description="Target role e.g. Python Developer, Machine Learning Intern")
    location: Optional[str] = Field(None, description="Preferred location e.g. Hyderabad, Remote")
    remote_only: bool = Field(False, description="Whether to filter specifically for remote jobs")
    limit: int = Field(default=20, ge=1, le=100)


class Job(BaseModel):
    job_id: str = Field(description="Unique deterministic hash/ID of the job")
    source: str = Field(description="Source identifier (remotive, linkedin, internshala)")
    title: str
    company: str
    location: str
    remote_type: str = Field(default="on_site", description="remote, hybrid, on_site")
    employment_type: Optional[str] = Field(None, description="full_time, part_time, internship, contract")
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = Field(None, description="internship, entry, mid, senior")
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    application_url: str
    source_url: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SourceStatus(BaseModel):
    source_name: str
    status: str = Field(description="ok, restricted_by_tos_or_waf, no_results, error")
    jobs_found: int = 0
    message: str


class JobSearchResponse(BaseModel):
    total_found: int
    jobs: List[Job]
    source_statuses: List[SourceStatus]