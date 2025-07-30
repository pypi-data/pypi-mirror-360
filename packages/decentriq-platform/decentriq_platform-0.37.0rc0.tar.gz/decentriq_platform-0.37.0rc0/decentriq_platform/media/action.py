"""
This module contains action classes for performing operations in a Media DCR.
"""

from ..client import Client
from ..types import JSONType
from decentriq_dcr_compiler.schemas.data_room import DataRoomAction
from .lookalike_audience_builder import LookalikeAudienceDefinition
from .rule_based_builder import RuleBasedAudienceDefinition
from .remarketing_audience_builder import RemarketingAudienceDefinition
from .api import (
    SeedAudience,
    CustomAudience,
)


class Action:
    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize an Action instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        self.dcr_id = dcr_id
        self.client = client
        self.session = client.create_session_v2()

    def _send_action(self, action: DataRoomAction) -> JSONType:
        """
        Send an action to the driver.

        **Parameters**:
        - `action`: The action to send to the driver

        **Returns**:
        - The response from the driver
        """
        return self.session.send_data_room_state_action_request(
            self.dcr_id, action.model_dump()
        )


class CreateLookalikeAudienceAction(Action):
    def __init__(
        self,
        dcr_id: str,
        client: Client,
        definition: LookalikeAudienceDefinition,
    ):
        """
        Initialize a CreateLookalikeAudienceAction instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        - `definition`: The definition of the lookalike audience to create
        """
        super().__init__(dcr_id, client)
        self.definition = definition

    def create(self) -> JSONType:
        """
        Create the lookalike audience.

        **Returns**:
        - The response from creating the lookalike audience
        """
        if isinstance(self.definition.source_audience, SeedAudience):
            source_ref_definition = {
                "kind": "SEED",
                "audienceType": self.definition.source_audience.audienceType,
            }
        elif isinstance(self.definition.source_audience, CustomAudience):
            source_ref_definition = {
                "id": self.definition.source_audience.id,
                "kind": "CUSTOM",
            }
        else:
            raise Exception(
                f"Invalid source audience type: {type(self.definition.source_audience)}"
            )

        definition = {
            "kind": "media",
            "createCustomAudience": {
                "definition": {
                    "kind": self.definition.kind,
                    "reach": self.definition.reach,
                    "sourceRef": source_ref_definition,
                    "excludeSeedAudience": self.definition.exclude_seed_audience,
                },
                "name": self.definition.name,
                "sharedWith": self.definition.shared_with,
            },
        }
        return self._send_action(DataRoomAction.model_validate(definition))


class CreateRuleBasedAudienceAction(Action):
    def __init__(
        self,
        dcr_id: str,
        client: Client,
        definition: RuleBasedAudienceDefinition,
    ):
        """
        Initialize a CreateRuleBasedAudienceAction instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        - `definition`: The definition of the rule based audience to create
        """
        super().__init__(dcr_id, client)
        self.definition = definition

    def create(self) -> JSONType:
        """
        Create the rule based audience.

        **Returns**:
        - The response from creating the rule based audience
        """
        if isinstance(self.definition.source_audience, SeedAudience):
            source_ref_definition = {
                "kind": "SEED",
                "audienceType": self.definition.source_audience.audienceType,
            }
        elif isinstance(self.definition.source_audience, CustomAudience):
            source_ref_definition = {
                "id": self.definition.source_audience.id,
                "kind": "CUSTOM",
            }
        else:
            raise Exception(
                f"Invalid source audience type: {type(self.definition.source_audience)}"
            )

        definition = {
            "kind": "media",
            "createCustomAudience": {
                "definition": {
                    "combine": (
                        [
                            combinator.as_dict()
                            for combinator in self.definition.combinators
                        ] if self.definition.combinators else None
                    ),
                    "filters": (
                        self.definition.filters.as_dict()
                        if self.definition.filters else None
                    ),
                    "kind": self.definition.kind,
                    "sourceRef": source_ref_definition,
                },
                "name": self.definition.name,
                "sharedWith": self.definition.shared_with,
            },
        }
        return self._send_action(DataRoomAction.model_validate(definition))


class CreateRemarketingAudienceAction(Action):
    def __init__(
        self,
        dcr_id: str,
        client: Client,
        definition: RemarketingAudienceDefinition,
    ):
        """
        Initialize a CreateRemarketingAudienceAction instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        - `definition`: The definition of the remarketing audience to create
        """
        super().__init__(dcr_id, client)
        self.definition = definition

    def create(self) -> JSONType:
        """
        Create the remarketing audience.

        **Returns**:
        - The response from creating the remarketing audience
        """
        source_ref_definition = {
            "audienceType": self.definition.source_audience_type,
        }

        definition = {
            "kind": "media",
            "createCustomAudience": {
                "definition": {
                    "kind": self.definition.kind,
                    "seedAudienceRef": source_ref_definition,
                },
                "name": self.definition.name,
                "sharedWith": self.definition.shared_with,
            },
        }
        return self._send_action(DataRoomAction.model_validate(definition))


class UpdateCustomAudienceAction(Action):
    def __init__(
        self,
        dcr_id: str,
        client: Client,
        audience: CustomAudience,
    ):
        """
        Initialize an UpdateCustomAudienceAction instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        - `audience`: The audience to update
        """
        super().__init__(dcr_id, client)
        self.audience = audience

    def update(self) -> JSONType:
        """
        Update the custom audience.

        **Returns**:
        - The response from updating the custom audience
        """
        definition = {
            "kind": "media",
            "updateCustomAudience": {
                "audienceId": self.audience.id,
                "definition": self.audience.definition.model_dump(),
                "name": self.audience.name,
                "sharedWith": self.audience.sharedWith,
            },
        }
        return self._send_action(DataRoomAction.model_validate(definition))


class GetAudiencePrerequisitesAction(Action):
    def __init__(self, dcr_id: str, client: Client, audience: CustomAudience):
        super().__init__(dcr_id, client)
        self.audience = audience

    def get(self) -> JSONType:
        definition = {
            "kind": "media",
            "getAudiencePrerequisites": {"audienceId": self.audience.id},
        }
        return self._send_action(DataRoomAction.model_validate(definition))


class DeleteCustomAudienceAction(Action):
    def __init__(
        self,
        dcr_id: str,
        client: Client,
        audience_id: str,
        force_delete_prerequisites: bool,
    ):
        """
        Initialize a DeleteCustomAudienceAction instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        - `audience_id`: The identifier for the audience to delete
        - `force_delete_prerequisites`: If true, the audience and all dependent audiences will be deleted. If false, the audience will only be deleted if it has no dependents.
        """
        super().__init__(dcr_id, client)
        self.audience_id = audience_id
        self.force_delete_prerequisites = force_delete_prerequisites

    def delete(self) -> JSONType:
        definition = {
            "kind": "media",
            "deleteCustomAudience": {
                "audienceId": self.audience_id,
                "forceDeletePrerequisites": self.force_delete_prerequisites,
            },
        }
        return self._send_action(DataRoomAction.model_validate(definition))
