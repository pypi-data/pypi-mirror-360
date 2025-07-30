"""
This module contains the API for interacting with a Media DCR.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Union, Tuple
from typing_extensions import Self
from enum import Enum
import json
from ..archv2.release_policy_builder import ReleasePolicyBuilder
from ..archv2.release_policy_builder import ReleasePolicyBuilder
from .compute_job import (
    ComputeJob,
    MediaInsightsJob,
    MediaAudiencesValidationReportJob,
    MediaOverlapStatisticsJob,
    MediaDataAttributesJob,
    MediaLookalikeAudienceStatisticsJob,
    MediaGetAudiencesJob,
    MediaEstimateAudienceSizeJob,
    MediaAudienceUserListJob,
    MediaBaseAudienceValidationReportsJob,
    MediaModelQualityReportJob,
)
from .action import (
    CreateLookalikeAudienceAction,
    CreateRuleBasedAudienceAction,
    CreateRemarketingAudienceAction,
    UpdateCustomAudienceAction,
    DeleteCustomAudienceAction,
)
from .lookalike_audience_builder import LookalikeAudienceDefinition
from .rule_based_builder import RuleBasedAudienceDefinition
from .remarketing_audience_builder import RemarketingAudienceDefinition
from .participant import Participant
from .api import CustomAudience, SeedAudience
from ..types import MatchingId, MATCHING_ID_INTERNAL_LOOKUP
from ..archv2.client import DataRoomAuditLog
from .audiences import AudienceType

if TYPE_CHECKING:
    from ..client import Client


class DatasetType(Enum):
    """
    Enum for the type of dataset.
    
    Members:
        - AUDIENCES
        - MATCHING_IDS
        - DEMOGRAPHICS
        - SEGMENTS
        - EMBEDDINGS
    """

    AUDIENCES = "audiences"
    MATCHING_IDS = "matching"
    DEMOGRAPHICS = "demographics"
    SEGMENTS = "segments"
    EMBEDDINGS = "embeddings"


class CollaborationType(str, Enum):
    """
    Represents the features supported by a DCR.

    Members:
        - INSIGHTS
        - LOOKALIKE
        - REMARKETING
        - RULE_BASED
    """

    INSIGHTS = "ENABLE_INSIGHTS"
    LOOKALIKE = "ENABLE_LOOKALIKE_AUDIENCES"
    REMARKETING = "ENABLE_REMARKETING"
    RULE_BASED = "ENABLE_RULED_BASED_AUDIENCES"


class DcrConfiguration:
    def __init__(self, dcr_id: str, data_room: DataRoom):
        content = json.loads(data_room["signedContent"]["content"])
        self.config = {
            "id": dcr_id,
            "name": content["name"],
            "participants": content["participantGroups"],
            "matching_id_format": content["matchingIdFormat"],
            "matching_id_hashing_algorithm": content["hashMatchingIdWith"],
            "collaboration_types": [],
        }

        features = content["features"]
        if "ENABLE_INSIGHTS" in features:
            self.config["collaboration_types"].append(CollaborationType.INSIGHTS.value)
        if "ENABLE_LOOKALIKE_AUDIENCES" in features:
            self.config["collaboration_types"].append(CollaborationType.LOOKALIKE.value)
        if "ENABLE_REMARKETING" in features:
            self.config["collaboration_types"].append(
                CollaborationType.REMARKETING.value
            )
        if "ENABLE_RULED_BASED_AUDIENCES" in features:
            self.config["collaboration_types"].append(
                CollaborationType.RULE_BASED.value
            )

    def __str__(self):
        """
        Return a JSON string representation of the configuration.
        """
        return json.dumps(self.config, indent=2)

    # Added to mimic the behaviour of Pydantic types to provide a
    # consistent interface for the user.
    def model_dump_json(self):
        """
        Return a JSON string representation of the configuration.
        """
        return json.dumps(self.config, indent=2)


class MediaDcr:
    """
    Class for managing Media Data Clean Room (DCR) operations.
    """

    def __init__(
        self,
        client: Client,
        *,
        name: Optional[str] = None,
        participants: Optional[List[Participant]] = None,
        collaboration_types: Optional[List[CollaborationType]] = None,
        matching_ids: Optional[List[MatchingId]] = None,
        hide_absolute_values: bool = False,
        _existing_dcr_id: Optional[str] = None,
    ):
        """
        Initialize a MediaDCR instance.

        Can be used either to create a new DCR (when dcr_id is None) or load an existing one.

        **Parameters**:
        - `client`: The client instance for API communication
        - `name`: Name for new DCR
        - `participants`: Participants for new DCR
        - `collaboration_types`: Collaboration types for new DCR
        - `matching_ids`: Matching IDs for new DCR
        - `hide_absolute_values`: Whether to hide absolute values from outputs
        - `_existing_dcr_id`: Optional ID of existing DCR to load (for internal use only)
        """
        self.client = client
        self.client_v2 = client.client_v2
        self.session_v2 = self.client.create_session_v2()

        if _existing_dcr_id is not None:
            self.id = _existing_dcr_id
        else:
            if not all([name, participants, matching_ids]):
                raise Exception(
                    "name, participants, and matching_ids are required when creating a new DCR"
                )

            # Check that there is only one matching id for now.
            if len(matching_ids) == 1:
                self.matching_id = matching_ids[0]
            elif len(matching_ids) == 0:
                raise Exception("No matching id provided")
            else:
                raise Exception("Only one matching id is currently supported")

            self.id = self._build(
                name,
                participants,
                collaboration_types or [],
                matching_ids,
                hide_absolute_values,
            )

    def _build(
        self,
        name: str,
        participants: List[Participant],
        collaboration_types: List[CollaborationType],
        matching_ids: List[MatchingId],
        hide_absolute_values: bool,
    ) -> str:
        """
        Build the Data Clean Room.
        """
        (
            matching_id_format,
            matching_id_hashing_algorithm,
        ) = MATCHING_ID_INTERNAL_LOOKUP[matching_ids[0]]
        create_data_room_definition = {
            "kind": "media",
            "audiencesPolicyId": None,
            "demographicsPolicyId": None,
            "embeddingsPolicyId": None,
            "enableDebugMode": False,
            "enableInsights": CollaborationType.INSIGHTS in collaboration_types,
            "enableLookalikeAudiences": CollaborationType.LOOKALIKE in collaboration_types,
            "enableRemarketing": CollaborationType.REMARKETING in collaboration_types,
            "enableDebugMode": False,
            "enableRuleBasedAudiences": CollaborationType.RULE_BASED in collaboration_types,
            "hashMatchingIdWith": matching_id_hashing_algorithm,
            "hideAbsoluteValuesFromInsights": hide_absolute_values,
            "matchingIdFormat": matching_id_format,
            "matchingIdsPolicyId": None,
            "name": name,
            "participantGroups": [
                participant.as_dict() for participant in participants
            ],
            "policies": [],  # Create the DCR without policies
            "version": "v0",
        }
        verification_key = self.session_v2.send_get_verification_key_request()
        data_room = self.client_v2.create_data_room(
            create_data_room_definition, verification_key
        )
        return data_room["id"]

    def provision_base_audience(self, data_lab_id: str) -> None:
        """
        Provision a base audience to the DCR.

        **Parameters**:
        - `data_lab_id`: The identifier of the DataLab from which to provision the base audience

        **Raises**:
        - `Exception`: If the DataLab is not validated or if provisioning fails
        """
        # Deprovision all existing datasets before provisioning new ones.
        # This ensures we don't end up with a mix of old and new datasets.
        self.deprovision_base_audience()

        # Check DataLab is validated
        data_lab = self.client.get_data_lab(data_lab_id)
        if not data_lab["isValidated"]:
            raise Exception("Cannot provision DataLab, not validated.")

        # Check compatibility
        data_lab_compatibility = self.client_v2.check_data_labs_compatibility(
            self.id, [data_lab_id]
        )
        error_messages = data_lab_compatibility["errorsByDataLab"][data_lab_id]
        if error_messages:
            messages = [e["message"] for e in error_messages]
            formatted_error_messages = ", ".join(messages)
            raise Exception(
                f"Cannot provision DataLab, incompatible. Error messages: {formatted_error_messages}"
            )

        dataset_manifest_hashes = [
            (d["name"], d["dataset"]["manifestHash"])
            for d in data_lab["datasets"]
            if d.get("dataset") is not None
        ]

        self._provision_base_audience(dataset_manifest_hashes)

    def _provision_base_audience(self, dataset_manifest_hashes: list[Tuple[str, str]]):
        dataset_policy_ids = {
            "MATCHING_DATA": None,
            "SEGMENTS_DATA": None,
            "DEMOGRAPHICS_DATA": None,
            "EMBEDDINGS_DATA": None,
        }
        for dataset_name, manifest_hash in dataset_manifest_hashes:
            dataset_type = None
            if dataset_name == "MATCHING_DATA":
                dataset_type = DatasetType.MATCHING_IDS
            elif dataset_name == "SEGMENTS_DATA":
                dataset_type = DatasetType.SEGMENTS
            elif dataset_name == "DEMOGRAPHICS_DATA":
                dataset_type = DatasetType.DEMOGRAPHICS
            elif dataset_name == "EMBEDDINGS_DATA":
                dataset_type = DatasetType.EMBEDDINGS
            else:
                raise ValueError(f"Unknown datalab dataset name: {dataset_name}")

            policy_id = self._create_release_policy(
                manifest_hash,
                dataset_type,
            )
            dataset_policy_ids[dataset_name] = policy_id

        # Provision datasets from DataLab to DCR
        provision_action = {
            "kind": "media",
            "provisionBaseAudiencePolicyIds": {
                "demographicsPolicyId": dataset_policy_ids.get("DEMOGRAPHICS_DATA"),
                "embeddingsPolicyId": dataset_policy_ids.get("EMBEDDINGS_DATA"),
                "matchingPolicyId": dataset_policy_ids.get("MATCHING_DATA"),
                "segmentsPolicyId": dataset_policy_ids.get("SEGMENTS_DATA"),
            },
        }
        self.session_v2.send_data_room_state_action_request(self.id, provision_action)

    def deprovision_base_audience(self) -> None:
        """
        Deprovision a base audience from the DCR.

        Removes all datasets associated with the base audience from the DCR by deprovisioning
        each dataset type.
        """
        deprovision_action = {"kind": "media", "deprovisionBaseAudiencePolicyIds": {}}
        self.session_v2.send_data_room_state_action_request(self.id, deprovision_action)

    def provision_seed_audiences(self, manifest_hash: str) -> None:
        """
        Provision seed audiences dataset to the DCR.

        **Parameters**:
        - `manifest_hash`: Hash of the seed audience dataset to provision
        """
        policy_id = self._create_release_policy(manifest_hash, DatasetType.AUDIENCES)
        dataset_action = {
            "kind": "media",
            "provisionSeedAudiencePolicyIds": {"audiencesPolicyId": policy_id},
        }
        self.session_v2.send_data_room_state_action_request(self.id, dataset_action)

    def deprovision_seed_audiences(self) -> None:
        """Deprovision seed audiences dataset from the DCR."""
        # Set policy_id to None to indicate that the dataset is no longer used.
        dataset_action = {"kind": "media", "deprovisionSeedAudiencePolicyIds": {}}
        self.session_v2.send_data_room_state_action_request(self.id, dataset_action)

    def create_lookalike_audience(
        self,
        definition: LookalikeAudienceDefinition,
    ) -> CustomAudience:
        """
        Create a lookalike audience based on the provided definition.

        **Parameters**:
        - `definition`: Definition of the lookalike audience to create

        **Returns**:
        - The created lookalike audience
        """
        action = CreateLookalikeAudienceAction(
            dcr_id=self.id,
            client=self.client,
            definition=definition,
        )
        response = action.create()
        lal_audience = CustomAudience.model_validate(
            response["createCustomAudience"]["audience"]
        )
        return lal_audience

    def create_rule_based_audience(
        self,
        definition: RuleBasedAudienceDefinition,
    ) -> CustomAudience:
        """
        Create a rule-based audience based on the provided definition.

        **Parameters**:
        - `definition`: Definition of the rule-based audience to create

        **Returns**:
        - The created rule-based audience
        """
        action = CreateRuleBasedAudienceAction(
            dcr_id=self.id,
            client=self.client,
            definition=definition,
        )
        response = action.create()
        rb_audience = CustomAudience.model_validate(
            response["createCustomAudience"]["audience"]
        )
        return rb_audience

    def create_remarketing_audience(
        self,
        definition: RemarketingAudienceDefinition,
    ) -> CustomAudience:
        """
        Create a remarketing audience based on the provided definition.

        **Parameters**:
        - `definition`: Definition of the remarketing audience to create

        **Returns**:
        - The created remarketing audience
        """
        action = CreateRemarketingAudienceAction(
            dcr_id=self.id,
            client=self.client,
            definition=definition,
        )
        response = action.create()
        rm_audience = CustomAudience.model_validate(
            response["createCustomAudience"]["audience"]
        )
        return rm_audience

    def get_insights(self) -> MediaInsightsJob:
        """
        Compute insights from the data room.

        **Returns**:
        - The job to compute insights
        """
        job = MediaInsightsJob(self.id, self.client)
        return self._run_compute_job(job)

    def get_base_audience_validation_reports(
        self,
    ) -> MediaBaseAudienceValidationReportsJob:
        """
        Get the validation reports for the DCR.

        **Returns**:
        - The job to compute the validation reports
        """
        job = MediaBaseAudienceValidationReportsJob(self.id, self.client)
        return self._run_compute_job(job)

    def get_seed_audiences_validation_report(
        self,
    ) -> MediaAudiencesValidationReportJob:
        """
        Get the validation report for seed audiences data.

        **Returns**:
        - The job to compute the seed audiences validation report
        """
        job = MediaAudiencesValidationReportJob(self.id, self.client)
        return self._run_compute_job(job)

    def get_overlap_statistics(self) -> MediaOverlapStatisticsJob:
        """
        Compute overlap statistics.

        **Returns**:
        - The job to compute the overlap statistics
        """
        job = MediaOverlapStatisticsJob(self.id, self.client)
        return self._run_compute_job(job)

    def get_data_attributes(self) -> MediaDataAttributesJob:
        """
        Get data attributes.

        **Returns**:
        - The job to get the data attributes
        """
        job = MediaDataAttributesJob(self.id, self.client)
        return self._run_compute_job(job)

    def get_lookalike_audience_statistics(
        self, audience: AudienceType,
    ) -> MediaLookalikeAudienceStatisticsJob:
        """
        Get statistics for lookalike audiences.

        **Returns**:
        - The job to get the lookalike audience statistics
        """
        job = MediaLookalikeAudienceStatisticsJob(self.id, audience, self.client)
        return self._run_compute_job(job)

    def get_audiences(
        self,
    ) -> MediaGetAudiencesJob:
        """
        Get audiences for a specific user.

        **Returns**:
        - The job to get the audiences for the specified user
        """
        participants = self.get_participants()
        user_participant_id = None
        for participant in participants:
            if self.client.user_email in participant.emails:
                user_participant_id = participant.id
                break
        if user_participant_id is None:
            raise Exception(f"User {self.client.user_email} does not appear in any of the participants")
        else:
            job = MediaGetAudiencesJob(
                self.id,
                self.client.user_email,
                self.client,
                participant_id=user_participant_id,
            )
            return self._run_compute_job(job)

    def share_audiences(
        self, audiences: List[CustomAudience], participants: List[Participant]
    ):
        """
        Share the audiences with the participant group.

        **Parameters**:
        - `audiences`: The audiences to share
        - `participants`: The participants to share the audiences with
        """
        for audience in audiences:
            audience.sharedWith = [participant.id for participant in participants]
            action = UpdateCustomAudienceAction(self.id, self.client, audience)
            action.update()

    def delete_audiences(
        self,
        audiences: List[CustomAudience],
        *,
        delete_dependent_audiences: bool = False,
    ) -> None:
        """
        Delete audiences.

        **Parameters**:
        - `audiences`: The audiences to delete
        - `delete_dependent_audiences`: If true, the supplied audiences and all dependent audiences will be deleted. If false, the supplied audiences will only be deleted if they have no dependents.
        """
        for audience in audiences:
            # Delete the user requested audiences
            action = DeleteCustomAudienceAction(
                self.id, self.client, audience.id, delete_dependent_audiences
            )
            action.delete()

    def get_audience_size(
        self, audience: Union[SeedAudience, CustomAudience]
    ) -> MediaEstimateAudienceSizeJob:
        """
        Get the size of an audience.

        **Parameters**:
        - `audience`: The audience to estimate the size of

        **Returns**:
        - The job to get the size of the audience
        """
        job = MediaEstimateAudienceSizeJob(self.id, audience, self.client)
        return self._run_compute_job(job)

    def get_audience_user_list(
        self, audience: Union[SeedAudience, CustomAudience]
    ) -> MediaAudienceUserListJob:
        """
        Get the user list for an audience.

        **Parameters**:
        - `audience`: The audience to get the user list for

        **Returns**:
        - The job to get the user list for the audience
        """
        job = MediaAudienceUserListJob(self.id, audience, self.client)
        return self._run_compute_job(job)

    def get_audit_log(self) -> List[DataRoomAuditLog]:
        """
        Get the audit log for the data room.

        **Returns**:
        - Audit log
        """
        verification_key = self.session_v2.send_get_verification_key_request()
        verified_audit_log = self.client_v2.get_data_room_audit_log(
            self.id, verification_key
        )
        return verified_audit_log

    def _create_release_policy(
        self, manifest_hash: str, dataset_type: DatasetType
    ) -> str:
        """
        Create a release policy for a dataset.

        **Parameters**:
        - `manifest_hash`: The hash of the dataset
        - `dataset_type`: The type of the dataset

        **Returns**:
        - The id of the created release policy
        """
        release_policy = (
            ReleasePolicyBuilder(self.client, self.id, manifest_hash)
            .with_target_leaf_node_name(dataset_type.value)
            .build()
        )
        policy_id = self.session_v2.create_policy(release_policy)
        return policy_id

    @classmethod
    def from_existing(cls, dcr_id: str, client: Client) -> Self:
        """
        Construct a MediaDCR from an existing DCR with the given ID.

        **Parameters**:
        - `dcr_id`: The id of the DCR
        - `client`: The client from which a session is created

        **Returns**:
        - The MediaDCR instance
        """
        return cls(client=client, _existing_dcr_id=dcr_id)

    def get_participants(self) -> List[Participant]:
        """
        Get the participants of the DCR.

        **Returns**:
        - The list of participants in the DCR
        """
        verification_key = self.session_v2.send_get_verification_key_request()
        dr = self.client_v2.get_data_room(self.id, verification_key)
        content = json.loads(dr["signedContent"]["content"])
        existing_participants = content["participantGroups"]
        return [
            Participant(
                emails=pg["emails"],
                permissions=pg["permissions"],
                role=pg["role"],
                id=pg["id"],
                organization_id=pg["organizationId"],
            )
            for pg in existing_participants if "model.quality@decentriq.com" not in pg["emails"]
        ]

    def get_configuration(self) -> DcrConfiguration:
        """
        Get the configuration of the DCR.

        **Returns**:
        - The configuration of the DCR
        """
        verification_key = self.session_v2.send_get_verification_key_request()
        dr = self.client_v2.get_data_room(self.id, verification_key)
        return DcrConfiguration(self.id, dr)

    def _run_compute_job(self, compute_job: ComputeJob) -> ComputeJob:
        """
        Run a compute job and return the result.

        **Parameters**:
        - `compute_job`: The compute job to run

        **Returns**:
        - The compute job
        """
        compute_job.run()
        return compute_job

    def _retrieve_model_quality_report(self) -> MediaModelQualityReportJob:
        job = MediaModelQualityReportJob(self.id, self.client)
        return self._run_compute_job(job)
