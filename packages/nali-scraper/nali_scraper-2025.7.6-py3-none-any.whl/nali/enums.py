from enum import Enum

from .exceptions import InvalidSchoolError


class School(Enum):
    TEMPLATE = "template"

    # Add more universities here, e.g., HANSUNG = "hansung"

    @classmethod
    def validate(cls, school):
        if not isinstance(school, cls):
            raise InvalidSchoolError(f"Invalid school. Must be one of: {[s.value for s in cls]}")
