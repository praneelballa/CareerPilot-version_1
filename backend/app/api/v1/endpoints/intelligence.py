import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.intelligence import (
    AutoJobDiscoveryRequest,
    RankedJobMatch,
    ResumeTailoringResult,
    ApplicationEmailResult
)
from app.schemas.matching import MatchingRequest
from app.services.auto_match_service import AutoMatchService
from app.services.job_repository import JobRepository
from app.agents.resume_tailor_agent import ResumeTailorAgent
from typing import List

router = APIRouter()
settings = get_settings()
auto_match_service = AutoMatchService()
tailor_agent = ResumeTailorAgent()
job_repo = JobRepository()


def load_candidate(candidate_id: str) -> CandidateProfile:
    path = Path(settings.PROCESSED_DIR) / f"{candidate_id}.json"
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile '{candidate_id}' not found."
        )
    with open(path, "r", encoding="utf-8") as f:
        return CandidateProfile(**json.load(f))


@router.post("/auto-discover", response_model=List[RankedJobMatch], status_code=status.HTTP_200_OK)
async def auto_discover_jobs(payload: AutoJobDiscoveryRequest):
    """
    Discovers live opportunities inferred directly from the uploaded resume's
    technical skills, experience, and projects. No manual skill entry required.
    """
    return await auto_match_service.discover_and_rank_jobs(payload)


@router.post("/tailor-resume", response_model=ResumeTailoringResult, status_code=status.HTTP_200_OK)
async def tailor_resume(payload: MatchingRequest):
    """
    Produces grounded resume revisions and identified weaknesses based on
    factual candidate profile data compared with target job requirements.
    """
    profile = load_candidate(payload.candidate_id)
    job = await job_repo.get_job_by_id(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found in repository.")
    return await tailor_agent.generate_resume_improvements(profile, job)


@router.post("/generate-email", response_model=ApplicationEmailResult, status_code=status.HTTP_200_OK)
async def generate_email(payload: MatchingRequest):
    """
    Generates a personalized application email grounded in actual resume evidence.
    """
    profile = load_candidate(payload.candidate_id)
    job = await job_repo.get_job_by_id(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found in repository.")
    return await tailor_agent.generate_application_email(profile, job)