from typing import Optional, List, Dict
from pydantic import BaseModel

from dasl_api import (
    DbuiV1ObservableEventsList,
    DbuiV1ObservableEventsListItemsInnerNotable,
    DbuiV1ObservableEventsListItemsInner,
    DbuiV1TransformRequest,
    DbuiV1TransformRequestInput,
    DbuiV1TableColumnDetails,
    DbuiV1TransformRequestTransformsInner,
    DbuiV1TransformRequestTransformsInnerPresetOverrides,
    DbuiV1TransformResponse,
    DbuiV1TransformResponseStagesInner,
    ContentV1DatasourcePresetAutoloaderCloudFiles,
    DbuiV1TransformRequestAutoloaderInput,
)

from .datasource import DataSource, FieldSpec, FieldUtils
from .helpers import Helpers


class Dbui(BaseModel):
    class TableColumnDetails(BaseModel):
        """
        Table column details.

        Attributes:
            name (Optional[str]):
                The column name.
            type_name (Optional[str]):
                The name of the column type.
            type_detail (Optional[str]):
                Additional information about the column's type.
            position (Optional[int]):
                The column's index in the table.
            nullable (Optional[bool]):
                Indicates if this column is nullable.
        """

        name: Optional[str] = None
        type_name: Optional[str] = None
        type_detail: Optional[str] = None
        position: Optional[int] = None
        nullable: Optional[bool] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[DbuiV1TableColumnDetails],
        ) -> Optional["Dbui.TableColumnDetails"]:
            if obj is None:
                return None
            return Dbui.TableColumnDetails(
                name=obj.name,
                type_name=obj.type_name,
                type_detail=obj.type_detail,
                position=obj.position,
                nullable=obj.nullable,
            )

        def to_api_obj(self) -> DbuiV1TableColumnDetails:
            return DbuiV1TableColumnDetails(
                name=self.name,
                type_name=self.type_name,
                type_detail=self.type_detail,
                position=self.position,
                nullable=self.nullable,
            )

    class ObservableEvents(BaseModel):
        class Notable(BaseModel):
            id: Optional[str] = None
            rule_name: Optional[str] = None
            summary: Optional[str] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsListItemsInnerNotable],
            ) -> Optional["Dbui.ObservableEvents.Notable"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.Notable(
                    id=obj.id, rule_name=obj.rule_name, summary=obj.summary
                )

        class Event(BaseModel):
            var_from: Optional[str] = None
            adjust_by: Optional[float] = None
            notable: Optional["Dbui.ObservableEvents.Notable"] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsListItemsInner],
            ) -> Optional["Dbui.ObservableEvents.Event"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.Event(
                    var_from=obj.var_from,
                    adjust_by=obj.adjust_by,
                    notable=Dbui.ObservableEvents.Notable.from_api_obj(obj.notable),
                )

        class EventsList(BaseModel):
            cursor: Optional[str] = None
            items: List["Dbui.ObservableEvents.Event"] = []

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1ObservableEventsList],
            ) -> Optional["Dbui.ObservableEvents.EventsList"]:
                if obj is None:
                    return None

                return Dbui.ObservableEvents.EventsList(
                    cursor=obj.cursor,
                    items=[
                        Dbui.ObservableEvents.Event.from_api_obj(item)
                        for item in obj.items
                    ],
                )


