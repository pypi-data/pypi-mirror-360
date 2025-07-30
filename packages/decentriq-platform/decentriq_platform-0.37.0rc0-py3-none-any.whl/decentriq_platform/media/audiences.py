from typing import List, Union
from .api import SeedAudience, CustomAudience

"""
This module contains classes for managing different types of audiences.
"""

AudienceType = Union[SeedAudience, CustomAudience]


class Audiences:
    """
    Class for managing and accessing different types of audiences.
    """

    def __init__(self, audiences: List[AudienceType]):
        """
        Initialize an Audiences instance.

        **Parameters**:
        - `audiences`: List of audience objects to manage
        """
        self.audiences = audiences

    def list(self) -> List[AudienceType]:
        """
        List all audiences.

        **Returns**:
        - List of all audiences
        """
        return self.audiences

    def get_seed_audience(self, audience_type: str) -> SeedAudience:
        """
        Get a seed audience by type.

        **Parameters**:
        - `audience_type`: Type of the seed audience to retrieve

        **Returns**:
        - Seed audience with the given type

        **Raises**:
        - `Exception`: If no seed audience is found with the given type or multiple seed audiences found with the given type
        """
        seed_audiences = [
            a
            for a in self.audiences
            if isinstance(a, SeedAudience) and a.audienceType == audience_type
        ]
        if len(seed_audiences) == 0:
            raise Exception(f"No seed audience found with type {audience_type}")
        if len(seed_audiences) > 1:
            raise Exception(f"Multiple seed audiences found with type {audience_type}")
        return seed_audiences[0]

    def get_custom_audience(self, name: str) -> CustomAudience:
        """
        Get a custom audience by name.

        **Parameters**:
        - `name`: Name of the custom audience to retrieve

        **Returns**:
        - Custom audience with the given name

        **Raises**:
        - `Exception`: If no custom audience is found or multiple custom audiences found with the given name
        """
        custom_audiences = [
            a
            for a in self.audiences
            if isinstance(a, CustomAudience) and a.name == name
        ]
        if len(custom_audiences) == 0:
            raise Exception(f"No custom audience found with name {name}")
        if len(custom_audiences) > 1:
            raise Exception(f"Multiple custom audiences found with name {name}")
        return custom_audiences[0]

    def is_lookalike_audience(audience: AudienceType) -> bool:
        """
        Check if an audience is a lookalike audience.

        **Parameters**:
        - `audience`: The audience to check

        **Returns**:
        - True if the audience is a lookalike audience, False otherwise

        **Raises**:
        - `Exception`: If the audience type is not supported
        """
        if isinstance(audience, SeedAudience):
            return False
        elif isinstance(audience, CustomAudience):
            return audience.definition.kind == "LOOKALIKE"
        else:
            raise Exception(f"Unsupported audience type: {type(audience)}")
