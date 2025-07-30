from enum import Enum
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from typing import Literal, TypedDict, Dict, List, Union

from ..types import JSONType
from ..api import Api, Endpoints

from decentriq_dcr_compiler.schemas.data_room import (
    DataRoomComputeAction as DataRoomComputeActionSchema,
    AuditLogLine,
)

class SignedContent(TypedDict):
    id: str
    content: str
    signatureHex: str
    version: int
    casIndex: int

class DataRoom(TypedDict):
    id: str
    ownerId: str
    isStopped: bool
    signedContent: SignedContent


class Action(TypedDict):
    id: str
    data_room_id: str
    jobs: List[str]


class Job(TypedDict):
    id: str


class TaskView(TypedDict):
    name: str
    results: Dict[str, str]
    dependencies: List[str]
    completed: List[str]


class JobTasksView(TypedDict):
    tasks: Dict[str, TaskView]
    target_task: str


class JobStatus(str, Enum):
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"


class JobStatusView(TypedDict):
    status: JobStatus
    registered_at: str
    completed_at: str

class DataRoomAuditLogUnverified(TypedDict):
    signed_content: SignedContent


class DataRoomAuditLog(TypedDict):
    logs: List[AuditLogLine]


class DataRoomActionSummary(TypedDict):
    action: str
    jobs: List[str]


class DataRoomActionsView(TypedDict):
    actions: Dict[str, DataRoomActionSummary]


class DataLabCompatibilityResponse(TypedDict):
    errorsByDataLab: Dict[str, List[str]]

class PolicyStatus(str, Enum):
    OK = "ok"
    NOT_FOUND = "not_found"
    NOT_PROVISIONED = "not_provisioned"

class PolicyNotFound(TypedDict):
    status: Literal[PolicyStatus.NOT_FOUND]

class PolicyNotProvisioned(TypedDict):
    status: Literal[PolicyStatus.NOT_PROVISIONED]

class PolicyMetadata(TypedDict):
    status: Literal[PolicyStatus.OK]
    manifest_hash_hex: str
    target_leaf: str

Policy = Union[PolicyNotFound, PolicyNotProvisioned, PolicyMetadata]


