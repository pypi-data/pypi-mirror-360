from __future__ import annotations
from typing import List
from typing_extensions import Self
from .participant import Participant


class RemarketingAudienceDefinition:
    """
    Class representing the definition of a remarketing audience.
    """

    def __init__(
        self,
        *,
        name: str,
        source_audience_type: str,
        shared_with: List[Participant],
    ) -> None:
        """
        Initialize a remarketing audience definition.

        **Parameters**:
        - `name`: Name of the remarketing audience
        - `source_audience_type`: The audience type of the seed audience to build from
        - `shared_with`: List of participant groups to share with
        """
        self.name = name
        self.source_audience_type = source_audience_type
        self.kind = "REMARKETING"
        self.shared_with = [participant.id for participant in shared_with]


class RemarketingAudienceBuilder:
    """
    Builder for constructing remarketing audience definitions.
    """

    def __init__(
        self,
        *,
        name: str,
        source_audience_type: str,
    ) -> None:
        """
        Initialise the remarketing audience builder.

        **Parameters**:
        - `name`: Name of the remarketing audience.
        - `source_audience_type`: The audience type of the seed audience that the remarketing audience will be built from.
        """
        self.name = name
        self.source_audience_type = source_audience_type
        self.shared_with = []

    def with_share_with_participants(self, participants: List[Participant]) -> Self:
        """
        Make the remarketing audience available to the given participants.

        **Parameters**:
        - `participants`: The participants to share the remarketing audience with

        **Returns**:
        - The updated remarketing audience builder
        """
        self.shared_with = participants
        return self

    def build(self) -> RemarketingAudienceDefinition:
        """
        Build the remarketing audience definition.

        **Returns**:
        - The remarketing audience definition
        """
        return RemarketingAudienceDefinition(
            name=self.name,
            source_audience_type=self.source_audience_type,
            shared_with=self.shared_with,
        )
