import io
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import zipfile
from typing_extensions import Self
from abc import ABC, abstractmethod
from decentriq_dcr_compiler.schemas.data_room import DataRoomComputeAction
from .api import (
    ComputeInsightsResult,
    OverlapStatisticsResult,
    ValidationReport,
    DataAttributesResult,
    LookalikeAudienceStatisticsResult,
    GetSeedAudiencesResult,
    GetCustomAudiencesResult,
    SeedAudience,
    CustomAudience,
)
from ..client import Client
from ..storage import Key
from .audiences import Audiences, AudienceType
from .audience_statistics_result import LalAudienceStatistics
from .validation_reports import ValidationReports

"""
This module contains job classes for interacting with a Media DCR.
"""


class ComputeJob(ABC):
    """
    Abstract base class for compute jobs in a Media DCR.
    """

    def __init__(
        self,
        dcr_id: str,
        action: DataRoomComputeAction,
        result_zip_file_name: str,
        client: Client,
    ):
        """
        Initialize a compute job.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `action`: The compute action to perform
        - `result_zip_file_name`: The name of the file in the zip to get the result from
        - `client`: The client instance for API communication
        """
        self.dcr_id = dcr_id
        self.client = client
        self.client_v2 = (
            client.client_v2
        )  # TODO: Remove this once we have a single client
        self.session = client.create_session_v2()
        self.action = action
        self.result_zip_file_name = result_zip_file_name
        self.job_id = None

    def run(self) -> None:
        """
        Run the compute job.

        **Raises**:
        - `Exception`: If the computation has already been run
        """
        if self.job_id is not None:
            raise Exception("Computation has already been run")
        job = self.client_v2.create_job(
            self.dcr_id, self.action.model_dump(mode="json")
        )
        self.job_id = job["id"]

    def wait_for_completion(
        self, timeout: Optional[int] = None, sleep_interval: int = 1
    ) -> Self:
        """
        Wait for the compute job to complete.

        **Parameters**:
        - `timeout`: The maximum time to wait for the job to complete, in seconds
        - `sleep_interval`: The interval to wait between checks, in seconds

        **Returns**:
        - The compute job
        """
        start_time = time.time()
        while not self.is_complete():
            if timeout and time.time() - start_time > timeout:
                raise Exception("Computation did not complete within timeout")
            time.sleep(sleep_interval)
        return self

    def is_complete(self) -> bool:
        """
        Check if the compute job is complete.

        **Returns**:
        - True if the job is complete, False otherwise
        """
        if self.job_id is None:
            raise Exception("Computation has not been run")
        job_status = self.client_v2.get_job_status(self.job_id)
        return job_status["completed_at"] is not None

    @abstractmethod
    def result(self) -> Any:
        # Each job instance should implement this method and
        # return the appropriate type which represents the job result.
        pass

    def get_result(self) -> bytes:
        """
        Get the result of the compute job.

        **Returns**:
        - The content of the result file as bytes or raises an exception if the job failed
        """
        if self.job_id is None:
            raise Exception(f"Job '{self.job_id}' has not been run")

        job_status = self.client_v2.get_job_status(self.job_id)
        if job_status["completed_at"] is None:
            raise Exception(f"Job '{self.job_id}' is not complete")

        job_tasks_view = self.client_v2.get_job_tasks(self.job_id)
        if job_status["status"] == "Failed":
            error_messages = []
            for task_view in job_tasks_view["tasks"].values():
                for selector, result_hash in task_view["results"].items():
                    if selector.startswith("error"):
                        if task_view["completed"].includes(selector):
                            result = self.download_result(result_hash)
                            result_bytes = result.read()
                            error_messages.append(
                                (task_view["name"], result_bytes.decode("utf-8"))
                            )
            formatted_error_messages = "\n".join(
                [
                    f"{task_name}: {error_message}"
                    for task_name, error_message in error_messages
                ]
            )
            raise Exception(
                f"Job '{self.job_id}' failed with errors: {formatted_error_messages}"
            )
        elif job_status["status"] == "Success":
            task_result_hash = job_tasks_view["tasks"][job_tasks_view["target_task"]][
                "results"
            ]["success"]
            result = self.download_result(task_result_hash)
            result_bytes = result.read()
            zip = zipfile.ZipFile(io.BytesIO(result_bytes), "r")
            if self.result_zip_file_name in zip.namelist():
                return zip.read(self.result_zip_file_name)
            else:
                raise Exception(f"Did not find {self.result_zip_file_name} in zip")
        else:
            raise Exception(
                f"Job '{self.job_id}' has an unexpected status: {job_status['status']}"
            )

    def download_result(self, task_result_hash: str) -> io.RawIOBase:
        """
        Download the result of the compute job.

        **Parameters**:
        - `task_result_hash`: The hash of the task result to download

        **Returns**:
        - The result of the compute job
        """
        manifest_hash, encryption_key = self._get_result_encryption_key(
            task_result_hash
        )
        key = Key(material=encryption_key)
        return self.client.download_job_result(
            self.job_id, manifest_hash, task_result_hash, key
        )

    def _get_result_encryption_key(self, task_result_hash: str) -> Tuple[str, bytes]:
        """
        Get the encryption key for the result of the compute job.

        **Parameters**:
        - `task_result_hash`: The hash of the task result to get the encryption key for

        **Returns**:
        - The encryption key for the result
        """
        manifest_hash, encryption_key = (
            self.session.send_retrieve_result_encryption_key_request(
                self.job_id, task_result_hash
            )
        )
        return manifest_hash, encryption_key

    def _get_task_result_hash(self, task_name: str) -> str:
        """
        Get the hash of the task result for a given task name.

        **Parameters**:
        - `task_name`: The name of the task to get the result hash for

        **Returns**:
        - The hash of the task result
        """
        job_tasks = self.client_v2.get_job_tasks(self.job_id)
        for _id, task_properties in job_tasks["tasks"].items():
            if task_properties["name"] == task_name:
                return task_properties["results"]["success"]
        raise Exception(f"Did not find task result hash for task {task_name}")


