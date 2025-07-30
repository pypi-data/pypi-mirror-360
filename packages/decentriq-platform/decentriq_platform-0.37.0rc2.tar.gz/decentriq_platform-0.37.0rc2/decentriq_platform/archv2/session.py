from __future__ import annotations
import json
from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    cast
)

from ..types import JSONType
from ..connection import Connection
from ..channel import EnclaveError
from ..proto import (
    GcgRequestV2,
    AuthenticatedRequest,
    AuthenticatedResponse,
    DcrActionRequest,
    CreatePolicyRequest,
    CreatePolicyResponse,
    ExportResultAsDatasetRequest,
    RawExport,
    RetrieveResultEncryptionKeyRequest,
    RetrieveResultEncryptionKeyResponse,
    ReleasePolicy,
    GetVerificationKeyRequest,
)
from ..proto.secret_store_pb2 import (
    SecretStoreEntry,
    SecretStoreRequest,
    SecretStoreResponse,
    GetSecretRequest,
    RemoveSecretRequest,
    CreateSecretRequest,
    UpdateSecretAclRequest,
)
from .secret import Secret

from decentriq_dcr_compiler.schemas.secret_store_entry_state import SecretStoreEntryState, SECRET_STORE_ENTRY_STATE_VERSION, v0
from decentriq_dcr_compiler.schemas.data_room import DataRoomAction as DataRoomActionSchema

if TYPE_CHECKING:
    from ..client import Client

__all__ = [
    "SessionV2",
]

