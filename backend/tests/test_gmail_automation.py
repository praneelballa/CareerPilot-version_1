import pytest
from app.schemas.application import (
    ApplicationDraft,
    ApplicationStatus,
    HumanApprovalRequest
)
from app.services.job_repository import JobRepository
from app.services.gmail_service import GmailService


@pytest.mark.asyncio
async def test_security_invariant_blocks_unapproved_send(client):
    repo = JobRepository()

    # Create unapproved application in DRAFT state
    draft = ApplicationDraft(
        id="app-sec-01",
        candidate_id="cand_sec",
        job_id="job_sec",
        company_name="Acme",
        recipient="test@acme.com",
        subject="Application",
        body="Hello",
        status=ApplicationStatus.DRAFT
    )
    await repo.save_application(draft)

    # Attempt to dispatch immediately
    res = client.post(f"/api/v1/applications/{draft.id}/send")
    assert res.status_code == 403
    assert "HUMAN_APPROVED" in res.json()["detail"]

    # Transition to READY_FOR_REVIEW without explicit human approval
    draft.status = ApplicationStatus.READY_FOR_REVIEW
    await repo.save_application(draft)

    res_review = client.post(f"/api/v1/applications/{draft.id}/send")
    assert res_review.status_code == 403


@pytest.mark.asyncio
async def test_human_approval_gate_enforcement(client, tmp_path):
    repo = JobRepository()

    # Create dummy attachment
    dummy_att = tmp_path / "resume.pdf"
    dummy_att.write_text("Dummy resume")

    draft = ApplicationDraft(
        id="app-gate-02",
        candidate_id="cand_gate",
        job_id="job_gate",
        company_name="Google",
        recipient=None,
        subject="SWE Application",
        body="Application body",
        attachment_path=str(dummy_att),
        status=ApplicationStatus.READY_FOR_REVIEW
    )
    await repo.save_application(draft)

    # 1. Approval fails if human_confirmed is False
    res_false = client.post(
        f"/api/v1/applications/{draft.id}/approve",
        json={"recipient": "recruiter@google.com", "subject": "SWE", "body": "Body", "human_confirmed": False}
    )
    assert res_false.status_code == 400

    # 2. Approval fails if recipient is invalid
    res_bad_email = client.post(
        f"/api/v1/applications/{draft.id}/approve",
        json={"recipient": "not-an-email", "subject": "SWE", "body": "Body", "human_confirmed": True}
    )
    assert res_bad_email.status_code == 422

    # 3. Successful human approval
    res_ok = client.post(
        f"/api/v1/applications/{draft.id}/approve",
        json={"recipient": "recruiter@google.com", "subject": "SWE", "body": "Body", "human_confirmed": True}
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["status"] == "HUMAN_APPROVED"


@pytest.mark.asyncio
async def test_idempotent_double_send_prevention(client, monkeypatch):
    repo = JobRepository()

    draft = ApplicationDraft(
        id="app-idem-03",
        candidate_id="cand_idem",
        job_id="job_idem",
        company_name="Meta",
        recipient="jobs@meta.com",
        subject="AI Engineer",
        body="Hello",
        status=ApplicationStatus.SENT,
        gmail_message_id="msg-12345"
    )
    await repo.save_application(draft)

    # Attempting to re-send an already SENT application returns 409 Conflict
    res = client.post(f"/api/v1/applications/{draft.id}/send")
    assert res.status_code == 409
    assert "already sent" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_full_approved_send_mock(client, monkeypatch, tmp_path):
    repo = JobRepository()

    dummy_att = tmp_path / "resume.pdf"
    dummy_att.write_text("Dummy resume")

    draft = ApplicationDraft(
        id="app-mock-04",
        candidate_id="cand_mock",
        job_id="job_mock",
        company_name="OpenAI",
        recipient="careers@openai.com",
        subject="Research Engineer",
        body="Cover letter",
        attachment_path=str(dummy_att),
        status=ApplicationStatus.HUMAN_APPROVED
    )
    await repo.save_application(draft)

    # Mock GmailAuthService.is_connected & GmailService.send_application_email
    monkeypatch.setattr("app.services.gmail_auth.GmailAuthService.is_connected", lambda: True)
    monkeypatch.setattr(
        "app.services.gmail_service.GmailService.send_application_email",
        lambda recipient, subject, body, attachment_path: "gmail-mock-id-777"
    )

    res = client.post(f"/api/v1/applications/{draft.id}/send")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SENT"
    assert data["gmail_message_id"] == "gmail-mock-id-777"

    # Confirm status persisted to DB
    updated = await repo.get_application(draft.id)
    assert updated.status == ApplicationStatus.SENT
    assert updated.gmail_message_id == "gmail-mock-id-777"

    # Confirm audit log was written
    logs = await repo.get_audit_logs(draft.id)
    actions = [l.action for l in logs]
    assert "send_completed" in actions