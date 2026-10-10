from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.matching import MatchMetrics, SkillEvidence, SkillGapItem, RoadmapMilestone


class BulletImprovement(BaseModel):
    original_evidence: str = Field(..., description="Original quote or bullet from candidate profile")
    weakness: str = Field(..., description="Why this bullet is weak (e.g., lacks metrics, missing target keywords)")
    suggested_rewrite: str = Field(..., description="Targeted revision using Action + Context + Measurable Impact based ONLY on candidate facts")


class ResumeTailoringResult(BaseModel):
    candidate_id: str
    job_id: str
    target_role: str
    target_company: str
    targeted_summary: str = Field(..., description="Tailored professional summary emphasizing verified qualifications")
    bullet_improvements: List[BulletImprovement] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list, description="Keywords to highlight if candidate possesses them")
    recommended_skills_to_learn: List[str] = Field(default_factory=list, description="Skills not found in resume that should be learned")


class ApplicationEmailResult(BaseModel):
    candidate_id: str
    job_id: str
    target_role: str
    target_company: str
    subject_line: str
    email_body: str
    key_selling_points: List[str]


class AutoJobDiscoveryRequest(BaseModel):
    candidate_id: str
    location: Optional[str] = None
    remote_only: bool = False
    limit: int = Field(default=20, ge=1, le=50)


class RankedJobMatch(BaseModel):
    job_id: str
    source: str
    title: str
    company: str
    location: str
    remote_type: str
    description: str
    required_skills: List[str]
    application_url: str
    composite_score: float
    semantic_similarity: float
    skill_coverage: float
    location_alignment: float