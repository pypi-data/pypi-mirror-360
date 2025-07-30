from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import lit, col as col_, sum as sum_, when
from dasl_client.preset_development.preview_parameters import *
from dasl_client.preset_development.stage import *
from dasl_client.preset_development.errors import *
import yaml
from IPython import get_ipython


class PreviewEngine:
    """
    This class deserializes the in-development preset's YAML and performs a series of
    validation steps before attempting to compile each stage's table and execute them
    based on the provided PreviewParameters.

    Upon successful execution, output is generated for each successfully executed
    stage's table operations. Additionally, if Gold stages are computed, their outputs
    are validated against the provided Gold stage tables to ensure compatibility on a
    per-table-name basis with the Unity Catalog.

    For example, a preset Gold stage table named "http_activity" will be checked against
    the corresponding table in the Unity Catalog schema—also named "http_activity" to
    confirm that inserting into the Unity Catalog most likely not cause errors.
    """

    def __init__(
        self, spark: SparkSession, preset_yaml_str: str, ds_params: PreviewParameters
    ):
        """
        Creates the PreviewEngine using the given preset YAML and datasource parameters.
        The YAML is deserialized here and checked to verify whether the requested
        pretransform name, if provided, exists in the preset.

        Instance Attributes:
            ds_params (PreviewParameters): The input datasource's configuration.
            preset (Dict[str, Any]): The deserialized preset YAML.
            pretransform_name (str): The name of the requested pretransform. Defaults to None.
            pre (Stage): Stores the pretransform Stage object internally.
            silver (List[Stage]): Stores the Silver Stage objects internally.
            gold (List[Stage]): Stores the Gold Stage objects internally.
        """
        self._spark = spark
        self._ds_params = ds_params
        self._preset = yaml.safe_load(preset_yaml_str)
        self._pretransform_name = ds_params._pretransform_name

        self._validate_gold_inputs(
            self._preset.get("silver", None), self._preset.get("gold", None)
        )
        if self._pretransform_name:
            self._validate_pretransform_name(
                self._preset.get("silver", None), self._pretransform_name
            )

        self._bronze = None
        self._pre = None
        self._silver = []
        self._gold = []
        self._result_df_map: Tuple[
            DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]
        ] = (None, {}, {})

    def _validate_pretransform_name(
        self, silver: Dict[str, str], pretransform_name: str
    ) -> None:
        """
        Validates the given pretransform name exists in the provided preset's Silver
        PreTransform stages.
        """
        if not silver:
            raise NoSilverStageProvdedError(", but pretransform name provided")
        if not (silver_pre_transform := silver.get("preTransform", None)):
            raise NoSilverPreTransformStageProvdedError()
        silver_pre_output_names = []
        for table in silver_pre_transform:
            if not (name := table.get("name", None)):
                raise MissingTableFieldError(
                    "Silver pretransform",
                    table.get("name", "<stage missing name>"),
                    "name",
                )
            silver_pre_output_names += [name]
        if pretransform_name not in silver_pre_output_names:
            raise PreTransformNotFound()

    def _validate_gold_inputs(
        self, silver: Dict[str, str], gold: Dict[str, str]
    ) -> None:
        """
        Validate gold tables all have a silver table to input from.
        """
        if not gold:
            return

        if not len(gold):
            return

        if not silver:
            raise NoSilverStageProvdedError(", but gold stage is present")

        gold_input_names = []
        for table in gold:
            if not (input := table.get("input", None)):
                raise MissingTableFieldError(
                    "Gold", table.get("name", "<stage missing name>"), "input"
                )
            gold_input_names += [input]

        if not (silver_transform := silver.get("transform", None)):
            raise NoSilverTransformStageProvdedError()
        silver_output_names = []
        for table in silver_transform:
            if not (name := table.get("name", None)):
                raise MissingTableFieldError(
                    "Silver transform", table.get("name", ""), "name"
                )
            silver_output_names += [name]

        missing_keys = set(gold_input_names) - set(silver_output_names)
        if missing_keys:
            raise MissingSilverKeysError(missing_keys)

    def _compile_stages(self) -> None:
        """
        Creates Stage objects, setting pretransform to None if not provided.
        """
        pretransform = None
        if self._pretransform_name:
            for table in self._preset["silver"]["preTransform"]:
                if table["name"] == self._pretransform_name:
                    self._pre = Stage(self._spark, "silver pretransform", table)
                    break

        self._silver = [
            Stage(self._spark, "silver transform", table)
            for table in self._preset.get("silver", {}).get("transform", [])
        ]
        self._gold = [
            Stage(self._spark, "gold", table) for table in self._preset.get("gold", [])
        ]

    def _run(
        self, df: DataFrame
    ) -> Tuple[DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]]:
        """
        Runs all stages, in medallion stage order. This allows prior stage outputs to feed
        into later stage inputs.

        Returns:
            Dataframes containing the output from each run Stage.
        """
        if self._pre:
            df = self._pre.run(df)

        silver_output_map = {}
        for table in self._silver:
            silver_output_map[table._name] = table.run(df)

        gold_output_map = {}
        for table in self._gold:
            # We store as gold_name/silver_input to prevent clobbering on duplicate gold table use.
            gold_output_map[f"{table._name}/{table._input}"] = table.run(
                silver_output_map[table._input]
            )

        return (
            (df, silver_output_map, gold_output_map)
            if self._pre
            else (None, silver_output_map, gold_output_map)
        )

    def _render_output(
        self,
        input_df: DataFrame,
        stage_dataframes: Tuple[DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]],
        gold_table_catalog: str,
        gold_table_schema: str,
    ) -> None:
        """
        Displays formatted HTML output from executed Stages' DataFrames.
        """
        # TODO: Investigate further into using Databricks's style sheets here.

        # Get the Databricks built-in functions out the namespace.
        ipython = get_ipython()
        if ipython is not None:
            displayHTML = ipython.user_ns["displayHTML"]
            display = ipython.user_ns["display"]
        else:
            displayHTML = lambda x: print(x)
            display = lambda x: x.show()

        def d(txt, lvl) -> None:
            displayHTML(
                f"""
                <div style="background-color: 
                background-color: rgb(18, 23, 26); padding: 0; margin: 0;">
                    <h{lvl} style="margin: 0; background-color: rgb(244, 234, 229);">{txt}</h{lvl}>
                </div>
                """
            )

        def check_struct_compatibility(
            target_field: StructField, df_field: StructField, prefix=""
        ):
            if not (
                isinstance(target_field.dataType, StructType)
                and isinstance(df_field.dataType, StructType)
            ):
                return

            target_fields = {
                field.name: field for field in target_field.dataType.fields
            }
            for field in df_field.dataType.fields:
                if field.name not in target_fields:
                    raise GoldTableCompatibilityError(
                        f"Extra field found in gold stage output STRUCT column {prefix}{target_field.name}: {field.name}"
                    )
                else:
                    if isinstance(field.dataType, StructType):
                        check_struct_compatibility(
                            target_fields[field.name],
                            field,
                            prefix=prefix + target_field.name + ".",
                        )

        (pre_df, silver, gold) = stage_dataframes
        d("Input", 1)
        display(input_df)
        d("Silver Pre-Transform", 1)
        if pre_df:
            display(pre_df)
        else:
            d("Skipped", 2)
        d("Silver Transform", 1)
        for name, df in silver.items():
            d(f"{name}", 2)
            display(df)
        d("Gold", 1)
        for name, df in gold.items():
            d(f"{name}", 2)
            d("Stage output", 3)
            display(df)

            # NOTE: Name is stored as Gold_name/Silver_input. So we need to get just the Gold table
            # name that we are comparing the dataframe metadata to.
            name = name.split("/")[0]
            fqn_gold_table_name = f"{self.force_apply_backticks(gold_table_catalog)}.{self.force_apply_backticks(gold_table_schema)}.{self.force_apply_backticks(name)}"

            if not self._spark.catalog.tableExists(f"{fqn_gold_table_name}"):
                raise UnknownGoldTableError(name, gold_table_schema)

            # Performs the type check.
            delta_df = self._spark.table(f"{fqn_gold_table_name}").limit(0)
            unioned_df = delta_df.unionByName(df, allowMissingColumns=True)

            # Now we check no new columns.
            if not set(df.columns).issubset(delta_df.columns):
                raise GoldTableCompatibilityError(
                    f"Extra columns provided: {', '.join([col for col in df.columns if col not in delta_df.columns])}"
                )

            # Now we check no new fields in STRUCT columns.
            for field in delta_df.schema.fields:
                if isinstance(field.dataType, StructType) and field.name in df.columns:
                    # Retrieve the corresponding field from the DataFrame's schema.
                    df_field = next(f for f in df.schema.fields if f.name == field.name)
                    check_struct_compatibility(field, df_field)

            # Check nullable columns exist, and data what we are inserting is set.
            non_nullable_cols = [
                field.name for field in delta_df.schema.fields if not field.nullable
            ]
            null_checks = [
                sum_(when(col_(col).isNull(), 1).otherwise(0)).alias(col)
                for col in non_nullable_cols
            ]
            null_counts = df.select(null_checks).collect()[0].asDict()
            cols_with_nulls = []
            try:
                cols_with_nulls = [
                    col_name for col_name, count in null_counts.items() if count > 0
                ]
            except TypeError:
                # There were no records returned and so null_counts == None.
                pass
            if cols_with_nulls:
                raise GoldTableCompatibilityError(
                    f"Record with null data found for non-nullable columns: {', '.join([col for col in cols_with_nulls])}"
                )

            d("Resultant gold table preview", 3)
            display(unioned_df)

    def is_backtick_escaped(self, name: str) -> bool:
        """
        check if a given (column) name is backtick escaped or not
        :param name: column name
        :return: bool
        """
        return name.startswith("`") and name.endswith("`")

    def force_apply_backticks(self, name: str) -> str:
        """
        forces application of backticks to the given (column) name as a single unit
        if it already has backticks this is a noop
        :param name: column name
        :return: str
        """
        if self.is_backtick_escaped(name):
            return name
        return f"`{name}`"

    def evaluate(self, gold_table_schema: str, display: bool = True) -> None:
        """
        Evaluates the loaded preset YAML using the input datasource configuration to load
        records. Finally, checks that the output from the Gold stages is compatible with
        the Unity Catalog Gold tables.
        """
        s = gold_table_schema.split(".")
        if len(s) != 2:
            raise InvalidGoldTableSchemaError(gold_table_schema)
        catalog_name = s[0].lstrip("`").rstrip("`")
        schema_name = s[1].lstrip("`").rstrip("`")
        if any(
            row.catalog == catalog_name
            for row in self._spark.sql("SHOW CATALOGS").collect()
        ):
            if not any(
                row.databaseName == schema_name
                for row in self._spark.sql(
                    f"SHOW SCHEMAS IN `{catalog_name}`"
                ).collect()
            ):
                raise InvalidGoldTableSchemaError(
                    gold_table_schema,
                    f"Schema {schema_name} not found in catalog {catalog_name} or insufficient permissions.",
                )
        else:
            raise InvalidGoldTableSchemaError(
                gold_table_schema,
                f"Catalog {catalog_name} not found or insufficient permissions.",
            )

        # If we are using the autoloader, fetch format from preset and others.
        if self._ds_params._mode == "autoloader":
            if not (autoloader_conf := self._preset.get("autoloader", None)):
                raise MissingAutoloaderConfigError()
            if not (file_format := autoloader_conf.get("format", None)):
                raise AutoloaderMissingFieldError("format")
            self._ds_params.set_autoloader_format(file_format)
            if schemaFile := autoloader_conf.get("schemaFile", None):
                self._ds_params.set_autoloader_schema_file(schemaFile)
            if multiline := autoloader_conf.get("multiline", None):
                if multiline == "true":
                    self._ds_params.set_multiline(True)
                else:
                    self._ds_params.set_multiline(False)
            if cloudFiles := autoloader_conf.get("cloudFiles", None):
                if schema_hints := cloudFiles.get("schemaHints", None):
                    self._ds_params.set_autoloader_cloudfiles_schema_hints(schema_hints)
                if schema_hints_file := cloudFiles.get("schemaHintsFile", None):
                    self._ds_params.set_autoloader_cloudfiles_schema_hint_file(
                        schema_hints_file
                    )

        self._compile_stages()

        with self._ds_params as df:
            self._bronze = df
            self._result_df_map = self._run(df)
            if display:
                self._render_output(
                    df,
                    self._result_df_map,
                    self.force_apply_backticks(catalog_name),
                    self.force_apply_backticks(schema_name),
                )

    def results(
        self,
    ) -> Tuple[DataFrame, DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]]:
        return self._bronze, *self._result_df_map
