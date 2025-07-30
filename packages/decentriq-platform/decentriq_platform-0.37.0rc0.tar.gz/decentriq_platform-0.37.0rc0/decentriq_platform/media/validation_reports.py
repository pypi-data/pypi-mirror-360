import json
from .api import ValidationReport


class ValidationReports:
    """
    A class to represent the validation reports for a DCR.
    """

    def __init__(
        self,
        matching: ValidationReport,
        segments: ValidationReport,
        demographics: ValidationReport,
    ):
        """
        Initialize a ValidationReports instance.

        **Parameters**:
        - `matching`: The matching validation report
        - `segments`: The segments validation report
        - `demographics`: The demographics validation report
        """
        self.formatted_reports = {
            "matching": matching.model_dump(),
            "segments": segments.model_dump(),
            "demographics": demographics.model_dump(),
        }

    def __str__(self):
        """
        Return a JSON string representation of the validation reports.
        """
        return f"{json.dumps(self.formatted_reports, indent=2)}"

    # Added to mimic the behaviour of Pydantic types to provide a
    # consistent interface for the user.
    def model_dump_json(self):
        """
        Return a JSON string representation of the validation reports.
        """
        return json.dumps(self.formatted_reports, indent=2)
