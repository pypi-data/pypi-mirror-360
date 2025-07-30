from __future__ import annotations
from typing_extensions import Self
from ..proto.release_policy_pb2 import (
    ReleasePolicy,
    ReleasePolicyV0,
    SecretSource,
    SecretStoreSource,
    AllowedComputeContext,
    DcrComputeContext,
)
from ..client import Client

class ReleasePolicyBuilder:
    def __init__(self, client: Client, dcr_id: str, manifest_hash: str):
        """
        Initialise an instance of the ReleasePolicyBuilder.

        **Parameters**:
        - `client`: Client object.
        - `dcr_id`: Unique identifier of the DataRoom.
        - `manifest_hash`: Unique identifier of the dataset for which the policy will be created.
        """
        self.client = client
        self.dcr_id = dcr_id
        self.manifest_hash = manifest_hash
        self.target_leaf_node_name = None

    def with_target_leaf_node_name(self, leaf_node_name: str) -> Self:
        """
        Set the target leaf node name.

        **Parameters**:
        - `leaf_node_name`: Name of the leaf node.
        """
        self.target_leaf_node_name = leaf_node_name
        return self

    def build(self) -> ReleasePolicy:
        """
        Build a release policy.

        **Returns**:
        - `policy_id`: Unique identifier of the release policy.
        """
        secret_id = self.client.get_dataset_encryption_key_secret_id(self.manifest_hash)
        if secret_id is None:
            raise Exception(
                f"Dataset with manifest hash {self.manifest_hash} has no associated secret"
            )

        return ReleasePolicy(
            v0=ReleasePolicyV0(
                secretSource=SecretSource(
                    secretStore=SecretStoreSource(secretId=secret_id),
                ),
                allowedComputeContext=AllowedComputeContext(
                    dcr=DcrComputeContext(
                        dataRoomId=self.dcr_id,
                        targetLeaf=self.target_leaf_node_name,
                    ),
                ),
            ),
        )