class MediaInsightsJob(ComputeJob):
    """
    A compute job for retrieving insights from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaInsightsJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "computeInsights": {}}
        )
        super().__init__(dcr_id, action, "segments.json", client)

    def result(self) -> ComputeInsightsResult:
        """
        Get the result of the MediaInsightsJob.

        **Returns**:
        - The result of the MediaInsightsJob
        """
        result = self.get_result()
        return ComputeInsightsResult.model_validate_json(result)


class MediaBaseAudienceValidationReportsJob:
    """
    A class to encapsulate the various base audience validation report jobs for a DCR.

    This class does not inherit from ComputeJob because it encapsulates multiple jobs rather than being a single job itself.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaBaseAudienceValidationReportsJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        self.dcr_id = dcr_id
        self.client = client
        self.validation_jobs = {
            "matching": MediaMatchingValidationReportJob(dcr_id, client),
            "segments": MediaSegmentsValidationReportJob(dcr_id, client),
            "demographics": MediaDemographicsValidationReportJob(dcr_id, client),
        }

    def run(self) -> None:
        """
        Run all validation jobs.
        """
        [job.run() for job in self.validation_jobs.values()]

    def wait_for_completion(
        self, timeout: Optional[int] = None, sleep_interval: int = 1
    ) -> Self:
        """
        Wait for the compute job to complete.

        **Parameters**:
        - `timeout`: The maximum time to wait for the job to complete, in seconds
        - `sleep_interval`: The interval to wait between checks, in seconds

        **Returns**:
        - The compute job
        """
        start_time = time.time()
        while not all([job.is_complete() for job in self.validation_jobs.values()]):
            if timeout and time.time() - start_time > timeout:
                raise Exception("Computation did not complete within timeout")
            time.sleep(sleep_interval)
        return self

    def result(self) -> ValidationReports:
        """
        Get the result of the MediaBaseAudienceValidationReportsJob.

        **Returns**:
        - The result of the MediaBaseAudienceValidationReportsJob
        """
        return ValidationReports(
            matching=self.validation_jobs["matching"].result(),
            segments=self.validation_jobs["segments"].result(),
            demographics=self.validation_jobs["demographics"].result(),
        )


