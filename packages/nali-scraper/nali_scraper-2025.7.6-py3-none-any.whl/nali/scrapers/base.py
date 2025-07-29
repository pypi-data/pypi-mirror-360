from abc import ABC, abstractmethod
from typing import final
import requests
from bs4 import BeautifulSoup

from ..exceptions import UnsupportedHTTPMethodError
from ..models import Notice


class BaseScraper(ABC):
    HEADERS = {"User-Agent": "Mozilla/5.0 (NaliBot/1.0)"}

    @final
    def fetch_page(self, *, url: str, method: str = "GET", **kwargs) -> BeautifulSoup:
        if method == "GET":
            resp = requests.get(url, headers=self.HEADERS, **kwargs)
        elif method == "POST":
            resp = requests.post(url, headers=self.HEADERS, **kwargs)
        else:
            raise UnsupportedHTTPMethodError("Unsupported HTTP method.")

        resp.raise_for_status()

        return BeautifulSoup(resp.text, "html.parser")

    @abstractmethod
    def scrape(self, page: int, search: str | None = None) -> list[Notice]:
        pass
