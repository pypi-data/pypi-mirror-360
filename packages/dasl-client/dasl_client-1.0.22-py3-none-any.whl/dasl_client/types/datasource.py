from pydantic import BaseModel
from typing import Dict, List, Optional

from dasl_api import (
    ContentV1DatasourcePresetAutoloaderCloudFiles,
    CoreV1DataSource,
    CoreV1DataSourceAutoloaderSpec,
    CoreV1DataSourceSpec,
    CoreV1DataSourceSpecCustom,
    CoreV1DataSourceSpecGold,
    CoreV1DataSourceSpecGoldPresetOverrides,
    CoreV1DataSourceSpecGoldPresetOverridesAddTablesInner,
    CoreV1DataSourceSpecGoldPresetOverridesAddTablesInnerCustom,
    CoreV1DataSourceSpecGoldPresetOverridesModifyTablesInner,
    CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom,
    CoreV1DataSourceSpecSilver,
    CoreV1DataSourceSpecSilverBronzeTablesInner,
    CoreV1DataSourceSpecSilverBronzeTablesInnerWatermark,
    CoreV1DataSourceSpecSilverPreTransform,
    CoreV1DataSourceSpecSilverPreTransformCustom,
    CoreV1DataSourceSpecSilverPreTransformPresetOverrides,
    CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInner,
    CoreV1DataSourceSpecSilverTransformPresetOverridesAddTablesInner,
    CoreV1DataSourceSpecSilverTransform,
    CoreV1DataSourceSpecSilverTransformPresetOverrides,
    CoreV1DataSourceSpecBronze,
    CoreV1DataSourceSpecBronzeClustering,
    CoreV1DataSourceFieldSpec,
    CoreV1DataSourceFieldSpecAssertInner,
    CoreV1DataSourceFieldSpecJoin,
    CoreV1DataSourceFieldSpecJoinWithCSV,
    CoreV1DataSourceFieldUtils,
    CoreV1DataSourceFieldUtilsUnreferencedColumns,
    CoreV1DataSourceFieldUtilsJsonExtractInner,
)

from .helpers import Helpers
from .types import Metadata, ResourceStatus, Schedule


class FieldSpec(BaseModel):
    """
    FieldSpec

    Attributes:
        name (Optional[str]):
            The name of the field.
        comment (Optional[str]):
            The comment to apply to the field.
        var_assert (Optional[List[FieldSpec.Assert]]):
            A list of SQL expressions that must evaluate to true for every
            processed row. If the assertion is false, an operational alert
            is raised using 'message' for each row.
        var_from (Optional[str]):
            This field obtains its value from the source column of this name.
            Use this to bring in a column from some upstream table.
        alias (Optional[str]):
            This field obtains its value from the destination (transformed)
            column of this name. Use this to alias a column from within the
            same table (ie. silver table). You cannot alias a column from
            some upstream table.
        expr (Optional[str]):
            This field obtains its value from the given SQL expression.
        literal (Optional[str]):
            This field obtains its value from the given literal string. For
            other data types, use expr.
        join (Optional[FieldSpec.Join]):
            This field obtains its value from joining to another table.
    """

    class Assert(BaseModel):
        """
        An assertion within a FieldSpec.

        Attributes:
            expr (Optional[str]):
                The SQL expression that must evaluate to true for every
                processed row.
            message (Optional[str]):
                The message to include in the operational alert if the
                assertion fails.
        """

        expr: Optional[str] = None
        message: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceFieldSpecAssertInner],
        ) -> "FieldSpec.Assert":
            if obj is None:
                return None
            return FieldSpec.Assert(
                expr=obj.expr,
                message=obj.message,
            )

        def to_api_obj(self) -> CoreV1DataSourceFieldSpecAssertInner:
            return CoreV1DataSourceFieldSpecAssertInner(
                expr=self.expr,
                message=self.message,
            )

    class Join(BaseModel):
        """
        A join expression within a FieldSpec.

        Attributes:
            with_table (Optional[str]):
                The table to join to.
            with_csv (Optional[FieldSpec.Join.WithCSV]):
                The CSV configuration used for the join.
            lhs (Optional[str]):
                The column in the source dataframe to join on.
            rhs (Optional[str]):
                The column in the joined table to join on.
            select (Optional[str]):
                A SQL expression to create the new field from the joined
                dataset.
        """

        class WithCSV(BaseModel):
            """
            A CSV file used for joins within a FieldSpec.

            Attributes:
                path (Optional[str]):
                    The path to the CSV file.
            """

            path: Optional[str] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1DataSourceFieldSpecJoinWithCSV],
            ) -> "FieldSpec.Join.WithCSV":
                if obj is None:
                    return None
                return FieldSpec.Join.WithCSV(path=obj.path)

            def to_api_obj(self) -> CoreV1DataSourceFieldSpecJoinWithCSV:
                return CoreV1DataSourceFieldSpecJoinWithCSV(path=self.path)

        with_table: Optional[str] = None
        with_csv: Optional["FieldSpec.Join.WithCSV"] = None
        lhs: Optional[str] = None
        rhs: Optional[str] = None
        select: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceFieldSpecJoin],
        ) -> "FieldSpec.Join":
            if obj is None:
                return None
            return FieldSpec.Join(
                with_table=obj.with_table,
                with_csv=FieldSpec.Join.WithCSV.from_api_obj(obj.with_csv),
                lhs=obj.lhs,
                rhs=obj.rhs,
                select=obj.select,
            )

        def to_api_obj(self) -> CoreV1DataSourceFieldSpecJoin:
            return CoreV1DataSourceFieldSpecJoin(
                with_table=self.with_table,
                with_csv=Helpers.maybe(lambda o: o.to_api_obj(), self.with_csv),
                lhs=self.lhs,
                rhs=self.rhs,
                select=self.select,
            )

    name: Optional[str] = None
    comment: Optional[str] = None
    var_assert: Optional[List["FieldSpec.Assert"]] = None
    var_from: Optional[str] = None
    alias: Optional[str] = None
    expr: Optional[str] = None
    literal: Optional[str] = None
    join: Optional["FieldSpec.Join"] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1DataSourceFieldSpec]) -> "FieldSpec":
        if obj is None:
            return None
        var_assert = None
        if obj.var_assert is not None:
            var_assert = [
                FieldSpec.Assert.from_api_obj(item) for item in obj.var_assert
            ]
        return FieldSpec(
            name=obj.name,
            comment=obj.comment,
            var_assert=var_assert,
            var_from=obj.var_from,
            alias=obj.alias,
            expr=obj.expr,
            literal=obj.literal,
            join=FieldSpec.Join.from_api_obj(obj.join),
        )

    def to_api_obj(self) -> CoreV1DataSourceFieldSpec:
        var_assert = None
        if self.var_assert is not None:
            var_assert = [item.to_api_obj() for item in self.var_assert]
        to_api_obj = lambda o: o.to_api_obj()
        return CoreV1DataSourceFieldSpec(
            name=self.name,
            comment=self.comment,
            var_assert=var_assert,
            var_from=self.var_from,
            alias=self.alias,
            expr=self.expr,
            literal=self.literal,
            join=Helpers.maybe(to_api_obj, self.join),
        )


