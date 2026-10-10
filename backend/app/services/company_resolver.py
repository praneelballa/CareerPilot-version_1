import ipaddress
import re
from urllib.parse import urlparse
import tldextract
from typing import Optional
from app.schemas.company import ResolvedDomain


class CompanyResolver:
    # Well-known job boards to ignore when attempting to derive official company domains
    JOB_BOARDS = {
        "linkedin.com", "remotive.com", "internshala.com", "indeed.com",
        "glassdoor.com", "lever.co", "greenhouse.io", "workday.com",
        "smartrecruiters.com", "ziprecruiter.com"
    }

    @classmethod
    def is_safe_url(cls, target_url: str) -> bool:
        """
        Guards against SSRF, loopback, private networks, and invalid protocols.
        """
        try:
            parsed = urlparse(target_url)
            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Check if domain resolves to a private or loopback IP literal
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                    return False
            except ValueError:
                pass  # Hostname is not a raw IP, proceed

            if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
                return False

            return True
        except Exception:
            return False

    @classmethod
    def resolve_from_job(cls, company_name: str, application_url: str, source_url: str) -> ResolvedDomain:
        cleaned_company = company_name.strip()

        # 1. Attempt extracting company domain from application URL (if direct ATS/corporate link)
        for url in [application_url, source_url]:
            if not url or not cls.is_safe_url(url):
                continue

            extracted = tldextract.extract(url)
            registered_domain = f"{extracted.domain}.{extracted.suffix}".lower()

            if registered_domain and registered_domain not in cls.JOB_BOARDS:
                homepage = f"https://www.{registered_domain}"
                return ResolvedDomain(
                    company_name=cleaned_company,
                    official_domain=registered_domain,
                    homepage_url=homepage,
                    confidence=0.85,
                    source_method="extracted_from_apply_url"
                )

        # 2. Canonical domain synthesis for known company entities
        sanitized_slug = re.sub(r"[^a-zA-Z0-9]", "", cleaned_company).lower()
        if sanitized_slug:
            guessed_domain = f"{sanitized_slug}.com"
            return ResolvedDomain(
                company_name=cleaned_company,
                official_domain=guessed_domain,
                homepage_url=f"https://www.{guessed_domain}",
                confidence=0.55,
                source_method="canonical_slug_inference"
            )

        return ResolvedDomain(
            company_name=cleaned_company,
            confidence=0.0,
            source_method="unresolved"
        )