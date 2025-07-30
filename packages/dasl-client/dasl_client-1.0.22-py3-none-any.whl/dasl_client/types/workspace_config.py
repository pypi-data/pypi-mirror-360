from pydantic import BaseModel
from typing import Dict, List, Optional

from dasl_api import (
    WorkspaceV1ExportConfig,
    WorkspaceV1ExportConfigSlackConfig,
    WorkspaceV1ExportConfigWebhookConfig,
    WorkspaceV1ExportConfigWebhookConfigDestination,
    WorkspaceV1WorkspaceConfig,
    WorkspaceV1WorkspaceConfigSpec,
    WorkspaceV1WorkspaceConfigSpecDefaultConfig,
    WorkspaceV1WorkspaceConfigSpecDetectionRuleMetadata,
    WorkspaceV1WorkspaceConfigSpecManagedRetentionInner,
    WorkspaceV1WorkspaceConfigSpecManagedRetentionInnerOverridesInner,
    WorkspaceV1WorkspaceConfigSpecObservables,
    WorkspaceV1WorkspaceConfigSpecObservablesKindsInner,
    WorkspaceV1WorkspaceConfigSpecSystemTablesConfig,
    WorkspaceV1DefaultConfig,
    WorkspaceV1DefaultConfigComputeGroupOverridesValue,
)

from .helpers import Helpers
from .types import Metadata, ResourceStatus


class ExportConfig(BaseModel):
    """
    Configuration settings for exporting notables, operational alerts, and
    other events.

    Attributes:
        destination (Optional[str]):
            Name of the destination. 'webhook' or 'slack'.
        export_open_only (Optional[bool]):
            If true, only open events are exported. If false, any event not
            in state ClosedAsExported  will be exported.
        webhook_config (Optional[ExportConfig.WebhookConfig]):
            Set when exporting to a webhook.
        slack_config (Optional[ExportConfig.SlackConfig]):
            Set when exporting to slack.
    """

    class WebhookDestination(BaseModel):
        """
        Configuration settings for exporting to a webhook.

        Attributes:
            value (Optional[str]):
            scope (Optional[str]):
            key (Optional[str]):
        """

        value: Optional[str] = None
        scope: Optional[str] = None
        key: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[WorkspaceV1ExportConfigWebhookConfigDestination],
        ) -> "ExportConfig.WebhookDestination":
            if obj is None:
                return None
            return ExportConfig.WebhookDestination(
                value=obj.value,
                scope=obj.scope,
                key=obj.key,
            )

        def to_api_obj(self) -> WorkspaceV1ExportConfigWebhookConfigDestination:
            return WorkspaceV1ExportConfigWebhookConfigDestination(
                value=self.value,
                scope=self.scope,
                key=self.key,
            )

    class WebhookConfig(BaseModel):
        """
        Configuration settings for exporting to a webhook.

        Attributes:
            destination (Optional[ExportConfig.WebhookDestination]):
        """

        destination: Optional["ExportConfig.WebhookDestination"] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[WorkspaceV1ExportConfigWebhookConfig],
        ) -> "ExportConfig.WebhookConfig":
            if obj is None:
                return None
            return ExportConfig.WebhookConfig(
                destination=ExportConfig.WebhookDestination.from_api_obj(
                    obj.destination
                )
            )

        def to_api_obj(self) -> WorkspaceV1ExportConfigWebhookConfig:
            if self.destination is None:
                return None
            return WorkspaceV1ExportConfigWebhookConfig(
                destination=self.destination.to_api_obj(),
            )

    class SlackConfig(BaseModel):
        """
        Configuration settings for exporting to Slack.

        Attributes:
            token (Optional[ExportConfig.WebhookDestination]):
            channel (Optional[str]):
            message (Optional[str]):
        """

        token: Optional["ExportConfig.WebhookDestination"] = None
        channel: Optional[str] = None
        message: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[WorkspaceV1ExportConfigSlackConfig],
        ) -> "ExportConfig.SlackConfig":
            if obj is None:
                return None
            return ExportConfig.SlackConfig(
                token=ExportConfig.WebhookDestination.from_api_obj(obj.token),
                channel=obj.channel,
                message=obj.message,
            )

        def to_api_obj(self) -> WorkspaceV1ExportConfigSlackConfig:
            token = None
            if self.token is not None:
                token = self.token.to_api_obj()
            return WorkspaceV1ExportConfigSlackConfig(
                token=token,
                channel=self.channel,
                message=self.message,
            )

    destination: Optional[str] = None
    export_open_only: Optional[bool] = None
    webhook_config: Optional["ExportConfig.WebhookConfig"] = None
    slack_config: Optional["ExportConfig.SlackConfig"] = None

    @staticmethod
    def from_api_obj(obj: Optional[WorkspaceV1ExportConfig]) -> "ExportConfig":
        if obj is None:
            return None
        return ExportConfig(
            destination=obj.destination,
            export_open_only=obj.export_open_only,
            webhook_config=ExportConfig.WebhookConfig.from_api_obj(obj.webhook_config),
            slack_config=ExportConfig.SlackConfig.from_api_obj(obj.slack_config),
        )

    def to_api_obj(self) -> WorkspaceV1ExportConfig:
        slack_config = None
        if self.slack_config is not None:
            slack_config = self.slack_config.to_api_obj()

        webhook_config = None
        if self.webhook_config is not None:
            webhook_config = self.webhook_config.to_api_obj()

        return WorkspaceV1ExportConfig(
            destination=self.destination,
            export_open_only=self.export_open_only,
            webhook_config=webhook_config,
            slack_config=slack_config,
        )


