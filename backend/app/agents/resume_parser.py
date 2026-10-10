import json
from groq import AsyncGroq
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.services.skill_normalizer import SkillNormalizer

settings = get_settings()

EXACT_SCHEMA_PROMPT = """
You are an expert ATS resume extraction engine.
You MUST output ONLY a valid JSON object matching this exact flat structure:

{
  "name": "Candidate Full Name",
  "email": "candidate@example.com",
  "phone": "+1234567890",
  "location": "City, Country",
  "summary": "Professional summary...",
  "education": [
    {
      "institution": "University Name",
      "degree": "B.Tech / B.S.",
      "field_of_study": "Computer Science",
      "start_year": "2022",
      "end_year": "2026",
      "grade_or_gpa": "8.5"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "role": "Role Title",
      "location": "Location",
      "start_date": "Jan 2024",
      "end_date": "Present",
      "responsibilities": ["bullet point 1", "bullet point 2"]
    }
  ],
  "projects": [
    {
      "title": "Project Name",
      "description": "Project overview",
      "technologies": ["Python", "FastAPI"],
      "link": "https://github.com/..."
    }
  ],
  "skills": {
    "programming_languages": ["Python", "C++"],
    "frameworks": ["FastAPI", "React"],
    "libraries": ["PyTorch"],
    "databases": ["PostgreSQL"],
    "cloud_and_tools": ["Docker", "Git"],
    "ai_and_ml": ["RAG", "NLP"],
    "soft_skills": ["Leadership", "Communication"]
  },
  "certifications": ["Cert 1", "Cert 2"],
  "achievements": ["Achievement 1"],
  "links": ["https://linkedin.com/..."]
}

CRITICAL RULES:
1. Do NOT nest 'name' under 'personal_info'. It must be at the root.
2. Under 'projects', use key 'title', NEVER 'name'.
3. 'certifications' must be a list of strings, NOT dictionaries.
4. Output raw JSON only.
"""

def sanitize_extracted_dict(data: dict, candidate_id: str) -> dict:
    if "personal_info" in data and isinstance(data["personal_info"], dict):
        p_info = data.pop("personal_info")
        for k in ["name", "email", "phone", "location", "summary"]:
            if k in p_info and k not in data:
                data[k] = p_info[k]

    if not data.get("name"):
        data["name"] = "Candidate"
    data["candidate_id"] = candidate_id

    if "projects" in data and isinstance(data["projects"], list):
        clean_projects = []
        for p in data["projects"]:
            if isinstance(p, dict):
                if "title" not in p and "name" in p:
                    p["title"] = p.pop("name")
                if "title" not in p:
                    p["title"] = "Project"
                if "description" not in p:
                    p["description"] = ""
                if "technologies" not in p or not isinstance(p["technologies"], list):
                    p["technologies"] = []
                clean_projects.append(p)
        data["projects"] = clean_projects

    if "certifications" in data and isinstance(data["certifications"], list):
        clean_certs = []
        for c in data["certifications"]:
            if isinstance(c, dict):
                clean_certs.append(c.get("name") or c.get("title") or str(c))
            elif isinstance(c, str):
                clean_certs.append(c)
        data["certifications"] = clean_certs

    if "skills" not in data or not isinstance(data["skills"], dict):
        data["skills"] = {}

    return data


class ResumeParserAgent:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            self.client = None
        else:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def parse_resume_text(self, candidate_id: str, raw_text: str) -> CandidateProfile:
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API Key is missing. Configure GROQ_API_KEY in backend/.env."
            )

        user_content = f"Resume text to parse:\n\n{raw_text[:4000]}"

        try:
            response = await self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": EXACT_SCHEMA_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=900,
            )

            raw_json = response.choices[0].message.content
            if not raw_json:
                raise ValueError("Received empty response from Groq.")

            raw_data = json.loads(raw_json)
            sanitized_data = sanitize_extracted_dict(raw_data, candidate_id)
            
            profile = CandidateProfile(**sanitized_data)
            profile.skills = SkillNormalizer.normalize_skills(profile.skills)
            return profile

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Groq failed to structure candidate profile: {str(e)}"
            )