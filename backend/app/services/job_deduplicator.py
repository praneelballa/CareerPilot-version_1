from typing import List, Set
from app.schemas.job import Job


class JobDeduplicator:
    @staticmethod
    def deduplicate(jobs: List[Job]) -> List[Job]:
        seen_keys: Set[str] = set()
        unique_jobs: List[Job] = []

        for job in jobs:
            # Composite primary deduplication key: normalized company + normalized title + primary url
            comp_norm = "".join(filter(str.isalnum, job.company.lower()))
            title_norm = "".join(filter(str.isalnum, job.title.lower()))
            url_norm = job.application_url.rstrip("/").split("?")[0]

            primary_fingerprint = f"{comp_norm}::{title_norm}"
            url_fingerprint = url_norm if len(url_norm) > 10 else primary_fingerprint

            if primary_fingerprint in seen_keys or url_fingerprint in seen_keys:
                continue

            seen_keys.add(primary_fingerprint)
            seen_keys.add(url_fingerprint)
            unique_jobs.append(job)

        return unique_jobs