class FieldUtils(BaseModel):
    """
    FieldUtils

    Attributes:
        unreferenced_columns (Optional[FieldUtils.UnreferencedColumns]):
            Defines whether columns not referenced in the FieldSpecs should
            be preserved or omitted.
        json_extract (Optional[List[FieldUtils.JsonExtract]]):
            A list of configurations for extracting JSON fields from a column.
    """

    class UnreferencedColumns(BaseModel):
        """
        Configuration related to unreferenced columns.

        Attributes:
            preserve (Optional[bool]):
                Indicates whether columns not referenced in the FieldSpecs
                should be preserved.
            embed_column (Optional[str]):
                Specifies a name for a new column to contain all unreferenced
                fields.
            omit_columns (Optional[List[str]]):
                Lists columns to exclude from the output.
            duplicate_prefix (Optional[str]):
                Adds a prefix to resolve ambiguous duplicate field names.
        """

        preserve: Optional[bool] = None
        embed_column: Optional[str] = None
        omit_columns: Optional[List[str]] = None
        duplicate_prefix: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceFieldUtilsUnreferencedColumns],
        ) -> "FieldUtils.UnreferencedColumns":
            if obj is None:
                return None
            return FieldUtils.UnreferencedColumns(
                preserve=obj.preserve,
                embed_column=obj.embed_column,
                omit_columns=obj.omit_columns,
                duplicate_prefix=obj.duplicate_prefix,
            )

        def to_api_obj(self) -> CoreV1DataSourceFieldUtilsUnreferencedColumns:
            return CoreV1DataSourceFieldUtilsUnreferencedColumns(
                preserve=self.preserve,
                embed_column=self.embed_column,
                omit_columns=self.omit_columns,
                duplicate_prefix=self.duplicate_prefix,
            )

    class JsonExtract(BaseModel):
        """
        Configuration for extracting JSON fields from table columns.

        Attributes:
            source (Optional[str]):
                The column name containing JSON string(s) to extract from.
            omit_fields (Optional[List[str]]):
                Specifies high-level fields to exclude from extraction.
            duplicate_prefix (Optional[str]):
                Adds a prefix to resolve duplicate field names during
                extraction.
            embed_column (Optional[str]):
                Specifies a column name to store the extracted JSON object.
        """

        source: Optional[str] = None
        omit_fields: Optional[List[str]] = None
        duplicate_prefix: Optional[str] = None
        embed_column: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceFieldUtilsJsonExtractInner],
        ) -> "FieldUtils.JsonExtract":
            if obj is None:
                return None
            return FieldUtils.JsonExtract(
                source=obj.source,
                omit_fields=obj.omit_fields,
                duplicate_prefix=obj.duplicate_prefix,
                embed_column=obj.embed_column,
            )

        def to_api_obj(self) -> CoreV1DataSourceFieldUtilsJsonExtractInner:
            return CoreV1DataSourceFieldUtilsJsonExtractInner(
                source=self.source,
                omit_fields=self.omit_fields,
                duplicate_prefix=self.duplicate_prefix,
                embed_column=self.embed_column,
            )

    unreferenced_columns: Optional["FieldUtils.UnreferencedColumns"] = None
    json_extract: Optional[List["FieldUtils.JsonExtract"]] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1DataSourceFieldUtils]) -> "FieldUtils":
        if obj is None:
            return None
        json_extract = None
        if obj.json_extract is not None:
            json_extract = [
                FieldUtils.JsonExtract.from_api_obj(item) for item in obj.json_extract
            ]
        return FieldUtils(
            unreferenced_columns=FieldUtils.UnreferencedColumns.from_api_obj(
                obj.unreferenced_columns
            ),
            json_extract=json_extract,
        )

    def to_api_obj(self) -> CoreV1DataSourceFieldUtils:
        json_extract = None
        if self.json_extract is not None:
            json_extract = [item.to_api_obj() for item in self.json_extract]
        return CoreV1DataSourceFieldUtils(
            unreferenced_columns=self.unreferenced_columns.to_api_obj(),
            json_extract=json_extract,
        )