class TransformRequest(BaseModel):
    """
    The transform request identifies the starting data (either with an
    autoloader spec or an input block) and then specifies a chain of
    transforms to be performed on the data. The response includes the data
    at each intermediate stage (e.g. input/autoloaded data, pre-transform,
    silver).

    Attributes:
        input (TransformRequest.Input):
            The input block containing the columns metadata and data.
        autoloader_input (Autoloader):
            The autoloader input configuration.
        use_preset (str):
            Indicates which preset to use for the transforms.
        transforms (List[TransformRequest.Transform]):
            A list of transform configurations.
    """

    class Input(BaseModel):
        """
        Input data for the transform request.

        Attributes:
            columns (List[Dbui.TableColumnDetails]):
                A list of metadata about the columns.
            data (List[Dict[str, str]]):
                The data represented as a list of dictionaries.
        """

        columns: List[Dbui.TableColumnDetails]
        data: List[Dict[str, str]]

        @staticmethod
        def from_api_obj(
            obj: Optional[DbuiV1TransformRequestInput],
        ) -> Optional["TransformRequest.Input"]:
            if obj is None:
                return None
            return TransformRequest.Input(
                columns=[
                    Dbui.TableColumnDetails.from_api_obj(item) for item in obj.columns
                ],
                data=obj.data,
            )

        def to_api_obj(self) -> DbuiV1TransformRequestInput:
            return DbuiV1TransformRequestInput(
                columns=[item.to_api_obj() for item in self.columns],
                data=self.data,
            )

    class Autoloader(BaseModel):
        """
        Autoloader configuration for the DataSource.

        Attributes:
            format (Optional[str]):
                The format of the data (e.g., json, parquet, csv, etc.).
            location (str):
                External location for the volume in Unity Catalog.
            schema_file (Optional[str]):
                An optional file containing the schema of the data source.
            cloud_files (Optional[Autoloader.CloudFiles]):
                CloudFiles configuration.
        """

        class CloudFiles(BaseModel):
            """
            CloudFiles configuration for the Autoloader.

            Attributes:
                schema_hints_file (Optional[str]):
                schema_hints (Optional[str]):
            """

            schema_hints_file: Optional[str] = None
            schema_hints: Optional[str] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[ContentV1DatasourcePresetAutoloaderCloudFiles],
            ) -> "TransformRequest.Autoloader.CloudFiles":
                if obj is None:
                    return None
                return TransformRequest.Autoloader.CloudFiles(
                    schema_hints_file=obj.schema_hints_file,
                    schema_hints=obj.schema_hints,
                )

            def to_api_obj(self) -> ContentV1DatasourcePresetAutoloaderCloudFiles:
                return ContentV1DatasourcePresetAutoloaderCloudFiles(
                    schema_hints_file=self.schema_hints_file,
                    schema_hints=self.schema_hints,
                )

        format: Optional[str] = None
        location: str
        schema_file: Optional[str] = None
        var_schema: Optional[str] = None
        cloud_files: Optional["TransformRequest.Autoloader.CloudFiles"] = None
        row_count: Optional[int] = None
        row_offset: Optional[int] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[DbuiV1TransformRequestAutoloaderInput],
        ) -> "Optional[TransformRequest.Autoloader]":
            if obj is None:
                return None
            return TransformRequest.Autoloader(
                format=obj.format,
                location=obj.location,
                schema_file=obj.schema_file,
                var_schema=obj.var_schema,
                cloud_files=TransformRequest.Autoloader.CloudFiles.from_api_obj(
                    obj.cloud_files
                ),
                row_count=obj.row_count,
                row_offset=obj.row_offset,
            )

        def to_api_obj(self) -> DbuiV1TransformRequestAutoloaderInput:
            return DbuiV1TransformRequestAutoloaderInput(
                format=self.format,
                location=self.location,
                schemaFile=self.schema_file,
                schema=self.var_schema,
                cloudFiles=Helpers.maybe(lambda o: o.to_api_obj(), self.cloud_files),
                rowCount=self.row_count,
                rowOffset=self.row_offset,
            )

    class Transform(BaseModel):
        """
        A transform configuration to apply to the data.

        Attributes:
            transform_type (str):
                The type of transform (one of SilverPreTransform,
                SilverTransform, Gold).
            use_preset_table (str):
                Indicates which table to use within the preset's transform
                type for Silver and Gold.
            filter (str):
                Filter expression.
            post_filter (str):
                Filter expression applied after the transform.
            preset_overrides (TransformRequest.Transform.PresetOverrides):
                Overrides for the preset configuration.
            add_fields (List[FieldSpec]):
                Additional field specifications to add.
            utils (FieldUtils):
                Utility configurations for handling fields.
        """

        class PresetOverrides(BaseModel):
            """
            Preset overrides for a transform configuration.

            Attributes:
                omit_fields (List[str]):
                    A list of fields to omit from the preset.
            """

            omit_fields: Optional[List[str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[DbuiV1TransformRequestTransformsInnerPresetOverrides],
            ) -> Optional["TransformRequest.Transform.PresetOverrides"]:
                if obj is None:
                    return None
                return TransformRequest.Transform.PresetOverrides(
                    omit_fields=obj.omit_fields,
                )

            def to_api_obj(
                self,
            ) -> DbuiV1TransformRequestTransformsInnerPresetOverrides:
                return DbuiV1TransformRequestTransformsInnerPresetOverrides(
                    omit_fields=self.omit_fields,
                )

        transform_type: str
        use_preset_table: Optional[str] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None
        preset_overrides: Optional["TransformRequest.Transform.PresetOverrides"] = None
        add_fields: Optional[List[FieldSpec]] = None
        utils: Optional[FieldUtils] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[DbuiV1TransformRequestTransformsInner],
        ) -> Optional["TransformRequest.Transform"]:
            if obj is None:
                return None
            add_fields = None
            if obj.add_fields is not None:
                add_fields = [FieldSpec.from_api_obj(item) for item in obj.add_fields]
            return TransformRequest.Transform(
                transform_type=obj.transform_type,
                use_preset_table=obj.use_preset_table,
                filter=obj.filter,
                post_filter=obj.post_filter,
                preset_overrides=TransformRequest.Transform.PresetOverrides.from_api_obj(
                    obj.preset_overrides
                ),
                add_fields=add_fields,
                utils=FieldUtils.from_api_obj(obj.utils),
            )

        def to_api_obj(self) -> DbuiV1TransformRequestTransformsInner:
            add_fields = None
            if self.add_fields is not None:
                add_fields = [item.to_api_obj() for item in self.add_fields]
            to_api_obj = lambda o: o.to_api_obj()
            return DbuiV1TransformRequestTransformsInner(
                transform_type=self.transform_type,
                use_preset_table=self.use_preset_table,
                filter=self.filter,
                post_filter=self.post_filter,
                preset_overrides=Helpers.maybe(to_api_obj, self.preset_overrides),
                add_fields=add_fields,
                utils=Helpers.maybe(to_api_obj, self.utils),
            )

    input: Optional["TransformRequest.Input"] = None
    autoloader_input: Optional["TransformRequest.Autoloader"] = None
    use_preset: Optional[str] = None
    transforms: List["TransformRequest.Transform"]

    @staticmethod
    def from_api_obj(obj: DbuiV1TransformRequest) -> "TransformRequest":
        return TransformRequest(
            input=TransformRequest.Input.from_api_obj(obj.input),
            autoloader_input=TransformRequest.Autoloader.from_api_obj(
                obj.autoloader_input
            ),
            use_preset=obj.use_preset,
            transforms=[
                TransformRequest.Transform.from_api_obj(item) for item in obj.transforms
            ],
        )

    def to_api_obj(self) -> DbuiV1TransformRequest:
        to_api_obj = lambda o: o.to_api_obj()
        return DbuiV1TransformRequest(
            input=Helpers.maybe(to_api_obj, self.input),
            autoloader_input=Helpers.maybe(to_api_obj, self.autoloader_input),
            use_preset=self.use_preset,
            transforms=[item.to_api_obj() for item in self.transforms],
        )