class ValidationReportJob(ComputeJob):
    """
    A compute job for retrieving validation reports from a Media DCR.
    """

    def __init__(self, dcr_id: str, action: DataRoomComputeAction, client: Client):
        """
        Initialize a ValidationReportJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `action`: The compute action to perform
        - `client`: The client instance for API communication
        """
        super().__init__(dcr_id, action, "validation-report.json", client)

    def get_validation_report(self) -> ValidationReport:
        """
        Get the validation report for the given task name.

        **Parameters**:
        - `task_name`: The name of the task to get the validation report for

        **Returns**:
        - The validation report
        """
        result = self.get_result()
        return ValidationReport.model_validate_json(result)


class MediaMatchingValidationReportJob(ValidationReportJob):
    """
    A compute job for retrieving matching validation reports from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaMatchingValidationReportJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getMatchingValidationReport": {}}
        )
        super().__init__(dcr_id, action, client)

    def result(self) -> ValidationReport:
        """
        Get the result of the MediaMatchingValidationReportJob.

        **Returns**:
        - The result of the MediaMatchingValidationReportJob
        """
        return self.get_validation_report()


class MediaSegmentsValidationReportJob(ValidationReportJob):
    """
    A compute job for retrieving segments validation reports from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaSegmentsValidationReportJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getSegmentsValidationReport": {}}
        )
        super().__init__(dcr_id, action, client)

    def result(self) -> ValidationReport:
        """
        Get the result of the MediaSegmentsValidationReportJob.

        **Returns**:
        - The result of the MediaSegmentsValidationReportJob
        """
        return self.get_validation_report()


class MediaDemographicsValidationReportJob(ValidationReportJob):
    """
    A compute job for retrieving demographics validation reports from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaDemographicsValidationReportJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getDemographicsValidationReport": {}}
        )
        super().__init__(dcr_id, action, client)

    def result(self) -> ValidationReport:
        """
        Get the result of the MediaDemographicsValidationReportJob.

        **Returns**:
        - The result of the MediaDemographicsValidationReportJob
        """
        return self.get_validation_report()


class MediaAudiencesValidationReportJob(ValidationReportJob):
    """
    A compute job for retrieving audiences validation reports from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaAudiencesValidationReportJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getAudiencesValidationReport": {}}
        )
        super().__init__(dcr_id, action, client)

    def result(self) -> ValidationReport:
        """
        Get the result of the MediaAudiencesValidationReportJob.

        **Returns**:
        - The result of the MediaAudiencesValidationReportJob
        """
        return self.get_validation_report()