class BronzeSpec(BaseModel):
    """
    Configuration for bronze table within a DataSource.

    Attributes:
        clustering (Optional[BronzeSpec.Clustering]):
            Describes optional liquid clustering configuration for the
            bronze table.
        bronze_table (Optional[str]):
            The name of the bronze table to create and hold the imported data.
        skip_bronze_loading (Optional[bool]):
            Indicates whether to skip the bronze loading step.
    """

    class Clustering(BaseModel):
        """
        Configuration of liquid clustering for a bronze table.

        Attributes:
            column_names (Optional[List[str]]):
                List of column names to include in liquid clustering.
            time_column (Optional[str]):
                Name of the column that holds 'time' information for
                clustering.
        """

        column_names: Optional[List[str]] = None
        time_column: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecBronzeClustering],
        ) -> "BronzeSpec.Clustering":
            if obj is None:
                return None
            return BronzeSpec.Clustering(
                column_names=obj.column_names,
                time_column=obj.time_column,
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecBronzeClustering:
            return CoreV1DataSourceSpecBronzeClustering(
                column_names=self.column_names,
                time_column=self.time_column,
            )

    clustering: Optional["BronzeSpec.Clustering"] = None
    bronze_table: Optional[str] = None
    skip_bronze_loading: Optional[bool] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1DataSourceSpecBronze]) -> "BronzeSpec":
        if obj is None:
            return None
        return BronzeSpec(
            clustering=BronzeSpec.Clustering.from_api_obj(obj.clustering),
            bronze_table=obj.bronze_table,
            skip_bronze_loading=obj.skip_bronze_loading,
        )

    def to_api_obj(self) -> CoreV1DataSourceSpecBronze:
        return CoreV1DataSourceSpecBronze(
            clustering=Helpers.maybe(lambda o: o.to_api_obj(), self.clustering),
            bronze_table=self.bronze_table,
            skip_bronze_loading=self.skip_bronze_loading,
        )