class TransformResponse(BaseModel):
    """
    The transform response contains the results of the chain of transforms
    applied on the data.

    Attributes:
        stages (List[TransformResponse.Stages]):
            A list of stages representing each intermediate transform step.
    """

    class Stages(BaseModel):
        """
        A stage in the transform response.

        Attributes:
            transform_type (str):
                The type of transform applied in this stage (one of
                SilverPreTransform, SilverTransform, Gold, Input).
            columns (List[Dbui.TableColumnDetails]):
                A list of metadata about the columns returned in this stage.
            data (List[Dict[str, str]]):
                The data represented as a list of dictionaries.
        """

        transform_type: str
        columns: List[Dbui.TableColumnDetails]
        data: List[Dict[str, str]]

        @staticmethod
        def from_api_obj(
            obj: DbuiV1TransformResponseStagesInner,
        ) -> "TransformResponse.Stages":
            return TransformResponse.Stages(
                transform_type=obj.transform_type,
                columns=[
                    Dbui.TableColumnDetails.from_api_obj(item) for item in obj.columns
                ],
                data=obj.data,
            )

        def to_api_obj(self) -> DbuiV1TransformResponseStagesInner:
            return DbuiV1TransformResponseStagesInner(
                transform_type=self.transform_type,
                columns=[item.to_api_obj() for item in self.columns],
                data=self.data,
            )

    stages: List["TransformResponse.Stages"]

    @staticmethod
    def from_api_obj(obj: DbuiV1TransformResponse) -> "TransformResponse":
        return TransformResponse(
            stages=[TransformResponse.Stages.from_api_obj(item) for item in obj.stages],
        )

    def to_api_obj(self) -> DbuiV1TransformResponse:
        return DbuiV1TransformResponse(
            stages=[item.to_api_obj() for item in self.stages],
        )
