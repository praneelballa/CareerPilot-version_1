import json
from typing import List, Optional
from groq import AsyncGroq
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.job import Job
from app.schemas.company import CompanyResearch
from app.schemas.application import ResumeSuggestion, SuggestionCategory

settings = get_settings()


class OptimizationSuggestionsWrapper(BaseModel):
    suggestions: List[ResumeSuggestion] = Field(default_factory=list)


class GroundedEmailWrapper(BaseModel):
    subject: str
    body: str


class ApplicationPackagingAgent:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            self.client = None
        else:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate_suggestions(
        self, profile: CandidateProfile, job: Job, company: Optional[CompanyResearch]
    ) -> List[ResumeSuggestion]:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API Key missing in backend/.env"
            )

        system_instruction = (
            "You are an ATS compliance auditor.\n"
            "STRICT RULES:\n"
            "1. NEVER fabricate candidate experience or tools.\n"
            "2. If candidate lacks a skill, set is_skill_gap=True and category=unproven_skill_gap.\n"
            "3. Return JSON with 'suggestions' list of 3-5 items."
        )

        user_prompt = f"""
Candidate: {profile.name}
Summary: {profile.summary}
Skills: {profile.skills.model_dump_json()}
Bullets: {[b for exp in profile.experience for b in exp.responsibilities][:4]}
Projects: {[p.title for p in profile.projects][:3]}

Job: {job.title} at {job.company}
Required: {job.required_skills}
Description: {(job.description or '')[:800]}
"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=850,
            )
            data = json.loads(response.choices[0].message.content)
            wrapper = OptimizationSuggestionsWrapper(**data)
            for idx, sug in enumerate(wrapper.suggestions):
                sug.id = f"sug-{idx+1}"
            return wrapper.suggestions
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Optimization analysis failed: {str(e)}"
            )

    async def generate_grounded_email(
        self,
        profile: CandidateProfile,
        job: Job,
        company: Optional[CompanyResearch],
        tailored_summary: Optional[str]
    ) -> GroundedEmailWrapper:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API Key missing in backend/.env"
            )

        system_instruction = (
            "Draft a concise, grounded application email.\n"
            "Address 'Hiring Team'. Reference verified projects.\n"
            "Return JSON with 'subject' and 'body'."
        )

        company_facts = [f.fact for f in company.relevant_facts][:2] if company else []
        prompt = f"""
Candidate: {profile.name}
Summary: {tailored_summary or profile.summary}
Projects: {[p.title for p in profile.projects][:3]}

Job: {job.title} at {job.company}
Company Facts: {company_facts}
"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=850,
            )
            data = json.loads(response.choices[0].message.content)
            return GroundedEmailWrapper(**data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email synthesis failed: {str(e)}"
            )