import asyncio
from typing import List, Tuple
from app.schemas.job import Job, JobSearchFilter, JobSearchResponse, SourceStatus
from app.services.job_sources.remotive import RemotiveJobSource
from app.services.job_sources.linkedin import LinkedInCompliantSource
from app.services.job_sources.internshala import InternshalaCompliantSource
from app.services.job_deduplicator import JobDeduplicator
from app.services.job_repository import JobRepository


class JobDiscoveryService:
    def __init__(self):
        self.sources = [
            RemotiveJobSource(),
            LinkedInCompliantSource(),
            InternshalaCompliantSource()
        ]
        self.repository = JobRepository()

    async def discover_jobs(self, filters: JobSearchFilter) -> JobSearchResponse:
        # Run source adapters concurrently
        tasks = [source.search(filters) for source in self.sources]
        results: List[Tuple[List[Job], SourceStatus]] = await asyncio.gather(*tasks, return_exceptions=False)

        aggregated_jobs: List[Job] = []
        source_statuses: List[SourceStatus] = []

        for jobs, status in results:
            aggregated_jobs.extend(jobs)
            source_statuses.append(status)

        # Normalization and Deduplication
        unique_jobs = JobDeduplicator.deduplicate(aggregated_jobs)

        # Persistence
        if unique_jobs:
            await self.repository.save_jobs(unique_jobs)

        return JobSearchResponse(
            total_found=len(unique_jobs),
            jobs=unique_jobs,
            source_statuses=source_statuses
        )