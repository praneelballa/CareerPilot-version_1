import pytest
from app.schemas.job import Job, JobSearchFilter, SourceStatus
from app.services.job_deduplicator import JobDeduplicator
from app.services.job_sources.remotive import RemotiveJobSource


def test_job_deduplication():
    job1 = Job(
        job_id="1",
        source="remotive",
        title="ML Engineer",
        company="Anthropic",
        location="Remote",
        description="Build models",
        application_url="https://company.com/apply/1",
        source_url="https://company.com/jobs/1"
    )
    job2 = Job(
        job_id="2",
        source="linkedin",
        title="ml engineer", # duplicate case variation
        company="Anthropic",
        location="San Francisco",
        description="Duplicate position",
        application_url="https://company.com/apply/1", # Identical apply URL
        source_url="https://linkedin.com/jobs/view/2"
    )
    job3 = Job(
        job_id="3",
        source="remotive",
        title="Backend Engineer",
        company="Google",
        location="Remote",
        description="Different job",
        application_url="https://google.com/apply/3",
        source_url="https://google.com/jobs/3"
    )

    deduped = JobDeduplicator.deduplicate([job1, job2, job3])
    assert len(deduped) == 2
    assert deduped[0].company == "Anthropic"
    assert deduped[1].company == "Google"


@pytest.mark.asyncio
async def test_remotive_normalization_fixture(monkeypatch):
    source = RemotiveJobSource()

    # Mock HTTP response to avoid external network dependency in automated unit tests
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "jobs": [
                    {
                        "id": 1234,
                        "url": "https://remotive.com/job/1234",
                        "title": "Python AI Backend Engineer",
                        "company_name": "DeepMind",
                        "candidate_required_location": "Worldwide",
                        "job_type": "full_time",
                        "publication_date": "2026-03-01T12:00:00",
                        "tags": ["Python", "FastAPI", "PyTorch"],
                        "description": "<p>We are seeking an <b>AI Engineer</b>.</p>",
                        "salary": "$120k - $140k"
                    }
                ]
            }

    async def mock_get(*args, **kwargs):
        return MockResponse()

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    filters = JobSearchFilter(role="Python AI", location="Worldwide")
    jobs, status_log = await source.search(filters)

    assert status_log.status == "ok"
    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Python AI Backend Engineer"
    assert job.company == "DeepMind"
    assert "<b>" not in job.description
    assert "FastAPI" in job.required_skills
    assert job.salary == "$120k - $140k"


def test_api_search_endpoint(client):
    response = client.post("/api/v1/jobs/search", json={"role": "Software Engineer", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "total_found" in data
    assert "source_statuses" in data
    assert isinstance(data["jobs"], list)