from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class Education(BaseModel):
    institution: str = Field(description="Name of university or institution")
    degree: str = Field(description="Degree name e.g., B.Tech, B.S., M.S.")
    field_of_study: Optional[str] = Field(None, description="Field of study or major")
    start_year: Optional[str] = Field(None, description="Start date/year")
    end_year: Optional[str] = Field(None, description="End date/year or expected completion")
    grade_or_gpa: Optional[str] = Field(None, description="GPA or percentage if stated")


class Experience(BaseModel):
    company: str = Field(description="Organization name")
    role: str = Field(description="Job title/role")
    location: Optional[str] = Field(None, description="Location or Remote")
    start_date: Optional[str] = Field(None, description="Employment start date")
    end_date: Optional[str] = Field(None, description="Employment end date or 'Present'")
    responsibilities: List[str] = Field(default_factory=list, description="Key bullet points")


class Project(BaseModel):
    title: str = Field(description="Project name")
    description: str = Field(description="Summary of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="Repository or live URL")


class SkillCategories(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_and_tools: List[str] = Field(default_factory=list)
    ai_and_ml: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    candidate_id: str = Field(description="Unique candidate / document identifier")
    name: str = Field(description="Full name of candidate")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="Current city/country")
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: SkillCategories = Field(default_factory=SkillCategories)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list, description="GitHub, LinkedIn, Portfolio URLs")


class ResumeUploadResponse(BaseModel):
    candidate_id: str
    filename: str
    extracted_text_preview: str
    character_count: int
    message: str


class ResumeAnalyzeRequest(BaseModel):
    candidate_id: str