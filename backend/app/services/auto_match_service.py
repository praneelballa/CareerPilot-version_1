import json
from pathlib import Path
from typing import List
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.job import JobSearchFilter
from app.schemas.intelligence import AutoJobDiscoveryRequest, RankedJobMatch
from app.services.job_discovery import JobDiscoveryService
from app.services.matcher import DeterministicMatcher

settings = get_settings()


class AutoMatchService:
    def __init__(self):
        self.discovery_service = JobDiscoveryService()

    @staticmethod
    def derive_search_keywords(profile: CandidateProfile) -> str:
        """
        Synthesizes search keywords from the resume's skills,
        experience titles, and project context.
        """
        role_candidates = []
        if profile.experience:
            role_candidates.append(profile.experience[0].role)

        skills = profile.skills
        top_skills = (
            skills.ai_and_ml[:2] + 
            skills.programming_languages[:2] + 
            skills.frameworks[:2]
        )

        if role_candidates:
            # e.g., "Full Stack Developer Python React"
            return f"{role_candidates[0]} {' '.join(top_skills)}".strip()
        elif top_skills:
            return " ".join(top_skills)
        return "Software Engineer"

    async def discover_and_rank_jobs(self, request: AutoJobDiscoveryRequest) -> List[RankedJobMatch]:
        cand_path = Path(settings.PROCESSED_DIR) / f"{request.candidate_id}.json"
        if not cand_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate profile '{request.candidate_id}' not found. Please upload resume first."
            )

        with open(cand_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        profile = CandidateProfile(**profile_data)

        # 1. Automatically extract search terms from parsed resume
        derived_query = self.derive_search_keywords(profile)
        
        # 2. Discover real jobs compliant with terms of service
        search_filter = JobSearchFilter(
            role=derived_query,
            location=request.location or profile.location,
            remote_only=request.remote_only,
            limit=request.limit
        )

        discovery_result = await self.discovery_service.discover_jobs(search_filter)

        # Fallback if specific multi-term search yielded 0 jobs
        if not discovery_result.jobs and profile.skills.programming_languages:
            search_filter.role = profile.skills.programming_languages[0]
            discovery_result = await self.discovery_service.discover_jobs(search_filter)

        # 3. Deterministically rank all discovered jobs against candidate profile
        ranked_jobs: List[RankedJobMatch] = []
        for job in discovery_result.jobs:
            metrics, matched, missing = DeterministicMatcher.compute_metrics(profile, job)
            ranked_jobs.append(RankedJobMatch(
                job_id=job.job_id,
                source=job.source,
                title=job.title,
                company=job.company,
                location=job.location,
                remote_type=job.remote_type,
                description=job.description,
                required_skills=job.required_skills,
                application_url=job.application_url,
                composite_score=metrics.composite_score,
                semantic_similarity=metrics.semantic_similarity,
                skill_coverage=metrics.skill_coverage,
                location_alignment=metrics.location_alignment
            ))

        # Sort descending by composite score
        ranked_jobs.sort(key=lambda x: x.composite_score, reverse=True)
        return ranked_jobs