class MediaOverlapStatisticsJob(ComputeJob):
    """
    A compute job for retrieving overlap statistics from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaOverlapStatisticsJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "computeOverlapStatistics": {}}
        )
        super().__init__(dcr_id, action, "overlap.json", client)

    def result(self) -> OverlapStatisticsResult:
        """
        Get the result of the MediaOverlapStatisticsJob.

        **Returns**:
        - The result of the MediaOverlapStatisticsJob
        """
        result = self.get_result()
        return OverlapStatisticsResult.model_validate_json(result)


class MediaDataAttributesJob(ComputeJob):
    """
    A compute job for retrieving data attributes from a Media DCR.
    """

    def __init__(self, dcr_id: str, client: Client):
        """
        Initialize a MediaDataAttributesJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `client`: The client instance for API communication
        """
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getDataAttributes": {}}
        )
        super().__init__(dcr_id, action, "attributes.json", client)

    def result(self) -> DataAttributesResult:
        """
        Get the result of the MediaDataAttributesJob.

        **Returns**:
        - The result of the MediaDataAttributesJob
        """
        result = self.get_result()
        return DataAttributesResult.model_validate_json(result)


class MediaLookalikeAudienceStatisticsJob(ComputeJob):
    """
    A compute job for retrieving lookalike audience statistics from a Media DCR.
    """

    def __init__(self, dcr_id: str, audience: AudienceType, client: Client):
        """
        Initialize a MediaLookalikeAudienceStatisticsJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `audience`: The audience to get the statistics for
        - `client`: The client instance for API communication
        """
        if isinstance(audience, SeedAudience):
            audience_ref = {
                "kind": audience.kind.value,
                "audienceType": audience.audienceType,
            }
        elif isinstance(audience, CustomAudience):
            audience_ref = {
                "kind": "CUSTOM",
                "id": audience.id,
            }
        else:
            raise Exception(
                f"Cannot compute lookalike statistics for audience of unknown type: {type(audience)}"
            )
        action = DataRoomComputeAction.model_validate(
            {
                "kind": "media",
                "getLookalikeAudienceStatistics": {
                    "audienceRef": audience_ref
                },
            }
        )
        super().__init__(dcr_id, action, "lookalike_audience.json", client)

    def result(self) -> LalAudienceStatistics:
        """
        Get the result of the MediaLookalikeAudienceStatisticsJob.

        **Returns**:
        - Lookalike statistics as a LalAudienceStatistics object
        """
        result = self.get_result()
        lal_statistics_result = LookalikeAudienceStatisticsResult.model_validate_json(
            result
        )
        formatted_result = LalAudienceStatistics.from_dict(
            lal_statistics_result.model_dump()
        )
        return formatted_result


class _GetCustomAudiencesJob(ComputeJob):
    """
    A compute job for retrieving custom audiences from a Media DCR.
    """

    def __init__(self, dcr_id: str, user: str, client: Client):
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getCustomAudiences": {"user": user}}
        )
        super().__init__(dcr_id, action, "audiences.json", client)

    def result(self) -> GetCustomAudiencesResult:
        result = self.get_result()
        return GetCustomAudiencesResult.model_validate_json(result.decode("utf-8"))


class _GetSeedAudiencesJob(ComputeJob):
    """
    A compute job for retrieving seed audiences from a Media DCR.
    """

    def __init__(self, dcr_id: str, user: str, client: Client):
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "getSeedAudiences": {"user": user}}
        )
        super().__init__(dcr_id, action, "audiences.json", client)

    def result(self) -> GetSeedAudiencesResult:
        result = self.get_result()
        return GetSeedAudiencesResult.model_validate_json(result.decode("utf-8"))


class MediaGetAudiencesJob(ComputeJob):
    """
    A compute job for retrieving all audiences from a Media DCR.
    """

    def __init__(self, dcr_id: str, user: str, client: Client, participant_id: str):
        """
        Initialize a MediaGetAudiencesJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `user`: The user to get the audiences for
        - `client`: The client instance for API communication
        """
        self._custom = _GetCustomAudiencesJob(dcr_id, user, client)
        self._seed = _GetSeedAudiencesJob(dcr_id, user, client)
        self._participant_id = participant_id
        self._user_email = user

    def run(self):
        """
        Run the compute job.

        **Raises**:
        - `Exception`: If the computation has already been run
        """
        self._custom.run()
        self._seed.run()

    def wait_for_completion(
        self, timeout: Optional[int] = None, sleep_interval: int = 1
    ) -> Self:
        """
        Wait for the compute job to complete.

        **Parameters**:
        - `timeout`: The maximum time to wait for the job to complete, in seconds
        - `sleep_interval`: The interval to wait between checks, in seconds

        **Returns**:
        - The compute job
        """
        self._custom.wait_for_completion(timeout=timeout, sleep_interval=sleep_interval)
        self._seed.wait_for_completion(timeout=timeout, sleep_interval=sleep_interval)
        return self

    def is_complete(self) -> bool:
        """
        Check if the compute job is complete.

        **Returns**:
        - True if the job is complete, False otherwise
        """
        return self._custom.is_complete() and self._seed.is_complete()

    def result(self) -> Audiences:
        """
        Get the result of the MediaGetAudiencesJob.

        **Returns**:
        - The result of the MediaGetAudiencesJob
        """
        seed_result = self._seed.result()
        custom_result = self._custom.result()
        all_custom_audiences = custom_result.audiences
        # The backend will return all custom audiences that are either shared
        # with the user or that are dependencies of such audiences.
        # This is required because in the UI we also want to display information
        # about how some shared audience is constructed (e.g. the names of which
        # audiences are combined in a rule-based audience).
        # In the SDK this information is not required and for that reason these
        # audiences are removed here since they could not be exported by the
        # current user.
        accessible_custom_audiences = []
        for audience in all_custom_audiences:
            shared_with_participants = audience.sharedWith or []
            is_owner = audience.createdBy == self._user_email
            is_shared = self._participant_id in shared_with_participants
            if is_owner or is_shared:
                accessible_custom_audiences.append(audience)
        audiences: list[AudienceType] = accessible_custom_audiences + seed_result.audiences
        return Audiences(audiences)


class MediaEstimateAudienceSizeJob(ComputeJob):
    """
    A compute job for estimating audience size in a Media DCR.
    """

    def __init__(self, dcr_id: str, audience: AudienceType, client: Client):
        """
        Initialize a MediaEstimateAudienceSizeJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `audience`: The audience to get the size for
        - `client`: The client instance for API communication
        """
        self.is_lookalike = Audiences.is_lookalike_audience(audience)
        if isinstance(audience, SeedAudience):
            audience_ref = {
                "kind": audience.kind.value,
                "audienceType": audience.audienceType,
            }
        elif isinstance(audience, CustomAudience):
            audience_ref = {
                "kind": "CUSTOM",
                "id": audience.id,
            }

        action = DataRoomComputeAction.model_validate(
            {
                "kind": "media",
                "estimateAudienceSize": {
                    "audience": {"kind": "REF", "value": audience_ref}
                },
            }
        )
        super().__init__(dcr_id, action, "audience_size.json", client)

    def result(self) -> int:
        """
        Get the result of the MediaEstimateAudienceSizeJob.

        **Returns**:
        - The result of the MediaEstimateAudienceSizeJob
        """
        result = self.get_result()
        audience_size_result = json.loads(result)
        return int(audience_size_result["audience_size"])


class MediaAudienceUserListJob(ComputeJob):
    """
    A compute job for retrieving audience user lists from a Media DCR.
    """

    def __init__(self, dcr_id: str, audience: AudienceType, client: Client):
        """
        Initialize a MediaAudienceUserListJob instance.

        **Parameters**:
        - `dcr_id`: The identifier for the DCR
        - `audience`: The audience to get the user list for
        - `client`: The client instance for API communication
        """
        self.is_lookalike = Audiences.is_lookalike_audience(audience)
        if isinstance(audience, SeedAudience):
            audience_ref = {
                "kind": audience.kind.value,
                "audienceType": audience.audienceType,
            }
        elif isinstance(audience, CustomAudience):
            audience_ref = {
                "kind": "CUSTOM",
                "id": audience.id,
            }
        action = DataRoomComputeAction.model_validate(
            {
                "kind": "media",
                "getAudienceUserList": {"audienceRef": audience_ref},
            }
        )
        super().__init__(dcr_id, action, "audience_users.csv", client)

    def result(self) -> List[str]:
        """
        Get the result of the MediaAudienceUserListJob.

        **Returns**:
        - The result of the MediaAudienceUserListJob
        """
        result = self.get_result()
        result = result.decode("utf-8").splitlines()
        return [line for line in result if line]


class MediaModelQualityReportJob(ComputeJob):
    def __init__(self, dcr_id: str, client: Client):
        action = DataRoomComputeAction.model_validate(
            {"kind": "media", "retrieveModelQualityReport": {}}
        )
        super().__init__(dcr_id, action, "model_quality.json", client)

    def result(self) -> Dict[str, Any]:
        result = self.get_result()
        return json.loads(result.decode("utf-8"))
