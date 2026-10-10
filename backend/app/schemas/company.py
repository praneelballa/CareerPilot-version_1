from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ResolvedDomain(BaseModel):
    company_name: str
    official_domain: Optional[str] = None
    homepage_url: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_method: str = Field(default="job_url_inference")


class CompanyFactItem(BaseModel):
    fact: str = Field(..., description="Verifiable factual statement regarding the company")
    source_url: str = Field(..., description="Exact page URL from which the fact was extracted")


class CompanyResearch(BaseModel):
    company_name: str
    official_domain: str
    description: str = Field(..., description="Neutral summary of company business and domain")
    mission: Optional[str] = None
    values: List[str] = Field(default_factory=list)
    technology_focus: List[str] = Field(default_factory=list, description="Known engineering stacks, tools, or research areas")
    relevant_products: List[str] = Field(default_factory=list)
    career_information: Optional[str] = Field(None, description="Hiring ethos, team structure, or engineering culture summary")
    internship_information: Optional[str] = Field(None, description="Student/early-career specific program notes if found")
    relevant_facts: List[CompanyFactItem] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="completed", description="completed, partial, or blocked_by_policy")


class CompanyResearchRequest(BaseModel):
    job_id: str