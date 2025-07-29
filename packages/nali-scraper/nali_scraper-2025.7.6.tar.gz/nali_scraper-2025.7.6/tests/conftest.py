import pytest
from src.nali.enums import School


def pytest_addoption(parser):
    parser.addoption(
        "--school",
        action="store",
        default=None,
        help="Test a specific school scraper (e.g. --school=SEOUL)"
    )


@pytest.fixture
def target_school(request):
    val = request.config.getoption("--school")
    if val is not None:
        try:
            return School[val.upper()]
        except KeyError:
            raise pytest.UsageError(f"Invalid school name: {val}")
    return None
