import httpx
import hashlib
from typing import List, Tuple
from bs4 import BeautifulSoup
from app.schemas.job import Job, JobSearchFilter, SourceStatus
from app.services.job_sources.base import BaseJobSource


class InternshalaCompliantSource(BaseJobSource):
    source_name = "internshala"
    BASE_SEARCH_URL = "https://internshala.com/internships"

    def _generate_id(self, source: str, title: str, company: str, app_url: str) -> str:
        raw_key = f"{source}::{company.lower().strip()}::{title.lower().strip()}::{app_url.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    async def search(self, filters: JobSearchFilter) -> Tuple[List[Job], SourceStatus]:
        role_slug = filters.role.lower().replace(" ", "-")
        target_url = f"{self.BASE_SEARCH_URL}/keywords-{role_slug}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(target_url, headers=headers)

            if response.status_code in [403, 503] or "Cloudflare" in response.text:
                return [], SourceStatus(
                    source_name=self.source_name,
                    status="restricted_by_tos_or_waf",
                    jobs_found=0,
                    message="Internshala access protected by Cloudflare anti-bot verification. Request safely bypassed to avoid evading security mechanisms."
                )

            if response.status_code != 200:
                return [], SourceStatus(
                    source_name=self.source_name,
                    status="error",
                    jobs_found=0,
                    message=f"Internshala endpoint returned HTTP {response.status_code}"
                )

            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.find_all("div", class_="individual_internship")
            normalized_jobs: List[Job] = []

            for card in cards:
                title_elem = card.find("h3", class_="job-internship-name") or card.find("a", class_="view_detail_button")
                company_elem = card.find("p", class_="company-name")
                loc_elem = card.find("div", class_="row-1-item locations")

                if not (title_elem and company_elem):
                    continue

                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True)
                loc = loc_elem.get_text(strip=True) if loc_elem else "India"
                relative_url = title_elem.get("href") or ""
                app_url = f"https://internshala.com{relative_url}" if relative_url.startswith("/") else relative_url

                job_id = self._generate_id(self.source_name, title, company, app_url)

                normalized_jobs.append(Job(
                    job_id=job_id,
                    source=self.source_name,
                    title=title,
                    company=company,
                    location=loc,
                    remote_type="remote" if "work from home" in loc.lower() else "on_site",
                    employment_type="internship",
                    description=f"{title} internship at {company}.",
                    required_skills=[],
                    preferred_skills=[],
                    salary=None,
                    posted_date=None,
                    application_url=app_url,
                    source_url=app_url
                ))

                if len(normalized_jobs) >= filters.limit:
                    break

            return normalized_jobs, SourceStatus(
                source_name=self.source_name,
                status="ok" if normalized_jobs else "no_results",
                jobs_found=len(normalized_jobs),
                message=f"Found {len(normalized_jobs)} internship listings from Internshala."
            )

        except Exception as e:
            return [], SourceStatus(
                source_name=self.source_name,
                status="error",
                jobs_found=0,
                message=f"Internshala discovery query skipped: {str(e)}"
            )