from typing import List, Optional
from pydantic import BaseModel, Field


class MatchMetrics(BaseModel):
    semantic_similarity: float = Field(..., description="Cosine similarity between candidate and job (0.0 - 1.0)")
    skill_coverage: float = Field(..., description="Proportion of required skills satisfied (0.0 - 1.0)")
    location_alignment: float = Field(..., description="Alignment score for geographic/remote preferences (0.0 - 1.0)")
    composite_score: float = Field(..., description="Weighted total match score (0 - 100)")
    calculation_basis: Optional[str] = Field(
        default="Composite = (0.45 * Semantic) + (0.35 * Skills) + (0.20 * Location)",
        description="Formula or explanation breakdown for deterministic scoring"
    )


class SkillEvidence(BaseModel):
    skill: str
    in_resume: bool
    evidence_quote: Optional[str] = None
    job_requirement_context: Optional[str] = None


class SkillGapItem(BaseModel):
    skill: str
    priority: str = Field(default="important", description="critical, important, or optional")
    current_gap: str
    recommended_learning: str


class RoadmapMilestone(BaseModel):
    step: int
    title: str
    focus_area: str
    target_skills: List[str]
    practice_project: str
    recommended_resume_bullet: str


class AgentReasoningOutput(BaseModel):
    compatibility_explanation: str
    evidence_breakdown: List[SkillEvidence] = Field(default_factory=list)
    skill_gaps: List[SkillGapItem] = Field(default_factory=list)
    career_roadmap: List[RoadmapMilestone] = Field(default_factory=list)


class MatchingRequest(BaseModel):
    candidate_id: str
    job_id: str


class MatchingAnalysisResponse(BaseModel):
    candidate_id: str
    job_id: str
    job_title: str
    company: str
    metrics: MatchMetrics
    compatibility_explanation: str
    evidence_breakdown: List[SkillEvidence]
    skill_gaps: List[SkillGapItem]
    career_roadmap: List[RoadmapMilestone]


# Backwards compatibility alias for older endpoints and tests
JobMatchAnalysis = MatchingAnalysisResponse