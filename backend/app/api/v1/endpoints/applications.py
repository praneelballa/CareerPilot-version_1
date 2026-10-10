import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.config import get_settings
from app.schemas.candidate import CandidateProfile
from app.schemas.application import (
    ApplicationDraft,
    ApplicationStatus,
    HumanApprovalRequest,
    SendApplicationResponse,
    GenerateApplicationRequest,
    ApplyResumeChangesRequest,
    ResumeOptimizationResponse,
    ResumeVersion,
    AuditLogEntry
)
from app.agents.application_agents import ApplicationPackagingAgent
from app.services.job_repository import JobRepository
from app.services.gmail_service import GmailService
from app.services.gmail_auth import GmailAuthService

router = APIRouter()
settings = get_settings()
repo = JobRepository()
agent = ApplicationPackagingAgent()


def load_candidate(candidate_id: str) -> CandidateProfile:
    path = Path(settings.PROCESSED_DIR) / f"{candidate_id}.json"
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile '{candidate_id}' not found."
        )
    with open(path, "r", encoding="utf-8") as f:
        return CandidateProfile(**json.load(f))


def validate_attachment(candidate_id: str) -> Optional[str]:
    upload_dir = Path(settings.UPLOAD_DIR)
    for ext in [".pdf", ".docx"]:
        file_path = upload_dir / f"{candidate_id}{ext}"
        if file_path.exists() and file_path.stat().st_size > 0:
            return str(file_path)
    return None


@router.post("/optimize", response_model=ResumeOptimizationResponse, status_code=status.HTTP_200_OK)
async def analyze_resume_optimizations(payload: GenerateApplicationRequest):
    profile = load_candidate(payload.candidate_id)
    job = await repo.get_job_by_id(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found.")

    company = await repo.get_company_research(job.company)

    cached_suggs = await repo.get_suggestions_cache(payload.candidate_id, payload.job_id)
    if cached_suggs:
        return ResumeOptimizationResponse(
            candidate_id=payload.candidate_id,
            job_id=payload.job_id,
            suggestions=cached_suggs
        )

    suggestions = await agent.generate_suggestions(profile, job, company)
    await repo.save_suggestions_cache(payload.candidate_id, payload.job_id, suggestions)

    return ResumeOptimizationResponse(
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        suggestions=suggestions
    )


@router.post("/generate", response_model=ApplicationDraft, status_code=status.HTTP_201_CREATED)
async def generate_application(payload: GenerateApplicationRequest):
    profile = load_candidate(payload.candidate_id)
    job = await repo.get_job_by_id(payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Target job not found.")

    company = await repo.get_company_research(job.company)
    attachment_path = validate_attachment(payload.candidate_id)

    email_data = await agent.generate_grounded_email(profile, job, company, tailored_summary=None)

    app_id = f"app-{str(uuid.uuid4())[:8]}"
    draft = ApplicationDraft(
        id=app_id,
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        company_name=job.company,
        recipient=payload.recipient,  # Never fabricated; None unless supplied by user
        subject=email_data.subject,
        body=email_data.body,
        attachment_path=attachment_path,
        status=ApplicationStatus.DRAFT
    )

    await repo.save_application(draft)
    await repo.record_audit_log(app_id, "application_created", f"Created for {job.company}")
    return draft


@router.post("/{app_id}/resume-changes", response_model=ResumeVersion, status_code=status.HTTP_200_OK)
async def apply_resume_changes(app_id: str, payload: ApplyResumeChangesRequest):
    draft = await repo.get_application(app_id)
    if not draft:
        raise HTTPException(status_code=404, detail=f"Application '{app_id}' not found.")

    suggestions = await repo.get_suggestions_cache(draft.candidate_id, draft.job_id)
    if not suggestions:
        raise HTTPException(status_code=404, detail="No optimization suggestions found.")

    selected_set = set(payload.selected_suggestion_ids)
    applied_bullets = []
    applied_ids = []
    for s in suggestions:
        if s.id in selected_set and not s.is_skill_gap:
            applied_bullets.append(s.suggested_text)
            applied_ids.append(s.id)

    version_number = 1
    if draft.resume_version_id:
        existing_ver = await repo.get_resume_version(draft.resume_version_id)
        if existing_ver:
            version_number = existing_ver.version_number + 1

    version_id = f"res-v{version_number}-{str(uuid.uuid4())[:6]}"
    new_version = ResumeVersion(
        version_id=version_id,
        candidate_id=draft.candidate_id,
        parent_version_id=draft.resume_version_id,
        job_id=draft.job_id,
        version_number=version_number,
        applied_suggestion_ids=applied_ids,
        tailored_summary=f"Optimized for {draft.company_name} ({len(applied_ids)} enhancements applied)",
        modified_bullets=applied_bullets
    )

    await repo.save_resume_version(new_version)

    draft.resume_version_id = version_id
    draft.status = ApplicationStatus.READY_FOR_REVIEW
    draft.updated_at = datetime.now(timezone.utc).isoformat()
    await repo.save_application(draft)
    await repo.record_audit_log(app_id, "resume_version_created", f"Version {version_number} linked")

    return new_version


# MANDATORY HUMAN VALIDATION GATE
@router.post("/{app_id}/approve", response_model=ApplicationDraft, status_code=status.HTTP_200_OK)
async def approve_application_human_gate(app_id: str, payload: HumanApprovalRequest):
    """
    Mandatory human validation gate. Validates confirmed recipient,
    human confirmation boolean, and attachment. Transitions state strictly to HUMAN_APPROVED.
    """
    draft = await repo.get_application(app_id)
    if not draft:
        raise HTTPException(status_code=404, detail=f"Application '{app_id}' not found.")

    # 1. Require explicit human confirmation
    if not payload.human_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Human confirmation is required. You must check the review confirmation box."
        )

    # 2. Strict recipient syntax check (Never allow blank or fabricated emails)
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not payload.recipient or not re.match(email_regex, payload.recipient.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Valid recipient email address is required before approval."
        )

    # 3. Verify attachment integrity
    if not draft.attachment_path or not Path(draft.attachment_path).exists():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot approve: valid resume attachment file is missing or unreadable."
        )

    # 4. Save human edits and update state
    draft.recipient = payload.recipient.strip()
    draft.subject = payload.subject.strip()
    draft.body = payload.body.strip()
    draft.status = ApplicationStatus.HUMAN_APPROVED
    draft.updated_at = datetime.now(timezone.utc).isoformat()

    await repo.save_application(draft)
    await repo.record_audit_log(app_id, "human_approved", f"Approved for recipient {draft.recipient}")
    return draft


