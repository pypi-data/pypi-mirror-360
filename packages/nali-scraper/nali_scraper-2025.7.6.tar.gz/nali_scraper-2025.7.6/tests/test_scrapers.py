from src.nali import Nali, School, Notice

import pytest


@pytest.mark.parametrize("school", list(School))
def test_scraper_for_school(school, target_school):
    if target_school and school != target_school:
        pytest.skip(f"Skipping {school}, not the target")

    n = Nali(school)
    notices = n.get_notices(page=1)
    assert isinstance(notices, list)
    assert all(isinstance(n, Notice) for n in notices)
