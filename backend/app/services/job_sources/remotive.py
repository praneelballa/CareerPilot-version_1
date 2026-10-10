import httpx
import re
from typing import List, Tuple
from bs4 import BeautifulSoup
from app.schemas.job import Job, JobSearchFilter, SourceStatus
from app.services.job_sources.base import BaseJobSource
import hashlib


class RemotiveJobSource(BaseJobSource):
    source_name = "remotive"
    API_URL = "https://remotive.com/api/remote-jobs"

    def _strip_html(self, raw_html: str) -> str:
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "lxml")
        return soup.get_text(separator=" ", strip=True)

    def _generate_id(self, source: str, title: str, company: str, app_url: str) -> str:
        raw_key = f"{source}::{company.lower().strip()}::{title.lower().strip()}::{app_url.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    async def search(self, filters: JobSearchFilter) -> Tuple[List[Job], SourceStatus]:
        normalized_jobs: List[Job] = []
        params = {"search": filters.role}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.API_URL, params=params)

            if response.status_code != 200:
                return [], SourceStatus(
                    source_name=self.source_name,
                    status="error",
                    jobs_found=0,
                    message=f"Remotive API returned status {response.status_code}"
                )

            data = response.json()
            raw_jobs = data.get("jobs", [])

            for r_job in raw_jobs:
                title = r_job.get("title", "")
                company = r_job.get("company_name", "Unknown")
                location = r_job.get("candidate_required_location") or "Worldwide / Remote"
                url = r_job.get("url", "")

                # Location filtering if requested
                if filters.location and filters.location.lower() != "remote":
                    loc_target = filters.location.lower()
                    if loc_target not in location.lower() and "worldwide" not in location.lower():
                        continue

                clean_desc = self._strip_html(r_job.get("description", ""))
                tags = r_job.get("tags", [])
                
                # Determine employment type
                raw_type = (r_job.get("job_type") or "").lower()
                emp_type = "full_time" if "full" in raw_type else "contract" if "contract" in raw_type else "other"

                job_id = self._generate_id(self.source_name, title, company, url)

                normalized_jobs.append(Job(
                    job_id=job_id,
                    source=self.source_name,
                    title=title,
                    company=company,
                    location=location,
                    remote_type="remote",
                    employment_type=emp_type,
                    description=clean_desc[:2500],
                    required_skills=tags,
                    preferred_skills=[],
                    salary=r_job.get("salary") or None,
                    posted_date=r_job.get("publication_date"),
                    application_url=url,
                    source_url=url
                ))

                if len(normalized_jobs) >= filters.limit:
                    break

            return normalized_jobs, SourceStatus(
                source_name=self.source_name,
                status="ok" if normalized_jobs else "no_results",
                jobs_found=len(normalized_jobs),
                message=f"Successfully queried Remotive public API. Found {len(normalized_jobs)} jobs."
            )

        except Exception as e:
            return [], SourceStatus(
                source_name=self.source_name,
                status="error",
                jobs_found=0,
                message=f"Failed querying Remotive: {str(e)}"
            )