# GMAIL SEND EXECUTION & IDEMPOTENCY GUARD
@router.post("/{app_id}/send", response_model=SendApplicationResponse, status_code=status.HTTP_200_OK)
async def send_application_via_gmail(app_id: str):
    """
    Dispatches email through Gmail API.
    ENFORCES SECURITY INVARIANT: status MUST equal HUMAN_APPROVED.
    IDEMPOTENCY: Rejects double-sending if already SENT.
    """
    draft = await repo.get_application(app_id)
    if not draft:
        raise HTTPException(status_code=404, detail=f"Application '{app_id}' not found.")

    # Idempotency check
    if draft.status == ApplicationStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already sent. Accidental re-transmission is blocked."
        )

    # Strict invariant validation
    if draft.status != ApplicationStatus.HUMAN_APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security violation: Application status is '{draft.status}'. Only 'HUMAN_APPROVED' applications can be dispatched."
        )

    # Verify Gmail connection
    if not GmailAuthService.is_connected():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gmail account is not connected. Authorize via Gmail OAuth first."
        )

    # Mark as SENDING
    draft.status = ApplicationStatus.SENDING
    draft.updated_at = datetime.now(timezone.utc).isoformat()
    await repo.save_application(draft)
    await repo.record_audit_log(app_id, "send_started")

    try:
        msg_id = GmailService.send_application_email(
            recipient=draft.recipient,
            subject=draft.subject,
            body=draft.body,
            attachment_path=draft.attachment_path
        )

        sent_time = datetime.now(timezone.utc).isoformat()
        draft.status = ApplicationStatus.SENT
        draft.gmail_message_id = msg_id
        draft.sent_at = sent_time
        draft.updated_at = sent_time

        await repo.save_application(draft)
        await repo.record_audit_log(app_id, "send_completed", f"Gmail Message ID: {msg_id}")

        return SendApplicationResponse(
            application_id=draft.id,
            status=ApplicationStatus.SENT,
            gmail_message_id=msg_id,
            sent_at=sent_time,
            message="Application sent successfully from connected Gmail account."
        )

    except Exception as e:
        draft.status = ApplicationStatus.FAILED
        draft.updated_at = datetime.now(timezone.utc).isoformat()
        await repo.save_application(draft)
        await repo.record_audit_log(app_id, "send_failed", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gmail dispatch failed: {str(e)}"
        )


@router.get("/", response_model=List[ApplicationDraft], status_code=status.HTTP_200_OK)
async def list_all_applications():
    return await repo.list_applications()


@router.get("/{app_id}", response_model=ApplicationDraft, status_code=status.HTTP_200_OK)
async def get_application_by_id(app_id: str):
    draft = await repo.get_application(app_id)
    if not draft:
        raise HTTPException(status_code=404, detail=f"Application '{app_id}' not found.")
    return draft


@router.get("/{app_id}/audit-logs", response_model=List[AuditLogEntry], status_code=status.HTTP_200_OK)
async def get_audit_trail(app_id: str):
    return await repo.get_audit_logs(app_id)