class ClientV2:
    def __init__(self, api: Api):
        self.api = api

    """
    Data Room API
    """

    def create_data_room(
        self, create_data_room: JSONType, verification_key: bytes
    ) -> DataRoom:
        body = {"payload": json.dumps(create_data_room)}
        response = self.api.post(
            endpoint=Endpoints.DATA_ROOMS_COLLECTION,
            req_body=json.dumps(body),
            headers={"Content-type": "application/json"},
        )
        if response.status_code == 201 and "Location" in response.headers:
            location = response.headers["Location"]
            data_room_id = location.split("/")[-1]
            return self.get_data_room(data_room_id, verification_key)
        else:
            raise Exception(
                f"Failed to create data room: {response.status_code} {response.text}"
            )

    def get_data_room(self, data_room_id: str, verification_key: bytes) -> DataRoom:
        endpoint = Endpoints.DATA_ROOM.replace(":data_room_id", data_room_id)
        unverified_data_room: DataRoom = self.api.get(
            endpoint=endpoint,
        ).json()
        return self._verify_data_room(unverified_data_room, verification_key)

    def _verify_data_room(
        self, unverified_data_room: DataRoom, verification_key: bytes
    ) -> DataRoom:
        verified_signed_content = self._get_verified_signed_content(
            unverified_data_room["id"],
            "dcr_state",
            unverified_data_room["signedContent"],
            verification_key,
        )
        verified_data_room = unverified_data_room
        verified_data_room["signedContent"]["content"] = verified_signed_content["content"]
        return verified_data_room

    def get_data_room_audit_log(
        self, data_room_id: str, verification_key: bytes
    ) -> DataRoomAuditLog:
        endpoint = Endpoints.DATA_ROOM_AUDIT_LOG.replace(":data_room_id", data_room_id)
        response: DataRoomAuditLogUnverified = self.api.get(
            endpoint=endpoint,
        ).json()
        verified_audit_log = self._verify_audit_log(
            data_room_id, response, verification_key
        )
        return verified_audit_log

    def _verify_audit_log(
        self,
        dcr_id: str,
        unverified_audit_log: DataRoomAuditLogUnverified,
        verification_key: bytes,
    ) -> DataRoomAuditLog:
        signed_content = self._get_verified_signed_content(
            dcr_id,
            "dcr_audit_log",
            unverified_audit_log["signed_content"],
            verification_key,
        )
        content = json.loads(signed_content["content"])
        return DataRoomAuditLog(logs=[AuditLogLine.model_validate(c) for c in content])

    def _get_verified_signed_content(
        self,
        dcr_id: str,
        content_type: str,
        signed_content: SignedContent,
        verification_key: bytes,
    ) -> SignedContent:
        dcr_id_bytes = dcr_id.encode("utf-8")
        version_bytes = signed_content["version"].to_bytes(4, "little")
        content_type_bytes = content_type.encode("utf-8")
        content_bytes = signed_content["content"].encode("utf-8")
        # Concatenate bytes in same order as Rust
        sign_over_payload = (
            dcr_id_bytes + version_bytes + content_type_bytes + content_bytes
        )
        # Verify using ed25519
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(verification_key)
        try:
            public_key.verify(
                bytes.fromhex(signed_content["signatureHex"]), sign_over_payload
            )
            return signed_content
        except Exception:
            raise Exception("Invalid signed content")

    def get_data_room_actions(self, data_room_id: str) -> DataRoomActionsView:
        endpoint = Endpoints.DATA_ROOM_ACTIONS.replace(":data_room_id", data_room_id)
        response: DataRoomActionsView = self.api.get(
            endpoint=endpoint,
        ).json()
        return response

    def get_data_room_policies(self, data_room_id: str, policy_ids: List[str]) -> Dict[str, Policy]:
        endpoint = Endpoints.DATA_ROOM_POLICIES.replace(":data_room_id", data_room_id)
        response: Dict[str, Policy] = self.api.post(
            endpoint=endpoint,
            req_body=json.dumps(policy_ids),
            headers={"Content-type": "application/json"},
        ).json()
        return response

    def stop_data_room(self, data_room_id: str) -> None:
        endpoint = Endpoints.DATA_ROOM_STOP.replace(":data_room_id", data_room_id)
        self.api.post(
            endpoint=endpoint,
        )

    """
    Action API
    """

    def get_data_room_action_info(
        self, data_room_id: str, data_room_compute_action: JSONType
    ) -> Action:
        body = {
            "payload": data_room_compute_action,
            "data_room_id": data_room_id,
        }
        response: Action = self.api.post(
            endpoint=Endpoints.ACTIONS_COLLECTION,
            req_body=json.dumps(body),
            headers={"Content-type": "application/json"},
        ).json()
        return response

    """
    Job API
    """

    def create_job(self, data_room_id: str, data_room_compute_action: JSONType) -> Job:
        body = {
            "payload": json.dumps(data_room_compute_action),
            "data_room_id": data_room_id,
        }
        response = self.api.post(
            endpoint=Endpoints.JOBS_COLLECTION,
            req_body=json.dumps(body),
            headers={"Content-type": "application/json"},
        )
        if response.status_code == 201 and "Location" in response.headers:
            location = response.headers["Location"]
            job_id = location.split("/")[-1]
            return self.get_job(job_id)
        else:
            raise Exception(
                f"Failed to create job: {response.status_code} {response.text}"
            )

    def get_job(self, job_id: str) -> Job:
        endpoint = Endpoints.JOB.replace(":job_id", job_id)
        response: Job = self.api.get(
            endpoint=endpoint,
        ).json()
        return response

    def get_job_tasks(self, job_id: str) -> JobTasksView:
        endpoint = Endpoints.JOB_TASKS_COLLECTION.replace(":job_id", job_id)
        response: JobTasksView = self.api.get(
            endpoint=endpoint,
        ).json()
        return response

    def get_job_status(self, job_id: str) -> JobStatusView:
        endpoint = Endpoints.JOB_STATUS.replace(":job_id", job_id)
        response: JobStatusView = self.api.get(
            endpoint=endpoint,
        ).json()
        return response

    def get_job_freshness(self, job_id: str) -> bool:
        endpoint = Endpoints.JOB_FRESHNESS.replace(":job_id", job_id)
        response: bool = self.api.get(
            endpoint=endpoint,
        ).json()
        return response

    """
    Compatibility API
    """

    def check_data_labs_compatibility(
        self, data_room_id: str, data_lab_ids: List[str]
    ) -> DataLabCompatibilityResponse:
        body = {"mediaDcrId": data_room_id, "dataLabIds": data_lab_ids}
        response: DataLabCompatibilityResponse = self.api.post(
            endpoint=Endpoints.CHECK_DATA_LABS_COMPATIBILITY,
            req_body=json.dumps(body),
            headers={"Content-type": "application/json"},
        ).json()
        return response
