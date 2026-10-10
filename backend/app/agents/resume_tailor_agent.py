import json
from groq import AsyncGroq
from fastapi import HTTPException, status
from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.job import Job
from app.schemas.intelligence import ResumeTailoringResult, ApplicationEmailResult

settings = get_settings()


class ResumeTailorAgent:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            self.client = None
        else:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate_resume_improvements(self, profile: CandidateProfile, job: Job) -> ResumeTailoringResult:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API Key missing in backend/.env"
            )

        system_instruction = (
            "You are a Technical Resume Strategist.\n"
            "Analyze candidate qualifications against the job description.\n"
            "STRICT RULES:\n"
            "1. NEVER fabricate metrics or projects.\n"
            "2. Identify genuine weaknesses in existing bullets.\n"
            "3. Rewrite bullets using ONLY verified skills.\n"
            "4. Return valid JSON matching ResumeTailoringResult schema."
        )

        prompt = f"""
Candidate: {profile.name}
Summary: {profile.summary}
Skills: {profile.skills.model_dump_json()}
Top Experience: {[b for exp in profile.experience for b in exp.responsibilities][:4]}
Projects: {[p.title for p in profile.projects][:3]}

Job: {job.title} at {job.company}
Required Skills: {job.required_skills}
Description: {(job.description or '')[:800]}
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
            result = ResumeTailoringResult(**data)
            result.candidate_id = profile.candidate_id
            result.job_id = job.job_id
            result.target_role = job.title
            result.target_company = job.company
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resume tailoring agent failed: {str(e)}"
            )

    async def generate_application_email(self, profile: CandidateProfile, job: Job) -> ApplicationEmailResult:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API Key missing in backend/.env"
            )

        system_instruction = (
            "Write a concise, professional job application email based on actual resume evidence.\n"
            "Output valid JSON with: subject_line, email_body, key_selling_points."
        )

        prompt = f"""
Candidate: {profile.name}
Role/Summary: {profile.summary}
Skills: {profile.skills.model_dump_json()}
Projects: {[p.title for p in profile.projects][:3]}

Job: {job.title} at {job.company}
Description: {(job.description or '')[:800]}
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
            result = ApplicationEmailResult(**data)
            result.candidate_id = profile.candidate_id
            result.job_id = job.job_id
            result.target_role = job.title
            result.target_company = job.company
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Application email generator failed: {str(e)}"
            )