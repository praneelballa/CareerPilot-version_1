from typing import Tuple, List
from app.schemas.candidate import CandidateProfile
from app.schemas.job import Job
from app.schemas.matching import MatchMetrics
from app.services.embedding_service import EmbeddingService

class DeterministicMatcher:
    @staticmethod
    def get_candidate_skills_flat(profile: CandidateProfile) -> List[str]:
        """Safely extract all skills into a flat list from SkillCategories."""
        skills = []
        if hasattr(profile.skills, "model_dump"):
            data = profile.skills.model_dump()
            for skill_list in data.values():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
        elif hasattr(profile.skills, "dict"):
            data = profile.skills.dict()
            for skill_list in data.values():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
        return skills

    @classmethod
    def compute_metrics(cls, profile: CandidateProfile, job: Job) -> Tuple[MatchMetrics, List[str], List[str]]:
        candidate_skills = cls.get_candidate_skills_flat(profile)
        cand_skill_lower = {s.lower().strip() for s in candidate_skills}

        job_req_skills = job.required_skills
        matched_skills = []
        missing_skills = []

        for req in job_req_skills:
            if req.lower().strip() in cand_skill_lower:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        skill_coverage = len(matched_skills) / len(job_req_skills) if job_req_skills else 1.0

        cand_loc = (profile.location or "").lower()
        job_loc = (job.location or "").lower()
        job_remote = (job.remote_type or "").lower()

        if "remote" in job_remote or "remote" in cand_loc or "worldwide" in job_loc:
            loc_score = 1.0
        elif cand_loc and job_loc and (cand_loc in job_loc or job_loc in cand_loc):
            loc_score = 1.0
        else:
            loc_score = 0.5

        cand_text = f"{profile.summary}\nSkills: {', '.join(candidate_skills)}"
        job_text = f"{job.title}\n{job.description}\nSkills: {', '.join(job_req_skills)}"
        semantic_sim = EmbeddingService.compute_similarity(cand_text, job_text)

        composite = (0.45 * semantic_sim + 0.35 * skill_coverage + 0.20 * loc_score) * 100.0

        basis = (
            f"Composite = (0.45 * {semantic_sim:.4f}) + "
            f"(0.35 * {skill_coverage:.4f}) + "
            f"(0.20 * {loc_score:.4f})"
        )

        metrics = MatchMetrics(
            semantic_similarity=round(semantic_sim, 4),
            skill_coverage=round(skill_coverage, 4),
            location_alignment=round(loc_score, 4),
            composite_score=round(composite, 2),
            calculation_basis=basis
        )

        return metrics, matched_skills, missing_skills