class WorkspaceConfigObservables(BaseModel):
    """
    Configuration of observables for the workspace.

    Attributes:
        kinds (Optional[List[ObservablesKinds]]):
        relationships (Optional[List[str]]):
    """

    class ObservablesKinds(BaseModel):
        """
        Configuration of a concrete kind of observable.

        Attributes:
            name (Optional[str]):
            sql_type (Optional[str]):
        """

        name: Optional[str] = None
        sql_type: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: WorkspaceV1WorkspaceConfigSpecObservablesKindsInner,
        ) -> "WorkspaceConfigObservables.ObservablesKinds":
            return WorkspaceConfigObservables.ObservablesKinds(
                name=obj.name,
                sql_type=obj.sql_type,
            )

        def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecObservablesKindsInner:
            return WorkspaceV1WorkspaceConfigSpecObservablesKindsInner(
                name=self.name,
                sql_type=self.sql_type,
            )

    kinds: Optional[List[ObservablesKinds]] = None
    relationships: Optional[List[str]] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[WorkspaceV1WorkspaceConfigSpecObservables],
    ) -> "WorkspaceConfigObservables":
        if obj is None:
            return None

        kinds = None
        if obj.kinds is not None:
            kinds = [
                WorkspaceConfigObservables.ObservablesKinds.from_api_obj(item)
                for item in obj.kinds
            ]
        return WorkspaceConfigObservables(
            kinds=kinds,
            relationships=obj.relationships,
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecObservables:
        kinds = None
        if self.kinds is not None:
            kinds = [item.to_api_obj() for item in self.kinds]
        return WorkspaceV1WorkspaceConfigSpecObservables(
            kinds=kinds,
            relationships=self.relationships,
        )


class DefaultConfig(BaseModel):
    """
    Configuration of the schemas, notebook storage locations, checkpoint
    storage locations, and so forth, for each concrete resource type and
    a global fallback that applies to resources which do not have a
    specified DefaultConfig.

    Attributes:
        datasources (Optional[DefaultConfig.Config]):
            Configuration that applies to DataSources. May be omitted.
        transforms (Optional[DefaultConfig.Config]):
            Configuration that applies to Transforms. May be omitted.
        rules (Optional[DefaultConfig.Config]):
            Configuration that applies to Rules. May be omitted.
        var_global (Optional[DefaultConfig.Config]):
            Configuration that applies globally to resources without a
            resource-specific configuration specified. Must be specified.
    """

    class Config(BaseModel):
        """
        Default configuration for a specific resource type.

        Attributes:
            notebook_location (Optional[str]):
                A location for user created/edited/provided notebook.
            bronze_schema (Optional[str]):
                Name of the bronze schema in the catalog.
            silver_schema (Optional[str]):
                Name of the silver schema in the catalog.
            gold_schema (Optional[str]):
                Name of the gold schema in the catalog.
            catalog_name (Optional[str]):
                The catalog name to use as the resource's default.
            default_max_resources_per_job (Optional[int]):
                Default maximum number of resources that can be placed into
                a single job, subject to compute_group_overrides.
            checkpoint_location (Optional[str]):
                The location to store checkpoints for streaming writes. If
                not provided, the daslStoragePath will be used.
            compute_group_overrides (Optional[Dict[str, DefaultConfig.Config.ComputeGroupOverrides]]):
                Overrides for the maximum number of resources that can be
                placed into a single job, keyed by the compute group name.
        """

        class ComputeGroupOverrides(BaseModel):
            """
            Specifies the maximum number of resources that can be placed
            into a single job.

            Attributes:
                max_resources_per_job (Optional[int]):
                    The maximum number of resources that can be placed into a
                    job before a new job will be created.
            """

            max_resources_per_job: Optional[int] = None

            @staticmethod
            def from_api_obj(
                obj: Optional["DefaultConfig.Config.ComputeGroupOverrides"],
            ) -> "DefaultConfig.Config.ComputeGroupOverrides":
                return DefaultConfig.Config.ComputeGroupOverrides(
                    max_resources_per_job=obj.max_resources_per_job,
                )

            def to_api_obj(self) -> WorkspaceV1DefaultConfigComputeGroupOverridesValue:
                return WorkspaceV1DefaultConfigComputeGroupOverridesValue(
                    max_resources_per_job=self.max_resources_per_job,
                )

        notebook_location: Optional[str] = None
        bronze_schema: Optional[str] = None
        silver_schema: Optional[str] = None
        gold_schema: Optional[str] = None
        catalog_name: Optional[str] = None
        default_max_resources_per_job: Optional[int] = None
        checkpoint_location: Optional[str] = None
        compute_group_overrides: Optional[
            Dict[str, "DefaultConfig.Config.ComputeGroupOverrides"]
        ] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[WorkspaceV1DefaultConfig],
        ) -> "DefaultConfig.Config":
            if obj is None:
                return None

            compute_group_overrides = None
            if obj.compute_group_overrides is not None:
                compute_group_overrides = {
                    key: DefaultConfig.Config.ComputeGroupOverrides.from_api_obj(value)
                    for key, value in obj.compute_group_overrides.items()
                }
            return DefaultConfig.Config(
                notebook_location=obj.notebook_location,
                bronze_schema=obj.bronze_schema,
                silver_schema=obj.silver_schema,
                gold_schema=obj.gold_schema,
                catalog_name=obj.catalog_name,
                default_max_resources_per_job=obj.default_max_resources_per_job,
                checkpoint_location=obj.checkpoint_location,
                compute_group_overrides=compute_group_overrides,
            )

        def to_api_obj(self) -> WorkspaceV1DefaultConfig:
            compute_group_overrides = None
            if self.compute_group_overrides is not None:
                compute_group_overrides = {
                    key: value.to_api_obj()
                    for key, value in self.compute_group_overrides.items()
                }
            return WorkspaceV1DefaultConfig(
                notebook_location=self.notebook_location,
                bronze_schema=self.bronze_schema,
                silver_schema=self.silver_schema,
                gold_schema=self.gold_schema,
                catalog_name=self.catalog_name,
                default_max_resources_per_job=self.default_max_resources_per_job,
                checkpoint_location=self.checkpoint_location,
                compute_group_overrides=compute_group_overrides,
            )

    datasources: Optional["DefaultConfig.Config"] = None
    transforms: Optional["DefaultConfig.Config"] = None
    rules: Optional["DefaultConfig.Config"] = None
    var_global: Optional["DefaultConfig.Config"] = None

    @staticmethod
    def from_api_obj(
        obj: WorkspaceV1WorkspaceConfigSpecDefaultConfig,
    ) -> "DefaultConfig":
        return DefaultConfig(
            datasources=DefaultConfig.Config.from_api_obj(obj.datasources),
            transforms=DefaultConfig.Config.from_api_obj(obj.transforms),
            rules=DefaultConfig.Config.from_api_obj(obj.rules),
            var_global=DefaultConfig.Config.from_api_obj(obj.var_global),
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecDefaultConfig:
        datasources = None
        if self.datasources is not None:
            datasources = self.datasources.to_api_obj()

        transforms = None
        if self.transforms is not None:
            transforms = self.transforms.to_api_obj()

        rules = None
        if self.rules is not None:
            rules = self.rules.to_api_obj()

        var_global = None
        if self.var_global is not None:
            var_global = self.var_global.to_api_obj()

        return WorkspaceV1WorkspaceConfigSpecDefaultConfig(
            datasources=datasources,
            transforms=transforms,
            rules=rules,
            var_global=var_global,
        )


class ManagedRetention(BaseModel):
    """
    Configuration of cleanup jobs for old data stored by DASL.

    Attributes:
        catalog (str):
            The name of the catalog.
        var_schema (str):
            The name of the schema.
        column (Optional[str]):
            The name of the column.
        duration (Optional[str]):
            The duration for which to retain data in the schema. It may also
            be "forever" to indicate data should not be deleted.
        overrides (Optional[List[ManagedRetention.Overrides]]):
            Overrides for per-table retention rules within the specified
            catalog and schema.
    """

    class Overrides(BaseModel):
        """
        Per-table retention override settings.

        Attributes:
            table (str):
                The name of the table in the catalog and schema.
            column (Optional[str]):
                The name of the column.
            duration (Optional[str]):
                The duration for which to retain data in the table. It may
                also be "forever" to indicate data should not be deleted.
        """

        table: str
        column: Optional[str] = None
        duration: Optional[str] = None  # TODO: consider using duration type?

        @staticmethod
        def from_api_obj(
            obj: WorkspaceV1WorkspaceConfigSpecManagedRetentionInnerOverridesInner,
        ) -> "ManagedRetention.Overrides":
            return ManagedRetention.Overrides(
                table=obj.table,
                column=obj.column,
                duration=obj.duration,
            )

        def to_api_obj(
            self,
        ) -> WorkspaceV1WorkspaceConfigSpecManagedRetentionInnerOverridesInner:
            return WorkspaceV1WorkspaceConfigSpecManagedRetentionInnerOverridesInner(
                table=self.table,
                column=self.column,
                duration=self.duration,
            )

    catalog: str
    var_schema: str
    column: Optional[str] = None
    duration: Optional[str] = None
    overrides: Optional[List["ManagedRetention.Overrides"]] = None

    @staticmethod
    def from_api_obj(
        obj: WorkspaceV1WorkspaceConfigSpecManagedRetentionInner,
    ) -> "ManagedRetention":
        overrides = None
        if obj.overrides is not None:
            overrides = [
                ManagedRetention.Overrides.from_api_obj(item) for item in obj.overrides
            ]
        return ManagedRetention(
            catalog=obj.catalog,
            var_schema=obj.var_schema,
            column=obj.column,
            duration=obj.duration,
            overrides=overrides,
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecManagedRetentionInner:
        overrides = None
        if self.overrides is not None:
            overrides = [item.to_api_obj() for item in self.overrides]
        return WorkspaceV1WorkspaceConfigSpecManagedRetentionInner(
            catalog=self.catalog,
            var_schema=self.var_schema,
            column=self.column,
            duration=self.duration,
            overrides=overrides,
        )


class SystemTablesConfig(BaseModel):
    """
    Specifies where system data (i.e. metadata managed by the DASL
    control plane) will be stored.

    Attributes:
        catalog_name (str):
            The name of the catalog in which to store data.
        var_schema (str):
            The name of the schema in which to create tables.
    """

    catalog_name: str
    var_schema: str

    @staticmethod
    def from_api_obj(
        obj: WorkspaceV1WorkspaceConfigSpecSystemTablesConfig,
    ) -> "SystemTablesConfig":
        return SystemTablesConfig(
            catalog_name=obj.catalog_name,
            var_schema=obj.var_schema,
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecSystemTablesConfig:
        return WorkspaceV1WorkspaceConfigSpecSystemTablesConfig(
            catalog_name=self.catalog_name,
            var_schema=self.var_schema,
        )


class DetectionRuleMetadata(BaseModel):
    """
    DetectionRuleMetadata

    Attributes:
        detection_categories (Optional[List[str]]):
    """

    detection_categories: Optional[List[str]] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[WorkspaceV1WorkspaceConfigSpecDetectionRuleMetadata],
    ) -> "DetectionRuleMetadata":
        if obj is None:
            return None
        return DetectionRuleMetadata(
            detection_categories=obj.detection_categories,
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfigSpecDetectionRuleMetadata:
        return WorkspaceV1WorkspaceConfigSpecDetectionRuleMetadata(
            detection_categories=self.detection_categories,
        )


class WorkspaceConfig(BaseModel):
    """
    General configuration settings for the Workspace.

    Attributes:
        metadata (Optional[Metadata]):
            Common resource metadata; generally managed by the control plane.
        system_tables_config (SystemTablesConfig):
            Configuration for the storage of metadata by the control plane.
        default_sql_warehouse (Optional[str]):
            Default SQL warehouse to use for executing certain queries. May
            be overridden in some cases.
        detection_rule_metadata (Optional[DetectionRuleMetadata]):
            Detection rule metadata.
        notable_export (Optional[ExportConfig]):
            Settings related to the export of notables to various destinations.
        operational_alert_export (Optional[ExportConfig]):
            Settings related to the export of operational alerts to various
            destinations.
        observables (Optional[WorkspaceConfigObservables]):
            Declaration of the types of observables generated by the system.
        dasl_storage_path (Optional[str]):
            The path to a directory where DASL can store internal files and
            state.
        dasl_custom_presets_path (Optional[str]):
            An optional path to a directory containing user defined presets.
        default_config (Optional[DefaultConfig]):
            Configuration settings regarding storage of bronze, silver, and
            gold tables and related assets for each resource type.
        managed_retention (Optional[List[ManagedRetention]]):
            Configuration of regular cleanup (i.e. pruning) jobs for various
            catalogs, schemas, and tables.
        status (Optional[ResourceStatus]):
            Common resource status; wholly managed by the control plane.
    """

    metadata: Optional[Metadata] = None
    system_tables_config: SystemTablesConfig
    default_sql_warehouse: Optional[str] = None
    detection_rule_metadata: Optional[DetectionRuleMetadata] = None
    notable_export: Optional[ExportConfig] = None
    operational_alert_export: Optional[ExportConfig] = None
    observables: Optional[WorkspaceConfigObservables] = None
    dasl_storage_path: Optional[str] = None
    dasl_custom_presets_path: Optional[str] = None
    default_config: Optional[DefaultConfig] = None
    managed_retention: Optional[List[ManagedRetention]] = None
    status: Optional[ResourceStatus] = None

    @staticmethod
    def from_api_obj(obj: WorkspaceV1WorkspaceConfig) -> "WorkspaceConfig":
        spec = obj.spec

        managed_retention = None
        if spec.managed_retention is not None:
            managed_retention = [
                ManagedRetention.from_api_obj(item) for item in spec.managed_retention
            ]

        return WorkspaceConfig(
            metadata=Metadata.from_api_obj(obj.metadata),
            system_tables_config=SystemTablesConfig.from_api_obj(
                spec.system_tables_config
            ),
            default_sql_warehouse=spec.default_sql_warehouse,
            detection_rule_metadata=DetectionRuleMetadata.from_api_obj(
                spec.detection_rule_metadata
            ),
            notable_export=ExportConfig.from_api_obj(spec.notable_export),
            operational_alert_export=ExportConfig.from_api_obj(
                spec.operational_alert_export
            ),
            observables=WorkspaceConfigObservables.from_api_obj(spec.observables),
            dasl_storage_path=spec.dasl_storage_path,
            dasl_custom_presets_path=spec.dasl_custom_presets_path,
            default_config=DefaultConfig.from_api_obj(spec.default_config),
            managed_retention=managed_retention,
            status=ResourceStatus.from_api_obj(obj.status),
        )

    def to_api_obj(self) -> WorkspaceV1WorkspaceConfig:

        managed_retention = None
        if self.managed_retention is not None:
            managed_retention = [item.to_api_obj() for item in self.managed_retention]

        to_api_obj = lambda o: o.to_api_obj()

        return WorkspaceV1WorkspaceConfig(
            api_version="v1",
            kind="WorkspaceConfig",
            metadata=Helpers.maybe(to_api_obj, self.metadata),
            spec=WorkspaceV1WorkspaceConfigSpec(
                system_tables_config=self.system_tables_config.to_api_obj(),
                default_sql_warehouse=self.default_sql_warehouse,
                detection_rule_metadata=Helpers.maybe(
                    to_api_obj, self.detection_rule_metadata
                ),
                notable_export=Helpers.maybe(to_api_obj, self.notable_export),
                operational_alert_export=Helpers.maybe(
                    to_api_obj, self.operational_alert_export
                ),
                observables=Helpers.maybe(to_api_obj, self.observables),
                dasl_storage_path=self.dasl_storage_path,
                dasl_custom_presets_path=self.dasl_custom_presets_path,
                default_config=Helpers.maybe(to_api_obj, self.default_config),
                managed_retention=managed_retention,
            ),
            status=Helpers.maybe(to_api_obj, self.status),
        )
