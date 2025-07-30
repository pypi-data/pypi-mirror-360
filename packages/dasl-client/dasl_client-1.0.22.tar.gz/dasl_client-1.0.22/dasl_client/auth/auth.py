import abc
import base64
import time
from datetime import datetime

from dasl_api import (
    api,
    WorkspaceV1AuthenticateRequest,
    ApiClient,
    WorkspaceV1RequestSecretRequest,
)
from databricks.sdk.errors import ResourceDoesNotExist

from dasl_client.conn.conn import get_base_conn
from dasl_client.errors.errors import handle_errors
from databricks.sdk import WorkspaceClient
from typing import Optional

# The minimum age of a conn that we allow. Generally, clients are issued for
# a small batch of operations (one or two requests), not long-running
# operations. This threshold should be tuned to the longest expected operation
# using a single conn.
EXPIRY_OVERLAP_SECONDS = 600


class Authorization(abc.ABC):
    """
    A common interface for Authentication
    """

    @abc.abstractmethod
    def client(self) -> ApiClient:
        raise NotImplementedError("conn method must be implemented")

    def workspace(self) -> str:
        raise NotImplementedError("client method must be implemented")


class ServiceAccountKeyAuth(Authorization):
    """
    Authorisation implementation for Service Account Keys
    """

    def __init__(
        self, workspace: str, service_account_key: str, host: Optional[str] = None
    ):
        self._workspace = workspace
        self._service_account_key = service_account_key
        self._client = get_base_conn(host=host)
        self.expiry: int = int(datetime.now().timestamp())

    def client(self) -> ApiClient:
        """
        Return an API conn that can be used to issue an API request to the
        configured host. The associated bearer token is valid for at least
        EXPIRY_OVERLAP_SECONDS.
        :return: An API conn with valid auth
        """
        if int(datetime.now().timestamp()) > self.expiry - EXPIRY_OVERLAP_SECONDS:
            self.refresh()
        return self._client

    def workspace(self) -> str:
        """
        Return the client associated with this Service Account Key
        :return: The client name.
        """
        return self._workspace

    @handle_errors
    def refresh(self):
        """
        A helper function to refresh the bearer token used for authentication.
        :return:
        """
        req = WorkspaceV1AuthenticateRequest(
            service_account_key=self._service_account_key
        )
        handler = api.WorkspaceV1Api(api_client=self._client)

        resp = handler.workspace_v1_authenticate(
            workspace=self._workspace, workspace_v1_authenticate_request=req
        )
        self._client.set_default_header("Authorization", f"Bearer {resp.token}")
        verification = api.DbuiV1Api(self._client).dbui_v1_verify_auth()
        self.expiry = verification.expiry


class DatabricksTokenAuth(Authorization):
    """
    Authorization implementation using Databricks Tokens. Note that this will not work on most databricks
    workspaces using Premium or Enterprise tier databricks.
    """

    def __init__(self, workspace: str, token: str, host: Optional[str] = None):
        self._workspace = workspace
        self._databricks_token = token
        self._client = get_base_conn(host=host)
        self.expiry: int = int(datetime.now().timestamp())

    def client(self) -> ApiClient:
        """
        Return an API conn that can be used to issue an API request to the
        configured host. The associated bearer token is valid for at least
        EXPIRY_OVERLAP_SECONDS.
        :return: An API conn with valid auth
        """
        if int(datetime.now().timestamp()) > self.expiry - EXPIRY_OVERLAP_SECONDS:
            self.refresh()
        return self._client

    def workspace(self) -> str:
        """
        Return the client associated with this Databricks Token
        :return: The client name.
        """
        return self._workspace

    @handle_errors
    def refresh(self):
        """
        A helper function to refresh the bearer token used for authentication.
        :return:
        """
        req = WorkspaceV1AuthenticateRequest(
            databricks_api_token=self._databricks_token
        )
        handler = api.WorkspaceV1Api(api_client=self._client)

        resp = handler.workspace_v1_authenticate(
            workspace=self._workspace, workspace_v1_authenticate_request=req
        )
        self._client.set_default_header("Authorization", f"Bearer {resp.token}")
        verification = api.DbuiV1Api(self._client).dbui_v1_verify_auth()
        self.expiry = verification.expiry


class DatabricksSecretAuth(Authorization):
    """
    Authorization implementation using Databricks Secrets
    """

    def __init__(self, workspace: str, host: Optional[str] = None):
        self._workspace = workspace
        self._client = get_base_conn(host=host)
        self._principal = WorkspaceClient().current_user.me().user_name
        self.expiry: int = int(datetime.now().timestamp())

    def client(self) -> ApiClient:
        """
        Return an API conn that can be used to issue an API request to the
        configured host. The associated bearer token is valid for at least
        EXPIRY_OVERLAP_SECONDS.
        :return: An API conn with valid auth
        """
        if int(datetime.now().timestamp()) > self.expiry - EXPIRY_OVERLAP_SECONDS:
            self.refresh()
        return self._client

    def workspace(self) -> str:
        """
        Return the client associated with this Databricks Token
        :return: The client name.
        """
        return self._workspace

    @handle_errors
    def refresh(self):
        """
        A helper function to refresh the bearer token used for authentication.
        :return:
        """
        # First we do a pre-authenticate call to refresh the secret. It doesn't really matter if we race
        # here with others, as long as the secret ends up with a recent value in it. The secret can be used
        # more than once, but it does expire
        req = WorkspaceV1RequestSecretRequest(
            principalName=self._principal,
        )
        handler = api.WorkspaceV1Api(api_client=self._client)
        resp = handler.workspace_v1_request_secret(
            workspace=self._workspace, workspace_v1_request_secret_request=req
        )
        secret_name = resp.secret_name
        secret_value = ""
        for tries in range(3):
            try:
                secret_value = (
                    WorkspaceClient().secrets.get_secret(secret_name, "token").value
                )
                break
            except ResourceDoesNotExist:
                # Maybe there is a race here, let's retry
                time.sleep(0.5)
        if len(secret_value) == 0:
            raise RuntimeError(f"failed to complete secret auth")

        req = WorkspaceV1AuthenticateRequest(
            databricks_secret=base64.b64decode(secret_value).decode("utf-8"),
        )
        handler = api.WorkspaceV1Api(api_client=self._client)

        resp = handler.workspace_v1_authenticate(
            workspace=self._workspace, workspace_v1_authenticate_request=req
        )
        self._client.set_default_header("Authorization", f"Bearer {resp.token}")
        verification = api.DbuiV1Api(self._client).dbui_v1_verify_auth()
        self.expiry = verification.expiry
