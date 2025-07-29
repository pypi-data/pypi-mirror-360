from .enums import School
from .exceptions import ScrapingError
from .scrapers import get_scraper
from .models import Notice


class Nali:
    def __init__(self, school: School):
        School.validate(school)
        self.school = school
        self.__scraper = get_scraper(school)

    def get_notices(self, *, page: int = 1, search: str | None = None) -> list[Notice]:
        try:
            return self.__scraper.scrape(page, search)
        except Exception as e:
            raise ScrapingError(f"Failed to scrape notices: {str(e)}")