class SilverSpec(BaseModel):
    """
    Configuration for silver table in a DataSource.

    Attributes:
        bronze_tables (Optional[List[SilverSpec.BronzeTable]]):
            A list of bronze tables to be joined for silver transformation.
        pre_transform (Optional[SilverSpec.PreTransform]):
            Pretransformation configuration.
        transform (Optional[SilverSpec.Transform]):
            Transformation configuration for silver processing.
    """

    class BronzeTable(BaseModel):
        """
        Reference to a bronze table for a silver table.

        Attributes:
            name (Optional[str]):
                Name of the bronze table.
            streaming (Optional[bool]):
                True if the input should be streamed from the bronze table.
            watermark (Optional[SilverSpec.BronzeTable.Watermark]):
                Bronze table watermark.
            alias (Optional[str]):
                Alias name for the table.
            join_type (Optional[str]):
                How to join to the preceding table.
            join_expr (Optional[str]):
                The join condition expression.
        """

        class Watermark(BaseModel):
            """
            Watermark for a bronze source table within a silver table.

            Attributes:
                event_time_column (Optional[str]):
                    Which column is the event time for the delay threshold.
                delay_threshold (Optional[str]):
                    A time duration string for the watermark delay.
                drop_duplicates (Optional[List[str]]):
                    Columns to pass to pyspark dropDuplicates.
            """

            event_time_column: Optional[str] = None
            delay_threshold: Optional[str] = None
            drop_duplicates: Optional[List[str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1DataSourceSpecSilverBronzeTablesInnerWatermark],
            ) -> "SilverSpec.BronzeTable.Watermark":
                if obj is None:
                    return None
                return SilverSpec.BronzeTable.Watermark(
                    event_time_column=obj.event_time_column,
                    delay_threshold=obj.delay_threshold,
                    drop_duplicates=obj.drop_duplicates,
                )

            def to_api_obj(
                self,
            ) -> CoreV1DataSourceSpecSilverBronzeTablesInnerWatermark:
                return CoreV1DataSourceSpecSilverBronzeTablesInnerWatermark(
                    event_time_column=self.event_time_column,
                    delay_threshold=self.delay_threshold,
                    drop_duplicates=self.drop_duplicates,
                )

        name: Optional[str] = None
        streaming: Optional[bool] = None
        watermark: Optional["SilverSpec.BronzeTable.Watermark"] = None
        alias: Optional[str] = None
        join_type: Optional[str] = None
        join_expr: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecSilverBronzeTablesInner],
        ) -> "SilverSpec.BronzeTable":
            if obj is None:
                return None
            return SilverSpec.BronzeTable(
                name=obj.name,
                streaming=obj.streaming,
                watermark=SilverSpec.BronzeTable.Watermark.from_api_obj(obj.watermark),
                alias=obj.alias,
                join_type=obj.join_type,
                join_expr=obj.join_expr,
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecSilverBronzeTablesInner:
            return CoreV1DataSourceSpecSilverBronzeTablesInner(
                name=self.name,
                streaming=self.streaming,
                watermark=Helpers.maybe(lambda o: o.to_api_obj(), self.watermark),
                alias=self.alias,
                join_type=self.join_type,
                join_expr=self.join_expr,
            )

    class PreTransform(BaseModel):
        """
        Pre-transform for a silver table.

        Attributes:
            use_preset (Optional[str]):
                Preset to use.
            skip_pre_transform (Optional[bool]):
                If True, skip pre-transform entirely.
            custom (Optional[SilverSpec.PreTransform.Custom]):
                Custom pretransform function and options.
            filter (Optional[str]):
                A SQL filter to apply at the beginning of the preTransform
                phase.
            post_filter (Optional[str]):
                A SQL filter to apply at the end of the preTransform phase.
            preset_overrides (Optional[SilverSpec.PreTransform.PresetOverrides]):
                Overrides for preset filters.
            add_fields (Optional[List[FieldSpec]]):
                User defined fields to add to the transformation.
        """

        class Custom(BaseModel):
            """
            Custom pre-transform function for silver table.

            Attributes:
                function (Optional[str]):
                options (Optional[Dict[str, str]]):
            """

            function: Optional[str] = None
            options: Optional[Dict[str, str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1DataSourceSpecSilverPreTransformCustom],
            ) -> "SilverSpec.PreTransform.Custom":
                if obj is None:
                    return None
                return SilverSpec.PreTransform.Custom(
                    function=obj.function,
                    options=obj.options,
                )

            def to_api_obj(self) -> CoreV1DataSourceSpecSilverPreTransformCustom:
                return CoreV1DataSourceSpecSilverPreTransformCustom(
                    function=self.function,
                    options=self.options,
                )

        class PresetOverrides(BaseModel):
            """
            Overrides for the preset.

            Attributes:
                omit_fields (Optional[List[str]]):
                    A list of fields to omit from the chosen preset.
            """

            omit_fields: Optional[List[str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1DataSourceSpecSilverPreTransformPresetOverrides],
            ) -> "SilverSpec.PreTransform.PresetOverrides":
                if obj is None:
                    return None
                return SilverSpec.PreTransform.PresetOverrides(
                    omit_fields=obj.omit_fields
                )

            def to_api_obj(
                self,
            ) -> CoreV1DataSourceSpecSilverPreTransformPresetOverrides:
                return CoreV1DataSourceSpecSilverPreTransformPresetOverrides(
                    omit_fields=self.omit_fields,
                )

        use_preset: Optional[str] = None
        skip_pre_transform: Optional[bool] = None
        custom: Optional["SilverSpec.PreTransform.Custom"] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None
        preset_overrides: Optional["SilverSpec.PreTransform.PresetOverrides"] = None
        add_fields: Optional[List[FieldSpec]] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecSilverPreTransform],
        ) -> "SilverSpec.PreTransform":
            if obj is None:
                return None
            add_fields = None
            if obj.add_fields is not None:
                add_fields = [FieldSpec.from_api_obj(item) for item in obj.add_fields]
            return SilverSpec.PreTransform(
                use_preset=obj.use_preset,
                skip_pre_transform=obj.skip_pre_transform,
                custom=SilverSpec.PreTransform.Custom.from_api_obj(obj.custom),
                filter=obj.filter,
                post_filter=obj.post_filter,
                preset_overrides=SilverSpec.PreTransform.PresetOverrides.from_api_obj(
                    obj.preset_overrides
                ),
                add_fields=add_fields,
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecSilverPreTransform:
            add_fields = None
            if self.add_fields is not None:
                add_fields = [item.to_api_obj() for item in self.add_fields]
            to_api_obj = lambda o: o.to_api_obj()
            return CoreV1DataSourceSpecSilverPreTransform(
                use_preset=self.use_preset,
                skip_pre_transform=self.skip_pre_transform,
                custom=Helpers.maybe(to_api_obj, self.custom),
                filter=self.filter,
                post_filter=self.post_filter,
                preset_overrides=Helpers.maybe(to_api_obj, self.preset_overrides),
                add_fields=add_fields,
            )

    class Transform(BaseModel):
        """
        Silver table transform.

        Attributes:
            skip_silver_transform (Optional[bool]):
                If True, skip transform entirely.
            preset_overrides (Optional[SilverSpec.Transform.PresetOverrides]):
                Preset overrides for the silver transformation.
        """

        class PresetOverrides(BaseModel):
            """
            Overrides for preset transform settings.

            Attributes:
                modify_tables (Optional[List[SilverSpec.Transform.PresetOverrides.ModifyTables]]):
                    Modifications forexisting tables.
                omit_tables (Optional[List[str]]):
                    A list of tables to omit from the preset.
                add_tables (Optional[List[SilverSpec.Transform.PresetOverrides.AddTables]]):
                    User defined tables to include in the transformation.
            """

            class Custom(BaseModel):
                """
                Custom function for use in silver table transform.

                Attributes:
                    function (Optional[str]):
                    options (Optional[Dict[str, str]]):
                """

                function: Optional[str] = None
                options: Optional[Dict[str, str]] = None

                @staticmethod
                def from_api_obj(
                    obj: Optional[
                        CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom
                    ],
                ) -> "SilverSpec.Transform.PresetOverrides.Custom":
                    if obj is None:
                        return None
                    return SilverSpec.Transform.PresetOverrides.Custom(
                        function=obj.function,
                        options=obj.options,
                    )

                def to_api_obj(
                    self,
                ) -> CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom:
                    return CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom(
                        function=self.function,
                        options=self.options,
                    )

            class ModifyTables(BaseModel):
                """
                Table modifications as part of a silver transform.

                Attributes:
                    name (Optional[str]):
                    custom (Optional[SilverSpec.Transform.PresetOverrides.Custom]):
                    omit_fields (Optional[List[str]]):
                    override_liquid_columns (Optional[List[str]]):
                    add_fields (Optional[List[FieldSpec]]):
                    filter (Optional[str]):
                    post_filter (Optional[str]):
                    utils (Optional[FieldUtils]):
                """

                name: Optional[str] = None
                custom: Optional["SilverSpec.Transform.PresetOverrides.Custom"] = None
                omit_fields: Optional[List[str]] = None
                override_liquid_columns: Optional[List[str]] = None
                add_fields: Optional[List[FieldSpec]] = None
                filter: Optional[str] = None
                post_filter: Optional[str] = None
                utils: Optional[FieldUtils] = None

                @staticmethod
                def from_api_obj(
                    obj: Optional[
                        CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInner
                    ],
                ) -> "SilverSpec.Transform.PresetOverrides.ModifyTables":
                    if obj is None:
                        return None
                    add_fields = None
                    if obj.add_fields is not None:
                        add_fields = [
                            FieldSpec.from_api_obj(item) for item in obj.add_fields
                        ]
                    return SilverSpec.Transform.PresetOverrides.ModifyTables(
                        name=obj.name,
                        custom=SilverSpec.Transform.PresetOverrides.Custom.from_api_obj(
                            obj.custom
                        ),
                        omit_fields=obj.omit_fields,
                        override_liquid_columns=obj.override_liquid_columns,
                        add_fields=add_fields,
                        filter=obj.filter,
                        post_filter=obj.post_filter,
                        utils=FieldUtils.from_api_obj(obj.utils),
                    )

                def to_api_obj(
                    self,
                ) -> (
                    CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInner
                ):
                    add_fields = None
                    if self.add_fields is not None:
                        add_fields = [item.to_api_obj() for item in self.add_fields]
                    to_api_obj = lambda o: o.to_api_obj()
                    return CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInner(
                        name=self.name,
                        custom=Helpers.maybe(to_api_obj, self.custom),
                        omit_fields=self.omit_fields,
                        override_liquid_columns=self.override_liquid_columns,
                        add_fields=add_fields,
                        filter=self.filter,
                        post_filter=self.post_filter,
                        utils=Helpers.maybe(to_api_obj, self.utils),
                    )

            class AddTables(BaseModel):
                """
                Tables to add during a silver table transform.

                Attributes:
                    custom (Optional[SilverSpec.Transform.PresetOverrides.Custom]):
                    name (Optional[str]):
                    filter (Optional[str]):
                    post_filter (Optional[str]):
                    override_liquid_columns (Optional[List[str]]):
                    fields (Optional[List[FieldSpec]]):
                    utils (Optional[FieldUtils]):
                """

                custom: Optional["SilverSpec.Transform.PresetOverrides.Custom"] = None
                name: Optional[str] = None
                filter: Optional[str] = None
                post_filter: Optional[str] = None
                override_liquid_columns: Optional[List[str]] = None
                fields: Optional[List[FieldSpec]] = None
                utils: Optional[FieldUtils] = None

                @staticmethod
                def from_api_obj(
                    obj: Optional[
                        CoreV1DataSourceSpecSilverTransformPresetOverridesAddTablesInner
                    ],
                ) -> "SilverSpec.Transform.PresetOverrides.AddTables":
                    if obj is None:
                        return None
                    fields = None
                    if obj.fields is not None:
                        fields = [FieldSpec.from_api_obj(item) for item in obj.fields]
                    return SilverSpec.Transform.PresetOverrides.AddTables(
                        custom=SilverSpec.Transform.PresetOverrides.Custom.from_api_obj(
                            obj.custom
                        ),
                        name=obj.name,
                        filter=obj.filter,
                        post_filter=obj.post_filter,
                        override_liquid_columns=obj.override_liquid_columns,
                        fields=fields,
                        utils=FieldUtils.from_api_obj(obj.utils),
                    )

                def to_api_obj(
                    self,
                ) -> CoreV1DataSourceSpecSilverTransformPresetOverridesAddTablesInner:
                    fields = None
                    if self.fields is not None:
                        fields = [item.to_api_obj() for item in self.fields]
                    to_api_obj = lambda o: o.to_api_obj()
                    return CoreV1DataSourceSpecSilverTransformPresetOverridesAddTablesInner(
                        custom=Helpers.maybe(to_api_obj, self.custom),
                        name=self.name,
                        filter=self.filter,
                        post_filter=self.post_filter,
                        override_liquid_columns=self.override_liquid_columns,
                        fields=fields,
                        utils=Helpers.maybe(to_api_obj, self.utils),
                    )

            modify_tables: Optional[
                List["SilverSpec.Transform.PresetOverrides.ModifyTables"]
            ] = None
            omit_tables: Optional[List[str]] = None
            add_tables: Optional[
                List["SilverSpec.Transform.PresetOverrides.AddTables"]
            ] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1DataSourceSpecSilverTransformPresetOverrides],
            ) -> "SilverSpec.Transform.PresetOverrides":
                if obj is None:
                    return None
                modify_tables = None
                if obj.modify_tables is not None:
                    modify_tables = [
                        SilverSpec.Transform.PresetOverrides.ModifyTables.from_api_obj(
                            item
                        )
                        for item in obj.modify_tables
                    ]
                add_tables = None
                if obj.add_tables is not None:
                    add_tables = [
                        SilverSpec.Transform.PresetOverrides.AddTables.from_api_obj(
                            item
                        )
                        for item in obj.add_tables
                    ]
                return SilverSpec.Transform.PresetOverrides(
                    modify_tables=modify_tables,
                    omit_tables=obj.omit_tables,
                    add_tables=add_tables,
                )

            def to_api_obj(self) -> CoreV1DataSourceSpecSilverTransformPresetOverrides:
                modify_tables = None
                if self.modify_tables is not None:
                    modify_tables = [item.to_api_obj() for item in self.modify_tables]
                add_tables = None
                if self.add_tables is not None:
                    add_tables = [item.to_api_obj() for item in self.add_tables]
                return CoreV1DataSourceSpecSilverTransformPresetOverrides(
                    modify_tables=modify_tables,
                    omit_tables=self.omit_tables,
                    add_tables=add_tables,
                )

        skip_silver_transform: Optional[bool] = None
        do_not_materialize: Optional[bool] = None
        preset_overrides: Optional["SilverSpec.Transform.PresetOverrides"] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecSilverTransform],
        ) -> "SilverSpec.Transform":
            if obj is None:
                return None
            return SilverSpec.Transform(
                skip_silver_transform=obj.skip_silver_transform,
                do_not_materialize=obj.do_not_materialize,
                preset_overrides=SilverSpec.Transform.PresetOverrides.from_api_obj(
                    obj.preset_overrides
                ),
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecSilverTransform:
            return CoreV1DataSourceSpecSilverTransform(
                skipSilverTransform=self.skip_silver_transform,
                doNotMaterialize=self.do_not_materialize,
                presetOverrides=Helpers.maybe(
                    lambda o: o.to_api_obj(), self.preset_overrides
                ),
            )

    bronze_tables: Optional[List["SilverSpec.BronzeTable"]] = None
    pre_transform: Optional["SilverSpec.PreTransform"] = None
    transform: Optional["SilverSpec.Transform"] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1DataSourceSpecSilver]) -> "SilverSpec":
        if obj is None:
            return None
        bronze_tables = None
        if obj.bronze_tables is not None:
            bronze_tables = [
                SilverSpec.BronzeTable.from_api_obj(item) for item in obj.bronze_tables
            ]
        return SilverSpec(
            bronze_tables=bronze_tables,
            pre_transform=SilverSpec.PreTransform.from_api_obj(obj.pre_transform),
            transform=SilverSpec.Transform.from_api_obj(obj.transform),
        )

    def to_api_obj(self) -> CoreV1DataSourceSpecSilver:
        bronze_tables = None
        if self.bronze_tables is not None:
            bronze_tables = [item.to_api_obj() for item in self.bronze_tables]
        to_api_obj = lambda o: o.to_api_obj()
        return CoreV1DataSourceSpecSilver(
            bronze_tables=bronze_tables,
            pre_transform=Helpers.maybe(to_api_obj, self.pre_transform),
            transform=Helpers.maybe(to_api_obj, self.transform),
        )


