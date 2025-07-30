import uuid
from typing import Any, Dict, List, Optional
from decentriq_dcr_compiler.schemas import Permission


class Participant:
    """
    A participant in a Data Clean Room.
    """

    def __init__(
        self,
        emails: List[str],
        permissions: List[Permission],
        role: str,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ):
        """
        Initialize a participant.

        **Parameters**:
        - `emails`: The emails of the participant
        - `permissions`: The permissions of the participant
        - `role`: The role of the participant
        - `id`: The id of the participant
        - `organization_id`: The organization id of the participant
        """
        self.id = str(uuid.uuid4()) if id is None else id
        self.role = role
        self.emails = emails
        self.permissions = permissions
        self.organization_id = organization_id

    def as_dict(self) -> Dict[str, Any]:
        """
        Return the participant as a dictionary.

        **Returns**:
        - The participant as a dictionary
        """
        return {
            "id": self.id,
            "role": self.role,
            "emails": self.emails,
            "permissions": [permission.value for permission in self.permissions],
            "organizationId": self.organization_id,
        }
