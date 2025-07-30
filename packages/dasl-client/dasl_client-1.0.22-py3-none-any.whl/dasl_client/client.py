from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Callable, Iterator, List, Optional, Tuple, TypeVar
from pydantic import Field
from pyspark.sql import DataFrame

from dasl_api import (
    CoreV1Api,
    DbuiV1Api,
    ContentV1Api,
    WorkspaceV1Api,
    WorkspaceV1CreateWorkspaceRequest,
    api,
)
from dasl_client.auth.auth import (
    Authorization,
    DatabricksSecretAuth,
    DatabricksTokenAuth,
    ServiceAccountKeyAuth,
)
from dasl_client.conn.conn import get_base_conn
from dasl_client.errors.errors import ConflictError, error_handler
from .helpers import Helpers

from .types import (
    AdminConfig,
    DataSource,
    Dbui,
    Metadata,
    Rule,
    WorkspaceConfig,
    TransformRequest,
    TransformResponse,
    DataSourcePresetsList,
    DataSourcePreset,
)


T = TypeVar("T")


class Client:
    """
    Antimatter security lakehouse client.
    """

    def __init__(
        self,
        auth: Authorization,
    ):
        """
        Initialize a new client. You should generally prefer to use
        the new_workspace function if creating a new workspace or the
        for_workspace function if connecting to an existing workspace.

        :param auth: Authorization instance for authorizing requests to
            the dasl control plane.
        :returns: Client
        """
        self.auth = auth

    @staticmethod
    def new_workspace(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Register a new workspace and return a client for it.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, an
            exception will be raised.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns: Client for the newly created workspace.
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()
            admin_config = AdminConfig(
                workspace_url=workspace_url,
                app_client_id=app_client_id,
                service_principal_id=service_principal_id,
                service_principal_secret=service_principal_secret,
            )
            workspace_name = Helpers.workspace_name_from_url(workspace_url)
            api_key = (
                api.WorkspaceV1Api(api_client=get_base_conn(host=dasl_host))
                .workspace_v1_create_workspace(
                    WorkspaceV1CreateWorkspaceRequest(
                        admin_user=admin_email,
                        workspace_name=workspace_name,
                        admin_config=admin_config.to_api_obj().spec,
                    )
                )
                .admin_service_account.apikey
            )
            return Client(
                ServiceAccountKeyAuth(workspace_name, api_key, host=dasl_host),
            )

    # TODO: should we allow user to use an API key here?
    @staticmethod
    def for_workspace(
        workspace_url: Optional[str] = None,
        service_account_token: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Create a client for the argument workspace, if specified, or
        the current workspace if running in databricks notebook context.

        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise,
            an exception will be raised.
        :param service_account_token: Antimatter service account token.
            If provided, the client will use this token for auth instead
            of (automatic) secret-based auth.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns: Client for the existing workspace.
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()

            if service_account_token is None:
                return Client(
                    DatabricksSecretAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        host=dasl_host,
                    ),
                )
            else:
                return Client(
                    ServiceAccountKeyAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        service_account_token,
                        host=dasl_host,
                    )
                )

    @staticmethod
    def new_or_existing(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        service_account_token: Optional[str] = None,
        dasl_host: str = Helpers.default_dasl_host,
    ) -> "Client":
        """
        Initialize a new client for the workspace associated with the
        argument Databricks workspace_url. If no such workspace exists,
        one will be created for you.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created. Ignored if
            the workspace already exists.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace. If
            the workspace already exists, the existing config will be
            updated to use this client ID.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
            If the workspace already exists, the existing config will be
            updated to use this service principal ID.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf. If the workspace already exists, the existing config
            will be updated to use this service principal secret.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, an
            exception will be raised. If the workspace already exists, the
            existing config will be updated to use this value.
        :param service_account_token: Antimatter service account token.
            If provided, the client will use this token for auth instead
            of (automatic) secret-based auth. Ignored if the workspace
            doesn't exist.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified unless you are testing against
            an alternative environment.
        :returns: Client for the newly created or existing workspace.
        """
        try:
            return Client.new_workspace(
                admin_email,
                app_client_id,
                service_principal_id,
                service_principal_secret,
                workspace_url,
                dasl_host,
            )
        except ConflictError:
            result = Client.for_workspace(
                workspace_url, service_account_token, dasl_host
            )
            result.put_admin_config(
                AdminConfig(
                    workspace_url=workspace_url,
                    app_client_id=app_client_id,
                    service_principal_id=service_principal_id,
                    service_principal_secret=service_principal_secret,
                )
            )
            return result

    def _workspace_client(self) -> WorkspaceV1Api:
        return WorkspaceV1Api(self.auth.client())

    def _core_client(self) -> CoreV1Api:
        return CoreV1Api(self.auth.client())

    def _dbui_client(self) -> DbuiV1Api:
        return DbuiV1Api(self.auth.client())

    def _content_client(self) -> ContentV1Api:
        return ContentV1Api(self.auth.client())

    def _workspace(self) -> str:
        return self.auth.workspace()

    def _list_iter_paginated(
        self,
        list_func: Callable[..., Any],
        convert: Callable[[Any], T],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Iterator[T]:
        """
        Generic helper for paginated list functions.
        """
        current_cursor = cursor
        results_so_far = 0
        while True:
            page_limit = limit - results_so_far if limit is not None else None
            if limit is not None and page_limit <= 0:
                break

            with error_handler():
                response = list_func(
                    workspace=self._workspace(),
                    cursor=current_cursor,
                    limit=page_limit,
                )

            for item in response.items:
                yield convert(item)
                results_so_far += 1

            current_cursor = (
                response.metadata.cursor if hasattr(response, "metadata") else None
            )
            if current_cursor is None:
                break

    def get_admin_config(self) -> AdminConfig:
        """
        Retrieve the AdminConfig from the DASL server. Note that the
        service principal secret will be redacted server side, so if you
        plan to make changes and issue a request using put_admin_config,
        you will need to repopulate the service_principal_secret correctly
        before passing the result back to put_admin_config.

        :returns: AdminConfig containing the current settings.
        """
        with error_handler():
            return AdminConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_admin_config(
                    self._workspace()
                )
            )

    def put_admin_config(
        self,
        config: AdminConfig,
    ) -> None:
        """
        Update the AdminConfig stored in the DASL server. See the AdminConfig
        docs for details about its contents.

        :param config: AdminConfig to replace the existing. Note that the
            service principal credentials will be verified server side before
            the request is accepted.
        """
        with error_handler():
            self._workspace_client().workspace_v1_put_admin_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_config(self) -> WorkspaceConfig:
        """
        Retrieve the WorkspaceConfig from the DASL server. The returned
        value can be updated directly and passed to put_config in order
        to make changes.

        :returns: WorkspaceConfig containing the current configuration.
        """
        with error_handler():
            return WorkspaceConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_config(self._workspace())
            )

    def put_config(
        self,
        config_in: WorkspaceConfig,
    ) -> None:
        """
        Update the WorkspaceConfig stored in the DASL server. See the
        WorkspaceConfig docs for dtails about its contents.

        :param config_in: WorkspaceConfig to replace the existing.
        :returns: WorkspaceConfig. Note that the returned value is a
            clone of config_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            config = deepcopy(config_in)
            if config.metadata is None:
                config.metadata = Metadata(
                    name="config",
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            config.metadata.version = None

            self._workspace_client().workspace_v1_put_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_datasource(self, name: str) -> DataSource:
        """
        Get the DataSource with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_datasource
        in order to make changes.

        :param name: The unique name of the DataSource within this workspace
        :returns: DataSource
        """
        with error_handler():
            return DataSource.from_api_obj(
                self._core_client().core_v1_get_data_source(self._workspace(), name)
            )

    def delete_datasource(self, name: str) -> None:
        """
        Delete the DataSource with the argument name from the DASL server.
        The DataSource will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the DataSource within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_data_source(self._workspace(), name)

    def list_datasources(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> Iterator[DataSource]:
        """
        List the DataSources in this workspace. Each yielded DataSource
        contains all fields in the DataSource as if it were fetched
        using the get_datasource method.

        :param cursor: The ID of a DataSource. If specified, the results
            will contain DataSources starting (lexically) directly after
            this DataSource. If not specified, then the results will begin
            with the lexically least DataSource.
        :param limit: The maximum number of DataSources to yield. If there
            are fewer than this number of DataSources beginning directly
            after `cursor`, then all such DataSources will be yielded. If
            not specified, then all DataSources starting directly after
            `cursor` will be returned.
        :yields DataSource: One DataSource at a time in lexically
            increasing order
        """
        return self._list_iter_paginated(
            list_func=self._core_client().core_v1_list_data_sources,
            convert=DataSource.from_api_obj,
            cursor=cursor,
            limit=limit,
        )

    def create_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Create a new DataSource. The chosen name must be unique for your
        workspace, and cannot refer to a DataSource that already exists
        and has not been deleted. See the documentation for delete_datasource
        as there are some caveats around name reuse.

        :param name: The unique name of this DataSource in the workspace.
        :param ds_in: The specification of the DataSource to create. See
            the documentation for the DataSource type for more details.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_data_source(
                self._workspace(), ds.to_api_obj()
            )
            return DataSource.from_api_obj(result)

    def replace_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Replace an existing DataSource. The name must refer to a DataSource
        that already exists in your workspace.

        :param name: The name of the existing DataSource to replace.
        :param ds_in: The specification of the DataSource taking the place
            of the existing DataSource.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            ds.metadata.version = None

            result = self._core_client().core_v1_replace_data_source(
                self._workspace(),
                name,
                ds.to_api_obj(),
            )
            return DataSource.from_api_obj(result)

    def get_rule(self, name: str) -> Rule:
        """
        Get the Rule with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_rule
        in order to make changes.

        :param name: The unique name of the Rule within this workspace
        :returns: Rule
        """
        with error_handler():
            return Rule.from_api_obj(
                self._core_client().core_v1_get_rule(self._workspace(), name)
            )

    def delete_rule(self, name: str) -> None:
        """
        Delete the Rule with the argument name from the DASL server.
        The Rule will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the Rule within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_rule(self._workspace(), name)

    def list_rules(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> Iterator[Rule]:
        """
        List the Rules in this workspace. Each yielded Rule contains
        all fields in the Rule as if it were fetched using the
        get_rule method.

        :param cursor: The ID of a Rule. If specified, the results will
            contain DataSources starting (lexically) directly after this
            Rule. If not specified, then the results will begin with the
            lexically least Rule.
        :param limit: The maximum number of Rules to yield. If there are
            fewer than this number of Rules beginning directly after
            `cursor`, then all such Rules will be yielded. If not specified,
            then all Rules starting directly after `cursor` will be returned.
        :yields Rule: One Rule at a time in lexically increasing order.
        """
        return self._list_iter_paginated(
            list_func=self._core_client().core_v1_list_rules,
            convert=Rule.from_api_obj,
            cursor=cursor,
            limit=limit,
        )

    def create_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Create a new Rule. The chosen name must be unique for your
        workspace, and cannot refer to a Rule that already exists
        and has not been deleted. See the documentation for delete_rule
        as there are some caveats around name reuse.

        :param name: The unique name of this Rule in the workspace.
        :param rule_in: The specification of the Rule to create. See
            the documentation for the Rule type for more details.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_rule(
                self._workspace(), rule.to_api_obj()
            )
            return Rule.from_api_obj(result)

    def replace_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Replace an existing Rule. The name must refer to a Rule
        that already exists in your workspace.

        :param name: The name of the existing Rule to replace.
        :param rule_in: The specification of the Rule taking the place
            of the existing Rule.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            rule.metadata.version = None

            result = self._core_client().core_v1_replace_rule(
                self._workspace(),
                name,
                rule.to_api_obj(),
            )
        return Rule.from_api_obj(result)

    def exec_rule(
        self, rule_in: Rule, df: DataFrame
    ) -> Tuple[DataFrame, Optional[DataFrame]]:
        """
        Locally execute a Rule. Must be run from within a Databricks
        notebook or else an exception will be raised. This is intended
        to facilitate Rule development.

        :param rule_in: The specification of the Rule to execute.
        :param df: The DataFrame to use as the input to the Rule.
        :returns Tuple[DataFrame, Optional[DataFrame]]: The first
            element of the tuple contains the notables produced by
            the rule, and the second element contains the observables
            or None if no observables were produced.
        """
        Helpers.ensure_databricks()
        with error_handler():
            result = self._core_client().core_v1_render_rule(
                self._workspace(),
                rule_in.to_api_obj(),
            )

            try:
                import notebook_utils
            except ImportError as e:
                raise ImportError(
                    "Package 'notebook_utils' not found. "
                    "Install it within this this notebook using "
                    f"%pip install {result.notebook_utils_path}"
                )

            namespace = {}
            exec(result.content, namespace)
            return namespace["generate"](df)

    def adhoc_transform(
        self,
        warehouse: str,
        request: TransformRequest,
        timeout: timedelta = timedelta(minutes=5),
    ) -> TransformResponse:
        """
        Run a sequence of ADHOC transforms against a SQL warehouse to
        mimic the operations performed by a datasource.

        :param warehouse: The warehouse ID to run the transforms against.
        :param request: The request containing the transforms to run.
        :return: a TransformResponse object containing the results
            after running the transforms.
        :raises: NotFoundError if the rule does not exist
        :raises: Exception for a server-side error or timeout
        """
        with error_handler():
            status = self._dbui_client().dbui_v1_transform(
                self._workspace(),
                warehouse,
                request.to_api_obj(),
            )

            begin = datetime.now()
            while datetime.now() - begin < timeout:
                sleep(5)
                status = self._dbui_client().dbui_v1_transform_status(
                    self._workspace(), status.id
                )

                if status.status == "failure":
                    raise Exception(f"adhoc transform failed with {status.error}")
                elif status.status == "success":
                    return TransformResponse.from_api_obj(status.result)

            raise Exception("timed out waiting for adhoc transform result")

    def get_observable_events(
        self,
        warehouse: str,
        kind: str,
        value: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dbui.ObservableEvents.EventsList:
        """
        Get the observable events associated with a specific field and value.

        :param warehouse: The warehouse id to perform the operation on
        :param kind: The observable kind
        :param value: The observable value
        :param cursor: A cursor to be used when paginating results
        :param limit: A limit of the number of results to return
        :returns: EventsList
        """
        with error_handler():
            return Dbui.ObservableEvents.EventsList.from_api_obj(
                self._dbui_client().dbui_v1_get_observable_events(
                    self._workspace(),
                    warehouse=warehouse,
                    kind=kind,
                    value=value,
                    cursor=cursor,
                    limit=limit,
                )
            )

    def list_presets(self) -> DataSourcePresetsList:
        """
        List the Presets in this workspace. This will include any user defined
        presets if a custom presets path has been configured in the workspace.

        :returns: DataSourcePresetsList
        """
        with error_handler():
            return DataSourcePresetsList.from_api_obj(
                self._content_client().content_v1_get_preset_data_sources(
                    self._workspace(),
                )
            )

    def get_preset(self, name: str) -> DataSourcePreset:
        """
        Get the preset with the argument name from the DASL server. If the preset name
        begins with 'internal_' it will instead be collected from the user catalog,
        provided a preset path is set in the workspace config.

        :param name: The unique name of the DataSource preset within this workspace.
        :returns: DataSourcePreset
        """
        with error_handler():
            return DataSourcePreset.from_api_obj(
                self._content_client().content_v1_get_preset_datasource(
                    self._workspace(), name
                )
            )

    def purge_preset_cache(self) -> None:
        """
        Purge the datasource cache presets. This will cause the DASL workspace
        to fetch presets from provided sources.
        """
        with error_handler():
            self._content_client().content_v1_preset_purge_cache(self._workspace())
