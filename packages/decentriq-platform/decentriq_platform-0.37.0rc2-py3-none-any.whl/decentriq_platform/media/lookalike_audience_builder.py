from __future__ import annotations
from typing import List, Union
from typing_extensions import Self
from .api import SeedAudience, CustomAudience
from .audiences import AudienceType
from .participant import Participant

class LookalikeAudienceDefinition:
    """
    Class representing the definition of a lookalike audience.
    """

    def __init__(
        self,
        *,
        name: str,
        reach: int,
        exclude_seed_audience: bool,
        source_audience: Union[SeedAudience, CustomAudience],
        shared_with: List[Participant],
    ) -> None:
        """
        Initialize a lookalike audience definition.

        **Parameters**:
        - `name`: Name of the lookalike audience
        - `reach`: The desired reach percentage (1-30)
        - `exclude_seed_audience`: Whether to exclude the seed audience
        - `source_audience`: The source audience to build from
        - `shared_with`: List of participant groups to share with
        """
        self.name = name
        self.reach = reach
        self.exclude_seed_audience = exclude_seed_audience
        self.source_audience = source_audience
        self.kind = "LOOKALIKE"
        self.shared_with = [participant.id for participant in shared_with]

class LookalikeAudienceBuilder:
    """
    Builder for constructing lookalike audience definitions.
    """

    def __init__(
        self,
        *,
        name: str,
        reach: int,
        source_audience: AudienceType,
    ) -> None:
        """
        Initialise the lookalike audience builder.

        **Parameters**:
        - `name`: Name of the lookalike audience.
        - `reach`: The desired reach of the lookalike audience expressed as a percentage between 1-30.
        - `source_audience_name`: Name of the source audience that the lookalike audience will be built from.
        """
        if not (0 <= reach <= 30):
            raise Exception(f"Reach value {reach} is not in range 0 to 30")

        self.name = name
        self.reach = reach
        self.source_audience = source_audience
        self.exclude_seed_audience = False
        self.shared_with = []

    def with_exclude_seed_audience(self) -> Self:
        """
        Exclude the seed audience from the lookalike audience.

        **Returns**:
        - The updated lookalike audience builder
        """
        self.exclude_seed_audience = True
        return self

    def with_share_with_participants(self, participants: List[Participant]) -> Self:
        """
        Make the lookalike audience available to the given participants.

        **Parameters**:
        - `participants`: The participants to share the lookalike audience with

        **Returns**:
        - The updated lookalike audience builder
        """
        self.shared_with = participants
        return self

    def build(self) -> LookalikeAudienceDefinition:
        """
        Build the lookalike audience definition.

        **Returns**:
        - The lookalike audience definition
        """
        return LookalikeAudienceDefinition(
            name=self.name,
            reach=self.reach,
            exclude_seed_audience=self.exclude_seed_audience,
            source_audience=self.source_audience,
            shared_with=self.shared_with,
        )
