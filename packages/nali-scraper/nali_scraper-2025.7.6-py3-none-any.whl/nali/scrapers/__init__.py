from ..enums import School

from .template import TemplateScraper


def get_scraper(school: School):
    scrapers = {
        School.TEMPLATE: TemplateScraper,
        # Add new scraper mappings here
    }

    return scrapers.get(school)()
