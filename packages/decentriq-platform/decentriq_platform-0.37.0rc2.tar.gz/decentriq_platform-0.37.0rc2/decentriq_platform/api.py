from enum import Enum

import requests
from requests import Response
from urllib3.util import Retry
from importlib.metadata import version

from .config import (
    DECENTRIQ_REQUEST_RETRY_BACKOFF_FACTOR,
    DECENTRIQ_REQUEST_RETRY_TOTAL,
)

retry = Retry(
    total=DECENTRIQ_REQUEST_RETRY_TOTAL,
    backoff_factor=DECENTRIQ_REQUEST_RETRY_BACKOFF_FACTOR,
)


class Endpoints(str, Enum):
    GRAPHQL = "/graphql"
    SESSION_MESSAGES = "/sessions/:sessionId/messages"
    SESSION_MESSAGES_V2 = "/sessions/:sessionId/messages_v2"
    USER_UPLOAD_CHUNKS = "/uploads/:uploadId/chunks/:chunkHash"
    # archV2
    ORGANIZATION_DATA_ROOMS_COLLECTION = "/organizations/:organization_id/datarooms"
    USER_DATA_ROOMS_COLLECTION = "/users/:user_id/datarooms"
    DATA_ROOMS_COLLECTION = f"/datarooms"
    DATA_ROOM = f"/datarooms/:data_room_id"
    DATA_ROOM_ACTIONS = f"/datarooms/:data_room_id/actions"
    DATA_ROOM_AUDIT_LOG = f"/datarooms/:data_room_id/auditlog"
    DATA_ROOM_POLICIES = f"/datarooms/:data_room_id/policies"
    DATA_ROOM_STOP = f"/datarooms/:data_room_id/stop"
    ACTIONS_COLLECTION = "/actions"
    JOBS_COLLECTION = "/jobs"
    JOB = "/jobs/:job_id"
    JOB_FRESHNESS = "/jobs/:job_id/freshness"
    JOB_STATUS = "/jobs/:job_id/status"
    JOB_TASKS_COLLECTION = "/jobs/:job_id/tasks"
    JOB_RESULT_CHUNKS_STREAM = "/jobs/:job_id/result/:task_result_hash/chunks"
    DATASET_CHUNKS_STREAM = "/datasets/:manifest_hash/chunks"
    CHECK_DATA_LABS_COMPATIBILITY = "/compatibility/check-data-labs-compatibility"

class ApiError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthorizationError(ApiError):
    pass


class NotFoundError(ApiError):
    pass


class BadRequestError(ApiError):
    pass


class ServerError(ApiError):
    pass


class Api:
    def __init__(
        self,
        platform_api_token,
        client_id,
        host,
        port,
        use_tls,
        api_prefix,
        additional_auth_headers={},
        timeout=None,
    ):
        session = requests.Session()
        if use_tls:
            protocol = "https"
        else:
            protocol = "http"
        self.base_url = f"{protocol}://{host}:{port}{api_prefix}"
        auth_headers = {
            "Authorization": "Bearer " + platform_api_token,
            "Authorization-Type": "app",
            "Authorization-Client": client_id,
        }
        auth_headers.update(additional_auth_headers)
        session.headers.update(auth_headers)
        self.session = session
        self.timeout = timeout
        self.sdk_version = version('decentriq_platform')

    @staticmethod
    def __check_response_status_code(response: Response):
        if response.status_code >= 200 and response.status_code <= 204:
            return

        response_text = response.text
        if response.status_code == 400:
            raise BadRequestError(response_text)
        elif response.status_code == 401 or response.status_code == 403:
            raise AuthorizationError(response_text)
        elif response.status_code == 404:
            raise NotFoundError(response_text)
        elif response.status_code >= 500 and response.status_code <= 504:
            raise ServerError(response_text)
        else:
            raise ApiError(response_text)

    def _request(self, method, endpoint, **kwargs):
        retry = kwargs.pop("retry", None)

        if 'headers' in kwargs and kwargs['headers'] is not None:
            kwargs['headers']['SDK_VERSION'] = self.sdk_version
        else:
            kwargs['headers'] = {'SDK_VERSION': self.sdk_version}

        url = self.base_url + endpoint
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except Exception as e:
            if retry is None:
                raise

            retry = retry.increment(method=method, url=url)
            retry.sleep()
            response = self._request(method, endpoint, retry=retry, **kwargs)
        Api.__check_response_status_code(response)
        return response

    def post(self, endpoint, req_body=None, headers=None, retry=None):
        response = self._request(
            method="POST",
            endpoint=endpoint,
            data=req_body,
            headers=headers,
            stream=True,
            retry=retry,
        )
        return response

    def post_multipart(self, endpoint, parts=None, headers=None, retry=None):
        response = self._request(
            method="POST", endpoint=endpoint, files=parts, headers=headers, retry=retry
        )
        return response

    def put(self, endpoint, req_body=None, headers=None, retry=None):
        response = self._request(
            method="PUT", endpoint=endpoint, data=req_body, headers=headers, retry=retry
        )
        return response

    def patch(self, endpoint, req_body=None, headers=None, retry=None):
        response = self._request(
            method="PATCH",
            endpoint=endpoint,
            data=req_body,
            headers=headers,
            retry=retry,
        )
        return response

    def get(self, endpoint, params=None, headers=None, retry=None):
        response = self._request(
            method="GET", endpoint=endpoint, params=params, headers=headers, retry=retry
        )
        return response

    def head(self, endpoint, headers=None, retry=None):
        response = self._request(
            method="HEAD", endpoint=endpoint, headers=headers, retry=retry
        )
        return response

    def delete(self, endpoint, headers=None, retry=None):
        response = self._request(
            method="DELETE", endpoint=endpoint, headers=headers, retry=retry
        )
        return response
