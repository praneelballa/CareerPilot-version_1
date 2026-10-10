from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SuggestionCategory(str, Enum):
    WEAK_WORDING = "weak_wording"
    TECHNICAL_SPECIFICITY = "missing_technical_specificity"
    MEASURABLE_IMPACT = "missing_measurable_impact"
    RELEVANT_EXISTING_SKILL = "missing_relevant_existing_skill"
    KEYWORD_ALIGNMENT = "keyword_alignment"
    SKILL_GAP = "unproven_skill_gap"


class ResumeSuggestion(BaseModel):
    id: str
    category: SuggestionCategory
    original_text: str
    suggested_text: str
    reason: str
    evidence: Optional[str] = None
    is_skill_gap: bool = False
    selected: bool = False


class ResumeVersion(BaseModel):
    version_id: str
    candidate_id: str
    parent_version_id: Optional[str] = None
    job_id: str
    version_number: int = 1
    applied_suggestion_ids: List[str] = Field(default_factory=list)
    tailored_summary: str
    modified_bullets: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApplicationDraft(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    company_name: str
    resume_version_id: Optional[str] = None
    recipient: Optional[str] = None
    subject: str
    body: str
    attachment_path: Optional[str] = None
    gmail_message_id: Optional[str] = None
    sent_at: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.DRAFT
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLogEntry(BaseModel):
    id: Optional[int] = None
    application_id: str
    action: str = Field(..., description="Action name e.g. human_approved, send_completed")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Optional[str] = None


class HumanApprovalRequest(BaseModel):
    recipient: str = Field(..., description="Confirmed recipient address")
    subject: str
    body: str
    human_confirmed: bool = Field(..., description="Must explicitly be True")


class SendApplicationResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    gmail_message_id: str
    sent_at: str
    message: str


class GmailAuthStatus(BaseModel):
    is_connected: bool
    email_address: Optional[str] = None


class GenerateApplicationRequest(BaseModel):
    candidate_id: str
    job_id: str
    recipient: Optional[str] = None


class ApplyResumeChangesRequest(BaseModel):
    selected_suggestion_ids: List[str]


class ResumeOptimizationResponse(BaseModel):
    candidate_id: str
    job_id: str
    suggestions: List[ResumeSuggestion]