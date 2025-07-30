from pydantic import BaseModel

from dasl_api import (
    WorkspaceV1AdminConfig,
    WorkspaceV1AdminConfigSpec,
    WorkspaceV1AdminConfigSpecAuth,
    WorkspaceV1AdminConfigSpecAuthAppClientId,
    WorkspaceV1AdminConfigSpecAuthServicePrincipal,
)


class AdminConfig(BaseModel):
    """
    Basic configuration of a Workspace in order to support authentication
    using Databricks and to allow the control plane to make API calls to
    Databricks.

    Attributes:
        workspace_url (str):
            The Databricks URL for the Databricks workspace.
        app_client_id (str):
            The client ID used by this workspace to use in three-legged OAuth.
        service_principal_id (str):
            The Databricks client ID for an OAuth secret associated with the
            service principal.
        service_principal_secret (str):
            The Databricks client secret for an OAuth secret associated with
            the service principal.
    """

    workspace_url: str
    app_client_id: str
    service_principal_id: str
    service_principal_secret: str

    @staticmethod
    def from_api_obj(obj: WorkspaceV1AdminConfig) -> "AdminConfig":
        return AdminConfig(
            workspace_url=obj.spec.auth.host,
            app_client_id=obj.spec.auth.app_client_id.client_id,
            service_principal_id=obj.spec.auth.service_principal.client_id,
            service_principal_secret=obj.spec.auth.service_principal.secret,
        )

    def to_api_obj(self) -> WorkspaceV1AdminConfig:
        return WorkspaceV1AdminConfig(
            api_version="v1",
            kind="AdminConfig",
            spec=WorkspaceV1AdminConfigSpec(
                auth=WorkspaceV1AdminConfigSpecAuth(
                    host=self.workspace_url,
                    app_client_id=WorkspaceV1AdminConfigSpecAuthAppClientId(
                        client_id=self.app_client_id,
                    ),
                    service_principal=WorkspaceV1AdminConfigSpecAuthServicePrincipal(
                        client_id=self.service_principal_id,
                        secret=self.service_principal_secret,
                    ),
                )
            ),
        )
