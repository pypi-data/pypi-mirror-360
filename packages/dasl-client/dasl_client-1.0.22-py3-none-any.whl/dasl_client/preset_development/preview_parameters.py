from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, lit, udf
from dasl_client.preset_development.errors import *
import uuid
from IPython import get_ipython


@udf(StringType())
def constant_udf(*args):
    return "<sortable_random_id>"


class PreviewParameters:
    """
    This class provides three methods for supplying input records to the preset development environment.

    **1. Input Mode:**
    In "input" mode, the user provides the schema and data directly using `StructType`, `StructField`,
    and a list of tuples representing the data. For example:

    ```python
    schema = StructType([
        StructField('name', StringType(), True),
        StructField('age', IntegerType(), True)
    ])

    data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)]

    data_source = PreviewParameters() \
        .from_input() \
        .set_data_schema(schema) \
        .set_data(data)
    ```

    **2. Autoloader Mode:**
    In "autoloader" mode, input is loaded using the `cloudFiles` format and settings defined in the preset's
    `autoloader` field. The format is fetched directly from the preset, while other required options must be
    provided manually. Example:

    ```python
    ds_params = PreviewParameters() \
        .from_autoloader() \
        .set_autoloader_location("s3://test-databucket/test-data") \
        .set_pretransform_name("name_of_pretransform") \
        .set_date_range("EdgeStartTimestamp", "2024-02-15 11:27:21", "2024-02-15 11:27:25")
    ```

    If you wish to skip the Silver PreTransform stage, simply omit the `pretransform_name` setting.

    **3. Table Mode:**
    This method reads input directly from a table:

    ```python
    ds_params = DataSourceParameters(spark) \
        .from_table() \
        .set_table("system.access.audit")
    ```

    **Note:**
    When using autoloader mode, this implementation requires a location to store a temporary schema for
    the loaded records. By default, this is set to `"dbfs:/tmp/schemas"`. You can change this using
    `set_autoloader_temp_schema_location`. Regardless of whether you use the default or a custom path,
    you must have write permissions for that location.
    """

    def __init__(self, spark: SparkSession) -> None:
        """
        Initializes the PreviewParameters instance with sparse default settings.

        Note: The preset development environment is intended to process only a small number
        of records at a time. By default, the record limit is set to 10, but this can be overridden
        if needed.

        Instance Attributes:
            mode (str): Indicates the source type ("input" or "autoloader").
            record_limit (int): Maximum number of records to load. Defaults to 10.
            autoloader_temp_schema_location (str): Temporary location to store the autoloader schema.
            time_column (str): Column name used for time-based filtering.
            start_time (str): Start time for filtering.
            end_time (str): End time for filtering.
            autoloader_location (str): Filesystem location for autoloader input.
            autoloader_format (str): Format of the data for autoloader.
            schema_file (str): Path to a file containing the schema definition.
            cloudfiles_schema_hints_file (str): Path to a file containing CloudFiles schema hints.
            cloudfiles_schema_hints (str): Directly provided CloudFiles schema hints.
            schema_uuid_str (str): Unique identifier for the schema (used in the autoloader schema path).
            schema (StructType): Schema definition for input data.
            data (dict): In-memory data used to create a DataFrame in "input" mode.
            pretransform_name (str): Name of the pre-transformation step.
            df (DataFrame): Internal Spark DataFrame loaded using the specified parameters.
        """
        self._spark = spark
        self._mode = None  # [input, autoloader]
        self._record_limit = 10
        self._autoloader_temp_schema_location = "dbfs:/tmp/schemas"

        self._time_column = None
        self._start_time = None
        self._end_time = None

        self._autoloader_location = None
        self._autoloader_format = None
        self._schema_file = None
        self._clouldfiles_schema_hints_file = None
        self._cloudfiles_schema_hints = None
        self._cloudfiles_reader_case_sensitive = "true"
        self._cloudfiles_multiline = "true"
        self._schema_uuid_str = str(uuid.uuid4())

        self._schema = None
        self._data = None

        self._table = None

        self._pretransform_name = None
        self._bronze_pre_transform: Optional[List[str]] = None

        self._df = None

    def __enter__(self):
        """
        Creates a DataFrame with data using the method specified. In the case of "autoloader",
        this will stream to a DataFrame that is then treated as a batch. This allows for easier
        emulation of some operations, while not giving up some of the options allowed by
        streaming.

        Returns:
            DataFrame: The resulting DataFrame with input data.
        """
        if self._mode == "input":
            self._df = self._spark.createDataFrame(self._data, self._schema)
        elif self._mode == "table":
            self._df = self._spark.table(self._table).limit(self._record_limit)
        elif self._mode == "autoloader":
            stream_df = (
                self._spark.readStream.format("cloudFiles")
                .option("cloudFiles.format", self._autoloader_format)
                .option("multiline", self._cloudfiles_multiline)
                .option("readerCaseSensitive", self._cloudfiles_reader_case_sensitive)
            )

            if self._schema_file:
                with open(self._schema_file, "r") as f:
                    stream_df = stream_df.schema(f.read().strip())
            else:
                stream_df = (
                    stream_df.option("inferSchema", "true")
                    .option("cloudFiles.inferColumnTypes", "true")
                    .option(
                        "cloudFiles.schemaLocation",
                        f"{self._autoloader_temp_schema_location}/{self._schema_uuid_str}",
                    )
                )

            if self._cloudfiles_schema_hints:
                stream_df = stream_df.option(
                    "cloudFiles.schemaHints", self._cloudfiles_schema_hints
                )
            elif self._clouldfiles_schema_hints_file:
                stream_df = stream_df.option(
                    "cloudFiles.schemaHintsFile", self._clouldfiles_schema_hints_file
                )

            stream_df = stream_df.load(self._autoloader_location).limit(
                self._record_limit
            )

            if self._bronze_pre_transform is not None:
                stream_df = stream_df.selectExpr(*self._bronze_pre_transform)

            query = (
                stream_df.writeStream.format("memory")
                .queryName("batch_data")
                .trigger(availableNow=True)
                .start()
            )

            query.awaitTermination()

            self._df = self._spark.table("batch_data")

        if self._time_column:
            self._df = self._df.filter(
                f"timestamp({self._time_column}) >= timestamp('{self._start_time}') AND timestamp({self._time_column}) < timestamp('{self._end_time}')"
            )

        self._df = self._df.withColumn("dasl_id", constant_udf())

        return self._df

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleans up the temporary schema created for streaming mode, if it was created.
        """

        # Get the Databricks built-in functions out the namespace.
        ipython = get_ipython()
        if ipython is not None:
            dbutils = ipython.user_ns["dbutils"]

            dbutils.fs.rm(
                f"{self._autoloader_temp_schema_location}/{self._schema_uuid_str}",
                recurse=True,
            )
        else:
            print(
                f"FYI, we are leaking temp data {self._autoloader_temp_schema_location}/{self._schema_uuid_str}"
            )

    def from_input(self):
        """
        Set the data source loader to "input" mode. Requires a schema and data to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "input"
        return self

    def from_autoloader(self):
        """
        Set the data source loader to "autoloader" mode. Requires at least autoloader location
        to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "autoloader"
        return self

    def from_table(self):
        """
        Set the data source loader to "table" mode. Requires a table name to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "table"
        return self

    def set_autoloader_temp_schema_location(self, path: str):
        """
        Set the location for the autoloader's streaming mode schema to be created. This is
        deleted at the end of a run.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._autoloader_temp_schema_location = path
        return self

    def set_data_schema(self, schema: StructType):
        """
        Set the input schema for "input" mode. For example:

        StructType([
            StructField('name', StringType(), True),
            StructField('age', IntegerType(), True)
        ])

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._schema = schema
        return self

    def set_data(self, data: Dict[str, str]):
        """
        Set the input data for "input" mode. For example:

        [("Peter", 15), ("Urvi", 13), ("Graeme", 8)]

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._data = data
        return self

    def set_autoloader_location(self, location: str):
        """
        Set where to load data from for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._autoloader_location = location
        return self

    def set_autoloader_format(self, file_format: str):
        """
        Used internally to set the autoloader format.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        if file_format.lower() == "jsonl":
            self._autoloader_format = "json"
            self.set_autoloader_multiline(False)
            return self
        self._autoloader_format = file_format
        return self

    def set_autoloader_schema_file(self, path: str):
        """
        Set the schema file path for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._schema_file = path
        return self

    def set_autoloader_cloudfiles_schema_hint_file(self, path: str):
        """
        Set the cloudFiles schema hints file path for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._clouldfiles_schema_hints_file = path
        return self

    def set_autoloader_cloudfiles_schema_hints(self, cloudfiles_schema_hints: str):
        """
        Set the cloudFiles schema hints string for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._cloudfiles_schema_hints = cloudfiles_schema_hints
        return self

    def set_autoloader_reader_case_sensitive(self, b: bool):
        """
        Set the cloudFiles reader case-sensitive boolean for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._cloudfiles_reader_case_sensitive = "true" if b else "false"
        return self

    def set_autoloader_multiline(self, b: bool):
        """
        Set the cloudFiles multiline boolean for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._cloudfiles_multiline = "true" if b else "false"
        return self

    def set_pretransform_name(self, pretransform_name: str):
        """
        Set the pretransform name to use, if desired. If not set, Silver PreTransform
        will be skipped.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._pretransform_name = pretransform_name
        return self

    def set_bronze_pre_transform(self, expr: List[str]):
        """
        Sets a pre-transform expression that will run before data is written to bronze

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._bronze_pre_transform = expr
        return self

    def set_date_range(self, column: str, start_time: str, end_time: str):
        """
        Set the TIMESTAMP column and date range to use as the input data filter to
        limit the number of records retrieved by the loader.

        Both start and end time must be TIMESTAMP compatible.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._time_column = column
        self._start_time = start_time
        self._end_time = end_time
        return self

    def set_input_record_limit(self, record_limit: int):
        """
        Set the LIMIT clause when retrieving records from the data source.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._record_limit = record_limit
        return self

    def set_table(self, table_name: str):
        """
        Set Unity Catalog table name for "table" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._table = table_name
        return self
