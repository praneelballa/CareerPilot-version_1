import httpx
import hashlib
from typing import List, Tuple
from bs4 import BeautifulSoup
from app.schemas.job import Job, JobSearchFilter, SourceStatus
from app.services.job_sources.base import BaseJobSource


class LinkedInCompliantSource(BaseJobSource):
    source_name = "linkedin"
    PUBLIC_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def _generate_id(self, source: str, title: str, company: str, app_url: str) -> str:
        raw_key = f"{source}::{company.lower().strip()}::{title.lower().strip()}::{app_url.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    async def search(self, filters: JobSearchFilter) -> Tuple[List[Job], SourceStatus]:
        params = {
            "keywords": filters.role,
            "location": filters.location or "",
            "start": 0
        }
        
        # Standard browser headers for public endpoints without bypassing WAF
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self.PUBLIC_SEARCH_URL, params=params, headers=headers)

            # If LinkedIn challenges the request or blocks it (429, 999, 403, 302 login redirect)
            if response.status_code in [429, 999, 403] or "authwall" in str(response.url):
                return [], SourceStatus(
                    source_name=self.source_name,
                    status="restricted_by_tos_or_waf",
                    jobs_found=0,
                    message="LinkedIn public endpoint presented an anti-bot/login challenge. Automated scraping was stopped to comply with ToS. Official LinkedIn Talent API keys required for direct feed access."
                )

            if response.status_code != 200:
                return [], SourceStatus(
                    source_name=self.source_name,
                    status="restricted_by_tos_or_waf",
                    jobs_found=0,
                    message=f"LinkedIn guest endpoint returned HTTP {response.status_code}."
                )

            soup = BeautifulSoup(response.text, "lxml")
            job_cards = soup.find_all("li")
            normalized_jobs: List[Job] = []

            for card in job_cards:
                title_elem = card.find("h3", class_="base-search-card__title")
                company_elem = card.find("h4", class_="base-search-card__subtitle")
                location_elem = card.find("span", class_="job-search-card__location")
                link_elem = card.find("a", class_="base-card__full-link")

                if not (title_elem and company_elem and link_elem):
                    continue

                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True)
                loc = location_elem.get_text(strip=True) if location_elem else "Not Specified"
                url = link_elem.get("href", "").split("?")[0]

                job_id = self._generate_id(self.source_name, title, company, url)

                normalized_jobs.append(Job(
                    job_id=job_id,
                    source=self.source_name,
                    title=title,
                    company=company,
                    location=loc,
                    remote_type="remote" if "remote" in loc.lower() or "remote" in title.lower() else "on_site",
                    employment_type="full_time",
                    description=f"Job opportunity for {title} at {company} located in {loc}.",
                    required_skills=[],
                    preferred_skills=[],
                    salary=None,
                    posted_date=None,
                    application_url=url,
                    source_url=url
                ))

                if len(normalized_jobs) >= filters.limit:
                    break

            return normalized_jobs, SourceStatus(
                source_name=self.source_name,
                status="ok" if normalized_jobs else "no_results",
                jobs_found=len(normalized_jobs),
                message=f"Parsed {len(normalized_jobs)} jobs from LinkedIn guest endpoint."
            )

        except Exception as e:
            return [], SourceStatus(
                source_name=self.source_name,
                status="error",
                jobs_found=0,
                message=f"LinkedIn discovery safely halted: {str(e)}"
            )