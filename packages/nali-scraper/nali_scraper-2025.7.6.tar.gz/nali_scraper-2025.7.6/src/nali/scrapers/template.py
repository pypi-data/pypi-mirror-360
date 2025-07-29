from datetime import datetime

from .base import BaseScraper
from ..exceptions import ScrapingError
from ..models import Notice


class TemplateScraper(BaseScraper):
    def scrape(self, page: int, search: str | None = None) -> list[Notice]:
        url = "https://example.com"

        soup = self.fetch_page(url=url)

        title = soup.find("title").text.strip()
        content = soup.find("p").text.strip()

        return [
            Notice(
                id=1,
                title=title,
                content=content,
                author="EXAMPLE",
                url="https://example.com",
                date=datetime.now()
            )
        ]
