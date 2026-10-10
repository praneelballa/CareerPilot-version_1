import pytest
from app.schemas.application import (
    ApplicationDraft,
    ApplicationStatus,
    ResumeSuggestion,
    SuggestionCategory,
    ResumeVersion
)
from app.services.job_repository import JobRepository


def test_resume_suggestion_skill_gap_handling():
    # If candidate lacks PyTorch, is_skill_gap must be True
    gap_suggestion = ResumeSuggestion(
        id="sug-1",
        category=SuggestionCategory.SKILL_GAP,
        original_text="Proficient in Python and scikit-learn",
        suggested_text="PyTorch appears to be a target requirement.",
        reason="No PyTorch evidence detected in candidate profile.",
        is_skill_gap=True,
        selected=False
    )
    assert gap_suggestion.is_skill_gap is True
    assert gap_suggestion.category == SuggestionCategory.SKILL_GAP


@pytest.mark.asyncio
async def test_resume_versioning_chain():
    repo = JobRepository()

    v1 = ResumeVersion(
        version_id="res-v1-001",
        candidate_id="cand_test",
        parent_version_id=None,
        job_id="job_test",
        version_number=1,
        applied_suggestion_ids=["sug-1"],
        tailored_summary="Base tailored resume",
        modified_bullets=["Enhanced high throughput pipeline metrics"]
    )
    await repo.save_resume_version(v1)

    v2 = ResumeVersion(
        version_id="res-v2-002",
        candidate_id="cand_test",
        parent_version_id=v1.version_id,
        job_id="job_test",
        version_number=2,
        applied_suggestion_ids=["sug-2"],
        tailored_summary="Second iteration",
        modified_bullets=["Added distributed Redis caching architecture"]
    )
    await repo.save_resume_version(v2)

    retrieved = await repo.get_resume_version("res-v2-002")
    assert retrieved is not None
    assert retrieved.parent_version_id == "res-v1-001"
    assert retrieved.version_number == 2


@pytest.mark.asyncio
async def test_application_approval_state():
    repo = JobRepository()

    draft = ApplicationDraft(
        id="app-test-99",
        candidate_id="cand_test",
        job_id="job_test",
        company_name="Stripe",
        subject="Backend Engineering Application - Alex Turing",
        body="Dear Hiring Team...",
        attachment_path="C:/fake/path/resume.pdf",
        status=ApplicationStatus.DRAFT
    )
    await repo.save_application(draft)

    loaded = await repo.get_application("app-test-99")
    assert loaded.status == ApplicationStatus.DRAFT

    # Transition to HUMAN_APPROVED
    loaded.status = ApplicationStatus.HUMAN_APPROVED
    await repo.save_application(loaded)

    re_loaded = await repo.get_application("app-test-99")
    assert re_loaded.status == ApplicationStatus.HUMAN_APPROVED