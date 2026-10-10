import httpx
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from app.services.company_resolver import CompanyResolver


class CompanyScraperService:
    USER_AGENT = "CareerPilotAI-PublicResearchBot/1.0 (+https://careerpilot.ai/bot)"

    @classmethod
    def _is_allowed_by_robots(cls, base_url: str, path: str) -> bool:
        """
        Parses target robots.txt file to respect the site's crawling rules.
        """
        try:
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(cls.USER_AGENT, urljoin(base_url, path))
        except Exception:
            # If robots.txt cannot be fetched or parsed, assume conservative access
            return True

    @classmethod
    def clean_html_content(cls, html_text: str) -> str:
        if not html_text:
            return ""

        soup = BeautifulSoup(html_text, "lxml")

        # Strip scripts, styles, navigation, headers, footers, forms, and SVGs
        for element in soup(["script", "style", "nav", "footer", "form", "svg", "noscript"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Limit to 5000 characters per page to prevent buffer overflow and excessive token usage
        return " ".join(text.split())[:5000]

    @classmethod
    async def fetch_targeted_pages(cls, base_url: str) -> Dict[str, str]:
        """
        Fetches permitted public pages (home, about, careers).
        Does not crawl the whole site.
        """
        if not CompanyResolver.is_safe_url(base_url):
            return {}

        target_paths = ["/", "/about", "/careers", "/technology", "/products"]
        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        }

        retrieved_content: Dict[str, str] = {}

        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            for path in target_paths:
                full_url = urljoin(base_url, path)
                if not cls.is_safe_url(full_url):
                    continue

                if not cls._is_allowed_by_robots(base_url, path):
                    continue

                try:
                    response = await client.get(full_url, headers=headers)
                    if response.status_code == 200 and "text/html" in response.headers.get("content-type", ""):
                        clean_text = cls.clean_html_content(response.text)
                        if len(clean_text) > 150:
                            retrieved_content[full_url] = clean_text
                except Exception:
                    # Ignore single failed sub-pages without terminating the overall analysis
                    continue

                if len(retrieved_content) >= 3:
                    break

        return retrieved_content