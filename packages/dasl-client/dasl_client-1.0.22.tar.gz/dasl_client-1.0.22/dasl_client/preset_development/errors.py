from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from typing import Dict, Any, List, Mapping, Tuple
from IPython import get_ipython


class PresetError(Exception):
    pass


class InvalidGoldTableSchemaError(PresetError):
    def __init__(self, schema: str, additional_message: str = ""):
        self.schema = schema
        message = (
            f"Malformed gold schema provided {schema}. {additional_message}".strip()
        )
        super().__init__(message)


class NoSilverStageProvdedError(PresetError):
    def __init__(self, additional_msg: str = ""):
        message = f"No silver stage provided{additional_msg}."
        super().__init__(message)


class NoSilverTransformStageProvdedError(PresetError):
    def __init__(
        self,
        message: str = "No silver transform stage provided, but gold stage is present.",
    ):
        super().__init__(message)


class PreTransformNotFound(PresetError):
    def __init__(
        self,
        message: str = "Requested silver pretransform name not found in preset's silver pretransforms.",
    ):
        super().__init__(message)


class NoSilverPreTransformStageProvdedError(PresetError):
    def __init__(
        self,
        message: str = "No silver transform stage provided, but prestransform name provided.",
    ):
        super().__init__(message)


class MissingTableFieldError(PresetError):
    def __init__(self, layer: str, table_name: str, field_name: str):
        self.layer = layer
        self.table_name = table_name
        self.field_name = field_name
        message = f"{layer} stage {table_name} is missing {field_name} field."
        super().__init__(message)


class DuplicateFieldNameError(PresetError):
    def __init__(self, stage: str, stage_name: str, field_name: str):
        self.stage = stage
        self.stage_name = stage_name
        self.field_name = field_name
        message = f"Duplicate field specification name found in {stage} stage {stage_name} named {field_name}."
        super().__init__(message)


class MalformedFieldError(PresetError):
    def __init__(self, stage: str, stage_name: str, field_name: str):
        self.stage = stage
        self.stage_name = stage_name
        self.field_name = field_name
        message = f"Please provide 1 operation only in {stage} stage {stage_name}'s field specification named {field_name}."
        super().__init__(message)


class MissingFieldNameError(PresetError):
    def __init__(self, stage: str, stage_name: str):
        self.stage = stage
        self.stage_name = stage_name
        message = (
            f"Field specification in {stage} stage {stage_name} missing name field."
        )
        super().__init__(message)


class MissingSilverKeysError(PresetError):
    def __init__(self, missing_keys: str):
        self.missing_keys = missing_keys
        message = f"Gold table/s have no corresponding input from silver table/s: {missing_keys}"
        super().__init__(message)


class MissingAutoloaderConfigError(PresetError):
    def __init__(
        self,
        message: str = "Autoloader mode selected, but no autoloader configuration found in preset.autoloader.",
    ):
        super().__init__(message)


class AutoloaderMissingFieldError(PresetError):
    def __init__(self, field_name: str):
        self.field_name = field_name
        message = f"Autoloader mode selected, but missing field {field_name} in preset."
        super().__init__(message)


class UnknownGoldTableError(PresetError):
    def __init__(self, table_name: str, schema: str):
        self.table_name = table_name
        self.schema = schema
        message = (
            f"The referenced Gold table name {table_name} does not exist in {schema}."
        )
        super().__init__(message)


class GoldTableCompatibilityError(PresetError):
    def __init__(self, message: str):
        super().__init__(message)


class ReferencedColumnMissingError(PresetError):
    def __init__(self, operation: str, column_name: str):
        self.operation = operation
        self.column_name = column_name
        message = f"The referenced column {column_name} was not found in the dataframe during {operation} operation."
        super().__init__(message)


class MissingJoinFieldError(PresetError):
    def __init__(self, field_name: str):
        self.field_name = field_name
        message = f"Join operation is missing required field {field_name}."
        super().__init__(message)


class MissingUtilityConfigurationFieldError(PresetError):
    def __init__(self, operation: str, field_name: str):
        self.operation = operation
        self.field_name = field_name
        message = f"The required configuration field {field_name} was not suppled in the {operation} operation."
        super().__init__(message)


class AssertionFailedError(PresetError):
    def __init__(self, expr: str, assertion_message: str, df: DataFrame):
        # Get the Databricks built-in functions out the namespace.
        ipython = get_ipython()
        if ipython is not None:
            display = ipython.user_ns["display"]
        else:
            display = lambda x: x.show()

        self.expr = expr
        self.assertion_message = assertion_message
        self.df = df
        message = f"The above rows failed the assertion expression {expr} with reason: {assertion_message}\n"
        display(df)
        super().__init__(message)