class GoldSpec(BaseModel):
    """
    Configuration for gold table in a DataSource.

    Attributes:
        omit_tables (Optional[List[str]]):
            A list of tables to omit from the preset.
        modify_tables (Optional[List[GoldSpec.ModifyTables]]):
            Modifications for existing gold table definitions.
        add_tables (Optional[List[GoldSpec.AddTables]]):
            User defined tables to add to the gold configuration.
    """

    class ModifyTables(BaseModel):
        """
        Modification to gold tables during transformation.

        Attributes:
            name (Optional[str]):
                Table name.
            source_table (Optional[str]):
                Used to match against the preset's gold stanzas input fields.
            custom (Optional[GoldSpec.ModifyTables.Custom]):
                Custom function for modifying tables.
            omit_fields (Optional[List[str]]):
                A list of fields to omit.
            add_fields (Optional[List[FieldSpec]]):
                Fields to add.
            filter (Optional[str]):
                A SQL filter to apply before processing.
            post_filter (Optional[str]):
                A SQL filter to apply after processing.
        """

        class Custom(BaseModel):
            """
            Custom function to use as part of a gold table modification.

            Attributes:
                function (Optional[str]):
                options (Optional[Dict[str, str]]):
            """

            function: Optional[str] = None
            options: Optional[Dict[str, str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[
                    CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom
                ],
            ) -> "GoldSpec.ModifyTables.Custom":
                if obj is None:
                    return None
                return GoldSpec.ModifyTables.Custom(
                    function=obj.function,
                    options=obj.options,
                )

            def to_api_obj(
                self,
            ) -> CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom:
                return CoreV1DataSourceSpecSilverTransformPresetOverridesModifyTablesInnerCustom(
                    function=self.function,
                    options=self.options,
                )

        name: Optional[str] = None
        source_table: Optional[str] = None
        custom: Optional["GoldSpec.ModifyTables.Custom"] = None
        omit_fields: Optional[List[str]] = None
        add_fields: Optional[List[FieldSpec]] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecGoldPresetOverridesModifyTablesInner],
        ) -> "GoldSpec.ModifyTables":
            if obj is None:
                return None
            add_fields = None
            if obj.add_fields is not None:
                add_fields = [FieldSpec.from_api_obj(item) for item in obj.add_fields]
            return GoldSpec.ModifyTables(
                name=obj.name,
                source_table=obj.source_table,
                custom=GoldSpec.ModifyTables.Custom.from_api_obj(obj.custom),
                omit_fields=obj.omit_fields,
                add_fields=add_fields,
                filter=obj.filter,
                post_filter=obj.post_filter,
            )

        def to_api_obj(
            self,
        ) -> CoreV1DataSourceSpecGoldPresetOverridesModifyTablesInner:
            add_fields = None
            if self.add_fields is not None:
                add_fields = [item.to_api_obj() for item in self.add_fields]
            to_api_obj = lambda o: o.to_api_obj()
            return CoreV1DataSourceSpecGoldPresetOverridesModifyTablesInner(
                name=self.name,
                source_table=self.source_table,
                custom=Helpers.maybe(to_api_obj, self.custom),
                omit_fields=self.omit_fields,
                add_fields=add_fields,
                filter=self.filter,
                post_filter=self.post_filter,
            )

    class AddTables(BaseModel):
        """
        Tables to add during gold table transformation.

        Attributes:
            custom (Optional[GoldSpec.AddTables.Custom]):
                Custom function for adding tables.
            name (Optional[str]):
                The name of the table to add.
            source_table (Optional[str]):
                The source table/dataframe for the gold table.
            filter (Optional[str]):
                A SQL filter to apply.
            post_filter (Optional[str]):
                A SQL filter to apply after processing.
            fields (Optional[List[FieldSpec]]):
                Field specifications for the new table.
        """

        class Custom(BaseModel):
            """
            Custom function for adding tables during gold transformation.

            Attributes:
                function (Optional[str]):
                options (Optional[Dict[str, str]]):
            """

            function: Optional[str] = None
            options: Optional[Dict[str, str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[
                    CoreV1DataSourceSpecGoldPresetOverridesAddTablesInnerCustom
                ],
            ) -> "GoldSpec.AddTables.Custom":
                if obj is None:
                    return None
                return GoldSpec.AddTables.Custom(
                    function=obj.function,
                    options=obj.options,
                )

            def to_api_obj(
                self,
            ) -> CoreV1DataSourceSpecGoldPresetOverridesAddTablesInnerCustom:
                return CoreV1DataSourceSpecGoldPresetOverridesAddTablesInnerCustom(
                    function=self.function,
                    options=self.options,
                )

        name: Optional[str] = None
        source_table: Optional[str] = None
        custom: Optional["GoldSpec.AddTables.Custom"] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None
        fields: Optional[List[FieldSpec]] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecGoldPresetOverridesAddTablesInner],
        ) -> "GoldSpec.AddTables":
            if obj is None:
                return None
            fields = None
            if obj.fields is not None:
                fields = [FieldSpec.from_api_obj(item) for item in obj.fields]
            return GoldSpec.AddTables(
                custom=GoldSpec.AddTables.Custom.from_api_obj(obj.custom),
                name=obj.name,
                source_table=obj.source_table,
                filter=obj.filter,
                post_filter=obj.post_filter,
                fields=fields,
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecGoldPresetOverridesAddTablesInner:
            fields = None
            if self.fields is not None:
                fields = [item.to_api_obj() for item in self.fields]
            to_api_obj = lambda o: o.to_api_obj()
            return CoreV1DataSourceSpecGoldPresetOverridesAddTablesInner(
                custom=Helpers.maybe(to_api_obj, self.custom),
                name=self.name,
                source_table=self.source_table,
                filter=self.filter,
                post_filter=self.post_filter,
                fields=fields,
            )

    omit_tables: Optional[List[str]] = None
    modify_tables: Optional[List["GoldSpec.ModifyTables"]] = None
    add_tables: Optional[List["GoldSpec.AddTables"]] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1DataSourceSpecGold]) -> "GoldSpec":
        if obj is None:
            return None
        omit_tables = None
        modify_tables = None
        add_tables = None
        if obj.preset_overrides is not None:
            omit_tables = obj.preset_overrides.omit_tables
            if obj.preset_overrides.modify_tables is not None:
                modify_tables = [
                    GoldSpec.ModifyTables.from_api_obj(item)
                    for item in obj.preset_overrides.modify_tables
                ]
            if obj.preset_overrides.add_tables is not None:
                add_tables = [
                    GoldSpec.AddTables.from_api_obj(item)
                    for item in obj.preset_overrides.add_tables
                ]
        return GoldSpec(
            omit_tables=omit_tables,
            modify_tables=modify_tables,
            add_tables=add_tables,
        )

    def to_api_obj(self) -> CoreV1DataSourceSpecGold:
        modify_tables = None
        if self.modify_tables is not None:
            modify_tables = [item.to_api_obj() for item in self.modify_tables]
        add_tables = None
        if self.add_tables is not None:
            add_tables = [item.to_api_obj() for item in self.add_tables]
        return CoreV1DataSourceSpecGold(
            preset_overrides=CoreV1DataSourceSpecGoldPresetOverrides(
                omit_tables=self.omit_tables,
                modify_tables=modify_tables,
                add_tables=add_tables,
            ),
        )