class SessionV2:
    """
    Class for managing the communication with an enclave.
    """

    client: Client
    connection: Connection
    keypair: Any

    def __init__(
        self,
        client: Client,
        connection: Connection,
    ):
        """
        `Session` instances should not be instantiated directly but rather
         be created using a `Client` object using  `decentriq_platform.Client.create_session_v2`.
        """
        self.client = client
        self.connection = connection

    def send_authenticated_request(
        self,
        authenticated_request: AuthenticatedRequest,
    ) -> AuthenticatedResponse:
        authenticated_request.apiToken = self.client.enclave_api_token
        request = GcgRequestV2(authenticated=authenticated_request)
        response = self.connection.send_request_v2(request)
        if response.HasField("failure"):
            raise EnclaveError(response.failure)
        successful_response = response.success
        if not successful_response.HasField("authenticated"):
            raise Exception(
                "Expected `authenticated` response, got "
                + str(successful_response.WhichOneof("response"))
            )
        authenticated_response = response.success.authenticated
        return authenticated_response

    def send_secret_store_request(
        self,
        request: SecretStoreRequest,
    ) -> SecretStoreResponse:
        authenticated_request = AuthenticatedRequest(secretStore=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("secretStore"):
            raise Exception(
                f"Expected `secretStore` response, got "
                + str(response.WhichOneof("response"))
            )
        secret_store_response = cast(SecretStoreResponse, response.secretStore)
        return secret_store_response

    def remove_secret(self, secret_id: str, expected_cas_index: int) -> bool:
        request = SecretStoreRequest(
            removeSecret=RemoveSecretRequest(
                id=secret_id,
                expectedCasIndex=expected_cas_index,
            )
        )
        secret_store_response = self.send_secret_store_request(request)
        if not secret_store_response.HasField("removeSecret"):
            raise Exception(
                f"Expected `removeSecret`, got "
                + str(secret_store_response.WhichOneof("response"))
            )
        return secret_store_response.removeSecret.removed

    def get_secret(self, secret_id: str) -> Tuple[Secret, int]:
        request = SecretStoreRequest(
            getSecret=GetSecretRequest(
                id=secret_id,
                version=SECRET_STORE_ENTRY_STATE_VERSION
            )
        )
        secret_store_response = self.send_secret_store_request(request)
        if not secret_store_response.HasField("getSecret"):
            raise Exception(
                f"Expected `getSecret`, got "
                + str(secret_store_response.WhichOneof("response"))
            )
        get_secret_response = secret_store_response.getSecret
        if not get_secret_response.HasField("secret"):
            raise Exception(
                f"Expected `secret` in `getSecret` response, got "
                + str(get_secret_response)
            )
        else:
            entry_state = SecretStoreEntryState.model_validate_json(get_secret_response.secret.state)
            return Secret(get_secret_response.secret.content, entry_state),  get_secret_response.casIndex

    def create_secret(self, secret: Secret) -> str:
        """Store a secret in the user's own enclave-protected secret store"""
        request = SecretStoreRequest(
            createSecret=CreateSecretRequest(
                secret=SecretStoreEntry(
                    content=secret.secret,
                    state=secret.state.model_dump_json().encode("utf-8")
                )
            )
        )
        secret_store_response = self.send_secret_store_request(request)
        if not secret_store_response.HasField("createSecret"):
            raise Exception(
                f"Expected `setSecret`, got "
                + str(secret_store_response.WhichOneof("response"))
            )
        return secret_store_response.createSecret.id

    def get_dataset_secret_id(self, manifest_hash: str) -> str:
        pass

    def update_secret_acl(self, secret_id: str, new_acl: v0.SecretStoreEntryAcl, expected_cas_index: int) -> bool:
        """Update a secret ACL"""
        request = SecretStoreRequest(
            updateSecretAcl=UpdateSecretAclRequest(
                id=secret_id,
                newAcl=new_acl.model_dump_json().encode("utf-8"),
                version=SECRET_STORE_ENTRY_STATE_VERSION,
                expectedCasIndex=expected_cas_index
            )
        )
        secret_store_response = self.send_secret_store_request(request)
        if not secret_store_response.HasField("updateSecretAcl"):
            raise Exception(
                f"Expected `updatedSecretAcl`, got "
                + str(secret_store_response.WhichOneof("response"))
            )
        return secret_store_response.updateSecretAcl.updated

    def create_policy(self, policy: ReleasePolicy) -> str:
        """Create a release policy and return the policy ID."""
        scope_id = self.client._ensure_dataset_scope()
        scope_id_bytes = bytes.fromhex(scope_id)

        request = CreatePolicyRequest(
            policy=policy,
            scope=scope_id_bytes
        )
        authenticated_request = AuthenticatedRequest(createPolicy=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("createPolicy"):
            raise Exception(
                f"Expected `createPolicy` response, got "
                + str(response.WhichOneof("response"))
            )
        return response.createPolicy.policyId

    def send_data_room_state_action_request(self, data_room_id: str, action: JSONType) -> JSONType:
        """Send a DCR action request."""
        validated_action = DataRoomActionSchema.model_validate(action)
        request = DcrActionRequest(
            dataRoomId=data_room_id,
            action=validated_action.model_dump_json().encode("utf-8")
        )
        authenticated_request = AuthenticatedRequest(dcrAction=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("dcrAction"):
            raise Exception(
                f"Expected `dcrAction` response, got "
                + str(response.WhichOneof("response"))
            )
        return json.loads(response.dcrAction.response)

    def send_retrieve_result_encryption_key_request(self, job_id: str, task_result_hash: str) -> Tuple[str, bytes]:
        """Retrieve the manifest hash and encryption key for a result."""
        request = RetrieveResultEncryptionKeyRequest(
            jobId=job_id,
            taskResultHashHex=task_result_hash
        )
        authenticated_request = AuthenticatedRequest(retrieveResultEncryptionKey=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("retrieveResultEncryptionKey"):
            raise Exception(
                f"Expected `retrieveResultEncryptionKey` response, got "
                + str(response.WhichOneof("response"))
            )
        return response.retrieveResultEncryptionKey.manifestHashHex, response.retrieveResultEncryptionKey.encryptionKey

    def send_export_result_as_dataset_request(self, job_id: str, task_result_hash: str, zip_path: Optional[str]) -> Tuple[str, str, str]:
        """Export a result as a dataset."""
        request = ExportResultAsDatasetRequest(
            jobId=job_id,
            taskResultHashHex=task_result_hash,
            raw=RawExport()
        )
        if zip_path is not None:
            request.zip.path = zip_path
        authenticated_request = AuthenticatedRequest(exportResultAsDataset=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("exportResultAsDataset"):
            raise Exception(
                f"Expected `exportResultAsDataset` response, got "
                + str(response.WhichOneof("response"))
            )
        return response.exportResultAsDataset.manifestHashHex, response.exportResultAsDataset.secretId, response.exportResultAsDataset.datasetId

    def send_get_verification_key_request(self) -> bytes:
        """Retrieve the verification key for a DCR."""
        request = GetVerificationKeyRequest()
        authenticated_request = AuthenticatedRequest(getVerificationKey=request)
        response = self.send_authenticated_request(authenticated_request)
        if not response.HasField("getVerificationKey"):
            raise Exception(
                f"Expected `getVerificationKey` response, got "
                + str(response.WhichOneof("response"))
            )
        return response.getVerificationKey.verificationKey
