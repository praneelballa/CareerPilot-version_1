import pytest
from app.services.auto_match_service import AutoMatchService
from app.schemas.candidate import CandidateProfile, SkillCategories, Experience


def test_derive_search_keywords_from_profile():
    profile = CandidateProfile(
        candidate_id="cand_test_01",
        name="Alex Turing",
        skills=SkillCategories(
            programming_languages=["Python", "TypeScript"],
            frameworks=["FastAPI", "React"],
            ai_and_ml=["Machine Learning", "RAG"]
        ),
        experience=[
            Experience(company="AI Labs", role="ML Engineer", responsibilities=["Built NLP pipelines"])
        ]
    )

    keywords = AutoMatchService.derive_search_keywords(profile)
    assert "ML Engineer" in keywords
    assert "Machine Learning" in keywords or "Python" in keywords