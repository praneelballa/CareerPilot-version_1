import pytest
from app.services.embedding_service import EmbeddingService
from app.services.matcher import DeterministicMatcher
from app.schemas.candidate import CandidateProfile, SkillCategories
from app.schemas.job import Job


def test_embedding_generation_and_cosine():
    text1 = "Deep learning and computer vision engineer specializing in PyTorch."
    text2 = "Machine learning specialist working on image classification and deep neural nets."
    text3 = "Corporate certified public accountant specializing in international tax audits."

    sim_high = EmbeddingService.compute_similarity(text1, text2)
    sim_low = EmbeddingService.compute_similarity(text1, text3)

    assert 0.0 <= sim_high <= 1.0
    assert 0.0 <= sim_low <= 1.0
    # Technical relevance assertion
    assert sim_high > sim_low


def test_deterministic_matcher_calculation():
    profile = CandidateProfile(
        candidate_id="cand_1",
        name="Alex Turing",
        location="Remote",
        skills=SkillCategories(
            programming_languages=["Python", "Go"],
            frameworks=["FastAPI"],
            cloud_and_tools=["Docker"]
        )
    )

    job = Job(
        job_id="job_1",
        source="remotive",
        title="Python Backend Engineer",
        company="ComputeCorp",
        location="Worldwide",
        remote_type="remote",
        description="We need a Python developer who knows FastAPI and Kubernetes.",
        required_skills=["Python", "FastAPI", "Kubernetes"],
        application_url="https://apply.com",
        source_url="https://apply.com"
    )

    metrics, matched, missing = DeterministicMatcher.compute_metrics(profile, job)

    assert "Python" in matched
    assert "FastAPI" in matched
    assert "Kubernetes" in missing
    assert round(metrics.skill_coverage, 2) == 0.67
    assert metrics.location_alignment == 1.0
    assert metrics.composite_score > 50.0
    assert "Composite =" in metrics.calculation_basis