class DataSource(BaseModel):
    """
    A DataSource resource.

    Attributes:
        metadata (Optional[Metadata]):
            Standard object metadata.
        source (Optional[str]):
            The name of the originator of the data.
        source_type (Optional[str]):
            The type of data being imported.
        schedule (Optional[Schedule]):
            The schedule for data ingestion.
        custom (Optional[DataSource.CustomNotebook]):
            A custom notebook for the datasource.
        use_preset (Optional[str]):
            The name of the preset to use for this data source.
        autoloader (Optional[DataSource.Autoloader]):
            Autoloader configuration.
        bronze (Optional[BronzeSpec]):
            Bronze table configuration.
        silver (Optional[SilverSpec]):
            Silver transformation configuration.
        gold (Optional[GoldSpec]):
            Gold transformation configuration.
        status (Optional[ResourceStatus]):
            The current status of the datasource.
    """

    class CustomNotebook(BaseModel):
        """
        A custom notebook for generating data.

        Attributes:
            notebook (Optional[str]):
                Path to the notebook in the Databricks workspace.
        """

        notebook: Optional[str] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceSpecCustom],
        ) -> "DataSource.CustomNotebook":
            if obj is None:
                return None
            return DataSource.CustomNotebook(
                notebook=obj.notebook,
            )

        def to_api_obj(self) -> CoreV1DataSourceSpecCustom:
            return CoreV1DataSourceSpecCustom(
                notebook=self.notebook,
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
            cloud_files (Optional[DataSource.Autoloader.CloudFiles]):
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
            ) -> "DataSource.Autoloader.CloudFiles":
                if obj is None:
                    return None
                return DataSource.Autoloader.CloudFiles(
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
        cloud_files: Optional["DataSource.Autoloader.CloudFiles"] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[CoreV1DataSourceAutoloaderSpec],
        ) -> "DataSource.Autoloader":
            if obj is None:
                return None
            return DataSource.Autoloader(
                format=obj.format,
                location=obj.location,
                schema_file=obj.schema_file,
                cloud_files=DataSource.Autoloader.CloudFiles.from_api_obj(
                    obj.cloud_files
                ),
            )

        def to_api_obj(self) -> CoreV1DataSourceAutoloaderSpec:
            return CoreV1DataSourceAutoloaderSpec(
                format=self.format,
                location=self.location,
                schema_file=self.schema_file,
                cloud_files=Helpers.maybe(lambda o: o.to_api_obj(), self.cloud_files),
            )

    metadata: Optional[Metadata] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    schedule: Optional[Schedule] = None
    custom: Optional["DataSource.CustomNotebook"] = None
    use_preset: Optional[str] = None
    use_preset_version: Optional[int] = None
    autoloader: Optional["DataSource.Autoloader"] = None
    bronze: Optional[BronzeSpec] = None
    silver: Optional[SilverSpec] = None
    gold: Optional[GoldSpec] = None
    status: Optional[ResourceStatus] = None

    @staticmethod
    def from_api_obj(obj: CoreV1DataSource) -> "DataSource":
        return DataSource(
            metadata=Metadata.from_api_obj(obj.metadata),
            source=obj.spec.source,
            source_type=obj.spec.source_type,
            schedule=Schedule.from_api_obj(obj.spec.schedule),
            custom=DataSource.CustomNotebook.from_api_obj(obj.spec.custom),
            use_preset=obj.spec.use_preset,
            use_preset_version=obj.spec.use_preset_version,
            autoloader=DataSource.Autoloader.from_api_obj(obj.spec.autoloader),
            bronze=BronzeSpec.from_api_obj(obj.spec.bronze),
            silver=SilverSpec.from_api_obj(obj.spec.silver),
            gold=GoldSpec.from_api_obj(obj.spec.gold),
            status=ResourceStatus.from_api_obj(obj.status),
        )

    def to_api_obj(self) -> CoreV1DataSource:
        to_api_obj = lambda o: o.to_api_obj()
        return CoreV1DataSource(
            api_version="v1",
            kind="DataSource",
            metadata=Helpers.maybe(to_api_obj, self.metadata),
            spec=CoreV1DataSourceSpec(
                source=self.source,
                source_type=self.source_type,
                schedule=Helpers.maybe(to_api_obj, self.schedule),
                custom=Helpers.maybe(to_api_obj, self.custom),
                use_preset=self.use_preset,
                use_preset_version=self.use_preset_version,
                autoloader=Helpers.maybe(to_api_obj, self.autoloader),
                bronze=Helpers.maybe(to_api_obj, self.bronze),
                silver=Helpers.maybe(to_api_obj, self.silver),
                gold=Helpers.maybe(to_api_obj, self.gold),
            ),
            status=Helpers.maybe(to_api_obj, self.status),
        )
